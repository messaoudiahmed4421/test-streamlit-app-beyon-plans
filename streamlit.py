"""
Chat-like Streamlit interface for the P&L multi-agent pipeline.
Designed for easy integration with the notebook logic and Streamlit Cloud deployment.
Run with: streamlit run web_interface.py
"""

from datetime import datetime
from io import BytesIO

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


APP_VERSION = "2.0-chat-workspace"

NAV_ITEMS = [
    "Workspace Chat",
    "Dashboard",
    "Dernieres Runs",
    "Performance",
    "Logs",
]

AGENTS_DATA = pd.DataFrame(
    {
        "Agent": ["A1", "A2", "A3", "A4", "A5"],
        "Statut": ["OK", "OK", "OK", "ERROR", "WAITING"],
        "Succes": [100, 92, 88, 50, 40],
        "Duree_s": [1.3, 2.7, 3.6, 4.1, 0.4],
    }
)

QUALITY_DATA = pd.DataFrame(
    {
        "Run": [1, 2, 3, 4, 5],
        "Date": ["23/03", "24/03", "25/03", "26/03", "27/03"],
        "Score Global": [5.5, 6.1, 6.4, 6.9, 7.2],
        "Actionnabilite": [3.0, 4.0, 5.0, 5.5, 6.0],
    }
)

STATIC_LOGS = [
    ("11:49:10", "A1", "SUCCESS", "DatabaseManager initialise"),
    ("11:49:14", "A1", "SUCCESS", "Normalize OK"),
    ("11:49:16", "A2", "SUCCESS", "Classification OK"),
    ("11:49:29", "A3", "SUCCESS", "Anomalies scored"),
    ("11:49:30", "A4", "ERROR", "google_search timeout"),
]


def init_state() -> None:
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [
            {
                "role": "assistant",
                "content": (
                    "Bienvenue. Chargez vos fichiers P&L, puis lancez une requete ici. "
                    "Le rapport et les graphes apparaissent a droite."
                ),
            }
        ]
    if "last_report" not in st.session_state:
        st.session_state.last_report = "Aucun rapport pour le moment."
    if "last_run_time" not in st.session_state:
        st.session_state.last_run_time = None
    if "uploaded_file_names" not in st.session_state:
        st.session_state.uploaded_file_names = []
    if "pipeline_status" not in st.session_state:
        st.session_state.pipeline_status = "idle"
    if "run_history" not in st.session_state:
        st.session_state.run_history = []


def run_pipeline_placeholder(query: str, uploaded_files: list) -> dict:
    """
    Placeholder to keep UI deployable now.
    Replace this function by your real pipeline call from colab x vscode.
    """
    names = [file.name for file in uploaded_files]
    st.session_state.pipeline_status = "running"

    kpis = pd.DataFrame(
        {
            "Metric": ["Anomalies", "Score A5", "Coverage", "Critical"],
            "Value": [17, 7.2, 0.86, 5],
        }
    )

    trend = pd.DataFrame(
        {
            "Period": ["Q1", "Q2", "Q3", "Q4"],
            "Budget": [100, 110, 120, 130],
            "Actual": [103, 118, 109, 149],
        }
    )
    trend["Variance"] = trend["Actual"] - trend["Budget"]

    fig_var = go.Figure()
    fig_var.add_trace(
        go.Bar(
            x=trend["Period"],
            y=trend["Variance"],
            marker_color=["#0f766e" if x >= 0 else "#dc2626" for x in trend["Variance"]],
            name="Variance",
        )
    )
    fig_var.update_layout(
        title="Budget vs Actual Variance",
        yaxis_title="Variance",
        template="plotly_dark",
        height=320,
        margin=dict(l=20, r=20, t=45, b=20),
    )

    fig_mix = px.pie(
        names=["Critique", "Majeur", "Mineur"],
        values=[5, 8, 4],
        title="Repartition des anomalies",
        color_discrete_sequence=["#dc2626", "#f59e0b", "#22c55e"],
        hole=0.45,
    )
    fig_mix.update_layout(
        height=320,
        margin=dict(l=20, r=20, t=45, b=20),
        paper_bgcolor="#0b1220",
        font_color="#f8fafc",
    )

    report = (
        f"Run termine pour la requete: '{query}'\n\n"
        f"Fichiers charges: {', '.join(names) if names else 'aucun'}\n"
        "- 17 anomalies detectees, 10 retenues\n"
        "- Score A5: 7.2/10\n"
        "- Priorite: investiguer les ecarts Q4 et les couts operationnels"
    )

    st.session_state.pipeline_status = "done"
    return {
        "report": report,
        "kpis": kpis,
        "figures": [fig_var, fig_mix],
    }


