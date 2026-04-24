"""
KONTRAX AI — Core Agent Logic
Handles: Clause Integrity Checking + Red-Flag Scanning
PDF parsing via pypdf (no llama_index dependency required)
"""

import json
import os
import re
import hashlib
import datetime
from pathlib import Path

import google.generativeai as genai
from dotenv import load_dotenv

# ── Setup ──────────────────────────────────────────────────────────────────────
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise EnvironmentError(
        "GEMINI_API_KEY not found. Create a .env file with GEMINI_API_KEY=your_key"
    )
genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-2.5-flash-lite")

# ── Load Mock Data ─────────────────────────────────────────────────────────────
MOCK_DIR = Path(__file__).parent / "mock_data"

with open(MOCK_DIR / "integrity_checklist.json", encoding="utf-8") as f:
    CHECKLIST = json.load(f)

with open(MOCK_DIR / "mock_watchlist.json", encoding="utf-8") as f:
    WATCHLIST = json.load(f)


# ═══════════════════════════════════════════════════════════════════════════════
# UTILITY FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def extract_pdf_text(uploaded_file) -> str:
    """
    Extract text from uploaded PDF using pypdf.
    Falls back gracefully if extraction fails.
    """
    try:
        import pypdf
        reader = pypdf.PdfReader(uploaded_file)
        pages_text = []
        for page in reader.pages:
            text = page.extract_text()
            if text:
                pages_text.append(text)
        full_text = "\n".join(pages_text)
        if not full_text.strip():
            return ""
        return full_text
    except Exception as e:
        return f"[PDF_EXTRACTION_ERROR: {str(e)}]"


