import pandas as pd
import streamlit as st
import streamlit.components.v1 as components


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
    """Apply custom styling for sidebar navigation buttons."""
    st.markdown(
        """
        <style>
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
        </style>
        """,
        unsafe_allow_html=True,
    )


def initialize_session_state() -> None:
    """Initialize only the dashboard navigation state."""
    st.session_state.setdefault("section", "Overview")


def get_webchat_url() -> str:
    """Read the public Copilot Studio webchat URL from secrets or use the default."""
    return st.secrets.get("COPILOT_WEBCHAT_URL", DEFAULT_WEBCHAT_URL)


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


@st.cache_data(show_spinner=False)
def load_leads_data() -> pd.DataFrame:
    """Load the live lead data from Google Sheets."""
    dataframe = pd.read_csv(CSV_URL)
    dataframe.columns = dataframe.columns.str.lower()
    dataframe["score"] = pd.to_numeric(dataframe.get("score"), errors="coerce")
    return dataframe


def format_score(score: object) -> str:
    """Render missing scores as N/A instead of pandas NaN."""
    if pd.isna(score):
        return "N/A"
    return str(score)


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
    st.dataframe(top, use_container_width=True)


def render_recommended_actions(df: pd.DataFrame) -> None:
    top = df[df["flagged"].astype(str).str.lower() == "yes"]
    top = top.sort_values(by="score", ascending=False).head(5)

    st.subheader("Recommended Actions")
    st.caption("Suggested outreach actions for the highest-value opportunities.")

    if top.empty:
        st.info("No flagged opportunities yet.")
        return

    for _, row in top.iterrows():
        st.markdown(
            f"""
            **{row.get('company', 'Unknown Company')}**  
            Role: {row.get('role', 'N/A')}  
            Score: {format_score(row.get('score'))} | Tier: {row.get('tier', 'N/A')}  
            Recommended action: {row.get('recommended_action', 'Contact this week.')}
            """
        )


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
    st.dataframe(df, use_container_width=True)


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

    selected_company = st.selectbox("Select a company", company_list)
    selected_row = df[df["company"] == selected_company].iloc[0]

    st.markdown(
        f"""
        ### {selected_row.get('company', 'Unknown Company')}

        **Role:** {selected_row.get('role', 'N/A')}  
        **Location:** {selected_row.get('location', 'N/A')}  
        **Score:** {format_score(selected_row.get('score'))}  
        **Tier:** {selected_row.get('tier', 'N/A')}  
        **Flagged:** {selected_row.get('flagged', 'N/A')}  

        **Signals:** {selected_row.get('signals', 'N/A')}  

        **Recommended Action:** {selected_row.get('recommended_action', 'Contact this week.')}  

        **Project Type:** {selected_row.get('project_type', 'N/A')}  
        **Urgency:** {selected_row.get('urgency', 'N/A')}
        """
    )


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
    render_header()
    render_sidebar_navigation()
    render_dashboard_section(st.session_state.section)
    render_copilot_webchat()


if __name__ == "__main__":
    main()