def export_report_bytes(report_text: str) -> bytes:
    buffer = BytesIO()
    buffer.write(report_text.encode("utf-8"))
    return buffer.getvalue()


st.set_page_config(
    page_title="P&L Chat Pipeline",
    page_icon="PL",
    layout="wide",
    initial_sidebar_state="expanded",
)

init_state()

st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600;700&family=IBM+Plex+Sans:wght@400;500;600&display=swap');

html, body, [class*="css"], .stApp {
    font-family: 'IBM Plex Sans', sans-serif;
}

h1, h2, h3 {
    font-family: 'Space Grotesk', sans-serif;
}

.stApp {
    background:
      radial-gradient(circle at 12% 10%, rgba(20,184,166,0.12), transparent 30%),
      radial-gradient(circle at 88% 15%, rgba(59,130,246,0.14), transparent 32%),
      linear-gradient(165deg, #070b14 0%, #0b1220 100%);
}

[data-testid="stAppViewContainer"] {
    color: #f8fafc;
}

[data-testid="stAppViewContainer"] h1,
[data-testid="stAppViewContainer"] h2,
[data-testid="stAppViewContainer"] h3,
[data-testid="stAppViewContainer"] p,
[data-testid="stAppViewContainer"] label,
[data-testid="stAppViewContainer"] li,
[data-testid="stChatMessageContent"] p {
    color: #f8fafc !important;
}

[data-testid="stAppViewContainer"] [data-testid="stVerticalBlockBorderWrapper"],
[data-testid="stAppViewContainer"] [data-testid="stChatMessage"],
[data-testid="stAppViewContainer"] [data-testid="stTextArea"],
[data-testid="stAppViewContainer"] [data-testid="stFileUploader"],
[data-testid="stAppViewContainer"] [data-testid="stMetric"] {
    background-color: #121a2b !important;
    border-color: #2a3449 !important;
}

[data-testid="stAppViewContainer"] .stTextArea textarea,
[data-testid="stAppViewContainer"] input,
[data-testid="stAppViewContainer"] [data-baseweb="select"] {
    color: #f8fafc !important;
    background-color: #0f172a !important;
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1f2937 0%, #111827 100%);
}

[data-testid="stSidebar"] * {
    color: #e5e7eb !important;
}

.panel-title {
    font-weight: 700;
    letter-spacing: 0.2px;
    color: #f8fafc;
    margin-bottom: 8px;
}
</style>
""",
    unsafe_allow_html=True,
)

st.title("P&L Pipeline Workspace")
st.caption("Interface chat + upload + rapport + graphes, prete pour branchement pipeline reel.")

with st.sidebar:
    page = st.radio("Navigation", NAV_ITEMS, index=0)
    st.markdown("---")
    st.markdown("### Chargement fichiers")
    uploaded_files = st.file_uploader(
        "Importer budget, actuals, mapping...",
        accept_multiple_files=True,
        type=["csv", "xlsx", "xls", "json", "txt"],
    )
    st.session_state.uploaded_file_names = [f.name for f in uploaded_files] if uploaded_files else []
    st.write(f"Fichiers en session: {len(st.session_state.uploaded_file_names)}")
    for name in st.session_state.uploaded_file_names:
        st.write(f"- {name}")

    st.markdown("---")
    st.markdown("### Etat pipeline")
    st.write(f"Statut: {st.session_state.pipeline_status}")
    if st.session_state.last_run_time:
        st.caption(f"Dernier run: {st.session_state.last_run_time}")

if page == "Workspace Chat":
    main_left, main_right = st.columns([1.15, 1], gap="large")

    with main_left:
        st.markdown('<div class="panel-title">Conversation & Requetes</div>', unsafe_allow_html=True)
        with st.container(border=True, height=530):
            for msg in st.session_state.chat_history:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])

        prompt = st.chat_input("Ecrire une requete pipeline (ex: Analyse les variances Q4 et propose plan d'action).")

        if prompt:
            st.session_state.chat_history.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.spinner("Execution du pipeline..."):
                result = run_pipeline_placeholder(prompt, uploaded_files or [])

            st.session_state.last_report = result["report"]
            st.session_state.last_figures = result["figures"]
            st.session_state.last_kpis = result["kpis"]
            run_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            st.session_state.last_run_time = run_time
            st.session_state.run_history.append(
                {
                    "time": run_time,
                    "query": prompt,
                    "files": len(uploaded_files or []),
                    "status": "done",
                }
            )

            assistant_msg = "Pipeline execute. Rapport et graphes mis a jour."
            st.session_state.chat_history.append({"role": "assistant", "content": assistant_msg})
            with st.chat_message("assistant"):
                st.markdown(assistant_msg)

    with main_right:
        st.markdown('<div class="panel-title">Rapport</div>', unsafe_allow_html=True)
        with st.container(border=True, height=250):
            st.text_area(
                "Rapport genere",
                value=st.session_state.last_report,
                height=190,
                label_visibility="collapsed",
            )

        st.download_button(
            "Telecharger le rapport (.txt)",
            data=export_report_bytes(st.session_state.last_report),
            file_name="pipeline_report.txt",
            mime="text/plain",
            use_container_width=True,
        )

        st.markdown("\n")
        st.markdown('<div class="panel-title">Graphes</div>', unsafe_allow_html=True)
        with st.container(border=True):
            if "last_kpis" in st.session_state:
                kpi_cols = st.columns(4)
                for idx, row in st.session_state.last_kpis.iterrows():
                    kpi_cols[idx].metric(row["Metric"], row["Value"])

            if "last_figures" in st.session_state:
                for fig in st.session_state.last_figures:
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Les graphes apparaitront ici apres le premier run.")

elif page == "Dashboard":
    st.subheader("Vue Performance Pipeline")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Runs", str(len(st.session_state.run_history)))
    c2.metric("Score A5", "7.2 / 10")
    c3.metric("Anomalies", "17")
    c4.metric("Etat", st.session_state.pipeline_status)

    d1, d2 = st.columns(2)
    with d1:
        fig_success = px.bar(
            AGENTS_DATA,
            x="Agent",
            y="Succes",
            color="Statut",
            title="Succes par agent",
            color_discrete_map={"OK": "#16a34a", "ERROR": "#dc2626", "WAITING": "#f59e0b"},
        )
        st.plotly_chart(fig_success, use_container_width=True)
    with d2:
        fig_duration = px.line(AGENTS_DATA, x="Agent", y="Duree_s", markers=True, title="Duree moyenne (s)")
        st.plotly_chart(fig_duration, use_container_width=True)

elif page == "Dernieres Runs":
    st.subheader("Historique des derniers runs")
    if st.session_state.run_history:
        history_df = pd.DataFrame(st.session_state.run_history)
        st.dataframe(history_df, use_container_width=True, hide_index=True)
    else:
        st.info("Aucun run execute pour le moment.")

    st.markdown("### Dernier rapport")
    st.code(st.session_state.last_report)

elif page == "Performance":
    st.subheader("Tendances de performance et qualite")
    p1, p2 = st.columns(2)
    with p1:
        fig_trend = px.line(
            QUALITY_DATA,
            x="Date",
            y="Score Global",
            markers=True,
            title="Evolution Score Global",
        )
        st.plotly_chart(fig_trend, use_container_width=True)
    with p2:
        fig_action = px.bar(QUALITY_DATA, x="Date", y="Actionnabilite", title="Actionnabilite")
        st.plotly_chart(fig_action, use_container_width=True)

elif page == "Logs":
    st.subheader("Logs importants")
    logs_df = pd.DataFrame(STATIC_LOGS, columns=["Time", "Agent", "Status", "Message"])
    st.dataframe(logs_df, use_container_width=True, hide_index=True)

st.markdown("---")
st.caption(f"P&L Chat Pipeline v{APP_VERSION} | {datetime.now().strftime('%Y-%m-%d')}")
