from pathlib import Path
import pandas as pd
import streamlit as st
from pathlib import Path
import plotly.express as px
import plotly.graph_objects as go

from src.auth import init_auth_state, login, logout, DEMO_EMAIL, DEMO_PASSWORD
from src.styles import inject_css


from src.vehicle_data import (
    load_vehicle_excel,
    validate_vehicle_data,
    clean_vehicle_data,
    get_data_summary
)

from io import BytesIO
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
)

from src.database import (
    get_years,
    get_vehicles_by_year,
    get_vehicle_data,
    get_vehicle_total_mass,
    get_material_composition,
    get_component_composition,
    get_unknown_material_mass,
    get_material_environmental_analysis,
    save_recommendation_validation,
    get_recommendation_validations,
    get_dashboard_kpis,
    get_dashboard_material_impact,
    get_dashboard_carbon_trend,
    get_vehicle_carbon_intensities, 
    save_aiec_report,
    get_aiec_reports,
    get_aiec_report_pdf
)

st.set_page_config(
    page_title="AIEC — Éco-conception industrielle",
    page_icon="♻️",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_css()
init_auth_state()
st.session_state.setdefault("page", "Tableau de bord")


def render_login():
    st.markdown(
        """
<style>
/* Masquer la sidebar sur la page de connexion */

/* Centrer le contenu principal */
div[data-testid="stMainBlockContainer"] {
    max-width: 560px;
    padding-top: 8vh;
    margin-left: auto;
    margin-right: auto;
}

/* En-tête de connexion */
.login-header {
    text-align: center;
    margin-bottom: 25px;
}

.login-brand {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 14px;
    margin-bottom: 30px;
}

.login-logo {
    width: 58px;
    height: 58px;
    border-radius: 14px;
    display: flex;
    justify-content: center;
    align-items: center;
    color: white;
    font-size: 24px;
    font-weight: 800;
    background: linear-gradient(
        135deg,
        #16a34a,
        #059669,
        #2563eb
    );
}

.login-brand-text {
    text-align: left;
}

.login-brand-title {
    font-size: 25px;
    font-weight: 800;
    color: #172033;
    line-height: 1.1;
}

.login-brand-subtitle {
    font-size: 14px;
    color: #6b7280;
    margin-top: 4px;
}

.login-welcome {
    font-size: 29px;
    font-weight: 800;
    color: #172033;
    margin-bottom: 5px;
}

.login-description {
    font-size: 16px;
    color: #6b7280;
}

/* Style du formulaire Streamlit */
div[data-testid="stForm"] {
    background: white;
    padding: 30px;
    border: 1px solid #e4e8ef;
    border-radius: 16px;
    box-shadow: 0 12px 35px rgba(20, 32, 54, 0.08);
}

/* Bouton */
div[data-testid="stForm"] button {
    border-radius: 8px;
    min-height: 46px;
    font-weight: 600;
}
</style>
        """,
        unsafe_allow_html=True,
    )

    # Logo et titre
    st.markdown(
        """
<div class="login-header">

<div class="login-brand">

<div class="login-logo">
IA
</div>

<div class="login-brand-text">
<div class="login-brand-title">AIEC</div>
<div class="login-brand-subtitle">
Éco-conception industrielle
</div>
</div>

</div>

<div class="login-welcome">
Bienvenue
</div>

<div class="login-description">
Connectez-vous pour accéder à votre espace
</div>

</div>
        """,
        unsafe_allow_html=True,
    )

    # Formulaire
    with st.form("login_form"):

        email = st.text_input(
            "Email",
            placeholder="Entrez votre email"
        )

        password = st.text_input(
            "Mot de passe",
            type="password",
            placeholder="Entrez votre mot de passe"
        )

        remember = st.checkbox(
            "Se souvenir de moi"
        )

        submit = st.form_submit_button(
            "Se connecter",
            type="primary",
            use_container_width=True
        )

    # Vérification
    if submit:

        if login(email, password):

            st.success("Connexion réussie.")
            st.rerun()

        else:
            st.error("Email ou mot de passe incorrect.")

def render_sidebar():
    with st.sidebar:
        st.markdown(
            """
            <div class="brand-row" style="margin-bottom:16px;">
                <div class="brand-badge" style="width:40px;height:40px;font-size:17px;">IA</div>
                <div>
                    <p class="brand-title" style="font-size:21px;">AIEC</p>
                    <p class="brand-subtitle">Éco-conception</p>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        pages = [
            ("🏠", "Tableau de bord"),
            ("⬆️", "Importer fichiers CAO"),
            ("📊", "Analyse de l'IA"),
            ("💡", "Recommandations"),
            ("☑️", "Validation"),
            ("🛡️", "Conformité"),
            ("📄", "Rapports"),
        ]

        for icon, label in pages:
            selected = st.session_state.page == label
            if st.button(
                f"{icon}  {label}",
                key=f"nav_{label}",
                type="primary" if selected else "secondary",
                use_container_width=True,
            ):
                st.session_state.page = label
                st.rerun()

        st.divider()
        st.caption(st.session_state.user_email or "")
        if st.button("Se déconnecter", use_container_width=True):
            logout()
            st.rerun()


def render_header():
    st.markdown(
        f"""
        <div class="app-header">
            <div class="header-left">
                <div class="mini-badge">IA</div>
                <div>
                    <span class="header-title">AIEC</span>
                    <span class="header-subtitle">Éco-conception industrielle</span>
                </div>
            </div>
            <div class="user-chip">👤 {st.session_state.user_role}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

MATERIAL_COLORS = {
    "castAluminium": "#2563EB",
    "wroughtAluminium": "#60A5FA",
    "mildSteel": "#F97316",
    "highStrengthSteel": "#8B5CF6",
    "castIron": "#64748B",
    "magnesium": "#10B981",
}

def page_dashboard():

    st.markdown( 
        '<div class="page-title">Tableau de bord</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="page-subtitle">'
        'Vue d’ensemble des données véhicules et '
        'de leurs impacts environnementaux.'
        '</div>',
        unsafe_allow_html=True
    )

    try:

        # ==========================================
        # FILTRE ANNÉE
        # ==========================================
        years = get_years()

        selected_year = st.selectbox(
            "Année d’analyse",
            years,
            key="dashboard_year"
        )

        kpis = get_dashboard_kpis(
            selected_year
        )

        material_impact_df = (
            get_dashboard_material_impact(
                selected_year
            )
        )

        trend_df = (
            get_dashboard_carbon_trend()
        )

        # ==========================================
        # CALCULS KPI
        # ==========================================
        total_mass = (
            kpis["total_mass"]
            if kpis["total_mass"] is not None
            else 0
        )

        identified_mass = (
            kpis["identified_mass"]
            if kpis["identified_mass"] is not None
            else 0
        )

        unknown_mass = (
            kpis["unknown_mass"]
            if kpis["unknown_mass"] is not None
            else 0
        )

        total_carbon = (
            kpis["total_carbon"]
            if kpis["total_carbon"] is not None
            else 0
        )

        if identified_mass > 0:
            carbon_intensity = (
                total_carbon
                / identified_mass
            )
        else:
            carbon_intensity = 0

        # Couverture des matériaux
        if total_mass > 0:
            coverage_rate = (
                identified_mass
                / total_mass
                * 100
            )
        else:
            coverage_rate = 0

        # Part de masse non détaillée
        if total_mass > 0:
            unknown_rate = (
                unknown_mass
                / total_mass
                * 100
            )
        else:
            unknown_rate = 0

        # ==========================================
        # KPI CARDS
        # ==========================================

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.markdown(
                f"""<div class="kpi-card kpi-blue">
        <div class="kpi-label">🚗 Véhicules</div>
        <div class="kpi-value">{int(kpis["vehicle_count"]):,}</div>
        <div class="kpi-footer">Année {selected_year}</div>
        </div>""",
                unsafe_allow_html=True
            )

        with col2:
            st.markdown(
                f"""<div class="kpi-card kpi-purple">
        <div class="kpi-label">⚖️ Masse totale</div>
        <div class="kpi-value">{total_mass:,.0f} kg</div>
        <div class="kpi-footer">Véhicules analysés</div>
        </div>""",
                unsafe_allow_html=True
            )

        with col3:
            st.markdown(
                f"""<div class="kpi-card kpi-orange">
        <div class="kpi-label">🌱 Impact carbone estimé</div>
        <div class="kpi-value">{total_carbon:,.0f}</div>
        <div class="kpi-footer">kgCO₂e — matériaux identifiés</div>
        </div>""",
                unsafe_allow_html=True
            )

        with col4:
            st.markdown(
                f"""<div class="kpi-card kpi-green">
        <div class="kpi-label">📊 Couverture matériaux</div>
        <div class="kpi-value">{coverage_rate:.1f} %</div>
        <div class="kpi-footer">{unknown_mass:,.0f} kg non détaillés</div>
        </div>""",
                unsafe_allow_html=True
            )

        st.write("")
        st.divider()
        

        # =====================================================
        # QUALITÉ DES DONNÉES + INDICATEURS CLÉS
        # =====================================================

        st.markdown("### Qualité et synthèse des données")

        #unknown_rate = max(0, 100 - coverage_rate)

        left_quality, right_quality = st.columns([1, 1])

        # -----------------------------------------------------
        # QUALITÉ DES DONNÉES
        # -----------------------------------------------------

        with left_quality:

            st.markdown("#### Qualité des données")

            st.write("**Couverture matière**")

            st.progress(
                min(max(coverage_rate / 100, 0), 1)
            )

            st.caption(
                f"{coverage_rate:.1f} % de la masse totale "
                "est associée à un matériau identifié."
            )

            st.write("**Masse non détaillée**")

            st.progress(
                min(max(unknown_rate / 100, 0), 1)
            )

            st.caption(
                f"{unknown_rate:.1f} % de la masse ne dispose "
                "pas encore d'une caractérisation matière exploitable."
            )

            if coverage_rate >= 80:
                coverage_status = "Excellente"
            elif coverage_rate >= 60:
                coverage_status = "Correcte"
            else:
                coverage_status = "À améliorer"

            st.caption(
                f"Qualité de couverture : **{coverage_status}**"
            )


        # -----------------------------------------------------
        # INDICATEURS CLÉS
        # -----------------------------------------------------

        with right_quality:

            st.markdown("#### Indicateurs clés")

            if not material_impact_df.empty:

                top_material = material_impact_df.iloc[0]

                top_material_name = top_material["material"]
                top_material_impact = top_material["impact_kgco2e"]

                if total_carbon > 0:
                    top_material_share = (
                        top_material_impact
                        / total_carbon
                        * 100
                    )
                else:
                    top_material_share = 0

            else:

                top_material_name = "N/A"
                top_material_impact = 0
                top_material_share = 0

            metric1, metric2 = st.columns(2)

            metric1.metric(
                "Hotspot principal",
                top_material_name
            )

            metric2.metric(
                "Contribution carbone",
                f"{top_material_share:.1f} %"
            )

            metric3, metric4 = st.columns(2)

            metric3.metric(
                "Intensité carbone",
                f"{carbon_intensity:.2f} kgCO₂e/kg"
            )

            metric4.metric(
                "Familles de composants",
                int(kpis["component_count"])
            )

        # ==========================================
        # DEUXIÈME LIGNE KPI
        # ==========================================

        st.divider()

        # ==========================================
        # GRAPHIQUES
        # ==========================================

        left, right = st.columns(2)

        # --------------------------
        # DONUT
        # --------------------------
        
        with left:
            st.subheader("Répartition de l’impact par matériau")

            if not material_impact_df.empty:

                fig_pie = px.pie(
                    material_impact_df,
                    values="impact_kgco2e",
                    names="material",
                    hole=0.55,
                    color="material",
                    color_discrete_map=MATERIAL_COLORS
                )

                fig_pie.update_traces(
                    textposition="inside",
                    textinfo="percent"
                )

                fig_pie.update_layout(
                    margin=dict(
                        l=10,
                        r=10,
                        t=20,
                        b=10
                    ),
                    legend_title="Matériau"
                )

                st.plotly_chart(
                    fig_pie,
                    use_container_width=True
                )

        # --------------------------
        # BAR CHART
        # --------------------------
        
        with right:
            st.subheader("Matériaux les plus impactants")
            if not material_impact_df.empty:

                top_materials = (
                    material_impact_df
                    .head(6)
                    .sort_values(
                        "impact_kgco2e",
                        ascending=True
                    )
                )

                fig_bar = px.bar(
                    top_materials,
                    x="impact_kgco2e",
                    y="material",
                    orientation="h",
                    text="impact_kgco2e",
                    color="material",
                    color_discrete_map=MATERIAL_COLORS
                )

                fig_bar.update_traces(
                    texttemplate="%{text:.0f}",
                    textposition="outside"
                )

                fig_bar.update_layout(
                    xaxis_title="Impact (kgCO₂e)",
                    yaxis_title="",
                    showlegend=False,
                    margin=dict(
                        l=10,
                        r=30,
                        t=20,
                        b=10
                    )
                )

                st.plotly_chart(
                    fig_bar,
                    use_container_width=True
                )

        # ==========================================
        # HOTSPOTS GLOBAUX
        # ==========================================

        st.divider()
        st.subheader("Hotspots environnementaux globaux")

        if not material_impact_df.empty:

            global_hotspot_df = material_impact_df.copy()
            if total_carbon > 0:

                global_hotspot_df["carbon_share_percent"] = (
                    global_hotspot_df["impact_kgco2e"]
                    / total_carbon
                    * 100
                )

                global_hotspot_df["priority"] = (
                    global_hotspot_df["carbon_share_percent"]
                    .apply(classify_carbon_hotspot)
                )

            else:

                global_hotspot_df["carbon_share_percent"] = 0
                global_hotspot_df["priority"] = "Non calculable"

            global_hotspot_df = global_hotspot_df.sort_values(
                "impact_kgco2e",
                ascending=False
            )
            global_hotspot_display = global_hotspot_df.rename(
                columns={
                    "material": "Matériau",
                    "mass_kg": "Masse (kg)",
                    "impact_kgco2e": "Impact (kgCO₂e)",
                    "carbon_share_percent": "Part de l'impact (%)",
                    "priority": "Priorité"
                }
            )
            global_hotspot_display["Masse (kg)"] = (
                global_hotspot_display["Masse (kg)"].round(0)
            )
            global_hotspot_display["Impact (kgCO₂e)"] = (
                global_hotspot_display["Impact (kgCO₂e)"].round(0)
            )
            global_hotspot_display["Part de l'impact (%)"] = (
                global_hotspot_display[
                    "Part de l'impact (%)"
                ].round(1)
            )
            st.dataframe(
                global_hotspot_display[
                    [
                        "Matériau",
                        "Masse (kg)",
                        "Impact (kgCO₂e)",
                        "Part de l'impact (%)",
                        "Priorité"
                    ]
                ],
                use_container_width=True,
                hide_index=True
            )
    
        # ==========================================
        # TENDANCE
        # ==========================================

        st.subheader(
            "Évolution de l’impact carbone"
        )

        if not trend_df.empty:

            fig_trend = px.line(
                trend_df,
                x="year",
                y="impact_kgco2e",
                markers=True
            )

            fig_trend.update_layout(
                xaxis_title="Année",
                yaxis_title="Impact estimé (kgCO₂e)",
                hovermode="x unified"
            )

            st.plotly_chart(
                fig_trend,
                use_container_width=True
            )

        # ==========================================
        # SYNTHÈSE
        # ==========================================

        st.divider()

        if not material_impact_df.empty:

            top_material = (
                material_impact_df.iloc[0]
            )

            top_material_name = (
                top_material["material"]
            )

            top_material_impact = (
                top_material["impact_kgco2e"]
            )

            if total_carbon > 0:

                top_share = (
                    top_material_impact
                    / total_carbon
                    * 100
                )

            else:

                top_share = 0

            st.info(
                f"En {selected_year}, le matériau contribuant "
                f"le plus à l’impact estimé est "
                f"{top_material_name}, avec "
                f"{top_material_impact:,.0f} kgCO₂e "
                f"({top_share:.1f} % de l’impact analysé)."
            )

    except Exception as e:

        st.error(
            "Impossible de charger le tableau de bord."
        )

        st.exception(e)


def page_import_data():

    st.markdown(
        '<div class="page-title">Importer les données produit</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="page-subtitle">'
        'Importez une nomenclature ou un fichier de composition '
        'afin de lancer une analyse d’éco-conception.'
        '</div>',
        unsafe_allow_html=True,
    )

    # -----------------------------
    # IMPORT DU FICHIER
    # -----------------------------
    uploaded_file = st.file_uploader(
        "Déposez votre fichier Excel",
        type=["xlsx"],
        key="vehicle_excel_uploader",
        help="Format accepté : .xlsx"
    )

    # Aucun fichier
    if uploaded_file is None:
        st.info("Importez un fichier Excel pour commencer.")
        return

    # -----------------------------
    # FICHIER DÉTECTÉ
    # -----------------------------
    st.success(f"Fichier détecté : {uploaded_file.name}")

    try:

        with st.spinner("Lecture et préparation des données..."):

            # Lecture des feuilles
            df, sheets = load_vehicle_excel(uploaded_file)

            # Vérification des colonnes
            missing_columns = validate_vehicle_data(df)

            if missing_columns:
                st.error(
                    "Colonnes obligatoires manquantes : "
                    + ", ".join(missing_columns)
                )
                return

            # Nettoyage
            clean_df = clean_vehicle_data(df)

            # Vérification
            if clean_df.empty:
                st.error(
                    "Le fichier a été lu mais aucune donnée exploitable "
                    "n'a été trouvée après nettoyage."
                )
                return

            # Calcul du résumé
            summary = get_data_summary(clean_df)

            # Stockage pour les autres pages
            st.session_state["vehicle_data"] = clean_df
            st.session_state["vehicle_file_name"] = uploaded_file.name

        # -----------------------------
        # IMPORT RÉUSSI
        # -----------------------------
        st.success("Données importées avec succès.")

        st.write(
            "**Feuilles détectées :** "
            + ", ".join(sheets)
        )

        st.divider()

        # -----------------------------
        # INDICATEURS
        # -----------------------------
        st.subheader("Résumé du jeu de données")

        col1, col2, col3, col4 = st.columns(4)

        col1.metric(
            "Lignes",
            f"{summary['nombre_lignes']:,}".replace(",", " ")
        )

        col2.metric(
            "Véhicules",
            summary["nombre_vehicules"]
        )

        col3.metric(
            "Composants",
            summary["nombre_composants"]
        )

        col4.metric(
            "Matériaux",
            summary["nombre_materiaux"]
        )

        col5, col6, col7 = st.columns(3)

        col5.metric(
            "Éléments chimiques",
            summary["nombre_elements"]
        )

        col6.metric(
            "Année minimale",
            summary["annee_min"]
        )

        col7.metric(
            "Année maximale",
            summary["annee_max"]
        )

        # -----------------------------
        # APERÇU
        # -----------------------------
        st.divider()

        st.subheader("Aperçu des données")

        st.dataframe(
            clean_df.head(100),
            use_container_width=True,
            hide_index=True
        )

        # -----------------------------
        # CONTINUER
        # -----------------------------
        st.divider()

        if st.button(
            "Lancer l'analyse",
            type="primary",
            use_container_width=True
        ):
            st.session_state.page = "Analyse de l'IA"
            st.rerun()

    except Exception as e:

        st.error("Impossible de traiter le fichier.")

        # Très utile pendant notre développement
        st.exception(e)

def classify_hotspot(share):
    if share >= 20:
        return "Critique"
    elif share >= 10:
        return "Élevé"
    elif share >= 5:
        return "Modéré"
    else:
        return "Faible"

def classify_carbon_hotspot(share):
    if share >= 30:
        return "Priorité très élevée"
    elif share >= 20:
        return "Priorité élevée"
    elif share >= 10:
        return "Priorité modérée"
    else:
        return "Priorité faible"      


def generate_material_recommendation(material, priority):

    recommendations = {
        "wroughtAluminium": (
            "Étudier l'utilisation d'aluminium recyclé, "
            "la réduction de masse et l'optimisation des sections."
        ),

        "castAluminium": (
            "Évaluer une augmentation du contenu recyclé "
            "et optimiser la quantité de matière utilisée."
        ),

        "mildSteel": (
            "Étudier une réduction de masse, l'utilisation "
            "d'acier recyclé ou une nuance plus performante."
        ),

        "highStrengthSteel": (
            "Optimiser les épaisseurs afin de tirer parti "
            "des propriétés mécaniques de l'acier haute résistance."
        ),

        "castIron": (
            "Évaluer des alternatives plus légères lorsque "
            "les contraintes mécaniques le permettent."
        ),

        "magnesium": (
            "Vérifier l'origine et le procédé de fabrication "
            "du magnésium en raison de sa forte intensité carbone."
        ),
    }

    recommendation = recommendations.get(
        material,
        "Analyser des alternatives à plus faible impact environnemental."
    )

    return recommendation       

def calculate_carbon_score(
    vehicle_intensity,
    fleet_intensities
):

    if fleet_intensities.empty:
        return 0

    valid_intensities = (
        fleet_intensities[
            "carbon_intensity"
        ]
        .dropna()
    )

    if valid_intensities.empty:
        return 0

    percentile = (
        valid_intensities
        .le(vehicle_intensity)
        .mean()
        * 100
    )

    carbon_score = 100 - percentile

    return max(
        0,
        min(100, carbon_score)
    )   

def calculate_aiec_score(
    carbon_score,
    recyclability_score,
    data_quality_score
):

    return (
        0.40 * carbon_score
        + 0.40 * recyclability_score
        + 0.20 * data_quality_score
    )

def classify_data_confidence(score):

    if score >= 80:
        return "Élevée"

    elif score >= 60:
        return "Moyenne"

    else:
        return "Faible"

def classify_aiec_score(score):

    if score >= 80:
        return "Très bon"

    elif score >= 65:
        return "Bon"

    elif score >= 50:
        return "À améliorer"

    elif score >= 35:
        return "Faible"

    else:
        return "Critique"

def evaluate_aiec_criterion(value, good_threshold, warning_threshold):
    """
    Évalue un indicateur AIEC.
    Plus la valeur est élevée, meilleure est la situation.
    """

    if value >= good_threshold:
        return "Conforme au critère AIEC"

    elif value >= warning_threshold:
        return "À vérifier"

    else:
        return "Non conforme au critère AIEC"

def conformity_icon(status):

    if status == "Conforme au critère AIEC":
        return "✅"

    elif status == "À vérifier":
        return "⚠️"

    elif status == "Non conforme au critère AIEC":
        return "❌"

    else:
        return "🔎"

def page_ai():

    st.markdown(
        '<div class="page-title">Analyse des données</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="page-subtitle">'
        'Sélectionnez une année et un véhicule afin d’analyser '
        'sa composition.'
        '</div>',
        unsafe_allow_html=True,
    )

    try:

        # -------------------------
        # ANNÉES
        # -------------------------
        years = get_years()

        if not years:
            st.warning(
                "Aucune donnée disponible dans PostgreSQL."
            )
            return

        selected_year = st.selectbox(
            "Année",
            years
        )

        # -------------------------
        # VÉHICULES
        # -------------------------
        vehicles = get_vehicles_by_year(
            selected_year
        )

        if vehicles.empty:
            st.warning(
                "Aucun véhicule disponible pour cette année."
            )
            return

        vehicle_options = {
            f"{row['layer_1']} — {row['parent_description']}":
            row["layer_1"]
            for _, row in vehicles.iterrows()
        }

        selected_vehicle_label = st.selectbox(
            "Véhicule",
            list(vehicle_options.keys())
        )

        selected_vehicle = vehicle_options[
            selected_vehicle_label
        ]

        # -------------------------
        # CHARGEMENT DU VÉHICULE
        # -------------------------
        with st.spinner(
            "Chargement des données du véhicule..."
        ):

            vehicle_df = get_vehicle_data(
                selected_year,
                selected_vehicle
            )

            total_mass = get_vehicle_total_mass(
                selected_year,
                selected_vehicle
            )

            material_df = get_material_composition(
                selected_year,
                selected_vehicle
            )
            environmental_df = get_material_environmental_analysis(
                selected_year,
                selected_vehicle
            )

            component_df = get_component_composition(
                selected_year,
                selected_vehicle
            )

            unknown_material_mass = get_unknown_material_mass(
                selected_year,
                selected_vehicle
           )

        total_carbon = (
            environmental_df["impact_kgco2e"]
            .dropna()
            .sum()
        )

        st.divider()
        st.markdown("### Analyse visuelle des matériaux")

        graph_col1, graph_col2 = st.columns(2)

        with graph_col1:

            st.markdown("#### Répartition de la masse")

            if not environmental_df.empty:

                fig_mass = px.pie(
                    environmental_df,
                    names="material",
                    values="mass_kg",
                    hole=0.55
                )

                fig_mass.update_layout(
                    margin=dict(l=10, r=10, t=30, b=10),
                    legend_title_text="Matériau"
                )

                st.plotly_chart(
                    fig_mass,
                    use_container_width=True
                )


        with graph_col2:

            st.markdown("#### Répartition de l'impact carbone")

            if not environmental_df.empty:

                fig_carbon = px.pie(
                    environmental_df,
                    names="material",
                    values="impact_kgco2e",
                    hole=0.55
                )

                fig_carbon.update_layout(
                    margin=dict(l=10, r=10, t=30, b=10),
                    legend_title_text="Matériau"
                )

                st.plotly_chart(
                    fig_carbon,
                    use_container_width=True
                )

        if total_carbon > 0:
            environmental_df["carbon_share_percent"] = (
                environmental_df["impact_kgco2e"]
                / total_carbon
                * 100
            )
            environmental_df["carbon_priority"] = (
                environmental_df["carbon_share_percent"]
                .apply(classify_carbon_hotspot)
            )
        else:
            environmental_df["carbon_share_percent"] = 0
            environmental_df["carbon_priority"] = "Non calculable"


        if vehicle_df.empty:
            st.warning(
                "Aucune donnée trouvée pour ce véhicule."
            )
            return

        material_mass = material_df["mass_kg"].sum()
        if total_mass is not None and total_mass > 0:
            coverage_rate = (
                material_mass / total_mass * 100
            )
            unknown_rate = (
                unknown_material_mass / total_mass * 100
            )

        else:
            coverage_rate = 0
            unknown_rate = 0

        st.divider()

        st.session_state["analysis_year"] = selected_year
        st.session_state["analysis_vehicle"] = selected_vehicle
        st.session_state["analysis_vehicle_description"] = (
            vehicle_df["parent_description"].iloc[0]
        )
        st.session_state["analysis_total_carbon"] = total_carbon    

        st.markdown("## Synthèse environnementale")
        st.caption(
            "Analyse de la composition matière, de la couverture des données "
            "et des principaux contributeurs à l'impact carbone estimé."
        ) 
        k1, k2, k3, k4 = st.columns(4)
        k1.metric(
            "⚖️ Masse véhicule",
            f"{total_mass:,.1f} kg"
        )

        k2.metric(
            "🧱 Masse caractérisée",
            f"{material_mass:,.1f} kg"
        )

        k3.metric(
            "📊 Couverture matière",
            f"{coverage_rate:.1f} %"
        )

        k4.metric(
            "🌱 Impact carbone estimé",
            f"{total_carbon:,.1f} kgCO₂e"
        )  

        # -------------------------
        # INFORMATIONS
        # -------------------------
        st.subheader("Véhicule sélectionné")

        st.write(
            f"**Identifiant :** {selected_vehicle}"
        )

        st.write(
            f"**Description :** "
            f"{vehicle_df['parent_description'].iloc[0]}"
        )

        st.write(
            f"**Année :** {selected_year}"
        )

        # -----------------------------
        # INDICATEURS
        # -----------------------------

        # Ligne 1
        col1, col2, col3 = st.columns(3)
        col1.metric(
            "Masse du véhicule",
            f"{total_mass:,.1f} kg"
            if total_mass is not None
            else "N/A"
        )

        col2.metric(
            "Matériaux identifiés",
            f"{material_mass:,.1f} kg"
        )

        col3.metric(
            "Couverture matériaux",
            f"{coverage_rate:.1f} %"
        )

        # Ligne 2
        col4, col5, col6, col7 = st.columns(4)

        col4.metric(
            "Composants",
            component_df["component"].nunique()
        )

        col5.metric(
            "Matériaux",
            material_df["material"].nunique()
        )

        col6.metric(
            "Éléments chimiques",
            vehicle_df["layer_4"].nunique()
        )

        col7.metric(
            "Matériaux non détaillés",
            f"{unknown_material_mass:,.1f} kg"
        )

        st.divider()
        

        # -----------------------------
        # MATÉRIAUX
        # -----------------------------
        st.subheader("Composition par matériau")
        if material_df.empty:

            st.info(
                "Aucune donnée matériau disponible pour ce véhicule."
            )

        else:
            # Calcul de la part de chaque matériau
            if total_mass is not None and total_mass > 0:

                material_df["share_percent"] = (
                    material_df["mass_kg"]
                    / total_mass
                    * 100
                )
                material_df["hotspot"] = (
                    material_df["share_percent"]
                    .apply(classify_hotspot)
                )

            else:

                material_df["share_percent"] = 0
                material_df["hotspot"] = "Non calculable"
            # Préparation pour affichage
            materials_display = material_df.rename(
                columns={
                    "material": "Matériau",
                    "mass_kg": "Masse (kg)",
                    "share_percent": "Part du véhicule (%)",
                    "hotspot": "Niveau"
                }
            )
            # Arrondis
            materials_display["Masse (kg)"] = (
                materials_display["Masse (kg)"]
                .round(2)
            )
            materials_display["Part du véhicule (%)"] = (
                materials_display["Part du véhicule (%)"]
                .round(2)
            )
            # Affichage
            st.dataframe(
                materials_display,
                use_container_width=True,
                hide_index=True
            )

        st.subheader("Impact carbone estimé des matériaux")
        if environmental_df.empty:

            st.info(
                "Aucun facteur environnemental disponible."
            )

        else:

            environmental_display = environmental_df.rename(
                columns={
                    "material": "Matériau",
                    "mass_kg": "Masse (kg)",
                    "emission_factor_kgco2e_per_kg": "Facteur (kgCO₂e/kg)",
                    "impact_kgco2e": "Impact estimé (kgCO₂e)",
                    "carbon_share_percent": "Part de l'impact (%)",
                    "carbon_priority": "Priorité",
                    "factor_type": "Type de facteur"
                }
            )

            environmental_display["Masse (kg)"] = (
                environmental_display["Masse (kg)"].round(2)
            )

            environmental_display["Facteur (kgCO₂e/kg)"] = (
                environmental_display[
                    "Facteur (kgCO₂e/kg)"
                ].round(2)
            )

            environmental_display["Impact estimé (kgCO₂e)"] = (
                environmental_display[
                    "Impact estimé (kgCO₂e)"
                ].round(2)
            )

            st.metric(
                "Impact carbone estimé des matériaux identifiés",
                f"{total_carbon:,.1f} kgCO₂e"
            )

            st.dataframe(
                environmental_display[
                    [
                        "Matériau",
                        "Masse (kg)",
                        "Facteur (kgCO₂e/kg)",
                        "Impact estimé (kgCO₂e)",
                        "Part de l'impact (%)",
                        "Priorité",
                        "Type de facteur"
                    ]
                ],
                use_container_width=True,
                hide_index=True
            )

            st.divider()
            st.subheader("Circularité des matériaux")

            circularity_df = environmental_df[
                [
                    "material",
                    "mass_kg",
                    "recyclability_rate",
                    "recycled_content_rate"
                ]
            ].copy()

            circularity_display = circularity_df.rename(
                columns={
                    "material": "Matériau",
                    "mass_kg": "Masse (kg)",
                    "recyclability_rate": "Recyclabilité (%)",
                    "recycled_content_rate": "Contenu recyclé (%)"
                }
            )

            circularity_display["Masse (kg)"] = (
                circularity_display["Masse (kg)"]
                .round(2)
            )

            st.dataframe(
                circularity_display,
                use_container_width=True,
                hide_index=True
            )

            known_recyclability_df = environmental_df[
                environmental_df["recyclability_rate"].notna()
            ].copy()

            known_recyclability_mass = (
                known_recyclability_df["mass_kg"].sum()
            )

            if material_mass > 0:
                circularity_coverage = (
                    known_recyclability_mass
                    / material_mass
                    * 100
                )
            else:
                circularity_coverage = 0
            
            st.metric(
                "Couverture des données de recyclabilité",
                f"{circularity_coverage:.1f} %"
            )

            if not known_recyclability_df.empty:
                weighted_recyclability = (
                    (
                        known_recyclability_df["mass_kg"]
                        * known_recyclability_df["recyclability_rate"]
                    ).sum()
                    / known_recyclability_df["mass_kg"].sum()
                )
            else:
                weighted_recyclability = None
            
            # ==========================================
            # SCORE DE CIRCULARITÉ
            # ==========================================

            recyclability_score = (
                weighted_recyclability
                if weighted_recyclability is not None
                else 0
            )

            if weighted_recyclability is not None:
                st.metric(
                    "Recyclabilité moyenne pondérée",
                    f"{weighted_recyclability:.1f} %"
                )
            else:
                st.metric(
                    "Recyclabilité moyenne pondérée",
                    "Non calculable"
                )

            # ==========================================
            # QUALITÉ DES DONNÉES
            # ==========================================

            # ==========================================
            # SCORE DE QUALITÉ DES DONNÉES
            # ==========================================

            material_data_quality = coverage_rate
            circularity_data_quality = circularity_coverage

            data_quality_score = (
                0.50 * material_data_quality
                + 0.50 * circularity_data_quality
            )

            data_confidence = classify_data_confidence(
                data_quality_score
            )

            # ==========================================
            # INTENSITÉ ET SCORE CARBONE
            # ==========================================

            if material_mass > 0:
                carbon_intensity_vehicle = (
                    total_carbon / material_mass
                )
            else:
                carbon_intensity_vehicle = 0
            
            fleet_carbon_df = get_vehicle_carbon_intensities(
                selected_year
            )

            if not fleet_carbon_df.empty:
                fleet_median_intensity = (
                    fleet_carbon_df[
                        "carbon_intensity"
                    ].median()
                )
            else:
                fleet_median_intensity = None

            if fleet_median_intensity is not None:
                st.caption(
                    f"Médiane du parc en {selected_year} : "
                    f"{fleet_median_intensity:.2f} kgCO₂e/kg"
                )

            carbon_score = calculate_carbon_score(
                carbon_intensity_vehicle,
                fleet_carbon_df
            )


            # ==========================================
            # SCORE GLOBAL AIEC
            # ==========================================

            aiec_score = calculate_aiec_score(
                carbon_score,
                recyclability_score,
                data_quality_score
            )

            aiec_level = classify_aiec_score(
                aiec_score
            )
            st.session_state["analysis_aiec_score"] = aiec_score
            st.session_state["analysis_aiec_level"] = aiec_level
            st.session_state["analysis_carbon_score"] = carbon_score
            st.session_state["analysis_recyclability_score"] = recyclability_score
            st.session_state["analysis_data_quality_score"] = data_quality_score
            st.session_state["analysis_carbon_intensity"] = carbon_intensity_vehicle
            st.session_state["analysis_material_coverage"] = coverage_rate
            st.session_state["analysis_circularity_coverage"] = circularity_coverage

            st.divider()
            st.subheader("Score environnemental AIEC")

            score_col1, score_col2, score_col3, score_col4 = (
                st.columns(4)
            )

            score_col1.metric(
                "Score carbone",
                f"{carbon_score:.0f}/100"
            )

            score_col2.metric(
                "Score circularité",
                f"{recyclability_score:.0f}/100"
            )

            score_col3.metric(
                "Qualité des données",
                f"{data_quality_score:.0f}/100"
            )

            score_col4.metric(
                "Score AIEC",
                f"{aiec_score:.0f}/100"
            )

            st.caption(
                f"Couverture matière : {coverage_rate:.1f} % | "
                f"Couverture recyclabilité : {circularity_coverage:.1f} %"
            )

            st.progress(
                min(max(aiec_score / 100, 0), 1)
            )

            st.markdown(
                f"### Niveau : **{aiec_level}**"
            )
            st.info(
                f"Niveau de confiance de l'analyse : **{data_confidence}**"
            )

            carbon_col1, carbon_col2 = st.columns(2)
            carbon_col1.metric(
                "Intensité carbone",
                f"{carbon_intensity_vehicle:.2f} kgCO₂e/kg"
            )

            carbon_col2.metric(
                "Score carbone relatif",
                f"{carbon_score:.0f}/100"
            )

        # -----------------------------
        # COMPOSANTS
        # -----------------------------
        st.subheader("Composition par composant")

        if component_df.empty:

            st.info(
                "Aucune donnée composant disponible pour ce véhicule."
            )

        else:

            components_display = component_df.rename(
                columns={
                    "component": "Composant",
                    "mass_kg": "Masse (kg)"
                }
            )

            components_display["Masse (kg)"] = (
                components_display["Masse (kg)"].round(2)
            )

            st.dataframe(
                components_display,
                use_container_width=True,
                hide_index=True
            )

        # -------------------------
        # DONNÉES BRUTES
        # -------------------------
        with st.expander(
            "Voir les données détaillées"
        ):

            st.dataframe(
                vehicle_df,
                use_container_width=True,
                hide_index=True
            )

    except Exception as e:

        st.error(
            "Erreur lors de l'accès à PostgreSQL."
        )

        st.exception(e)


def generate_material_recommendation(material):

    recommendations = {
        "wroughtAluminium": (
            "Étudier l'utilisation d'aluminium recyclé, "
            "réduire la masse lorsque cela est possible et "
            "optimiser les sections des pièces."
        ),

        "castAluminium": (
            "Augmenter la part d'aluminium recyclé et "
            "optimiser la quantité de matière utilisée."
        ),

        "mildSteel": (
            "Étudier la réduction de masse, l'utilisation "
            "d'acier recyclé et l'optimisation des épaisseurs."
        ),

        "highStrengthSteel": (
            "Optimiser les épaisseurs afin de tirer parti "
            "des propriétés mécaniques de l'acier haute résistance."
        ),

        "castIron": (
            "Évaluer des matériaux ou conceptions plus légères "
            "lorsque les contraintes mécaniques le permettent."
        ),

        "magnesium": (
            "Vérifier l'origine du magnésium et privilégier "
            "des filières à plus faible intensité carbone "
            "ou du magnésium recyclé."
        ),
    }

    return recommendations.get(
        material,
        "Étudier une alternative à plus faible impact environnemental."
    )

def page_recommendations():

    st.markdown(
        '<div class="page-title">Recommandations d’éco-conception</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="page-subtitle">'
        'Priorisation des matériaux à partir des résultats '
        'de l’analyse environnementale.'
        '</div>',
        unsafe_allow_html=True,
    )

    # Vérification qu'une analyse existe
    required_keys = [
        "analysis_year",
        "analysis_vehicle",
        "analysis_vehicle_description"
    ]

    if not all(
        key in st.session_state
        for key in required_keys
    ):

        st.warning(
            "Aucun véhicule n'a encore été analysé. "
            "Rendez-vous dans la page Analyse de l'IA."
        )

        return

    selected_year = st.session_state["analysis_year"]
    selected_vehicle = st.session_state["analysis_vehicle"]
    description = st.session_state[
        "analysis_vehicle_description"
    ]

    # Récupération depuis PostgreSQL
    environmental_df = get_material_environmental_analysis(
        selected_year,
        selected_vehicle
    )

    if environmental_df.empty:

        st.warning(
            "Aucune donnée environnementale disponible "
            "pour ce véhicule."
        )

        return

    # -----------------------------
    # CALCUL CARBONE
    # -----------------------------
    total_carbon = (
        environmental_df["impact_kgco2e"]
        .dropna()
        .sum()
    )

    if total_carbon <= 0:

        st.warning(
            "L'impact carbone ne peut pas être calculé."
        )

        return

    environmental_df["carbon_share_percent"] = (
        environmental_df["impact_kgco2e"]
        / total_carbon
        * 100
    )

    environmental_df["carbon_priority"] = (
        environmental_df["carbon_share_percent"]
        .apply(classify_carbon_hotspot)
    )

    # -----------------------------
    # VÉHICULE
    # -----------------------------
    st.subheader("Véhicule analysé")

    st.write(
        f"**Identifiant :** {selected_vehicle}"
    )

    st.write(
        f"**Description :** {description}"
    )

    st.write(
        f"**Année :** {selected_year}"
    )

    st.metric(
        "Impact carbone estimé des matériaux identifiés",
        f"{total_carbon:,.1f} kgCO₂e"
    )

    st.divider()

    # -----------------------------
    # PRIORITÉS
    # -----------------------------
    st.subheader("Matériaux prioritaires")

    priority_df = (
        environmental_df[
            environmental_df[
                "carbon_share_percent"
            ] >= 10
        ]
        .copy()
        .sort_values(
            "impact_kgco2e",
            ascending=False
        )
    )

    if priority_df.empty:

        st.info(
            "Aucun hotspot environnemental majeur "
            "n'a été identifié."
        )

        return

    # -----------------------------
    # RECOMMANDATIONS
    # -----------------------------
    for _, row in priority_df.iterrows():

        material = row["material"]

        mass = row["mass_kg"]

        impact = row["impact_kgco2e"]

        share = row["carbon_share_percent"]

        priority = row["carbon_priority"]

        emission_factor = row[
            "emission_factor_kgco2e_per_kg"
        ]

        recommendation = (
            generate_material_recommendation(
                material
            )
        )

        with st.container(border=True):

            st.markdown(
                f"### {material}"
            )

            col1, col2, col3, col4 = (
                st.columns(4)
            )

            col1.metric(
                "Masse",
                f"{mass:.1f} kg"
            )

            col2.metric(
                "Impact",
                f"{impact:.1f} kgCO₂e"
            )

            col3.metric(
                "Part de l'impact",
                f"{share:.1f} %"
            )

            col4.metric(
                "Priorité",
                priority
            )

            st.caption(
                f"Facteur utilisé : "
                f"{emission_factor:.2f} kgCO₂e/kg"
            )

            st.write(
                "**Recommandation AIEC :** "
                + recommendation
            )
    
            decision = st.selectbox(
                "Décision",
                [
                    "À étudier",
                    "Accepter",
                    "Rejeter"
                ],
                key=f"decision_{material}"
            )

            comment = st.text_area(
                "Commentaire ingénieur",
                key=f"comment_{material}"
            )

            if st.button(
                "Enregistrer la décision",
                key=f"save_{material}"
            ):
                save_recommendation_validation(
                    selected_year,
                    selected_vehicle,
                    material,
                    impact,
                    share,
                    priority,
                    recommendation,
                    decision,
                    comment
                )

                # On vide le cache pour que la page Validation
                # récupère immédiatement les nouvelles données
                get_recommendation_validations.clear()

                st.success(
                    "Décision enregistrée dans PostgreSQL."
                )

def generate_aiec_pdf(
    selected_year,
    selected_vehicle,
    description,
    total_mass,
    material_df,
    environmental_df,
    controls_df,
    regulatory_controls,
):
    """
    Génère le rapport PDF AIEC en mémoire.
    Retourne les données binaires du PDF.
    """

    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=1.5 * cm,
        leftMargin=1.5 * cm,
        topMargin=1.5 * cm,
        bottomMargin=1.5 * cm,
        title=f"Rapport AIEC - {selected_vehicle}",
        author="AIEC",
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "AIEC_Title",
        parent=styles["Title"],
        fontSize=22,
        leading=27,
        alignment=TA_CENTER,
        spaceAfter=10,
    )

    subtitle_style = ParagraphStyle(
        "AIEC_Subtitle",
        parent=styles["Normal"],
        fontSize=10,
        leading=14,
        alignment=TA_CENTER,
        textColor=colors.grey,
        spaceAfter=20,
    )

    section_style = ParagraphStyle(
        "AIEC_Section",
        parent=styles["Heading2"],
        fontSize=14,
        leading=18,
        spaceBefore=12,
        spaceAfter=8,
    )

    normal_style = styles["BodyText"]

    story = []

    # =====================================================
    # TITRE
    # =====================================================

    story.append(
        Paragraph(
            "AIEC — Rapport d'éco-conception",
            title_style
        )
    )

    story.append(
        Paragraph(
            "Assistant Intelligent d'Éco-Conception Circulaire",
            subtitle_style
        )
    )

    story.append(
        Paragraph(
            f"Rapport généré le "
            f"{datetime.now().strftime('%d/%m/%Y à %H:%M')}",
            subtitle_style
        )
    )

    story.append(Spacer(1, 10))

    # =====================================================
    # 1 - IDENTIFICATION
    # =====================================================

    story.append(
        Paragraph(
            "1. Identification du produit",
            section_style
        )
    )

    identification_data = [
        ["Information", "Valeur"],
        ["Véhicule", str(selected_vehicle)],
        ["Année", str(selected_year)],
        [
            "Masse totale",
            f"{total_mass:,.1f} kg"
            if total_mass is not None
            else "Non disponible"
        ],
        ["Description", str(description)],
    ]

    identification_table = Table(
        identification_data,
        colWidths=[5 * cm, 12 * cm],
        repeatRows=1
    )

    identification_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E5E7EB")),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#D1D5DB")),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ])
    )

    story.append(identification_table)
    story.append(Spacer(1, 15))

    # =====================================================
    # CALCULS
    # =====================================================

    material_mass = (
        material_df["mass_kg"].sum()
        if not material_df.empty
        else 0
    )

    total_carbon = (
        environmental_df["impact_kgco2e"].dropna().sum()
        if not environmental_df.empty
        else 0
    )

    material_coverage = (
        material_mass / total_mass * 100
        if total_mass is not None and total_mass > 0
        else 0
    )

    carbon_intensity = (
        total_carbon / material_mass
        if material_mass > 0
        else 0
    )

    circularity_coverage = st.session_state.get(
        "analysis_circularity_coverage",
        0
    )

    # =====================================================
    # 2 - INDICATEURS
    # =====================================================

    story.append(
        Paragraph(
            "2. Indicateurs environnementaux",
            section_style
        )
    )

    indicators = [
        ["Indicateur", "Valeur"],
        ["Masse totale", f"{total_mass:,.1f} kg"],
        ["Masse caractérisée", f"{material_mass:,.1f} kg"],
        ["Couverture matière", f"{material_coverage:.1f} %"],
        ["Impact carbone estimé", f"{total_carbon:,.1f} kgCO2e"],
        ["Intensité carbone", f"{carbon_intensity:.2f} kgCO2e/kg"],
        [
            "Couverture recyclabilité",
            f"{circularity_coverage:.1f} %"
        ],
    ]

    indicators_table = Table(
        indicators,
        colWidths=[9 * cm, 8 * cm],
        repeatRows=1
    )

    indicators_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E5E7EB")),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#D1D5DB")),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("PADDING", (0, 0), (-1, -1), 6),
        ])
    )

    story.append(indicators_table)

    # =====================================================
    # 3 - SCORE AIEC
    # =====================================================

    story.append(
        Paragraph(
            "3. Score environnemental AIEC",
            section_style
        )
    )

    aiec_score = st.session_state.get(
        "analysis_aiec_score",
        0
    )

    aiec_level = st.session_state.get(
        "analysis_aiec_level",
        "Non calculable"
    )

    carbon_score = st.session_state.get(
        "analysis_carbon_score",
        0
    )

    recyclability_score = st.session_state.get(
        "analysis_recyclability_score",
        0
    )

    data_quality_score = st.session_state.get(
        "analysis_data_quality_score",
        0
    )

    score_data = [
        ["Indicateur", "Score"],
        ["Score carbone", f"{carbon_score:.0f}/100"],
        ["Score circularité", f"{recyclability_score:.0f}/100"],
        ["Qualité des données", f"{data_quality_score:.0f}/100"],
        ["Score global AIEC", f"{aiec_score:.0f}/100"],
        ["Niveau", str(aiec_level)],
    ]

    score_table = Table(
        score_data,
        colWidths=[9 * cm, 8 * cm],
        repeatRows=1
    )

    score_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E5E7EB")),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#D1D5DB")),
            ("PADDING", (0, 0), (-1, -1), 6),
        ])
    )

    story.append(score_table)

    # =====================================================
    # 4 - COMPOSITION MATIÈRE
    # =====================================================

    story.append(
        Paragraph(
            "4. Composition matière",
            section_style
        )
    )

    if not material_df.empty:

        material_data = [
            ["Matériau", "Masse (kg)", "Part (%)"]
        ]

        for _, row in material_df.iterrows():

            mass = float(row["mass_kg"])

            share = (
                mass / total_mass * 100
                if total_mass
                else 0
            )

            material_data.append([
                str(row["material"]),
                f"{mass:.2f}",
                f"{share:.1f}",
            ])

        material_table = Table(
            material_data,
            colWidths=[
                8 * cm,
                4.5 * cm,
                4.5 * cm
            ],
            repeatRows=1
        )

        material_table.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E5E7EB")),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#D1D5DB")),
                ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
                ("PADDING", (0, 0), (-1, -1), 5),
            ])
        )

        story.append(material_table)

    # =====================================================
    # 5 - HOTSPOTS
    # =====================================================

    story.append(
        Paragraph(
            "5. Hotspots environnementaux",
            section_style
        )
    )

    if not environmental_df.empty:

        hotspot_data = [
            [
                "Matériau",
                "Impact kgCO2e",
                "Part",
                "Priorité"
            ]
        ]

        hotspot_df = environmental_df.copy()

        if total_carbon > 0:

            hotspot_df["share"] = (
                hotspot_df["impact_kgco2e"]
                / total_carbon
                * 100
            )

        else:

            hotspot_df["share"] = 0

        hotspot_df = hotspot_df.sort_values(
            "impact_kgco2e",
            ascending=False
        )

        for _, row in hotspot_df.iterrows():

            share = float(row["share"])

            hotspot_data.append([
                str(row["material"]),
                f"{row['impact_kgco2e']:.1f}",
                f"{share:.1f} %",
                classify_carbon_hotspot(share),
            ])

        hotspot_table = Table(
            hotspot_data,
            colWidths=[
                5 * cm,
                4 * cm,
                3 * cm,
                5 * cm
            ],
            repeatRows=1
        )

        hotspot_table.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E5E7EB")),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#D1D5DB")),
                ("PADDING", (0, 0), (-1, -1), 5),
            ])
        )

        story.append(hotspot_table)

    # =====================================================
    # 6 - RECOMMANDATIONS
    # =====================================================

    story.append(
        Paragraph(
            "6. Recommandations d'éco-conception",
            section_style
        )
    )

    if not environmental_df.empty and total_carbon > 0:

        recommendation_df = environmental_df.copy()

        recommendation_df["share"] = (
            recommendation_df["impact_kgco2e"]
            / total_carbon
            * 100
        )

        recommendation_df = recommendation_df[
            recommendation_df["share"] >= 10
        ].sort_values(
            "impact_kgco2e",
            ascending=False
        )

        if recommendation_df.empty:

            story.append(
                Paragraph(
                    "Aucune recommandation prioritaire identifiée.",
                    normal_style
                )
            )

        else:

            for _, row in recommendation_df.iterrows():

                material = str(row["material"])

                recommendation = (
                    generate_material_recommendation(
                        material
                    )
                )

                story.append(
                    Paragraph(
                        f"<b>{material}</b> — {recommendation}",
                        normal_style
                    )
                )

                story.append(Spacer(1, 6))

    # =====================================================
    # 7 - VALIDATION HUMAINE
    # =====================================================

    story.append(
        Paragraph(
            "7. Validation humaine",
            section_style
        )
    )

    try:

        validations_df = get_recommendation_validations()

        vehicle_validations = validations_df[
            (
                validations_df["year"].astype(str)
                == str(selected_year)
            )
            &
            (
                validations_df["vehicle"].astype(str)
                == str(selected_vehicle)
            )
        ].copy()

    except Exception:

        vehicle_validations = pd.DataFrame()

    if vehicle_validations.empty:

        story.append(
            Paragraph(
                "Aucune décision humaine enregistrée "
                "pour cette analyse.",
                normal_style
            )
        )

    else:

        validation_data = [
            [
                "Matériau",
                "Décision",
                "Commentaire"
            ]
        ]

        for _, row in vehicle_validations.iterrows():

            comment = row.get(
                "comment",
                ""
            )

            if pd.isna(comment):
                comment = ""

            validation_data.append([
                Paragraph(
                    str(row["material"]),
                    normal_style
                ),
                Paragraph(
                    str(row["decision"]),
                    normal_style
                ),
                Paragraph(
                    str(comment),
                    normal_style
                ),
            ])

        validation_table = Table(
            validation_data,
            colWidths=[
                4.5 * cm,
                4 * cm,
                8.5 * cm
            ],
            repeatRows=1
        )

        validation_table.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E5E7EB")),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#D1D5DB")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("PADDING", (0, 0), (-1, -1), 5),
            ])
        )

        story.append(validation_table)

    # =====================================================
    # 8 - CONFORMITÉ
    # =====================================================

    story.append(
        Paragraph(
            "8. Conformité",
            section_style
        )
    )

    conformity_data = [
        [
            "Critère",
            "Valeur",
            "Résultat"
        ]
    ]

    for _, row in controls_df.iterrows():

        conformity_data.append([
            Paragraph(
                str(row["Critère"]),
                normal_style
            ),
            str(row["Valeur"]),
            Paragraph(
                str(row["Statut"]),
                normal_style
            ),
        ])

    conformity_table = Table(
        conformity_data,
        colWidths=[
            6 * cm,
            3 * cm,
            8 * cm
        ],
        repeatRows=1
    )

    conformity_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E5E7EB")),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#D1D5DB")),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("PADDING", (0, 0), (-1, -1), 5),
        ])
    )

    story.append(conformity_table)
    story.append(Spacer(1, 12))

    for _, row in regulatory_controls.iterrows():

        story.append(
            Paragraph(
                f"<b>{row['Référentiel']}</b> : "
                f"{row['Statut']} — "
                f"{row['Justification']}",
                normal_style
            )
        )

        story.append(Spacer(1, 5))

    story.append(Spacer(1, 15))

    story.append(
        Paragraph(
            "Les résultats présentés constituent une aide "
            "à l'analyse et au contrôle. Le rapport AIEC "
            "ne constitue pas une certification réglementaire.",
            normal_style
        )
    )

    # =====================================================
    # GÉNÉRATION
    # =====================================================

    doc.build(story)

    pdf_data = buffer.getvalue()
    buffer.close()

    return pdf_data

