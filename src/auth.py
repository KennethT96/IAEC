import hashlib
import hmac
import os
import streamlit as st

# Compte de démonstration uniquement.
# En production : utiliser un fournisseur d'identité/SSO ou une base utilisateurs sécurisée.
DEMO_EMAIL = "ingenieur@aiec.local"
DEMO_PASSWORD = "Aiec2026!"

def _hash(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()

def check_credentials(email: str, password: str) -> bool:
    email_ok = hmac.compare_digest(email.strip().lower(), DEMO_EMAIL.lower())
    password_ok = hmac.compare_digest(_hash(password), _hash(DEMO_PASSWORD))
    return email_ok and password_ok

def init_auth_state() -> None:
    st.session_state.setdefault("authenticated", False)
    st.session_state.setdefault("user_email", None)
    st.session_state.setdefault("user_role", "Ingénieur")

def login(email: str, password: str) -> bool:
    if check_credentials(email, password):
        st.session_state.authenticated = True
        st.session_state.user_email = email.strip().lower()
        return True
    return False

def logout() -> None:
    st.session_state.authenticated = False
    st.session_state.user_email = None
    st.session_state.page = "Tableau de bord"
