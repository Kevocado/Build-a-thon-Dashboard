import streamlit as st
import pandas as pd

st.set_page_config(page_title="Magelli Lead Dashboard", layout="wide")

st.title("Magelli Consulting Opportunity Dashboard")
st.caption("AI-powered lead scoring and recommended outreach actions")

uploaded_file = st.file_uploader("Upload scored lead data", type=["csv", "xlsx"])

if uploaded_file:
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    st.success("Data loaded successfully")

    st.subheader("All Leads")
    st.dataframe(df, use_container_width=True)

    if "CLIPPED SCORE" in df.columns:
        score_col = "CLIPPED SCORE"
    elif "Score" in df.columns:
        score_col = "Score"
    else:
        score_col = df.columns[0]

    if "FLAGGED" in df.columns:
        flagged_col = "FLAGGED"
    elif "Flagged" in df.columns:
        flagged_col = "Flagged"
    else:
        flagged_col = None

    st.subheader("Top Recommended Opportunities")

    if flagged_col:
        top = df[df[flagged_col].astype(str).str.lower() == "yes"]
    else:
        top = df

    top = top.sort_values(by=score_col, ascending=False).head(5)
    st.dataframe(top, use_container_width=True)

    st.subheader("Recommended Actions")

    for _, row in top.iterrows():
        company = row.get("Company", "Unknown Company")
        role = row.get("Role", "Unknown Role")
        score = row.get(score_col, "")
        tier = row.get("TIER", row.get("Tier", ""))

        st.markdown(f"""
        **{company}**  
        Role: {role}  
        Score: {score} | Tier: {tier}  
        Recommended action: Contact this week and route to advisor review.
        """)

else:
    st.info("Upload a CSV or Excel file to view the dashboard.")
