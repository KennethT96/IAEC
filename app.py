from pathlib import Path
import pandas as pd
import streamlit as st

from src.auth import init_auth_state, login, logout, DEMO_EMAIL, DEMO_PASSWORD
from src.styles import inject_css

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
            ("⬆️", "Importer CAD"),
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


def page_import_cad():
    st.markdown('<div class="page-title">Importation de fichiers CAO</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="page-subtitle">Déposez un fichier industriel pour démarrer son analyse.</div>',
        unsafe_allow_html=True,
    )

    uploaded = st.file_uploader(
        "Déposez des fichiers CAO ici ou cliquez pour parcourir",
        type=["step", "stp", "iges", "igs", "dxf", "ifc", "stl", "pdf"],
        accept_multiple_files=False,
        help="Pour le MVP, STEP/STP est le format recommandé.",
    )

    st.markdown(
        """
        <div class="aiec-card" style="margin-top:16px;">
            <strong>Formats pris en charge dans le MVP</strong><br><br>
            <span class="format-chip">.STEP / .STP</span>
            <span class="format-chip">.IGES / .IGS</span>
            <span class="format-chip">.DXF</span>
            <span class="format-chip">.IFC</span>
            <span class="format-chip">.STL</span>
            <span class="format-chip">.PDF technique</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if uploaded is not None:
        st.session_state["cad_file_name"] = uploaded.name
        st.session_state["cad_file_size"] = uploaded.size
        st.success(f"Fichier chargé : {uploaded.name}")
        c1, c2 = st.columns(2)
        c1.metric("Nom", uploaded.name)
        c2.metric("Taille", f"{uploaded.size / 1024:.1f} Ko")
        st.info(
            "Étape suivante : connecter ce fichier au module d’extraction CAO "
            "(géométrie, volume, assemblage et métadonnées)."
        )


def page_ai():
    st.markdown('<div class="page-title">Analyse de l’IA</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="page-subtitle">Analyse environnementale et détection des points critiques.</div>',
        unsafe_allow_html=True,
    )

    if "cad_file_name" not in st.session_state:
        st.warning("Importez d’abord un fichier CAO.")
        return

    st.markdown(
        f"""
        <div class="aiec-card">
            <strong>Fichier sélectionné</strong>
            <p>{st.session_state["cad_file_name"]}</p>
            <p style="color:#6B7280;">
                Le moteur d’analyse CAO sera ajouté à l’étape suivante.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
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


if not st.session_state.authenticated:
    render_login()
    st.stop()

render_sidebar()
render_header()

page = st.session_state.page

if page == "Tableau de bord":
    page_dashboard()
elif page == "Importer CAD":
    page_import_cad()
elif page == "Analyse de l'IA":
    page_ai()
elif page == "Recommandations":
    placeholder_page("Recommandations", "Propositions d’amélioration de la conception.")
elif page == "Validation":
    placeholder_page("Validation", "Validation humaine des recommandations générées.")
elif page == "Conformité":
    placeholder_page("Conformité", "Contrôles réglementaires et critères d’éco-conception.")
elif page == "Rapports":
    placeholder_page("Rapports", "Génération et historique des rapports d’analyse.")
