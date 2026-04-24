import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
from io import BytesIO
from streamlit_autorefresh import st_autorefresh


CSV_URL = (
    "https://docs.google.com/spreadsheets/d/"
    "1DfkJfbrmAYICQaxyFx_jOzPszDa6AfilnxqnJgJm6vY/gviz/tq?tqx=out:csv&sheet=Final_Leads"
)
DEFAULT_WEBCHAT_URL = (
    "https://copilotstudio.microsoft.com/environments/"
    "Default-44467e6f-462c-4ea2-823f-7800de5434e3/bots/"
    "cr29b_agentXheyuy/webchat?__version__=2"
)


st.set_page_config(page_title="Magelli Lead Dashboard", layout="wide")


def inject_button_styles() -> None:
    """Apply custom styling for sidebar navigation buttons and dark theme."""
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap');
        html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }

        .stButton > button {
            width: 100%;
            text-align: center;
            font-size: 16px;
            font-weight: 600;
            padding: 12px 10px;
            margin: 5px 0;
            border-radius: 8px;
            border: none;
            background-color: transparent;
            color: white;
        }
        .stButton > button:hover {
            background-color: rgba(255,255,255,0.08);
        }

        /* Tier badges */
        .tier-a { background: rgba(0,233,122,0.1); border: 1px solid rgba(0,233,122,0.25); border-radius: 6px; padding: 3px 10px; color: #00e97a; font-size: 12px; font-weight: 600; display:inline-block; }
        .tier-b { background: rgba(61,142,248,0.1); border: 1px solid rgba(61,142,248,0.25); border-radius: 6px; padding: 3px 10px; color: #3d8ef8; font-size: 12px; font-weight: 600; display:inline-block; }
        .tier-c { background: rgba(245,166,35,0.1);  border: 1px solid rgba(245,166,35,0.25);  border-radius: 6px; padding: 3px 10px; color: #f5a623; font-size: 12px; font-weight: 600; display:inline-block; }
        .tier-d { background: rgba(74,88,120,0.1);   border: 1px solid rgba(74,88,120,0.25);   border-radius: 6px; padding: 3px 10px; color: #4a5878; font-size: 12px; font-weight: 600; display:inline-block; }

        /* Urgency badges */
        .urg-high   { background: rgba(0,233,122,0.1);  color: #00e97a; border-radius:20px; padding:3px 10px; font-size:11px; font-weight:500; display:inline-block; }
        .urg-medium { background: rgba(61,142,248,0.1); color: #3d8ef8; border-radius:20px; padding:3px 10px; font-size:11px; font-weight:500; display:inline-block; }
        .urg-low    { background: rgba(74,88,120,0.1);  color: #4a5878; border-radius:20px; padding:3px 10px; font-size:11px; font-weight:500; display:inline-block; }

        /* Lead cards */
        .lead-card { background: #0d1117; border: 1px solid #1e2d45; border-radius: 10px; padding: 18px 20px; margin-bottom: 12px; }
        .lead-card.lc-a { border-left: 3px solid #00e97a; }
        .lead-card.lc-b { border-left: 3px solid #3d8ef8; }
        .lead-card.lc-c { border-left: 3px solid #f5a623; }
        .lead-card.lc-d { border-left: 3px solid #253650; }
        .company-name { font-size: 15px; font-weight: 600; color: #e8eef7; }
        .role-name    { font-size: 13px; color: #8b9ab5; margin: 2px 0 10px 0; }
        .meta-row  { display:flex; gap:18px; flex-wrap:wrap; margin-bottom:8px; }
        .meta-item { font-size: 12px; color: #4a5878; }
        .meta-val  { color: #8b9ab5; font-weight: 500; }
        .score-bar-bg { background: #141b26; border-radius: 4px; height: 4px; margin: 8px 0; }
        .rationale-text { font-size: 12px; color: #4a5878; line-height: 1.55; margin-top: 8px; font-style: italic; }
        .signal-pill { display:inline-block; background: rgba(61,142,248,0.08); border: 1px solid rgba(61,142,248,0.18); border-radius:4px; padding:2px 8px; font-size:11px; color:#3d8ef8; margin-right:4px; margin-bottom:4px; }
        .section-divider { font-size:12px; font-weight:500; text-transform:uppercase; letter-spacing:.8px; color:#4a5878; margin:20px 0 12px 0; padding-bottom:8px; border-bottom:1px solid #1e2d45; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def initialize_session_state() -> None:
    """Initialize only the dashboard navigation state."""
    st.session_state.setdefault("section", "Overview")


def get_webchat_url() -> str:
    """Read the public Copilot Studio webchat URL from secrets or use the default."""
    try:
        return st.secrets.get("COPILOT_WEBCHAT_URL", DEFAULT_WEBCHAT_URL)
    except Exception:
        return DEFAULT_WEBCHAT_URL


def render_header() -> None:
    """Render the shared page header."""
    col1, col2 = st.columns([1, 6])

    with col1:
        st.markdown("<div style='margin-top: 25px;'></div>", unsafe_allow_html=True)
        st.image("gies_logo.jpg", width=110)

    with col2:
        st.title("Magelli Consulting Opportunity Dashboard")
        st.caption(
            "AI-powered prospect identification for the Magelli Office of Experiential Learning"
        )


def render_sidebar_navigation() -> None:
    """Render sidebar branding and dashboard navigation."""
    st.sidebar.image("gies_logo.jpg", width=140)
    st.sidebar.title("Magelli Opportunity Intelligence")
    st.sidebar.write(
        "Identify, prioritize, and act on high-value consulting opportunities."
    )

    navigation_sections = [
        "Overview",
        "Top Leads",
        "Recommended Actions",
        "Signal Insights",
        "Industry Trends",
        "All Leads",
        "Lead Detail View",
    ]

    if st.sidebar.button("Overview", use_container_width=True):
        st.session_state.section = "Overview"

    if st.sidebar.button("Top Leads", use_container_width=True):
        st.session_state.section = "Top Leads"

    if st.sidebar.button("Recommended Actions", use_container_width=True):
        st.session_state.section = "Recommended Actions"

    st.sidebar.markdown("---")

    if st.sidebar.button("Signal Insights", use_container_width=True):
        st.session_state.section = "Signal Insights"

    if st.sidebar.button("Industry Trends", use_container_width=True):
        st.session_state.section = "Industry Trends"

    st.sidebar.markdown("---")

    if st.sidebar.button("All Leads", use_container_width=True):
        st.session_state.section = "All Leads"

    if st.sidebar.button("Lead Detail View", use_container_width=True):
        st.session_state.section = "Lead Detail View"

    if st.session_state.section not in navigation_sections:
        st.session_state.section = "Overview"


@st.cache_data(ttl=30, show_spinner=False)
def load_leads_data() -> pd.DataFrame:
    """Load the live lead data from Google Sheets."""
    dataframe = pd.read_csv(CSV_URL)
    dataframe.columns = dataframe.columns.str.lower()
    # Normalise column names so the rest of the app works regardless of
    # which sheet tab uses which header spelling.
    dataframe = dataframe.rename(columns={
        "final_score":        "score",
        "signals_detected":   "signals",
        "industry_fit":       "industry",
        "geography_fit":      "geo_fit",
        "program_fit":        "prog_fit",
        "recommended_project":"recommended_action",
        "outreach_owner":     "owner",
    })
    dataframe["score"] = pd.to_numeric(dataframe.get("score"), errors="coerce")
    dataframe["raw_total"] = pd.to_numeric(dataframe.get("raw_total", 0), errors="coerce").fillna(0).astype(int)
    dataframe["age_decay"] = pd.to_numeric(dataframe.get("age_decay", 0), errors="coerce").fillna(0).astype(int)
    if "tier" in dataframe.columns:
        dataframe["tier"] = dataframe["tier"].astype(str).str.strip().str.upper()
    return dataframe


def format_score(score: object) -> str:
    """Render missing scores as N/A instead of pandas NaN."""
    if pd.isna(score):
        return "N/A"
    return str(score)


# ── PRESENTATION HELPERS ──────────────────────────────────────────────────────

def _tier_badge(t: str) -> str:
    cls = {"A": "tier-a", "B": "tier-b", "C": "tier-c"}.get(str(t).upper(), "tier-d")
    return f'<span class="{cls}">Tier {t}</span>'


def _urgency_badge(u: str) -> str:
    cls = {"high": "urg-high", "medium": "urg-medium", "low": "urg-low"}.get(str(u).lower(), "urg-low")
    return f'<span class="{cls}">{u}</span>'


def _score_bar(score: int, raw: int | None = None, decay: int | None = None) -> str:
    pct   = min(int(score) if not pd.isna(score) else 0, 100)
    color = "#00e97a" if pct >= 82 else "#3d8ef8" if pct >= 69 else "#f5a623" if pct >= 55 else "#253650"
    note  = ""
    if raw is not None and decay is not None:
        note = f'<span style="font-size:11px;color:#4a5878;margin-left:8px;">raw {raw} − decay {decay} = {score}</span>'
    return f'<div class="score-bar-bg"><div style="width:{pct}%;height:4px;background:{color};border-radius:4px;"></div></div>{note}'


def _signal_pills(signals_str: str) -> str:
    if not signals_str or str(signals_str).lower() in ["nan", "none", ""]:
        return '<span style="color:#4a5878;font-size:11px;">No signals</span>'
    pills = ""
    for s in str(signals_str).split(","):
        s = s.strip()
        if s:
            pills += f'<span class="signal-pill">{s}</span>'
    return pills


def _card_class(t: str) -> str:
    return {"A": "lc-a", "B": "lc-b", "C": "lc-c"}.get(str(t).upper(), "lc-d")


def render_lead_card(row: pd.Series) -> None:
    """Render a single lead as a styled dark card."""
    tier     = str(row.get("tier", "D")).upper()
    score    = row.get("score", 0)
    raw      = row.get("raw_total", None)
    decay    = row.get("age_decay", None)
    company  = str(row.get("company", ""))
    role     = str(row.get("role", ""))
    location = str(row.get("location", ""))
    urgency  = str(row.get("urgency", ""))
    project  = str(row.get("recommended_action", ""))
    owner    = str(row.get("owner", ""))
    rationale= str(row.get("rationale", ""))
    signals  = str(row.get("signals", ""))
    score_int = int(score) if not pd.isna(score) else 0

    st.markdown(f"""
    <div class="lead-card {_card_class(tier)}">
      <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:8px;">
        <div>
          <div class="company-name">{company}</div>
          <div class="role-name">{role}</div>
        </div>
        <div style="display:flex;gap:8px;align-items:center;flex-wrap:wrap;">
          {_tier_badge(tier)}
          <span style="font-family:'DM Mono',monospace;font-size:22px;font-weight:600;color:#e8eef7;">{format_score(score)}</span>
          {_urgency_badge(urgency)}
        </div>
      </div>
      {_score_bar(score_int, raw, decay)}
      <div class="meta-row">
        <div class="meta-item">📍 <span class="meta-val">{location}</span></div>
        <div class="meta-item">🎯 <span class="meta-val">{project}</span></div>
        <div class="meta-item">👤 <span class="meta-val">{owner}</span></div>
      </div>
      <div style="margin-bottom:6px;">{_signal_pills(signals)}</div>
      <div class="rationale-text">{rationale}</div>
    </div>
    """, unsafe_allow_html=True)


def render_filters(df: pd.DataFrame, default_tiers: list[str] | None = None) -> tuple:
    """Render tier / urgency / search filters and return the selected values."""
    if default_tiers is None:
        default_tiers = ["A", "B"]
    f1, f2, f3 = st.columns([1, 1, 2])
    with f1:
        tier_opts = ["A", "B", "C", "D"]
        tier_f = st.multiselect("Tier", tier_opts, default=default_tiers,
                                label_visibility="collapsed", placeholder="Filter by tier…")
    with f2:
        urg_opts = sorted(df["urgency"].dropna().unique().tolist()) if "urgency" in df.columns else []
        urg_f = st.multiselect("Urgency", urg_opts, label_visibility="collapsed",
                               placeholder="Filter by urgency…")
    with f3:
        search = st.text_input("Search", placeholder="Search company or role…",
                               label_visibility="collapsed")
    return tier_f, urg_f, search


def apply_filters(df: pd.DataFrame, tier_f: list, urg_f: list, search: str) -> pd.DataFrame:
    out = df.copy()
    if tier_f and "tier" in out.columns:
        out = out[out["tier"].isin(tier_f)]
    if urg_f and "urgency" in out.columns:
        out = out[out["urgency"].isin(urg_f)]
    if search:
        mask = (
            out.get("company", pd.Series(dtype=str)).astype(str).str.contains(search, case=False, na=False) |
            out.get("role",    pd.Series(dtype=str)).astype(str).str.contains(search, case=False, na=False)
        )
        out = out[mask]
    return out


def export_button(data: pd.DataFrame, label: str = "⬇ Export to Excel",
                  filename: str = "magelli_leads.xlsx") -> None:
    buf = BytesIO()
    data.to_excel(buf, index=False)
    buf.seek(0)
    st.download_button(label, data=buf, file_name=filename,
                       mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")


# ── SECTION RENDERERS ─────────────────────────────────────────────────────────

def render_overview(df: pd.DataFrame) -> None:
    total_leads = len(df)
    flagged_leads = len(df[df["flagged"].astype(str).str.lower() == "yes"])
    avg_score = round(df["score"].mean(), 1) if df["score"].notna().any() else 0

    st.subheader("Overview")
    st.caption("Summary of overall opportunity pipeline and scoring performance.")

    m1, m2, m3 = st.columns(3)
    m1.metric("Total Leads", total_leads)
    m2.metric("Flagged for Outreach", flagged_leads)
    m3.metric("Average Score", avg_score)

    st.markdown("### What this dashboard does")
    st.write(
        "This dashboard converts job-posting signals into prioritized consulting "
        "opportunities for Magelli staff to review and act on."
    )


def render_top_leads(df: pd.DataFrame) -> None:
    top = df[df["flagged"].astype(str).str.lower() == "yes"]
    top = top.sort_values(by="score", ascending=False).head(5)

    st.subheader("Top Recommended Opportunities")
    st.caption("Highest-priority consulting opportunities based on scoring and signals.")

    st.markdown('<div class="section-divider">Filters</div>', unsafe_allow_html=True)
    tier_f, urg_f, search = render_filters(top, default_tiers=["A", "B"])
    filtered = apply_filters(top, tier_f, urg_f, search)
    st.markdown(f"<div style='color:#4a5878;font-size:12px;margin-bottom:12px;'>{len(filtered)} leads shown</div>",
                unsafe_allow_html=True)
    for _, row in filtered.iterrows():
        render_lead_card(row)
    if not filtered.empty:
        export_button(filtered, filename="magelli_top_leads.xlsx")


def render_recommended_actions(df: pd.DataFrame) -> None:
    top = df[df["flagged"].astype(str).str.lower() == "yes"]
    top = top.sort_values(by="score", ascending=False).head(5)

    st.subheader("Recommended Actions")
    st.caption("Suggested outreach actions for the highest-value opportunities.")

    if top.empty:
        st.info("No flagged opportunities yet.")
        return

    st.markdown('<div class="section-divider">Filters</div>', unsafe_allow_html=True)
    tier_f, urg_f, search = render_filters(top, default_tiers=["A", "B"])
    filtered = apply_filters(top, tier_f, urg_f, search)
    st.markdown(f"<div style='color:#4a5878;font-size:12px;margin-bottom:12px;'>{len(filtered)} leads shown</div>",
                unsafe_allow_html=True)
    for _, row in filtered.iterrows():
        render_lead_card(row)


def render_signal_insights(df: pd.DataFrame) -> None:
    st.subheader("Signal Insights")
    st.caption("Breakdown of hiring and business signals driving opportunity scores.")

    if "signals" in df.columns:
        signal_counts = df["signals"].fillna("No signal listed").value_counts()
        st.bar_chart(signal_counts)
    else:
        st.info("No signal data available yet.")


def render_industry_trends(df: pd.DataFrame) -> None:
    st.subheader("Industry Trends")
    st.caption("Industries with the strongest concentration of high-value opportunities.")

    if "industry" in df.columns:
        industry_scores = df.groupby("industry")["score"].mean().sort_values(
            ascending=False
        )
        st.bar_chart(industry_scores)
    else:
        st.info("No industry data available yet.")


def render_all_leads(df: pd.DataFrame) -> None:
    st.subheader("All Leads")
    st.caption("Complete dataset of scraped and scored opportunities.")

    st.markdown('<div class="section-divider">Filters</div>', unsafe_allow_html=True)
    tier_f, urg_f, search = render_filters(df, default_tiers=["A", "B", "C", "D"])
    filtered = apply_filters(df.sort_values("score", ascending=False), tier_f, urg_f, search)
    st.markdown(f"<div style='color:#4a5878;font-size:12px;margin-bottom:12px;'>{len(filtered)} leads shown</div>",
                unsafe_allow_html=True)
    st.dataframe(filtered, use_container_width=True)
    export_button(filtered, filename="magelli_all_leads.xlsx")


def render_lead_detail_view(df: pd.DataFrame) -> None:
    st.subheader("Lead Detail View")
    st.caption(
        "Detailed breakdown of a selected opportunity, including signals and "
        "recommended actions."
    )

    company_list = df["company"].dropna().unique()

    if len(company_list) == 0:
        st.info("No companies available yet.")
        return

    selected_company = st.selectbox("Select a company", sorted(company_list))
    selected_row = df[df["company"] == selected_company].iloc[0]
    render_lead_card(selected_row)

    st.markdown('<div class="section-divider">Score Breakdown</div>', unsafe_allow_html=True)
    breakdown = pd.DataFrame({
        "Component": ["Raw Total", "Age Decay", "Final Score"],
        "Value": [
            selected_row.get("raw_total", "N/A"),
            f'−{selected_row.get("age_decay", 0)}',
            format_score(selected_row.get("score")),
        ],
    })
    st.dataframe(breakdown, use_container_width=True, hide_index=True)


def render_dashboard_section(section: str) -> None:
    """Render the selected dashboard view."""
    try:
        df = load_leads_data()
    except Exception as exc:  # noqa: BLE001
        st.error(f"Unable to load the Google Sheet data: {exc}")
        return

    st.success("Live Google Sheet connected successfully")

    if df.empty:
        st.warning("No leads available yet. Run the flow to populate the Google Sheet.")
        return

    if section == "Overview":
        render_overview(df)
    elif section == "Top Leads":
        render_top_leads(df)
    elif section == "Recommended Actions":
        render_recommended_actions(df)
    elif section == "Signal Insights":
        render_signal_insights(df)
    elif section == "Industry Trends":
        render_industry_trends(df)
    elif section == "All Leads":
        render_all_leads(df)
    elif section == "Lead Detail View":
        render_lead_detail_view(df)


def render_copilot_webchat() -> None:
    """Render the public Copilot Studio webchat at the bottom of the page."""
    st.markdown("---")
    st.subheader("Copilot Chat")
    st.caption("Chat with the public Copilot Studio agent directly from this page.")

    webchat_url = get_webchat_url()
    iframe_markup = f"""
    <iframe
        src="{webchat_url}"
        frameborder="0"
        style="width: 100%; height: 720px; border: 1px solid rgba(49, 51, 63, 0.2); border-radius: 12px;"
    ></iframe>
    """
    components.html(iframe_markup, height=740)


def main() -> None:
    inject_button_styles()
    initialize_session_state()
    st_autorefresh(interval=30_000)
    render_header()
    render_sidebar_navigation()
    render_dashboard_section(st.session_state.section)
    render_copilot_webchat()


if __name__ == "__main__":
    main()
