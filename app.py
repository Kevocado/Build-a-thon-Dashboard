import streamlit as st
import pandas as pd

st.set_page_config(page_title="Magelli Lead Dashboard", layout="wide")

st.title("Magelli Consulting Opportunity Dashboard")

csv_url = "https://docs.google.com/spreadsheets/d/1ANLigqPcPFjGn1hB2mwcvtcZupWmf0jhXjkguq3pcI0/export?format=csv"

df = pd.read_csv(csv_url)


# Normalize column names (VERY IMPORTANT)
df.columns = df.columns.str.lower()

st.success("Live Google Sheet connected successfully")

st.subheader("All Leads")
st.dataframe(df)

# Top leads
top = df[df["flagged"].astype(str).str.lower() == "yes"]
top = top.sort_values(by="score", ascending=False).head(5)

st.subheader("Top Recommended Opportunities")
st.dataframe(top)

# Recommended actions
st.subheader("Recommended Actions")

for _, row in top.iterrows():
    st.markdown(f"""
    **{row['company']}**  
    Role: {row['role']}  
    Score: {row['score']} | Tier: {row['tier']}  
    Recommended action: Contact this week.
    """)