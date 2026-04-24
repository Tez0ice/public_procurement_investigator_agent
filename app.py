"""
KONTRAX — Dark Theme, Showcase-Ready
Run: streamlit run app.py
"""

import streamlit as st
from agents import check_clause_integrity, scan_contract

st.set_page_config(
    page_title="KONTRAX",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=DM+Mono:wght@400;500&display=swap');

:root {
  --bg:        #0a0a0a;
  --surface:   #141414;
  --surface2:  #1c1c1c;
  --border:    #2a2a2a;
  --border2:   #333333;
  --green:     #4ade80;
  --green-dim: #166534;
  --amber:     #fbbf24;
  --red:       #f87171;
  --blue:      #60a5fa;
  --text:      #f5f5f5;
  --text2:     #a3a3a3;
  --text3:     #5a5a5a;
  --radius:    10px;
  --radius-lg: 14px;
}

*, *::before, *::after { box-sizing: border-box; }
#MainMenu, footer, header { visibility: hidden; }
section[data-testid="stSidebar"] { display: none !important; }

.stApp { background: var(--bg) !important; font-family: 'DM Sans', sans-serif; color: var(--text); }

p, span, div, label, li { color: var(--text) !important; font-family: 'DM Sans', sans-serif !important; }
h1,h2,h3,h4 { color: var(--text) !important; font-family: 'DM Sans', sans-serif !important; font-weight: 600 !important; }

/* Tabs */
[data-testid="stTabs"] [role="tablist"] {
  background: var(--surface) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--radius) !important;
  padding: 4px !important;
  gap: 4px !important;
}
[data-testid="stTabs"] [role="tab"] {
  font-family: 'DM Sans', sans-serif !important;
  font-weight: 500 !important; font-size: 0.88rem !important;
  color: var(--text2) !important; border-radius: 7px !important;
  padding: 0.5rem 1.2rem !important; border: none !important;
  background: transparent !important; transition: all 0.15s !important;
}
[data-testid="stTabs"] [role="tab"][aria-selected="true"] {
  background: var(--surface2) !important; color: var(--text) !important;
  border: 1px solid var(--border2) !important;
}
[data-testid="stTabs"] [role="tabpanel"] { padding-top: 1.5rem !important; }

/* Textarea */
textarea {
  background: var(--surface) !important; border: 1px solid var(--border2) !important;
  border-radius: var(--radius) !important; color: var(--text) !important;
  font-family: 'DM Mono', monospace !important; font-size: 0.82rem !important;
  line-height: 1.65 !important; padding: 0.9rem !important;
}
textarea:focus { border-color: var(--green) !important; box-shadow: 0 0 0 2px rgba(74,222,128,0.1) !important; }
textarea::placeholder { color: var(--text3) !important; }

/* File uploader */
[data-testid="stFileUploaderDropzone"] {
  background: var(--surface) !important; border: 2px dashed var(--border2) !important;
  border-radius: var(--radius-lg) !important; padding: 1.5rem !important;
}
[data-testid="stFileUploaderDropzone"]:hover { border-color: var(--green) !important; }
[data-testid="stFileUploaderDropzone"] * { color: var(--text2) !important; }

/* Buttons */
.stButton > button {
  font-family: 'DM Sans', sans-serif !important; font-weight: 600 !important;
  border-radius: var(--radius) !important; font-size: 0.9rem !important;
  transition: all 0.15s !important;
}
.stButton > button[kind="primary"] {
  background: var(--green) !important; color: #0a0a0a !important;
  border: none !important; padding: 0.6rem 1.8rem !important;
}
.stButton > button[kind="primary"]:hover {
  background: #86efac !important; transform: translateY(-1px) !important;
  box-shadow: 0 4px 16px rgba(74,222,128,0.25) !important;
}
.stButton > button[kind="primary"]:disabled { background: var(--border2) !important; color: var(--text3) !important; }
.stButton > button[kind="secondary"] {
  background: var(--surface2) !important; border: 1px solid var(--border2) !important;
  color: var(--text) !important; padding: 0.6rem 1.2rem !important;
}
.stButton > button[kind="secondary"]:hover { border-color: var(--text2) !important; }

