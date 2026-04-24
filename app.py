import streamlit as st
import pandas as pd

st.set_page_config(page_title="Magelli Lead Dashboard", layout="wide")

# Sidebar button styling
st.markdown("""
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
""", unsafe_allow_html=True)

# Header
col1, col2 = st.columns([1, 6])

with col1:
    st.markdown("<div style='margin-top: 25px;'></div>", unsafe_allow_html=True)
    st.image("gies_logo.jpg", width=110)

with col2:
    st.title("Magelli Consulting Opportunity Dashboard")
    st.caption("AI-powered prospect identification for the Magelli Office of Experiential Learning")

# Sidebar branding
st.sidebar.image("gies_logo.jpg", width=140)
st.sidebar.title("Magelli Opportunity Intelligence")
st.sidebar.write("Identify, prioritize, and act on high-value consulting opportunities.")

# Sidebar navigation
if "section" not in st.session_state:
    st.session_state.section = "Overview"

# Core workflow
if st.sidebar.button("Overview", use_container_width=True):
    st.session_state.section = "Overview"

if st.sidebar.button("Top Leads", use_container_width=True):
    st.session_state.section = "Top Leads"

if st.sidebar.button("Recommended Actions", use_container_width=True):
    st.session_state.section = "Recommended Actions"

st.sidebar.markdown("---")

# Analysis
if st.sidebar.button("Signal Insights", use_container_width=True):
    st.session_state.section = "Signal Insights"

if st.sidebar.button("Industry Trends", use_container_width=True):
    st.session_state.section = "Industry Trends"

st.sidebar.markdown("---")

# Data
if st.sidebar.button("All Leads", use_container_width=True):
    st.session_state.section = "All Leads"

if st.sidebar.button("Lead Detail View", use_container_width=True):
    st.session_state.section = "Lead Detail View"

section = st.session_state.section

# Load data
csv_url = "https://docs.google.com/spreadsheets/d/1DfkJfbrmAYICQaxyFx_jOzPszDa6AfilnxqnJgJm6vY/export?format=csv"
df = pd.read_csv(csv_url)
df.columns = df.columns.str.lower()

st.success("Live Google Sheet connected successfully")

if df.empty:
    st.warning("No leads available yet. Run the flow to populate the Google Sheet.")
    st.stop()

# Ensure numeric score
df["score"] = pd.to_numeric(df["score"], errors="coerce")

# Metrics
total_leads = len(df)
flagged_leads = len(df[df["flagged"].astype(str).str.lower() == "yes"])
avg_score = round(df["score"].mean(), 1) if df["score"].notna().any() else 0

# Top leads
top = df[df["flagged"].astype(str).str.lower() == "yes"]
top = top.sort_values(by="score", ascending=False).head(5)

# Sections

if section == "Overview":
    st.subheader("Overview")
    st.caption("Summary of overall opportunity pipeline and scoring performance.")

    m1, m2, m3 = st.columns(3)
    m1.metric("Total Leads", total_leads)
    m2.metric("Flagged for Outreach", flagged_leads)
    m3.metric("Average Score", avg_score)

    st.markdown("### What this dashboard does")
    st.write(
        "This dashboard converts job-posting signals into prioritized consulting opportunities "
        "for Magelli staff to review and act on."
    )

elif section == "Top Leads":
    st.subheader("Top Recommended Opportunities")
    st.caption("Highest-priority consulting opportunities based on scoring and signals.")

    st.dataframe(top, use_container_width=True)

elif section == "Recommended Actions":
    st.subheader("Recommended Actions")
    st.caption("Suggested outreach actions for the highest-value opportunities.")

    if top.empty:
        st.info("No flagged opportunities yet.")
    else:
        for _, row in top.iterrows():
            st.markdown(f"""
            **{row.get('company', 'Unknown Company')}**  
            Role: {row.get('role', 'N/A')}  
            Score: {row.get('score', 'N/A')} | Tier: {row.get('tier', 'N/A')}  
            Recommended action: {row.get('recommended_action', 'Contact this week.')}
            """)

elif section == "Signal Insights":
    st.subheader("Signal Insights")
    st.caption("Breakdown of hiring and business signals driving opportunity scores.")

    if "signals" in df.columns:
        signal_counts = df["signals"].fillna("No signal listed").value_counts()
        st.bar_chart(signal_counts)
    else:
        st.info("No signal data available yet.")

elif section == "Industry Trends":
    st.subheader("Industry Trends")
    st.caption("Industries with the strongest concentration of high-value opportunities.")

    if "industry" in df.columns:
        industry_scores = df.groupby("industry")["score"].mean().sort_values(ascending=False)
        st.bar_chart(industry_scores)
    else:
        st.info("No industry data available yet.")

elif section == "All Leads":
    st.subheader("All Leads")
    st.caption("Complete dataset of scraped and scored opportunities.")

    st.dataframe(df, use_container_width=True)

elif section == "Lead Detail View":
    st.subheader("Lead Detail View")
    st.caption("Detailed breakdown of a selected opportunity, including signals and recommended actions.")

    company_list = df["company"].dropna().unique()

    if len(company_list) == 0:
        st.info("No companies available yet.")
    else:
        selected_company = st.selectbox("Select a company", company_list)
        selected_row = df[df["company"] == selected_company].iloc[0]

        st.markdown(f"""
        ### {selected_row.get('company', 'Unknown Company')}

        **Role:** {selected_row.get('role', 'N/A')}  
        **Location:** {selected_row.get('location', 'N/A')}  
        **Score:** {selected_row.get('score', 'N/A')}  
        **Tier:** {selected_row.get('tier', 'N/A')}  
        **Flagged:** {selected_row.get('flagged', 'N/A')}  

        **Signals:** {selected_row.get('signals', 'N/A')}  

        **Recommended Action:** {selected_row.get('recommended_action', 'Contact this week.')}  

        **Project Type:** {selected_row.get('project_type', 'N/A')}  
        **Urgency:** {selected_row.get('urgency', 'N/A')}
        """)