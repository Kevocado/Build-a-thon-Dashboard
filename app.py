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
    padding: 14px 10px;
    margin: 8px 0;
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
st.sidebar.title("Magelli Lead Agent")
st.sidebar.write("Review scored consulting opportunities and recommended outreach actions.")

# Sidebar navigation without NAVIGATE label
if "section" not in st.session_state:
    st.session_state.section = "Overview"

if st.sidebar.button("Overview", use_container_width=True):
    st.session_state.section = "Overview"

if st.sidebar.button("All Leads", use_container_width=True):
    st.session_state.section = "All Leads"

if st.sidebar.button("Top Leads", use_container_width=True):
    st.session_state.section = "Top Leads"

if st.sidebar.button("Recommended Actions", use_container_width=True):
    st.session_state.section = "Recommended Actions"

section = st.session_state.section

# Load data
csv_url = "https://docs.google.com/spreadsheets/d/1ANLigqPcPFjGn1hB2mwcvtcZupWmf0jhXjkguq3pcI0/export?format=csv"
df = pd.read_csv(csv_url)
df.columns = df.columns.str.lower()

st.success("Live Google Sheet connected successfully")

if df.empty:
    st.warning("No leads available yet. Run the flow to populate the Google Sheet.")
    st.stop()

# Metrics
total_leads = len(df)
flagged_leads = len(df[df["flagged"].astype(str).str.lower() == "yes"])
avg_score = round(df["score"].mean(), 1)

# Top leads
top = df[df["flagged"].astype(str).str.lower() == "yes"]
top = top.sort_values(by="score", ascending=False).head(5)

# Sections
if section == "Overview":
    st.subheader("Overview")
    m1, m2, m3 = st.columns(3)
    m1.metric("Total Leads", total_leads)
    m2.metric("Flagged for Outreach", flagged_leads)
    m3.metric("Average Score", avg_score)

elif section == "All Leads":
    st.subheader("All Leads")
    st.dataframe(df, use_container_width=True)

elif section == "Top Leads":
    st.subheader("Top Recommended Opportunities")
    st.dataframe(top, use_container_width=True)

elif section == "Recommended Actions":
    st.subheader("Recommended Actions")

    for _, row in top.iterrows():
        st.markdown(f"""
        **{row['company']}**  
        Role: {row['role']}  
        Score: {row['score']} | Tier: {row['tier']}  
        Recommended action: {row.get('recommended_action', 'Contact this week.')}
        """)