/* Radio */
.stRadio [role="radiogroup"] { gap: 8px !important; }
.stRadio label {
  background: var(--surface) !important; border: 1px solid var(--border) !important;
  border-radius: var(--radius) !important; padding: 0.6rem 1.2rem !important;
  font-size: 0.88rem !important; color: var(--text2) !important; cursor: pointer !important;
}
.stRadio label:has(input:checked) {
  border-color: var(--green) !important; background: rgba(74,222,128,0.07) !important;
  color: var(--green) !important;
}

/* Metrics */
[data-testid="stMetric"] {
  background: var(--surface) !important; border: 1px solid var(--border) !important;
  border-radius: var(--radius) !important; padding: 1rem !important;
}
[data-testid="stMetricLabel"] { color: var(--text3) !important; font-size: 0.72rem !important; text-transform: uppercase; letter-spacing: 0.05em; }
[data-testid="stMetricValue"] { color: var(--text) !important; font-weight: 700 !important; font-size: 1.7rem !important; }

/* Expanders */
[data-testid="stExpander"] {
  background: var(--surface) !important; border: 1px solid var(--border) !important;
  border-radius: var(--radius) !important;
}
[data-testid="stExpander"] summary { color: var(--text) !important; font-weight: 500 !important; }
[data-testid="stExpander"] summary:hover { color: var(--green) !important; }

/* Alerts */
[data-testid="stAlert"] { border-radius: var(--radius) !important; }
.stInfo  { background: rgba(96,165,250,0.08) !important; border-left: 3px solid var(--blue) !important; }
.stSuccess { background: rgba(74,222,128,0.08) !important; border-left: 3px solid var(--green) !important; }
.stWarning { background: rgba(251,191,36,0.08) !important; border-left: 3px solid var(--amber) !important; }
.stError   { background: rgba(248,113,113,0.08) !important; border-left: 3px solid var(--red) !important; }

/* Caption */
.stCaption, [data-testid="stCaptionContainer"] p { color: var(--text3) !important; font-size: 0.76rem !important; }

/* Dialog */
[data-testid="stDialog"] > div {
  background: var(--surface) !important; border: 1px solid var(--border2) !important;
  border-radius: var(--radius-lg) !important; box-shadow: 0 24px 64px rgba(0,0,0,0.7) !important;
}

hr { border-color: var(--border) !important; }

/* ── Custom Components ───────────────────────────────── */
.hero {
  background: var(--surface); border: 1px solid var(--border2);
  border-radius: var(--radius-lg); padding: 1.75rem 2rem;
  margin-bottom: 1.75rem; display: flex; align-items: center; gap: 1.25rem;
}
.hero-icon  { font-size: 2.4rem; flex-shrink: 0; }
.hero-title { font-size: 1.55rem; font-weight: 700; color: var(--text); margin: 0; letter-spacing: -0.03em; }
.hero-sub   { font-size: 0.85rem; color: var(--text2); margin: 4px 0 0; }
.hero-pill  {
  display: inline-block; margin-top: 8px; font-size: 0.68rem; font-weight: 600;
  letter-spacing: 0.07em; color: var(--green); border: 1px solid var(--green-dim);
  background: rgba(74,222,128,0.06); border-radius: 99px; padding: 2px 10px;
}

.section-label {
  font-size: 0.68rem; font-weight: 600; letter-spacing: 0.09em;
  text-transform: uppercase; color: var(--text3) !important; margin-bottom: 8px;
}

.check-row {
  display: flex; gap: 10px; align-items: flex-start;
  padding: 0.65rem 0; border-bottom: 1px solid var(--border);
}
.check-icon { font-size: 1.1rem; flex-shrink: 0; margin-top: 1px; }
.check-title { font-size: 0.85rem; font-weight: 600; color: var(--text); }
.check-desc  { font-size: 0.77rem; color: var(--text2); margin-top: 2px; line-height: 1.4; }