def parse_json_safely(raw: str) -> dict:
    """Strip markdown fences and parse JSON robustly."""
    # Remove ```json ... ``` or ``` ... ```
    cleaned = re.sub(r"```(?:json)?\s*", "", raw).replace("```", "").strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        # Try to find JSON object/array within the text
        match = re.search(r"\{.*\}", cleaned, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except Exception:
                pass
    return {}


def hash_text(text: str) -> str:
    """Generate short SHA-256 hash for audit trail."""
    return hashlib.sha256(text.encode()).hexdigest()[:12]


def get_timestamp() -> str:
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# ═══════════════════════════════════════════════════════════════════════════════
# MODULE 1: CLAUSE INTEGRITY CHECKER
# ═══════════════════════════════════════════════════════════════════════════════

def check_clause_integrity(contract_text: str, language: str = "EN") -> dict:
    """
    Analyze contract/clause text against the integrity checklist.
    Returns structured findings with scores, missing clauses, and suggestions.
    """
    clauses = CHECKLIST["mandatory_clauses"]
    weak_patterns = CHECKLIST["weak_language_patterns"]
    scoring = CHECKLIST["scoring"]

    # ── Step 1: Rule-based keyword scan ───────────────────────────────────────
    text_lower = contract_text.lower()
    rule_findings = []
    score = 100  # Start at 100, deduct for issues

    for clause in clauses:
        found = any(kw.lower() in text_lower for kw in clause["keywords"])
        if not found:
            deduction = scoring["missing_mandatory"] if clause["required"] else scoring["missing_optional"]
            score += deduction  # deduction is negative
            rule_findings.append({
                "id": clause["id"],
                "name": clause["name"],
                "name_bm": clause["name_bm"],
                "status": "MISSING",
                "required": clause["required"],
                "severity": "HIGH" if clause["required"] else "MEDIUM",
                "suggestion_en": clause["suggestion_en"],
                "suggestion_bm": clause["suggestion_bm"],
                "trigger": f"Keywords not found: {', '.join(clause['keywords'][:3])}"
            })
        else:
            rule_findings.append({
                "id": clause["id"],
                "name": clause["name"],
                "name_bm": clause["name_bm"],
                "status": "PRESENT",
                "required": clause["required"],
                "severity": "OK",
                "trigger": "Keyword match found"
            })

    # ── Step 2: Weak language detection ───────────────────────────────────────
    weak_findings = []
    for pattern in weak_patterns:
        if pattern["pattern"].lower() in text_lower:
            weak_findings.append({
                "pattern": pattern["pattern"],
                "issue": pattern["issue"]
            })
            score += scoring["weak_language_per_instance"]

    score = max(0, min(100, score))

    # ── Step 3: LLM deep analysis ──────────────────────────────────────────────
    lang_instruction = (
        "Respond in Bahasa Malaysia." if language == "BM"
        else "Respond in English."
    )

    missing_clause_names = [
        f["name"] for f in rule_findings if f["status"] == "MISSING"
    ]

    llm_prompt = f"""You are a Malaysian government procurement integrity expert. Analyze this contract text for anti-corruption compliance.

{lang_instruction}

CONTRACT TEXT:
{contract_text[:4000]}

ALREADY DETECTED AS MISSING (by rule engine): {missing_clause_names}

Your task:
1. Confirm or correct the rule engine findings
2. Identify any OTHER integrity risks not covered by the rules
3. Assess the overall clause quality (language clarity, enforceability)
4. Rate the contract's anti-corruption posture

Return ONLY this JSON (no markdown fences):
{{
  "llm_assessment": "2-3 sentence overall assessment",
  "additional_risks": [
    {{"risk": "risk description", "severity": "HIGH/MEDIUM/LOW", "suggestion": "how to fix"}}
  ],
  "language_quality": "Strong/Moderate/Weak",
  "enforceability_score": 0-100,
  "top_priority_fix": "single most important change to make"
}}"""

    try:
        llm_response = model.generate_content(llm_prompt)
        llm_data = parse_json_safely(llm_response.text)
    except Exception as e:
        llm_data = {
            "llm_assessment": f"LLM analysis unavailable: {str(e)}",
            "additional_risks": [],
            "language_quality": "Unknown",
            "enforceability_score": 0,
            "top_priority_fix": "Manual review required"
        }

    # ── Step 4: Grade ──────────────────────────────────────────────────────────
    thresholds = scoring["grade_thresholds"]
    if score >= thresholds["strong"]:
        grade = "Strong"
        grade_color = "🟢"
        grade_bm = "Kuat"
    elif score >= thresholds["moderate"]:
        grade = "Moderate"
        grade_color = "🟡"
        grade_bm = "Sederhana"
    else:
        grade = "Weak"
        grade_color = "🔴"
        grade_bm = "Lemah"

    return {
        "score": score,
        "grade": grade,
        "grade_bm": grade_bm,
        "grade_color": grade_color,
        "clause_findings": rule_findings,
        "weak_language": weak_findings,
        "llm_analysis": llm_data,
        "input_hash": hash_text(contract_text),
        "timestamp": get_timestamp(),
        "mode": "clause_integrity_check"
    }


# ═══════════════════════════════════════════════════════════════════════════════
# MODULE 2: RED-FLAG SCANNER
# ═══════════════════════════════════════════════════════════════════════════════

def extract_contract_fields(text: str) -> dict:
    """
    Use Gemini to extract structured fields from contract text.
    """
    prompt = f"""You are a Malaysian procurement document parser. Extract structured data from this contract.

Return ONLY this JSON (no markdown fences, no extra text):
{{
  "vendor_name": "company name or null",
  "contract_value_rm": 0,
  "item_description": "what is being procured",
  "procurement_method": "open tender / limited tender / direct negotiation / quotation / unknown",
  "justification": "reason given for procurement method, or null",
  "contract_duration_months": 0,
  "commencement_date": "YYYY-MM-DD or null",
  "end_date": "YYYY-MM-DD or null",
  "ministry_agency": "procuring agency name or null",
  "signatories": ["name1", "name2"],
  "payment_terms": "summary of payment schedule or null",
  "variation_cap_mentioned": true/false,
  "audit_clause_mentioned": true/false,
  "beneficial_owner_mentioned": true/false
}}

CONTRACT TEXT (first 5000 chars):
{text[:5000]}"""

    try:
        response = model.generate_content(prompt)
        data = parse_json_safely(response.text)
        # Ensure numeric field is numeric
        if isinstance(data.get("contract_value_rm"), str):
            nums = re.findall(r"[\d,]+\.?\d*", data["contract_value_rm"].replace(",", ""))
            data["contract_value_rm"] = float(nums[0]) if nums else 0
        return data
    except Exception as e:
        return {"extraction_error": str(e)}


def run_red_flag_checks(contract: dict, full_text: str) -> list:
    """
    Rule-based + heuristic red flag detection.
    Each flag includes: type, severity, message, trigger, and suggested_action.
    """
    flags = []
    pep_vendors = [v["name"].lower() for v in WATCHLIST["pep_vendors"]]
    thresholds = WATCHLIST["procurement_method_thresholds"]
    high_risk_terms = WATCHLIST["high_risk_terms"]
    text_lower = full_text.lower()
    vendor = (contract.get("vendor_name") or "").lower()
    value = contract.get("contract_value_rm") or 0
    method = (contract.get("procurement_method") or "").lower()
    justification = (contract.get("justification") or "").lower()

    # ── Flag 1: PEP / Watchlist Vendor ────────────────────────────────────────
    for pep in WATCHLIST["pep_vendors"]:
        if pep["name"].lower() in vendor or pep["name"].lower() in text_lower:
            flags.append({
                "type": "WATCHLIST_MATCH",
                "severity": pep["risk_level"],
                "icon": "🔴" if pep["risk_level"] == "HIGH" else "🟡",
                "title": "Vendor on Integrity Watchlist",
                "title_bm": "Vendor dalam Senarai Pemantauan Integriti",
                "message": f"Vendor '{pep['name']}' appears on risk watchlist: {pep['reason']}",
                "trigger": f"Direct name match: '{pep['name']}'",
                "suggested_action": "Verify vendor status with SSM and MACC. Request director disclosure. Consider halting procurement pending investigation.",
                "suggested_action_bm": "Sahkan status vendor dengan SSM dan SPRM. Minta pendedahan pengarah. Pertimbangkan untuk menghenti perolehan sementara siasatan."
            })

    # ── Flag 2: Direct Negotiation Without Justification ──────────────────────
    if "direct negotiation" in method or "rundingan terus" in text_lower:
        urgency_keywords = ["urgent", "emergency", "darurat", "segera", "sole source",
                           "proprietary", "security", "keselamatan", "national security"]
        has_justification = any(kw in justification or kw in text_lower
                                for kw in urgency_keywords)
        if not has_justification:
            flags.append({
                "type": "DIRECT_NEGOTIATION_NO_JUSTIFICATION",
                "severity": "HIGH",
                "icon": "🔴",
                "title": "Direct Negotiation Without Adequate Justification",
                "title_bm": "Rundingan Terus Tanpa Justifikasi Mencukupi",
                "message": "Contract uses direct negotiation method but no urgency/sole-source justification was detected.",
                "trigger": "Method = direct negotiation; no urgency keywords in justification field",
                "suggested_action": "Request written justification memo. Verify compliance with Arahan Perbendaharaan threshold (RM50,000). Refer to Treasury Circular SPP 5/2007.",
                "suggested_action_bm": "Minta memo justifikasi bertulis. Sahkan pematuhan had Arahan Perbendaharaan (RM50,000). Rujuk Surat Pekeliling Perbendaharaan SPP 5/2007."
            })
        else:
            flags.append({
                "type": "DIRECT_NEGOTIATION_WITH_JUSTIFICATION",
                "severity": "MEDIUM",
                "icon": "🟡",
                "title": "Direct Negotiation — Justification Present (Verify)",
                "title_bm": "Rundingan Terus — Justifikasi Ada (Sahkan)",
                "message": "Direct negotiation used with some justification. Human verification required to confirm validity.",
                "trigger": "Method = direct negotiation; justification keywords detected",
                "suggested_action": "Verify justification is formally documented and approved by appropriate authority.",
                "suggested_action_bm": "Sahkan justifikasi didokumen secara formal dan diluluskan oleh pihak berkuasa yang sesuai."
            })

    # ── Flag 3: Contract Value vs Method Mismatch ──────────────────────────────
    if value > thresholds["open_tender_minimum_rm"] and "direct negotiation" in method:
        flags.append({
            "type": "VALUE_METHOD_MISMATCH",
            "severity": "HIGH",
            "icon": "🔴",
            "title": "Contract Value Exceeds Direct Negotiation Threshold",
            "title_bm": "Nilai Kontrak Melebihi Had Rundingan Terus",
            "message": f"Contract value RM{value:,.0f} exceeds the RM{thresholds['open_tender_minimum_rm']:,.0f} open tender threshold, but direct negotiation was used.",
            "trigger": f"Value RM{value:,.0f} > threshold RM{thresholds['open_tender_minimum_rm']:,.0f} AND method = direct negotiation",
            "suggested_action": "This likely violates Arahan Perbendaharaan 2023. Escalate to Audit Committee immediately. Contract may be voidable.",
            "suggested_action_bm": "Ini mungkin melanggar Arahan Perbendaharaan 2023. Eskalasikan kepada Jawatankuasa Audit segera. Kontrak mungkin boleh dibatalkan."
        })

    # ── Flag 4: Missing Variation Cap ─────────────────────────────────────────
    if not contract.get("variation_cap_mentioned"):
        flags.append({
            "type": "MISSING_VARIATION_CAP",
            "severity": "MEDIUM",
            "icon": "🟡",
            "title": "No Variation Cap Clause Detected",
            "title_bm": "Tiada Klausa Had Variasi Dikesan",
            "message": "Contract does not appear to cap allowable variations/change orders. Unlimited variations are a common vector for inflated final costs.",
            "trigger": "Field 'variation_cap_mentioned' = false",
            "suggested_action": "Add variation cap clause limiting changes to ≤15% of original contract sum per SPP provisions.",
            "suggested_action_bm": "Tambah klausa had variasi mengehadkan perubahan kepada ≤15% daripada jumlah kontrak asal mengikut peruntukan SPP."
        })

    # ── Flag 5: Missing Audit Rights ──────────────────────────────────────────
    if not contract.get("audit_clause_mentioned"):
        flags.append({
            "type": "MISSING_AUDIT_CLAUSE",
            "severity": "MEDIUM",
            "icon": "🟡",
            "title": "No Audit Rights Clause Detected",
            "title_bm": "Tiada Klausa Hak Audit Dikesan",
            "message": "Contract does not appear to contain a right-to-audit provision. This limits post-contract accountability.",
            "trigger": "Field 'audit_clause_mentioned' = false",
            "suggested_action": "Insert audit rights clause referencing MACC Act 2009 compliance and NAD access rights.",
            "suggested_action_bm": "Masukkan klausa hak audit yang merujuk pematuhan Akta SPRM 2009 dan hak akses NAD."
        })

    # ── Flag 6: High-Risk Terms ────────────────────────────────────────────────
    for term in high_risk_terms:
        if term.lower() in text_lower:
            flags.append({
                "type": "HIGH_RISK_TERM",
                "severity": "MEDIUM",
                "icon": "🟡",
                "title": f"High-Risk Term Detected: '{term}'",
                "title_bm": f"Terma Berisiko Tinggi Dikesan: '{term}'",
                "message": f"The phrase '{term}' was found in the contract. This term is associated with procurement irregularities.",
                "trigger": f"Text match: '{term}'",
                "suggested_action": f"Review context of '{term}'. Ensure proper authorization and documentation exist.",
                "suggested_action_bm": f"Semak konteks '{term}'. Pastikan kebenaran dan dokumentasi yang betul wujud."
            })

    # ── Flag 7: Price Benchmark Check ─────────────────────────────────────────
    benchmarks = WATCHLIST["price_benchmarks"]
    item_desc = (contract.get("item_description") or "").lower()
    for item_key, bench_data in benchmarks.items():
        if item_key.lower().replace("_", " ") in item_desc:
            bench_val = bench_data["benchmark_rm"]
            # Rough check: if contract value is > 2x benchmark per unit, flag it
            if value > 0 and value > bench_val * 2:
                pct_over = ((value - bench_val) / bench_val) * 100
                flags.append({
                    "type": "PRICE_ABOVE_BENCHMARK",
                    "severity": "MEDIUM",
                    "icon": "🟡",
                    "title": f"Price May Exceed Benchmark ({pct_over:.0f}% above)",
                    "title_bm": f"Harga Mungkin Melebihi Penanda Aras ({pct_over:.0f}% lebih)",
                    "message": f"Contract value RM{value:,.0f} is {pct_over:.0f}% above the benchmark for '{item_key}' (RM{bench_val:,.0f} per {bench_data['unit']}).",
                    "trigger": f"Item keyword match: '{item_key}'; Value RM{value:,.0f} vs benchmark RM{bench_val:,.0f}",
                    "suggested_action": f"Request price justification. Compare with ePerolehan historical rates. Source: {bench_data['source']}",
                    "suggested_action_bm": f"Minta justifikasi harga. Bandingkan dengan kadar sejarah ePerolehan. Sumber: {bench_data['source']}"
                })

    return flags


def llm_red_flag_analysis(contract: dict, flags: list, full_text: str, language: str = "EN") -> dict:
    """
    LLM provides holistic risk narrative and structured next steps.
    """
    lang_instruction = (
        "Respond in Bahasa Malaysia." if language == "BM" else "Respond in English."
    )
    flag_summary = "\n".join([f"- [{f['severity']}] {f['title']}: {f['message']}" for f in flags])

    prompt = f"""You are a Malaysian government procurement auditor. Review this contract analysis.

{lang_instruction}

CONTRACT EXTRACTED DATA:
{json.dumps(contract, indent=2, default=str)[:2000]}

RULE-BASED FLAGS ALREADY DETECTED:
{flag_summary if flag_summary else "None detected by rule engine."}

CONTRACT TEXT EXCERPT:
{full_text[:2000]}

Provide:
1. A concise risk narrative (3-4 sentences) explaining the overall risk posture
2. Any ADDITIONAL risks the rule engine may have missed
3. Prioritized next steps for the procurement officer
4. Overall risk classification: LOW / MEDIUM / HIGH / CRITICAL

Return ONLY this JSON (no markdown fences):
{{
  "risk_narrative": "3-4 sentence assessment",
  "additional_flags": [
    {{"title": "risk title", "message": "details", "severity": "HIGH/MEDIUM/LOW"}}
  ],
  "next_steps": [
    "Step 1: ...",
    "Step 2: ..."
  ],
  "overall_risk": "LOW/MEDIUM/HIGH/CRITICAL",
  "confidence": "HIGH/MEDIUM/LOW"
}}"""

    try:
        response = model.generate_content(prompt)
        return parse_json_safely(response.text)
    except Exception as e:
        return {
            "risk_narrative": f"LLM analysis unavailable: {str(e)}",
            "additional_flags": [],
            "next_steps": ["Manual review required"],
            "overall_risk": "UNKNOWN",
            "confidence": "LOW"
        }


def scan_contract(text_or_file, source_type: str = "text", language: str = "EN") -> dict:
    """
    Main entry point for the Red-Flag Scanner.
    source_type: 'text' or 'pdf'
    """
    # ── Extract text ───────────────────────────────────────────────────────────
    if source_type == "pdf":
        full_text = extract_pdf_text(text_or_file)
        if not full_text or full_text.startswith("[PDF_EXTRACTION_ERROR"):
            return {
                "error": "PDF text extraction failed. Please paste the contract text manually.",
                "error_bm": "Pengekstrakan teks PDF gagal. Sila tampal teks kontrak secara manual."
            }
    else:
        full_text = text_or_file

    if len(full_text.strip()) < 100:
        return {
            "error": "Input text too short. Please provide a complete contract or clause.",
            "error_bm": "Teks input terlalu pendek. Sila berikan kontrak atau klausa yang lengkap."
        }

    # ── Extract structured fields ──────────────────────────────────────────────
    contract_fields = extract_contract_fields(full_text)

    # ── Run rule-based flags ───────────────────────────────────────────────────
    flags = run_red_flag_checks(contract_fields, full_text)

    # ── LLM holistic analysis ──────────────────────────────────────────────────
    llm_analysis = llm_red_flag_analysis(contract_fields, flags, full_text, language)

    # ── Merge any additional LLM flags ────────────────────────────────────────
    for extra_flag in llm_analysis.get("additional_flags", []):
        extra_flag.setdefault("type", "LLM_DETECTED")
        extra_flag.setdefault("icon", "🟡" if extra_flag.get("severity") != "HIGH" else "🔴")
        extra_flag.setdefault("trigger", "LLM pattern analysis")
        extra_flag.setdefault("suggested_action", "Review and verify with procurement officer")
        extra_flag.setdefault("suggested_action_bm", "Semak dan sahkan dengan pegawai perolehan")
        extra_flag.setdefault("title_bm", extra_flag.get("title", ""))
        flags.append(extra_flag)

    # ── Compute risk score ─────────────────────────────────────────────────────
    severity_weights = {"HIGH": 30, "CRITICAL": 40, "MEDIUM": 15, "LOW": 5}
    risk_score = min(100, sum(
        severity_weights.get(f.get("severity", "LOW"), 5) for f in flags
    ))

    overall = llm_analysis.get("overall_risk", "UNKNOWN")
    if overall == "CRITICAL":
        risk_score = max(risk_score, 85)
    elif overall == "HIGH":
        risk_score = max(risk_score, 65)

    # ── Grade ──────────────────────────────────────────────────────────────────
    if risk_score >= 65:
        risk_label = "HIGH RISK"
        risk_label_bm = "RISIKO TINGGI"
        risk_color = "🔴"
    elif risk_score >= 35:
        risk_label = "MEDIUM RISK"
        risk_label_bm = "RISIKO SEDERHANA"
        risk_color = "🟡"
    else:
        risk_label = "LOW RISK"
        risk_label_bm = "RISIKO RENDAH"
        risk_color = "🟢"

    return {
        "contract_fields": contract_fields,
        "flags": flags,
        "risk_score": risk_score,
        "risk_label": risk_label,
        "risk_label_bm": risk_label_bm,
        "risk_color": risk_color,
        "llm_analysis": llm_analysis,
        "next_steps": llm_analysis.get("next_steps", []),
        "input_hash": hash_text(full_text),
        "timestamp": get_timestamp(),
        "mode": "red_flag_scan",
        "language": language
    }