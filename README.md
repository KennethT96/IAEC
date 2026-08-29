# AIEC MVP v2

Cette version ajoute :

- écran de connexion ;
- session utilisateur ;
- déconnexion ;
- interface proche de la maquette AIEC ;
- navigation latérale ;
- tableau de bord ;
- import de fichiers CAO ;
- modules IA / recommandations / validation / conformité / rapports préparés.

## Compte de démonstration


> Ce compte est uniquement destiné au prototype de mémoire. Il ne s'agit pas d'un système d'authentification de production.

## Installation

Depuis PowerShell :

```powershell
python -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

## Prochaine étape

Implémenter la lecture d'un fichier STEP/STP et extraire les premières caractéristiques CAO :
volume, surface, nombre de solides/composants et métadonnées disponibles.
