from pathlib import Path
import pandas as pd
import streamlit as st
from pathlib import Path

from src.auth import init_auth_state, login, logout, DEMO_EMAIL, DEMO_PASSWORD
from src.styles import inject_css


from src.vehicle_data import (
    load_vehicle_excel,
    validate_vehicle_data,
    clean_vehicle_data,
    get_data_summary
)

from src.database import (
    get_years,
    get_vehicles_by_year,
    get_vehicle_data,
    get_vehicle_total_mass,
    get_material_composition,
    get_component_composition,
    get_unknown_material_mass,
    get_material_environmental_analysis
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
    # CSS spécifique à la page de connexion
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


def page_dashboard():
    st.markdown('<div class="page-title">Tableau de bord</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="page-subtitle">Vue synthétique des analyses d’éco-conception.</div>',
        unsafe_allow_html=True,
    )

    c1, c2, c3, c4 = st.columns(4)
    values = [
        ("Analyses CAO", "0"),
        ("Produits analysés", "0"),
        ("Alertes critiques", "0"),
        ("Rapports générés", "0"),
    ]
    for col, (label, value) in zip([c1, c2, c3, c4], values):
        with col:
            st.markdown(
                f"""
                <div class="aiec-card">
                    <div class="metric-label">{label}</div>
                    <div class="metric-value">{value}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.write("")
    st.markdown(
        """
        <div class="aiec-card">
            <h3 style="margin-top:0;">Commencer une analyse</h3>
            <p style="color:#6B7280;">
                Importez un fichier CAO afin d’extraire ses données techniques puis lancer
                l’analyse environnementale et les recommandations d’éco-conception.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


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

        if "validated_recommendations" not in st.session_state:
            st.session_state["validated_recommendations"] = []

        recommendation_data = {
            "year": selected_year,
            "vehicle": selected_vehicle,
            "material": material,
            "impact_kgco2e": impact,
            "share_percent": share,
            "priority": priority,
            "recommendation": recommendation,
            "decision": decision,
            "comment": comment
        }

        st.session_state["validated_recommendations"].append(
            recommendation_data
        )

        st.success(
            "Décision enregistrée."
        )

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

def page_validation():

    st.markdown(
        '<div class="page-title">Validation des recommandations</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="page-subtitle">'
        'Validation humaine des recommandations proposées par AIEC.'
        '</div>',
        unsafe_allow_html=True,
    )

    if "validated_recommendations" not in st.session_state:
        st.info(
            "Aucune recommandation n'a encore été enregistrée."
        )
        return

    validations = st.session_state[
        "validated_recommendations"
    ]

    if not validations:
        st.info(
            "Aucune recommandation n'a encore été enregistrée."
        )
        return

    st.subheader("Décisions enregistrées")

    validation_df = pd.DataFrame(validations)

    validation_df = validation_df.rename(
        columns={
            "year": "Année",
            "vehicle": "Véhicule",
            "material": "Matériau",
            "impact_kgco2e": "Impact (kgCO₂e)",
            "share_percent": "Part de l'impact (%)",
            "priority": "Priorité",
            "recommendation": "Recommandation",
            "decision": "Décision",
            "comment": "Commentaire"
        }
    )

    st.dataframe(
        validation_df,
        use_container_width=True,
        hide_index=True
    )


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
    placeholder_page("Conformité", "Contrôles réglementaires et critères d’éco-conception.")
elif page == "Rapports":
    placeholder_page("Rapports", "Génération et historique des rapports d’analyse.")