.score-box {
  text-align: center; padding: 1.1rem 0.5rem;
  background: var(--surface); border: 1px solid var(--border2);
  border-radius: var(--radius-lg);
}
.score-num   { font-size: 2.8rem; font-weight: 700; line-height: 1; }
.score-denom { font-size: 0.72rem; color: var(--text3); margin-top: 2px; }
.score-lbl   { font-size: 0.82rem; font-weight: 600; margin-top: 6px; }

.bar-track { background: var(--border2); border-radius: 99px; height: 5px; margin-top: 8px; overflow: hidden; }

.flag-card {
  background: var(--surface); border: 1px solid var(--border);
  border-radius: var(--radius); padding: 0.85rem 1rem;
  margin-bottom: 6px; display: flex; gap: 0.85rem; align-items: flex-start;
}
.flag-dot   { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; margin-top: 5px; }
.flag-title { font-size: 0.87rem; font-weight: 600; color: var(--text); margin-bottom: 3px; }
.flag-msg   { font-size: 0.79rem; color: var(--text2); line-height: 1.45; }
.sev-badge  {
  font-size: 0.66rem; font-weight: 700; letter-spacing: 0.05em;
  padding: 2px 8px; border-radius: 99px; flex-shrink: 0; margin-top: 1px;
}

.clause-row {
  display: flex; align-items: center; gap: 10px;
  padding: 0.5rem 0; border-bottom: 1px solid var(--border); font-size: 0.85rem;
}

.step-row { display: flex; gap: 10px; align-items: flex-start; padding: 0.45rem 0; }
.step-num {
  width: 22px; height: 22px; border-radius: 50%; background: var(--green);
  color: #0a0a0a; font-size: 0.7rem; font-weight: 700;
  display: flex; align-items: center; justify-content: center; flex-shrink: 0; margin-top: 1px;
}
.step-text { font-size: 0.85rem; color: var(--text2); line-height: 1.5; }

.field-row {
  display: flex; justify-content: space-between; align-items: center;
  padding: 0.5rem 0; border-bottom: 1px solid var(--border); font-size: 0.83rem;
}
.field-key { color: var(--text3) !important; }
.field-val { color: var(--text) !important; font-weight: 500; font-family: 'DM Mono', monospace; font-size: 0.79rem; }

