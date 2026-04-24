import pandas as pd
import requests
import streamlit as st


DIRECT_LINE_BASE_URL = "https://directline.botframework.com/v3/directline"
USER_ID = "streamlit-user"
REQUEST_TIMEOUT = 30
CSV_URL = (
    "https://docs.google.com/spreadsheets/d/"
    "1DfkJfbrmAYICQaxyFx_jOzPszDa6AfilnxqnJgJm6vY/export?format=csv"
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
    """Create the session state values required by the dashboard and chat UI."""
    st.session_state.setdefault("section", "Overview")
    st.session_state.setdefault("messages", [])
    st.session_state.setdefault("conversation_id", None)
    st.session_state.setdefault("watermark", None)


def build_direct_line_headers(token: str) -> dict[str, str]:
    """Build common Direct Line headers using the bearer token from secrets."""
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }


def start_direct_line_conversation(token: str) -> str:
    """Start a Direct Line conversation and return its conversation id."""
    response = requests.post(
        f"{DIRECT_LINE_BASE_URL}/conversations",
        headers=build_direct_line_headers(token),
        timeout=REQUEST_TIMEOUT,
    )
    response.raise_for_status()
    payload = response.json()
    conversation_id = payload.get("conversationId")

    if not conversation_id:
        raise ValueError("Direct Line did not return a conversationId.")

    return conversation_id


def send_direct_line_message(token: str, conversation_id: str, message_text: str) -> None:
    """Send a message activity into the existing Direct Line conversation."""
    payload = {
        "type": "message",
        "from": {"id": USER_ID},
        "text": message_text,
    }

    response = requests.post(
        f"{DIRECT_LINE_BASE_URL}/conversations/{conversation_id}/activities",
        headers=build_direct_line_headers(token),
        json=payload,
        timeout=REQUEST_TIMEOUT,
    )
    response.raise_for_status()


def fetch_direct_line_activities(
    token: str, conversation_id: str, watermark: str | None
) -> tuple[list[dict], str | None]:
    """Fetch new activities since the last known watermark."""
    params = {}
    if watermark:
        params["watermark"] = watermark

    response = requests.get(
        f"{DIRECT_LINE_BASE_URL}/conversations/{conversation_id}/activities",
        headers=build_direct_line_headers(token),
        params=params,
        timeout=REQUEST_TIMEOUT,
    )
    response.raise_for_status()

    payload = response.json()
    return payload.get("activities", []), payload.get("watermark")


def get_direct_line_token() -> str:
    """Read the Direct Line token from Streamlit secrets."""
    try:
        token = st.secrets["DIRECT_LINE_TOKEN"]
    except Exception as exc:  # noqa: BLE001
        raise ValueError(
            "Missing DIRECT_LINE_TOKEN in Streamlit secrets. Add it to "
            ".streamlit/secrets.toml before using Copilot Chat."
        ) from exc
    return token


def ensure_conversation_started() -> bool:
    """Ensure the chat session has a Direct Line conversation id."""
    if st.session_state.conversation_id:
        return True

    try:
        token = get_direct_line_token()
        st.session_state.conversation_id = start_direct_line_conversation(token)
        st.session_state.watermark = None
        return True
    except requests.RequestException as exc:
        st.error(f"Unable to start the Copilot Studio conversation: {exc}")
    except ValueError as exc:
        st.error(str(exc))

    return False


def append_bot_messages(activities: list[dict]) -> int:
    """Store only bot-authored text messages in the chat transcript."""
    bot_message_count = 0

    for activity in activities:
        if activity.get("type") != "message":
            continue

        sender = activity.get("from", {})
        sender_id = sender.get("id")
        text = activity.get("text", "")

        # Ignore the user's echoed activity and only keep bot-authored text replies.
        if sender_id == USER_ID or not text:
            continue

        st.session_state.messages.append({"role": "assistant", "content": text})
        bot_message_count += 1

    return bot_message_count


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
    """Render sidebar branding and section navigation."""
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
        "Copilot Chat",
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

    st.sidebar.markdown("---")

    if st.sidebar.button("Copilot Chat", use_container_width=True):
        st.session_state.section = "Copilot Chat"

    # Keep the current section valid if the default changes in the future.
    if st.session_state.section not in navigation_sections:
        st.session_state.section = "Overview"


@st.cache_data(show_spinner=False)
def load_leads_data() -> pd.DataFrame:
    """Load the live lead data from Google Sheets."""
    dataframe = pd.read_csv(CSV_URL)
    dataframe.columns = dataframe.columns.str.lower()
    dataframe["score"] = pd.to_numeric(dataframe.get("score"), errors="coerce")
    return dataframe


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
            Score: {row.get('score', 'N/A')} | Tier: {row.get('tier', 'N/A')}  
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
        **Score:** {selected_row.get('score', 'N/A')}  
        **Tier:** {selected_row.get('tier', 'N/A')}  
        **Flagged:** {selected_row.get('flagged', 'N/A')}  

        **Signals:** {selected_row.get('signals', 'N/A')}  

        **Recommended Action:** {selected_row.get('recommended_action', 'Contact this week.')}  

        **Project Type:** {selected_row.get('project_type', 'N/A')}  
        **Urgency:** {selected_row.get('urgency', 'N/A')}
        """
    )


def render_dashboard_section(section: str) -> None:
    """Render the existing dashboard views for the selected section."""
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


def render_chat_history() -> None:
    """Render the current conversation transcript."""
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


def render_copilot_chat() -> None:
    """Render the Copilot Studio chat UI backed by Direct Line."""
    st.subheader("Copilot Chat")
    st.caption("Chat directly with the Microsoft Copilot Studio agent via Direct Line.")

    # Start the Direct Line conversation once and reuse it across reruns.
    if not ensure_conversation_started():
        return

    render_chat_history()

    user_prompt = st.chat_input("Ask the Copilot Studio agent a question")
    if not user_prompt:
        return

    st.session_state.messages.append({"role": "user", "content": user_prompt})
    with st.chat_message("user"):
        st.markdown(user_prompt)

    try:
        token = get_direct_line_token()
    except ValueError as exc:
        st.error(str(exc))
        return

    with st.spinner("Agent is thinking..."):
        try:
            # Post the user's activity to the existing conversation first.
            send_direct_line_message(
                token=token,
                conversation_id=st.session_state.conversation_id,
                message_text=user_prompt,
            )
            # Then pull back only activities newer than the last saved watermark.
            activities, new_watermark = fetch_direct_line_activities(
                token=token,
                conversation_id=st.session_state.conversation_id,
                watermark=st.session_state.watermark,
            )
        except requests.RequestException as exc:
            st.error(f"Unable to exchange messages with the Copilot Studio agent: {exc}")
            return

    # Persist the latest watermark so old activities are not replayed on rerun.
    st.session_state.watermark = new_watermark or st.session_state.watermark
    bot_message_count = append_bot_messages(activities)

    if bot_message_count == 0:
        st.warning("The agent did not return a text response for that message.")
        return

    # Render only the newly added bot messages after the API call completes.
    for message in st.session_state.messages[-bot_message_count:]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


def main() -> None:
    inject_button_styles()
    initialize_session_state()
    render_header()
    render_sidebar_navigation()

    section = st.session_state.section
    if section == "Copilot Chat":
        render_copilot_chat()
    else:
        render_dashboard_section(section)


if __name__ == "__main__":
    main()
