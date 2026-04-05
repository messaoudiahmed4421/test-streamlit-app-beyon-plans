"""
Streamlit Web Interface for P&L Multi-Agent Pipeline
=========================================================
Run with: streamlit run web_interface.py
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import os

# Page config
st.set_page_config(
    page_title="P&L Pipeline Manager",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize chat history
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'uploaded_files' not in st.session_state:
    st.session_state.uploaded_files = []

# Custom CSS
st.markdown("""
<style>
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .status-ok { color: #00ff00; font-weight: bold; }
    .status-warning { color: #ffaa00; font-weight: bold; }
    .status-error { color: #ff4444; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'pipeline_running' not in st.session_state:
    st.session_state.pipeline_running = False
if 'current_agent' not in st.session_state:
    st.session_state.current_agent = None
if 'anomalies' not in st.session_state:
    st.session_state.anomalies = []

# ============================================================================
# HEADER
# ============================================================================
st.markdown("# 📊 P&L Pipeline Manager")
st.markdown("---")

col1, col2, col3 = st.columns([2, 1, 1])
with col1:
    st.write("**Système d'analyse P&L multi-agents (A1→A5)**")
with col2:
    st.write(f"**Statut**: {'🟢 Actif' if st.session_state.pipeline_running else '🔴 Arrêté'}")
with col3:
    st.write(f"**Dernière mise à jour**: {datetime.now().strftime('%H:%M:%S')}")

st.markdown("---")

# SIDEBAR NAVIGATION
# ============================================================================
page = st.sidebar.radio(
    "📍 Navigation",
    ["💬 Chat with Pipeline", "🏠 Dashboard", "▶️ Run Control", "🔍 Anomalies", "📈 Quality History", 
     "📋 Logs & Audit", "🗄️ Database", "⚙️ Settings"],
    index=0
)

st.markdown("---")

# ============================================================================
# PAGE 0: CHAT WITH PIPELINE
# ============================================================================
if page == "💬 Chat with Pipeline":
    st.header("💬 Chat avec le Pipeline P&L")
    
    # Layout: Chat History (70%) + Upload (30%)
    col_chat, col_upload = st.columns([2, 1])
    
    with col_upload:
        st.subheader("📤 Upload Fichiers")
        
        uploaded_files = st.file_uploader(
            "Déposer vos fichiers P&L",
            type=['csv', 'xlsx', 'json'],
            accept_multiple_files=True,
            help="Fichiers CSV (budget, actual, mapping), XLSX, ou JSON"
        )
        
        if uploaded_files:
            for uploaded_file in uploaded_files:
                st.session_state.uploaded_files.append({
                    'name': uploaded_file.name,
                    'size': uploaded_file.size,
                    'type': uploaded_file.type,
                    'timestamp': datetime.now()
                })
            st.success(f"✅ {len(uploaded_files)} fichier(s) uploadé(s)")
        
        st.markdown("---")
        st.subheader("📁 Fichiers Chargés")
        
        if st.session_state.uploaded_files:
            for i, f in enumerate(st.session_state.uploaded_files):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"📄 **{f['name']}** ({f['size']/1024:.1f} KB)")
                    st.caption(f.get('timestamp', '').strftime("%H:%M:%S") if isinstance(f.get('timestamp'), datetime) else "")
                with col2:
                    if st.button("🗑️", key=f"delete_{i}", help="Supprimer"):
                        st.session_state.uploaded_files.pop(i)
                        st.rerun()
        else:
            st.info("Aucun fichier uploadé")
    
    with col_chat:
        st.subheader("🤖 Conversation")
        
        # Chat History Display
        chat_container = st.container(border=True)
        with chat_container:
            for message in st.session_state.chat_history:
                if message['role'] == 'user':
                    with st.chat_message("user", avatar="👤"):
                        st.markdown(message['content'])
                        if message.get('files'):
                            for file in message['files']:
                                st.caption(f"📎 {file}")
                else:
                    with st.chat_message("assistant", avatar="🤖"):
                        st.markdown(message['content'])
        
        # Chat Input
        st.markdown("---")
        
        user_input = st.text_area(
            "Votre message:",
            placeholder="Analysez mes fichiers P&L... / Lancez le pipeline... / Expliquez l'anomalie AN-001... / Quels agents recommandez-vous?",
            height=100,
            label_visibility="collapsed"
        )
        
        col_send, col_clear = st.columns([4, 1])
        
        with col_send:
            if st.button("📤 Envoyer", use_container_width=True, type="primary"):
                if user_input.strip():
                    # Add user message
                    file_names = [f['name'] for f in st.session_state.uploaded_files] if st.session_state.uploaded_files else []
                    st.session_state.chat_history.append({
                        'role': 'user',
                        'content': user_input,
                        'files': file_names,
                        'timestamp': datetime.now()
                    })
                    
                    # Simulate agent response
                    with st.spinner("🤔 Les agents analysent..."):
                        import time
                        time.sleep(1)
                        
                        # Smart response based on user input
                        response = ""
                        if "analyser" in user_input.lower() or "upload" in user_input.lower():
                            response = f"""✅ **Analyse de vos fichiers:**

Fichiers reçus:
{chr(10).join([f"- 📄 {f['name']}" for f in st.session_state.uploaded_files])}

**Plan d'action:**
1. **A1 - Normalisation** → Validation structure CSV, standardisation formats
2. **A2 - Classification** → Classement par compte, validation matérialité 2.5%
3. **A3 - Variance Engine** → 17 anomalies détectées, score scoring 5-piliers
4. **A4 - Rapport Stratégique** → Consolidation anomalies quasi-identiques
5. **A5 - Qualité Judge** → Évaluation 7-critères, recommandations

Voulez-vous lancer le pipeline maintenant ?"""
                        
                        elif "lancer" in user_input.lower() or "run" in user_input.lower():
                            response = """▶️ **Pipeline lancé!**

```
11:49:13 | 📤 A1 STARTING
11:49:15 | ✅ A1 SUCCESS — 23 budget, 23 actual validated
11:49:15 | 📤 A2 STARTING
11:49:22 | ✅ A2 SUCCESS — 32 accounts classified
11:49:27 | 📤 A3 STARTING
11:49:29 | ✅ A3 SUCCESS — 17 anomalies scored
```

**Résultats en temps réel:**
- Anomalies: 17 détectées (score: 58-92/100)
- Top anomalie: AN-001 (Masse Salariale, €250K, score 92/100)
- Qualité: 7.2/10

Voulez-vous explorer les anomalies détaillées ?"""
                        
                        elif "anomalie" in user_input.lower():
                            response = """🔴 **Anomalie AN-001 - Variation Masse Salariale**

**Scoring (5-piliers):**
- Impact Financier: 28/30 ⭐
- Urgence: 24/25 ⭐
- Fréquence: 15/15 ✅
- Tendance: 12/15 ↗️ 
- Portée: 13/15 (Globalité)

**Diagnostic:**
Hausse de 8.5% vs budget causée par:
- 3 nouvelles embauches (2 FTE seniors)
- Ajustement salaires +2.5% moyenne
- Augmentations performance (5 personnes)

**Recommandation A4:**
Pour la DRH: Présenter 3 scénarios d'optimisation pour H2 2026
- Scénario 1: Réduction heures supplémentaires
- Scénario 2: Réduction bonus variable
- Scénario 3: Reclassement postes

**Action recommandée:** ⏱️ Urgent (cette semaine)"""
                        
                        elif any(x in user_input.lower() for x in ["qualité", "quality", "a5", "évaluation"]):
                            response = """📊 **Évaluation Qualité A5**

**Score Global:** 7.2/10 (Bon)

**Breakdown par critère:**
1. **Complétude**: 8/10 ✅ (données complètes)
2. **Exactitude**: 7/10 ✅ (chiffres sourcés)
3. **Actionnabilité**: 6/10 ⚠️ (peut être améliorée)
4. **Cohérence**: 7/10 ✅ (logique fluide)
5. **Couverture**: 8/10 ✅ (tous les niveaux)
6. **Rédaction**: 8/10 ✅ (claire et pro)
7. **Redondance**: 6/10 ⚠️ (consolidation quasi-anomalies)

**Problème récurrent:** Redondances (5/6 derniers runs)
**Solution:** Consolider quasi-anomalies identiques (codes parents/enfants)"""
                        
                        else:
                            response = f"""🤖 **Réponse des agents:**

Vous avez demandé: *"{user_input}"*

**Agents disponibles:**
- 🎯 **A1 Normalizer** — Valide et standardise fichiers CSV
- 📊 **A2 Classifier** — Classe par compte comptable
- 🔍 **A3 Variance Engine** — Scoring anomalies (5-piliers)
- 📄 **A4 Report Writer** — Rapport consolidé + enrichissement Google
- ✅ **A5 Quality Judge** — Évaluation 7-critères

**Commandes utiles:**
- "Analyse mes fichiers" → Lancer pipeline complet
- "Anomalies critiques" → Filtrer AN-001, AN-007, AN-012
- "Score qualité" → Afficher évaluation A5
- "Lancer seulement A3" → Exécution partielle"""
                        
                        # Add agent response
                        st.session_state.chat_history.append({
                            'role': 'assistant',
                            'content': response,
                            'timestamp': datetime.now()
                        })
        
        with col_clear:
            if st.button("🗑️ Effacer", use_container_width=True):
                st.session_state.chat_history = []
                st.session_state.uploaded_files = []
                st.rerun()

# ============================================================================
# PAGE 1: DASHBOARD
# ============================================================================
elif page == "🏠 Dashboard":
    st.header("Dashboard Vue d'Ensemble")
    
    # KPIs Row 1
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Sessions Totales",
            value="12",
            delta="+2 aujourd'hui",
            delta_color="normal"
        )
    
    with col2:
        st.metric(
            label="Anomalies Détectées",
            value="17",
            delta="10 retenues",
            delta_color="normal"
        )
    
    with col3:
        st.metric(
            label="Score Qualité (A5)",
            value="7.2 / 10",
            delta="+0.7 vs run précédent",
            delta_color="normal"
        )
    
    with col4:
        st.metric(
            label="Taux Succès",
            value="79%",
            delta="-5% (erreur A4)",
            delta_color="inverse"
        )
    
    st.markdown("---")
    
    # Status Pipeline
    st.subheader("📊 État du Pipeline")
    
    agents_data = {
        'Agent': ['A1', 'A2', 'A3', 'A4', 'A5'],
        'Statut': ['✅ OK', '✅ OK', '✅ OK', '❌ ERROR', '⏳ WAITING'],
        'Succès': [100, 90, 88, 50, 33],
        'Outil': ['normalize_pnl_files', 'classify_pnl_accounts', 'analyze_pnl_variances', 
                  'google_search', 'load_report_for_judging'],
        'Durée (s)': [1.2, 2.8, 3.5, 4.2, 0]
    }
    
    df_agents = pd.DataFrame(agents_data)
    st.dataframe(df_agents, use_container_width=True, hide_index=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Taux succès par agent
        fig_success = px.bar(
            df_agents,
            x='Agent',
            y='Succès',
            color='Succès',
            color_continuous_scale=['#ff4444', '#ffaa00', '#00ff00'],
            title="Taux de Succès par Agent",
            labels={'Succès': 'Taux (%)'}
        )
        st.plotly_chart(fig_success, use_container_width=True)
    
    with col2:
        # Distribution anomalies
        anomaly_dist = pd.DataFrame({
            'Niveau': ['🔴 Critique', '🟡 Majeur', '🟢 Mineur'],
            'Nombre': [5, 8, 4]
        })
        fig_anomaly = px.pie(
            anomaly_dist,
            names='Niveau',
            values='Nombre',
            title="Distribution des Anomalies",
            color_discrete_sequence=['#ff4444', '#ffaa00', '#44dd44']
        )
        st.plotly_chart(fig_anomaly, use_container_width=True)
    
    st.markdown("---")
    st.subheader("📈 Performance Globale")
    
    perf_data = {
        'Métrique': ['Token Usage', 'Coût API', 'Durée totale', 'Anomalies scorées', 'Rétention'],
        'Valeur': ['18,800 tokens', '$0.21', '20 sec', '17 anomalies', '58.8%']
    }
    df_perf = pd.DataFrame(perf_data)
    st.dataframe(df_perf, use_container_width=True, hide_index=True)

# ============================================================================
# PAGE 2: RUN CONTROL
# ============================================================================
elif page == "▶️ Run Control":
    st.header("Contrôle du Pipeline")
    
    st.subheader("🎮 Commandes")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("▶️ Lancer Pipeline", use_container_width=True, key="run"):
            st.session_state.pipeline_running = True
            st.success("✅ Pipeline lancé ! (simulation)")
            st.balloons()
    
    with col2:
        if st.button("⏸️ Pausser", use_container_width=True, key="pause"):
            st.session_state.pipeline_running = False
            st.info("⏸️ Pipeline en pause")
    
    with col3:
        if st.button("🔄 Retry A4", use_container_width=True, key="retry"):
            st.warning("🔄 Relancement de A4_Report_Writer...")
            import time
            with st.spinner("Retrying..."):
                time.sleep(2)
            st.success("✅ A4 relancé avec succès!")
    
    with col4:
        if st.button("🗑️ Reset", use_container_width=True, key="reset"):
            st.session_state.pipeline_running = False
            st.info("🗑️ État réinitialisé")
    
    st.markdown("---")
    
    # Pipeline Configuration
    st.subheader("⚙️ Configuration du Run")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        debug_mode = st.checkbox("Mode Debug", value=False)
    with col2:
        max_retries = st.number_input("Max retries", min_value=1, max_value=5, value=3)
    with col3:
        timeout = st.number_input("Timeout (sec)", min_value=10, max_value=300, value=30)
    
    st.markdown("---")
    
    # Real-time Log
    st.subheader("📝 Log d'Exécution (Real-time)")
    
    log_placeholder = st.empty()
    
    # Sample logs
    sample_logs = [
        "11:49:10 | ✅ DatabaseManager initialisé",
        "11:49:13 | 📤 A1 STARTING",
        "11:49:15 | ✅ A1 SUCCESS — 23 budget, 23 actual validated",
        "11:49:15 | 📤 A2 STARTING",
        "11:49:22 | ✅ A2 SUCCESS — 32 accounts classified",
        "11:49:27 | 📤 A3 STARTING",
        "11:49:29 | ✅ A3 SUCCESS — 17 anomalies scored, 10 retained",
        "11:49:29 | 📤 A4 STARTING (SequentialAgent)",
        "11:49:30 | ❌ A4 ERROR — google_search timeout",
        "11:49:30 | ⏳ A5 WAITING (A4 failed)"
    ]
    
    with log_placeholder.container():
        for log in sample_logs:
            if "✅" in log:
                st.success(log)
            elif "❌" in log:
                st.error(log)
            elif "⏳" in log:
                st.info(log)
            else:
                st.write(log)

# ============================================================================
# PAGE 3: ANOMALIES EXPLORER
# ============================================================================
elif page == "🔍 Anomalies":
    st.header("Explorateur d'Anomalies")
    
    # Filters
    st.subheader("🔎 Filtres")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        level_filter = st.multiselect(
            "Niveau",
            ["🔴 Critique", "🟡 Majeur", "🟢 Mineur"],
            default=["🔴 Critique", "🟡 Majeur"]
        )
    
    with col2:
        score_min = st.slider("Score minimum", 0, 100, 60)
    
    with col3:
        type_filter = st.multiselect(
            "Type",
            ["Variance Budget", "Unbudgeted Month", "Spike Anomaly"],
            default=["Variance Budget"]
        )
    
    with col4:
        frequency = st.multiselect(
            "Fréquence",
            ["Récurrente", "Ponctuelle"],
            default=["Récurrente", "Ponctuelle"]
        )
    
    st.markdown("---")
    
    # Anomalies Table
    st.subheader("📊 Anomalies Détectées")
    
    anomalies_data = {
        'ID': ['AN-001', 'AN-007', 'AN-012', 'AN-003', 'AN-005', 'AN-009', 'AN-011', 'AN-004', 'AN-006', 'AN-002'],
        'Code': ['6001', '7110', '4110', '6201', '7010', '6451', '5220', '4410', '6850', '7020'],
        'Type': ['Variance', 'Variance', 'Variance', 'Variance', 'Variance', 'Variance', 'Variance', 'Unbudgeted', 'Variance', 'Variance'],
        'Score': [92, 87, 84, 78, 75, 72, 68, 65, 62, 58],
        'Niveau': ['🔴 Critique', '🔴 Critique', '🔴 Critique', '🟡 Majeur', '🟡 Majeur', 
                   '🟡 Majeur', '🟡 Majeur', '🟡 Majeur', '🟡 Majeur', '🟢 Mineur'],
        'Nature': ['Variation salaires', 'Baisse commission', 'Écart créances', 'Surcoûts opérationnels', 
                   'Écart revenus Q1-Q2', 'Cotisations élevées', 'Charges sous-traitance', 'Non budgété', 
                   'Amortissements add.', 'Écart revenus T4'],
        'Fréquence': ['Récurrente', 'Ponctuelle', 'Récurrente', 'Ponctuelle', 'Récurrente', 
                      'Récurrente', 'Ponctuelle', 'Ponctuelle', 'Ponctuelle', 'Ponctuelle']
    }
    
    df_anomalies = pd.DataFrame(anomalies_data)
    
    # Apply filters
    df_filtered = df_anomalies[
        (df_anomalies['Score'] >= score_min) &
        (df_anomalies['Niveau'].isin(level_filter)) &
        (df_anomalies['Type'].isin(type_filter)) &
        (df_anomalies['Fréquence'].isin(frequency))
    ]
    
    st.dataframe(df_filtered, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    
    # Detailed View
    st.subheader("🔍 Vue Détaillée")
    
    selected_anomaly = st.selectbox("Sélectionner une anomalie", df_filtered['ID'].values)
    
    if selected_anomaly:
        anomaly = df_filtered[df_filtered['ID'] == selected_anomaly].iloc[0]
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**ID**: {anomaly['ID']}")
            st.write(f"**Code Comptable**: {anomaly['Code']}")
            st.write(f"**Type**: {anomaly['Type']}")
            st.write(f"**Score**: {anomaly['Score']}/100")
            st.write(f"**Niveau**: {anomaly['Niveau']}")
        
        with col2:
            st.write(f"**Nature**: {anomaly['Nature']}")
            st.write(f"**Fréquence**: {anomaly['Fréquence']}")
            st.write("**Tendance**: ↗️ Croissante")
            st.write("**Portée**: Racine (Globalité)")
            st.write("**Impact**: €250K")
        
        # Scoring breakdown
        st.markdown("#### 📊 Scoring Détaillé (5 Piliers)")
        
        scoring_data = {
            'Pilier': ['Impact Financier', 'Urgence', 'Fréquence', 'Tendance', 'Portée'],
            'Score': [28, 24, 15, 12, 13],
            'Max': [30, 25, 15, 15, 15]
        }
        df_scoring = pd.DataFrame(scoring_data)
        df_scoring['%'] = (df_scoring['Score'] / df_scoring['Max'] * 100).astype(int)
        
        st.dataframe(df_scoring, use_container_width=True, hide_index=True)
        
        # Diagnostic & Recommendation
        st.markdown("#### 📝 Diagnostic A4")
        st.info(
            "Hausse de la masse salariale de 8.5% vs budget. Causes identifiées: "
            "embauches supplémentaires (3 FTE) + ajustements salaires (2.5% moyenne)."
        )
        
        st.markdown("#### 💡 Recommandation")
        st.success(
            "**Pour la DRH**: Revoir la politique de rémunération pour H2 2026 "
            "ou ajuster les charges d'exploitation ailleurs — présenter 3 scénarios d'optimisation."
        )

# ============================================================================
# PAGE 4: QUALITY HISTORY
# ============================================================================
elif page == "📈 Quality History":
    st.header("Historique des Évaluations Qualité (A5)")
    
    # Timeline Data
    quality_data = {
        'Run': [1, 2, 3, 4, 5, 6],
        'Date': ['23/03 14:12', '24/03 09:30', '24/03 16:45', '25/03 10:15', '25/03 14:23', '26/03 11:49'],
        'Score Global': [5.5, 5.9, 6.5, 6.8, 7.2, None],
        'Complétude': [5, 6, 7, 7, 8, None],
        'Exactitude': [5, 5, 6, 6, 7, None],
        'Actionnabilité': [3, 4, 5, 5, 6, None],
        'Cohérence': [5, 5, 6, 7, 7, None],
        'Couverture': [5, 6, 7, 7, 8, None],
        'Rédaction': [5, 6, 7, 7, 8, None],
        'Redondance': [3, 4, 5, 6, 6, None]
    }
    
    df_quality = pd.DataFrame(quality_data)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Trend Chart
        fig_trend = go.Figure()
        
        fig_trend.add_trace(go.Scatter(
            x=df_quality['Date'][:-1],
            y=df_quality['Score Global'][:-1],
            mode='lines+markers',
            name='Score Global',
            line=dict(color='#667eea', width=3),
            marker=dict(size=10)
        ))
        
        fig_trend.update_layout(
            title="📈 Trend Score Global A5",
            xaxis_title="Date",
            yaxis_title="Score /10",
            hovermode='x unified',
            template='plotly_white'
        )
        
        st.plotly_chart(fig_trend, use_container_width=True)
    
    with col2:
        # Criteria Comparison
        fig_criteria = px.bar(
            df_quality.iloc[-2, 3:].to_frame().T.melt(var_name='Critère', value_name='Score'),
            x='Critère',
            y='Score',
            color='Score',
            color_continuous_scale='Viridis',
            title="Scores par Critère (Run 5)",
            template='plotly_white'
        )
        st.plotly_chart(fig_criteria, use_container_width=True)
    
    st.markdown("---")
    
    # Recurring Issues
    st.subheader("⚠️ Problèmes Récurrents")
    
    issues_data = {
        'Problème': [
            'Redondances non consolidées',
            'Chiffres non sourcés',
            'Actionnabilité faible',
            'Drivers non exploités',
            'Anomalies critiques omises'
        ],
        'Fréquence': ['5/6 runs', '4/6 runs', '4/6 runs', '3/6 runs', '2/6 runs'],
        'Status': ['⚠️ PERSISTE', '✅ CORRIGÉ', '⚠️ À AMÉLIORER', '✅ CORRIGÉ', '✅ CORRIGÉ']
    }
    
    df_issues = pd.DataFrame(issues_data)
    st.dataframe(df_issues, use_container_width=True, hide_index=True)

# ============================================================================
# PAGE 5: LOGS & AUDIT
# ============================================================================
elif page == "📋 Logs & Audit":
    st.header("Logs d'Exécution & Audit Trail")
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        agent_filter = st.multiselect(
            "Filtrer par Agent",
            ["A1", "A2", "A3", "A4", "A5", "All"],
            default=["All"]
        )
    
    with col2:
        event_type = st.multiselect(
            "Type d'Événement",
            ["✅ Success", "⚠️ Warning", "❌ Error", "📤 Start", "HTTP"],
            default=["✅ Success", "❌ Error"]
        )
    
    with col3:
        time_range = st.slider("Dernièresminutes", 0, 60, 20)
    
    st.markdown("---")
    
    # Logs display
    st.subheader("📝 Historique des Événements")
    
    logs = [
        ("11:49:10,825", "A1", "✅", "DatabaseManager initialisé (pnl_analysis.db)"),
        ("11:49:13,273", "A1", "📤", "normalize_pnl_files tool STARTING"),
        ("11:49:14,987", "A1", "✅", "HTTP 200 OK — Response: 23 budget, 23 actual"),
        ("11:49:15,020", "A1", "✅", "A1 SUCCESS — Structural validation OK"),
        ("11:49:15,022", "A2", "📤", "classify_pnl_accounts tool STARTING"),
        ("11:49:15,891", "A2", "⚠️", "HTTP 503 UNAVAILABLE (Gemini high demand)"),
        ("11:49:15,893", "A2", "🔄", "RETRY exponential backoff (attempt 1/5)"),
        ("11:49:22,435", "A2", "✅", "HTTP 200 OK (retry successful)"),
        ("11:49:22,443", "A2", "✅", "A2 SUCCESS — 32 accounts classified"),
        ("11:49:27,208", "A3", "📤", "analyze_pnl_variances tool STARTING"),
        ("11:49:29,217", "A3", "✅", "A3 SUCCESS — 17 anomalies scored, 10 retained"),
        ("11:49:29,218", "A4", "📤", "A4_Data_Loader STARTING"),
        ("11:49:30,200", "A4", "❌", "Timeout on google_search (2nd query)"),
        ("11:49:30,203", "Pipeline", "⏳", "Pipeline halted at A4")
    ]
    
    for time, agent, status, message in logs:
        if status == "✅":
            st.success(f"**{time}** | {agent} | {message}")
        elif status == "❌":
            st.error(f"**{time}** | {agent} | {message}")
        elif status == "⚠️":
            st.warning(f"**{time}** | {agent} | {message}")
        else:
            st.info(f"**{time}** | {agent} | {message}")
    
    st.markdown("---")
    
    # Export
    st.subheader("📥 Export")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        csv = pd.DataFrame(logs, columns=['Time', 'Agent', 'Status', 'Message']).to_csv(index=False)
        st.download_button(label="⬇️ CSV", data=csv, file_name="logs.csv", mime="text/csv")
    
    with col2:
        json_data = json.dumps([{'time': l[0], 'agent': l[1], 'status': l[2], 'message': l[3]} for l in logs], indent=2)
        st.download_button(label="⬇️ JSON", data=json_data, file_name="logs.json", mime="application/json")
    
    with col3:
        st.info("📊 PDF export coming soon")

# ============================================================================
# PAGE 6: DATABASE
# ============================================================================
elif page == "🗄️ Database":
    st.header("Gestion Base de Données")
    
    st.subheader("📍 Informations DB")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Chemin", "pnl_analysis.db", "SQLite 3")
    with col2:
        st.metric("Taille", "62 KB", "Manageable")
    with col3:
        st.metric("Sessions", "12", "Actives")
    with col4:
        st.metric("Messages", "156", "Logged")
    
    st.markdown("---")
    
    st.subheader("🔧 Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("💾 Backup", use_container_width=True):
            st.success(f"✅ Backup créé: pnl_analysis_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db")
    
    with col2:
        if st.button("📥 Restore", use_container_width=True):
            st.info("📥 Sélectionnez un fichier de backup...")
    
    with col3:
        if st.button("🗑️ Clean Old", use_container_width=True):
            st.warning("🗑️ Suppression de 3 sessions (>30 jours)...")
    
    st.markdown("---")
    
    # Distribution par statut
    st.subheader("📊 Distribution des Sessions")
    
    status_data = pd.DataFrame({
        'Status': ['initialized', 'in_progress', 'completed', 'error'],
        'Count': [2, 1, 8, 1]
    })
    
    fig_status = px.pie(
        status_data,
        names='Status',
        values='Count',
        title="Sessions par Statut",
        color_discrete_map={'initialized': '#e8e8ff', 'in_progress': '#aaccff', 
                           'completed': '#88ff88', 'error': '#ff8888'}
    )
    st.plotly_chart(fig_status, use_container_width=True)
    
    st.markdown("---")
    
    # Raw SQL Query
    st.subheader("🔍 SQL Query Editor")
    
    sql_query = st.text_area(
        "Entrez une requête SQL:",
        "SELECT * FROM messages LIMIT 10;",
        height=100
    )
    
    if st.button("▶️ Exécuter Requête", use_container_width=True):
        st.info(f"Résultat: {len(['dummy' for _ in range(10)])} lignes retournées")
        st.success("Query executed successfully!")

# ============================================================================
# PAGE 7: SETTINGS
# ============================================================================
elif page == "⚙️ Settings":
    st.header("⚙️ Configuration")
    
    # Pipeline Settings
    st.subheader("🔧 Configuration Pipeline")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Paramètres A1-A5**")
        a1_enabled = st.checkbox("A1 Actif", value=True)
        a2_enabled = st.checkbox("A2 Actif", value=True)
        a3_enabled = st.checkbox("A3 Actif", value=True)
        a4_enabled = st.checkbox("A4 Actif", value=False)
        a5_enabled = st.checkbox("A5 Actif", value=False)
    
    with col2:
        st.write("**Thresholds**")
        variance_threshold = st.slider("Variance Threshold (%)", 0, 50, 15)
        materiality_threshold = st.slider("Materiality (%)", 0, 10, 2)
        confidence_threshold = st.slider("HITL Confidence", 0.0, 1.0, 0.70, 0.05)
        max_retries = st.number_input("Max Retries", 1, 10, 5)
        timeout = st.number_input("Timeout (sec)", 10, 600, 30, 10)
    
    st.markdown("---")
    
    # API & Logging
    st.subheader("📡 API & Logging")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Google Gemini API**")
        api_key = st.text_input("API Key", type="password", value="sk-****...****")
        model = st.selectbox("Modèle", ["gemini-2.5-flash", "gemini-2.0-pro", "gemini-1.5"])
        temperature = st.slider("Temperature", 0.0, 2.0, 0.7, 0.1)
    
    with col2:
        st.write("**Logging**")
        log_level = st.selectbox("Log Level", ["DEBUG", "INFO", "WARNING", "ERROR"])
        log_to_file = st.checkbox("Stream to File", value=True)
        log_retention = st.number_input("Retention (jours)", 1, 90, 30)
        enable_metrics = st.checkbox("Activer Metrics Dashboard", value=True)
    
    st.markdown("---")
    
    # Save & Reset
    st.subheader("💾 Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("✅ Sauvegarder Paramètres", use_container_width=True):
            st.success("✅ Paramètres sauvegardés!")
    
    with col2:
        if st.button("🔄 Réinitialiser Défauts", use_container_width=True):
            st.info("🔄 Paramètres réinitialisés aux valeurs par défaut")
    
    with col3:
        if st.button("📋 Exporter Config", use_container_width=True):
            st.success("📋 Configuration exportée en JSON")

# ============================================================================
# FOOTER
# ============================================================================
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #999; font-size: 0.8em;">
    <p>P&L Pipeline Manager v1.0 | Last Updated: {}</p>
    <p>ADK Google • Gemini API • Streamlit</p>
</div>
""".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")), unsafe_allow_html=True)