def page_conformity():

    st.markdown(
        '<div class="page-title">Conformité</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="page-subtitle">'
        'Contrôle des critères internes AIEC et préparation '
        'des vérifications réglementaires.'
        '</div>',
        unsafe_allow_html=True,
    )

    # ==========================================
    # VÉRIFICATION D'UNE ANALYSE EXISTANTE
    # ==========================================

    required_keys = [
        "analysis_year",
        "analysis_vehicle",
        "analysis_vehicle_description"
    ]

    if not all(
        key in st.session_state
        for key in required_keys
    ):
        st.warning(
            "Aucun véhicule n'a encore été analysé. "
            "Rendez-vous d'abord dans la page Analyse de l'IA."
        )
        return

    selected_year = st.session_state["analysis_year"]
    selected_vehicle = st.session_state["analysis_vehicle"]
    description = st.session_state[
        "analysis_vehicle_description"
    ]

    # ==========================================
    # RÉCUPÉRATION DES DONNÉES
    # ==========================================

    try:

        total_mass = get_vehicle_total_mass(
            selected_year,
            selected_vehicle
        )

        material_df = get_material_composition(
            selected_year,
            selected_vehicle
        )

        environmental_df = (
            get_material_environmental_analysis(
                selected_year,
                selected_vehicle
            )
        )

        unknown_material_mass = (
            get_unknown_material_mass(
                selected_year,
                selected_vehicle
            )
        )

    except Exception as e:

        st.error(
            "Impossible de charger les données de conformité."
        )

        st.exception(e)
        return

    # ==========================================
    # INFORMATIONS VÉHICULE
    # ==========================================

    st.subheader("Produit évalué")

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Véhicule",
        selected_vehicle
    )

    col2.metric(
        "Année",
        selected_year
    )

    col3.metric(
        "Masse",
        f"{total_mass:,.1f} kg"
        if total_mass is not None
        else "N/A"
    )

    st.caption(description)

    st.divider()

    # ==========================================
    # COUVERTURE MATIÈRE
    # ==========================================

    material_mass = (
        material_df["mass_kg"].sum()
        if not material_df.empty
        else 0
    )

    if total_mass is not None and total_mass > 0:

        material_coverage = (
            material_mass
            / total_mass
            * 100
        )

    else:

        material_coverage = 0

    material_status = evaluate_aiec_criterion(
        material_coverage,
        good_threshold=80,
        warning_threshold=60
    )

    # ==========================================
    # TRAÇABILITÉ CARBONE
    # ==========================================

    if (
        not environmental_df.empty
        and material_mass > 0
    ):

        carbon_known_df = environmental_df[
            environmental_df[
                "emission_factor_kgco2e_per_kg"
            ].notna()
        ]

        carbon_known_mass = (
            carbon_known_df["mass_kg"].sum()
        )

        carbon_coverage = (
            carbon_known_mass
            / material_mass
            * 100
        )

    else:

        carbon_coverage = 0

    carbon_status = evaluate_aiec_criterion(
        carbon_coverage,
        good_threshold=90,
        warning_threshold=70
    )

    # ==========================================
    # RECYCLABILITÉ
    # ==========================================

    if (
        not environmental_df.empty
        and material_mass > 0
    ):

        recycling_known_df = environmental_df[
            environmental_df[
                "recyclability_rate"
            ].notna()
        ]

        recycling_known_mass = (
            recycling_known_df["mass_kg"].sum()
        )

        recycling_coverage = (
            recycling_known_mass
            / material_mass
            * 100
        )

    else:

        recycling_coverage = 0

    recycling_status = evaluate_aiec_criterion(
        recycling_coverage,
        good_threshold=80,
        warning_threshold=60
    )

    # ==========================================
    # TABLEAU DES CONTRÔLES AIEC
    # ==========================================

    st.subheader("Contrôles internes AIEC")

    controls = [
        {
            "Critère": "Caractérisation matière",
            "Valeur": f"{material_coverage:.1f} %",
            "Statut": material_status,
            "Justification": (
                "Part de la masse totale associée "
                "à des matériaux identifiés."
            )
        },
        {
            "Critère": "Traçabilité carbone",
            "Valeur": f"{carbon_coverage:.1f} %",
            "Statut": carbon_status,
            "Justification": (
                "Part de la masse caractérisée disposant "
                "d'un facteur d'émission exploitable."
            )
        },
        {
            "Critère": "Données de recyclabilité",
            "Valeur": f"{recycling_coverage:.1f} %",
            "Statut": recycling_status,
            "Justification": (
                "Part de la masse caractérisée disposant "
                "d'une information de recyclabilité."
            )
        }
    ]

    controls_df = pd.DataFrame(controls)

    controls_df["Résultat"] = (
        controls_df["Statut"].apply(conformity_icon)
        + " "
        + controls_df["Statut"]
    )

    st.dataframe(
        controls_df[
            [
                "Critère",
                "Valeur",
                "Résultat",
                "Justification"
            ]
        ],
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    # ==========================================
    # CONTRÔLES RÉGLEMENTAIRES
    # ==========================================

    st.subheader("Vérifications réglementaires")

    regulatory_controls = pd.DataFrame(
        [
            {
                "Référentiel": "REACH",
                "Statut": "Contrôle réglementaire requis",
                "Justification": (
                    "Les données actuelles ne permettent pas "
                    "de conclure automatiquement sur la présence "
                    "de substances réglementées."
                )
            },
            {
                "Référentiel": "RoHS",
                "Statut": "Contrôle réglementaire requis",
                "Justification": (
                    "L'applicabilité et les substances concernées "
                    "doivent être vérifiées selon les composants "
                    "et le périmètre réglementaire du produit."
                )
            }
        ]
    )

    st.dataframe(
        regulatory_controls,
        use_container_width=True,
        hide_index=True
    )

    st.warning(
        "Les résultats présentés par AIEC constituent une aide "
        "au contrôle et à la préparation de la conformité. "
        "Ils ne constituent pas une certification réglementaire."
    )

    st.divider()
    st.subheader("Rapport")
    st.write(
        "Générez le rapport final correspondant "
        "à cette analyse."
    )
    if st.button(
        "📄 Générer le rapport AIEC",
        type="primary"
    ): 
        
        try:

            with st.spinner(
                "Génération du rapport AIEC..."
            ):

                pdf_data = generate_aiec_pdf(
                    selected_year=selected_year,
                    selected_vehicle=selected_vehicle,
                    description=description,
                    total_mass=total_mass,
                    material_df=material_df,
                    environmental_df=environmental_df,
                    controls_df=controls_df,
                    regulatory_controls=regulatory_controls,
                )

                aiec_score = st.session_state.get(
                    "analysis_aiec_score",
                    0
                )

                aiec_level = st.session_state.get(
                    "analysis_aiec_level",
                    "Non calculable"
                )

                report_id = save_aiec_report(
                    selected_vehicle,
                    selected_year,
                    description,
                    aiec_score,
                    aiec_level,
                    pdf_data
                )

                # Le nouveau rapport doit apparaître
                # immédiatement dans l'historique.
                get_aiec_reports.clear()

            st.success(
                f"Rapport AIEC généré avec succès "
                f"(rapport n°{report_id})."
            )

        except Exception as e:

            st.error(
                "Une erreur est survenue pendant "
                "la génération du rapport."
            )

            st.exception(e)
        

def placeholder_page(title, text):
    st.markdown(f'<div class="page-title">{title}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="page-subtitle">{text}</div>', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="aiec-card">
            <p style="margin:0;color:#6B7280;">
                Ce module sera implémenté dans un prochain sprint.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

def page_reports():

    st.markdown(
        '<div class="page-title">Rapports</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="page-subtitle">'
        'Historique des rapports d’éco-conception générés.'
        '</div>',
        unsafe_allow_html=True,
    )

    try:
        reports_df = get_aiec_reports()

    except Exception as e:

        st.error(
            "Impossible de récupérer l'historique des rapports."
        )

        st.exception(e)
        return

    if reports_df.empty:

        st.info(
            "Aucun rapport n'a encore été généré."
        )

        return

    # ==========================================
    # INDICATEURS
    # ==========================================

    col1, col2 = st.columns(2)

    col1.metric(
        "Rapports générés",
        len(reports_df)
    )

    col2.metric(
        "Véhicules analysés",
        reports_df["vehicle"].nunique()
    )

    st.divider()

    # ==========================================
    # HISTORIQUE
    # ==========================================

    st.subheader("Historique des rapports")

    for _, report in reports_df.iterrows():

        report_id = int(report["id"])

        vehicle = report["vehicle"]
        year = report["year"]
        score = report["aiec_score"]
        level = report["aiec_level"]
        generated_at = report["generated_at"]

        with st.container(border=True):

            col1, col2, col3, col4, col5 = (
                st.columns(
                    [2, 1, 1.3, 1.8, 1.5]
                )
            )

            col1.markdown(
                f"**{vehicle}**"
            )

            col1.caption(
                report.get(
                    "vehicle_description",
                    ""
                )
            )

            col2.write(
                f"**{year}**"
            )

            col3.metric(
                "Score",
                f"{score:.0f}/100"
            )

            col3.caption(
                str(level)
            )

            col4.write(
                generated_at.strftime(
                    "%d/%m/%Y %H:%M"
                )
                if hasattr(
                    generated_at,
                    "strftime"
                )
                else str(generated_at)
            )

            try:

                pdf_data = (
                    get_aiec_report_pdf(
                        report_id
                    )
                )

                if pdf_data:

                    col5.download_button(
                        "📄 Télécharger",
                        data=pdf_data,
                        file_name=(
                            f"Rapport_AIEC_"
                            f"{vehicle}_"
                            f"{year}.pdf"
                        ),
                        mime="application/pdf",
                        key=(
                            f"download_report_"
                            f"{report_id}"
                        )
                    )

                else:

                    col5.warning(
                        "PDF indisponible"
                    )

            except Exception:

                col5.error(
                    "Erreur PDF"
                )

def page_validation():

    st.markdown(
        '<div class="page-title">'
        'Validation des recommandations'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="page-subtitle">'
        'Historique des décisions prises sur les '
        'recommandations proposées par AIEC.'
        '</div>',
        unsafe_allow_html=True,
    )

    try:

        validation_df = get_recommendation_validations()

        if validation_df.empty:

            st.info(
                "Aucune recommandation n'a encore été validée."
            )

            return

        validation_display = validation_df.rename(
            columns={
                "year": "Année",
                "vehicle": "Véhicule",
                "material": "Matériau",
                "impact_kgco2e": "Impact (kgCO₂e)",
                "share_percent": "Part de l'impact (%)",
                "priority": "Priorité",
                "recommendation": "Recommandation",
                "decision": "Décision",
                "comment": "Commentaire",
                "validated_at": "Date de validation"
            }
        )

        validation_display["Impact (kgCO₂e)"] = (
            validation_display["Impact (kgCO₂e)"]
            .round(2)
        )

        validation_display["Part de l'impact (%)"] = (
            validation_display["Part de l'impact (%)"]
            .round(2)
        )

        st.subheader("Décisions enregistrées")

        st.dataframe(
            validation_display,
            use_container_width=True,
            hide_index=True
        )

    except Exception as e:

        st.error(
            "Erreur lors du chargement des validations."
        )

        st.exception(e)


if not st.session_state.authenticated:
    render_login()
    st.stop()


render_sidebar()
render_header()

page = st.session_state.page

if page == "Tableau de bord":
    page_dashboard()
elif page == "Importer fichiers CAO":
    page_import_data()
elif page == "Analyse de l'IA":
    page_ai()
elif page == "Recommandations":
    page_recommendations()
elif page == "Validation":
     page_validation()
elif page == "Conformité":
    page_conformity()
elif page == "Rapports":
    page_reports()