.disclaimer {
  font-size: 0.73rem; color: var(--text3) !important; text-align: center;
  border-top: 1px solid var(--border); padding-top: 1rem; margin-top: 2rem; line-height: 1.6;
}
</style>
""", unsafe_allow_html=True)


# ── Helpers ───────────────────────────────────────────────────────────────────
def score_color(s):
    return "#f87171" if s >= 65 else ("#fbbf24" if s >= 35 else "#4ade80")

def sev_dot(sev):
    return {"HIGH":"#f87171","CRITICAL":"#ef4444","MEDIUM":"#fbbf24","LOW":"#4ade80"}.get(sev,"#a3a3a3")

def sev_badge(sev):
    cfg = {
        "HIGH":     ("rgba(248,113,113,0.15)","#f87171"),
        "CRITICAL": ("rgba(239,68,68,0.15)",  "#ef4444"),
        "MEDIUM":   ("rgba(251,191,36,0.15)", "#fbbf24"),
        "LOW":      ("rgba(74,222,128,0.15)", "#4ade80"),
    }.get(sev, ("rgba(163,163,163,0.12)","#a3a3a3"))
    return f"<span class='sev-badge' style='background:{cfg[0]};color:{cfg[1]};'>{sev}</span>"


# ── Full Report Dialog ─────────────────────────────────────────────────────────
@st.dialog("Full Analysis Report", width="large")
def show_report(result: dict):
    mode  = result.get("mode","")
    score = result.get("score",0) if mode=="clause_integrity_check" else result.get("risk_score",0)
    color = score_color(score)
    llm   = result.get("llm_analysis", {})

    if mode == "clause_integrity_check":
        grade   = result.get("grade","")
        present = sum(1 for f in result.get("clause_findings",[]) if f["status"]=="PRESENT")
        missing = sum(1 for f in result.get("clause_findings",[]) if f["status"]=="MISSING")
        weak    = len(result.get("weak_language",[]))

        st.markdown(f"""
        <div style='background:var(--surface);border:1px solid var(--border2);border-radius:14px;
             padding:1.25rem 1.5rem;display:flex;align-items:center;gap:1.5rem;margin-bottom:1rem;'>
          <div style='text-align:center;min-width:80px;'>
            <div style='font-size:2.6rem;font-weight:700;color:{color};line-height:1;'>{score}</div>
            <div style='font-size:0.72rem;color:var(--text3);'>/100 integrity</div>
            <div style='font-size:0.82rem;font-weight:600;color:{color};margin-top:4px;'>{grade}</div>
          </div>
          <div style='flex:1;'>
            <div style='background:var(--border2);border-radius:99px;height:6px;overflow:hidden;'>
              <div style='height:6px;border-radius:99px;background:{color};width:{score}%;'></div>
            </div>
            <div style='font-size:0.78rem;color:var(--text3);margin-top:8px;'>
              {present} clauses present · {missing} missing · {weak} weak phrases
            </div>
          </div>
        </div>""", unsafe_allow_html=True)

        if llm.get("llm_assessment"): st.info(f"**AI Assessment —** {llm['llm_assessment']}")
        if llm.get("top_priority_fix"): st.success(f"🎯 **Top Priority Fix:** {llm['top_priority_fix']}")

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<div class='section-label'>Clause Checklist</div>", unsafe_allow_html=True)
        for f in result.get("clause_findings", []):
            ok   = f["status"]=="PRESENT"
            icon = "✅" if ok else ("🔴" if f.get("required") else "🟡")
            req  = "<span style='font-size:0.7rem;font-weight:700;color:#f87171;'>REQUIRED</span>" if f.get("required") and not ok else ""
            st.markdown(f"<div class='clause-row'><span>{icon}</span><span style='flex:1;'>{f.get('name','')}</span>{req}</div>", unsafe_allow_html=True)
            if not ok and f.get("suggestion_en"):
                st.caption(f"  → {f['suggestion_en']}")

        if result.get("weak_language"):
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("<div class='section-label'>Weak Language Patterns</div>", unsafe_allow_html=True)
            for w in result["weak_language"]:
                st.warning(f'`"{w["pattern"]}"` — {w["issue"]}')

        for r in llm.get("additional_risks",[]):
            icon = "🔴" if r.get("severity")=="HIGH" else "🟡"
            with st.expander(f"{icon} {r.get('risk','')}"):
                st.write(r.get("suggestion",""))

    else:
        flags = result.get("flags",[])
        label = result.get("risk_label","")
        high  = sum(1 for f in flags if f.get("severity") in ("HIGH","CRITICAL"))
        med   = sum(1 for f in flags if f.get("severity")=="MEDIUM")
        low_c = sum(1 for f in flags if f.get("severity")=="LOW")

        st.markdown(f"""
        <div style='background:var(--surface);border:1px solid var(--border2);border-radius:14px;
             padding:1.25rem 1.5rem;display:flex;align-items:center;gap:1.5rem;margin-bottom:1rem;'>
          <div style='text-align:center;min-width:80px;'>
            <div style='font-size:2.6rem;font-weight:700;color:{color};line-height:1;'>{score}</div>
            <div style='font-size:0.72rem;color:var(--text3);'>/100 risk</div>
            <div style='font-size:0.82rem;font-weight:600;color:{color};margin-top:4px;'>{label}</div>
          </div>
          <div style='flex:1;'>
            <div style='background:var(--border2);border-radius:99px;height:6px;overflow:hidden;'>
              <div style='height:6px;border-radius:99px;background:{color};width:{score}%;'></div>
            </div>
            <div style='font-size:0.78rem;color:var(--text3);margin-top:8px;'>
              {high} high · {med} medium · {low_c} low · {len(flags)} total flags
            </div>
          </div>
        </div>""", unsafe_allow_html=True)

        if llm.get("risk_narrative"): st.info(f"**Risk Narrative —** {llm['risk_narrative']}")

        fields = result.get("contract_fields",{})
        valid  = [(k,v) for k,v in fields.items() if v and k!="extraction_error"]
        if valid:
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("<div class='section-label'>Extracted Contract Data</div>", unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            for i,(k,v) in enumerate(valid):
                key_txt = k.replace("_"," ").title()
                val_txt = f"RM {v:,.0f}" if k=="contract_value_rm" and isinstance(v,(int,float)) else str(v)
                with (c1 if i%2==0 else c2):
                    st.markdown(f"<div class='field-row'><span class='field-key'>{key_txt}</span><span class='field-val'>{val_txt}</span></div>", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<div class='section-label'>All Red Flags</div>", unsafe_allow_html=True)
        if not flags:
            st.success("No red flags detected.")
        else:
            order = {"CRITICAL":0,"HIGH":0,"MEDIUM":1,"LOW":2}
            for f in sorted(flags, key=lambda x: order.get(x.get("severity","LOW"),2)):
                sev = f.get("severity","LOW")
                icon = "🔴" if sev in ("HIGH","CRITICAL") else ("🟡" if sev=="MEDIUM" else "🟢")
                with st.expander(f"{icon} {f.get('title','')}  ·  {sev}", expanded=(sev in ("HIGH","CRITICAL"))):
                    st.write(f.get("message",""))
                    if f.get("suggested_action"):
                        st.info(f"**Suggested Action:** {f['suggested_action']}")

        if result.get("next_steps"):
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("<div class='section-label'>Recommended Next Steps</div>", unsafe_allow_html=True)
            for i, step in enumerate(result["next_steps"],1):
                st.markdown(f"<div class='step-row'><div class='step-num'>{i}</div><div class='step-text'>{step}</div></div>", unsafe_allow_html=True)

    st.markdown("---")
    st.download_button("📄 Download Report (.md)",
        data=f"# KONTRAX Report\nGenerated: {result.get('timestamp','')}\nHash: {result.get('input_hash','')}\n\n{str(result)}",
        file_name=f"report_{result.get('input_hash','')}.md", mime="text/markdown",
        use_container_width=True)
    st.caption("⚠️ Advisory only. Verify all findings with a qualified procurement officer.")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE
# ══════════════════════════════════════════════════════════════════════════════

st.markdown("""
<div class="hero">
  <div class="hero-icon">🛡️</div>
  <div>
    <div class="hero-title">KONTRAX</div>
    <div class="hero-sub">Malaysian Government Procurement Integrity Advisor</div>
    <div class="hero-pill">PROTOTYPE · NOT LEGAL ADVICE</div>
  </div>
</div>
""", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["  📝  Clause Integrity Check  ", "  🔍  Red-Flag Contract Scan  "])


# ══════════════════ TAB 1 ══════════════════
with tab1:
    left, right = st.columns([3, 2], gap="large")

    with left:
        st.markdown("<div class='section-label'>Contract Text</div>", unsafe_allow_html=True)
        st.markdown("<p style='font-size:0.83rem;color:var(--text2);margin:0 0 10px;'>Paste any clause, section, or full contract draft. The AI scores integrity and flags missing protections.</p>", unsafe_allow_html=True)

        clause_text = st.text_area("c_input", height=260,
            placeholder="Paste contract clause or draft text here…",
            label_visibility="collapsed")

        col_meta, col_clr, col_run = st.columns([3, 1, 2])
        with col_meta:
            st.caption(f"{len(clause_text):,} chars · {len(clause_text.split()):,} words" if clause_text else "Min ~80 characters")
        with col_clr:
            if clause_text and st.button("Clear", key="clr1", use_container_width=True):
                st.rerun()
        with col_run:
            run_clause = st.button("Analyze →", type="primary", key="run1",
                use_container_width=True, disabled=(len(clause_text.strip()) < 80))

    with right:
        st.markdown("<div class='section-label'>What gets checked</div>", unsafe_allow_html=True)
        for icon, title, desc in [
            ("📋","Mandatory Clauses",  "Penalty/LAD, Performance Bond, Anti-Corruption, Audit Rights, Variation Cap"),
            ("🔤","Weak Language",      "Phrases like 'may consider' or 'best effort' that reduce enforceability"),
            ("⚖️","Legal Compliance",   "MACC Act 2009, Arahan Perbendaharaan, Companies Act 2016"),
            ("🤖","AI Assessment",      "Holistic narrative, risk identification, and top priority fix"),
        ]:
            st.markdown(f"<div class='check-row'><span class='check-icon'>{icon}</span><div><div class='check-title'>{title}</div><div class='check-desc'>{desc}</div></div></div>", unsafe_allow_html=True)

    if run_clause:
        if len(clause_text.strip()) < 80:
            st.warning("Please paste at least a paragraph of contract text.")
        else:
            with st.spinner("Analyzing clause integrity…"):
                try:
                    result = check_clause_integrity(clause_text)
                except Exception as e:
                    st.error(f"Analysis failed: {e}"); result = None

            if result:
                score   = result.get("score",0)
                grade   = result.get("grade","")
                color   = score_color(score)
                present = sum(1 for f in result.get("clause_findings",[]) if f["status"]=="PRESENT")
                missing = sum(1 for f in result.get("clause_findings",[]) if f["status"]=="MISSING")
                weak    = len(result.get("weak_language",[]))
                llm     = result.get("llm_analysis",{})

                st.markdown("---")
                st.markdown("<div class='section-label'>Results</div>", unsafe_allow_html=True)

                cs, cm1, cm2, cm3 = st.columns([1.5,1,1,1])
                with cs:
                    st.markdown(f"""<div class='score-box' style='border-top:3px solid {color};'>
                      <div class='score-num' style='color:{color};'>{score}</div>
                      <div class='score-denom'>/100 integrity</div>
                      <div class='score-lbl' style='color:{color};'>{grade}</div>
                    </div>""", unsafe_allow_html=True)
                cm1.metric("✅ Present",      present)
                cm2.metric("❌ Missing",      missing)
                cm3.metric("⚠️ Weak Phrases", weak)

                if llm.get("llm_assessment"):
                    st.markdown("<br>", unsafe_allow_html=True)
                    st.info(f"**AI Summary —** {llm['llm_assessment']}")
                if llm.get("top_priority_fix"):
                    st.success(f"🎯 **Top Priority Fix:** {llm['top_priority_fix']}")

                with st.expander("📋 Clause Checklist", expanded=True):
                    for f in result.get("clause_findings",[]):
                        ok   = f["status"]=="PRESENT"
                        icon = "✅" if ok else ("🔴" if f.get("required") else "🟡")
                        req  = "<span style='font-size:0.7rem;font-weight:700;color:#f87171;'>REQUIRED</span>" if f.get("required") and not ok else ""
                        st.markdown(f"<div class='clause-row'><span>{icon}</span><span style='flex:1;'>{f.get('name','')}</span>{req}</div>", unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("📊 View Full Report", type="primary", key="rep1"):
                    show_report(result)


# ══════════════════ TAB 2 ══════════════════
with tab2:
    left2, right2 = st.columns([3, 2], gap="large")

    with left2:
        st.markdown("<div class='section-label'>Input Method</div>", unsafe_allow_html=True)
        method = st.radio("method", ["📎  Upload PDF", "📋  Paste Text"],
            horizontal=True, label_visibility="collapsed")

        st.markdown("<br>", unsafe_allow_html=True)
        pdf_file  = None
        scan_text = ""

        if "PDF" in method:
            st.markdown("<div class='section-label'>PDF Contract</div>", unsafe_allow_html=True)
            pdf_file = st.file_uploader("pdf_up", type=["pdf"], label_visibility="collapsed")
            if pdf_file:
                st.success(f"📄 **{pdf_file.name}** ready to scan")
        else:
            st.markdown("<div class='section-label'>Contract Text</div>", unsafe_allow_html=True)
            scan_text = st.text_area("s_input", height=240,
                placeholder="Paste the full contract text here…",
                label_visibility="collapsed")
            if scan_text:
                st.caption(f"{len(scan_text):,} chars · {len(scan_text.split()):,} words")

        st.markdown("<br>", unsafe_allow_html=True)

        ready = (pdf_file is not None) if "PDF" in method else (len(scan_text.strip()) >= 100)
        run_scan = st.button("🔍  Scan for Red Flags  →", type="primary", key="run2",
            use_container_width=True, disabled=not ready)
        if not ready:
            st.caption("Upload a PDF or paste at least 100 characters to enable scanning.")

    with right2:
        st.markdown("<div class='section-label'>What gets detected</div>", unsafe_allow_html=True)
        for icon, title, desc in [
            ("🏢","Vendor Watchlist",    "Cross-checks vendor names against PEP/integrity risk watchlist"),
            ("📊","Method vs Value",     "Direct negotiation where open tender is required (>RM500k)"),
            ("📝","Missing Safeguards",  "No variation cap, no audit rights, no anti-corruption clause"),
            ("💰","Price Benchmarks",    "Contract value vs ePerolehan historical benchmarks"),
            ("🤖","AI Risk Narrative",   "Holistic risk summary with prioritized recommended next steps"),
        ]:
            st.markdown(f"<div class='check-row'><span class='check-icon'>{icon}</span><div><div class='check-title'>{title}</div><div class='check-desc'>{desc}</div></div></div>", unsafe_allow_html=True)

    if run_scan:
        with st.spinner("Scanning contract for red flags…"):
            try:
                if "PDF" in method:
                    result = scan_contract(pdf_file, source_type="pdf")
                else:
                    result = scan_contract(scan_text, source_type="text")
                if "error" in result:
                    st.error(result["error"]); result = None
            except Exception as e:
                st.error(f"Scan failed: {e}"); result = None

        if result:
            r_score = result.get("risk_score",0)
            r_label = result.get("risk_label","")
            flags   = result.get("flags",[])
            color   = score_color(r_score)
            high    = sum(1 for f in flags if f.get("severity") in ("HIGH","CRITICAL"))
            med     = sum(1 for f in flags if f.get("severity")=="MEDIUM")
            low_c   = sum(1 for f in flags if f.get("severity")=="LOW")
            llm     = result.get("llm_analysis",{})

            st.markdown("---")
            st.markdown("<div class='section-label'>Scan Results</div>", unsafe_allow_html=True)

            cs2, ch, cm, cl, ct = st.columns([1.5,1,1,1,1])
            with cs2:
                st.markdown(f"""<div class='score-box' style='border-top:3px solid {color};'>
                  <div class='score-num' style='color:{color};'>{r_score}</div>
                  <div class='score-denom'>/100 risk</div>
                  <div class='score-lbl' style='color:{color};'>{r_label}</div>
                </div>""", unsafe_allow_html=True)
            ch.metric("🔴 High",   high)
            cm.metric("🟡 Medium", med)
            cl.metric("🟢 Low",    low_c)
            ct.metric("📊 Total",  len(flags))

            if llm.get("risk_narrative"):
                st.markdown("<br>", unsafe_allow_html=True)
                st.info(f"**AI Risk Summary —** {llm['risk_narrative']}")

            top = [f for f in flags if f.get("severity") in ("HIGH","CRITICAL")][:3]
            if top:
                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown("<div class='section-label'>Critical Flags</div>", unsafe_allow_html=True)
                for f in top:
                    sev = f.get("severity","HIGH")
                    st.markdown(f"""<div class='flag-card'>
                      <div class='flag-dot' style='background:{sev_dot(sev)};'></div>
                      <div style='flex:1;'>
                        <div class='flag-title'>{f.get("title","")}</div>
                        <div class='flag-msg'>{f.get("message","")}</div>
                      </div>
                      {sev_badge(sev)}
                    </div>""", unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("📊 View Full Report & Next Steps", type="primary", key="rep2"):
                show_report(result)


st.markdown("<div class='disclaimer'>⚠️ <strong>PROTOTYPE — NOT LEGAL ADVICE.</strong><br>All AI findings are indicative only and must be verified by a qualified procurement officer or legal counsel.<br>References: Malaysian Treasury Guidelines · MACC Act 2009 · OCDS Standard · Companies Act 2016</div>", unsafe_allow_html=True)