import pandas as pd


REQUIRED_COLUMNS = [
    "ID_Country",
    "Year",
    "parent_description",
    "Layer 1",
    "Layer 2",
    "Layer 3",
    "Layer 4",
    "Value",
    "Unit",
]


def load_vehicle_excel(file):
    """
    Charge les feuilles Vehicle_composition_* d'un fichier Excel
    et les fusionne dans un seul DataFrame.
    """

    excel_file = pd.ExcelFile(file)

    data_sheets = [
        sheet
        for sheet in excel_file.sheet_names
        if sheet.startswith("Vehicle_composition")
    ]

    if not data_sheets:
        raise ValueError(
            "Aucune feuille 'Vehicle_composition' trouvée."
        )

    dataframes = []

    for sheet in data_sheets:

        df = pd.read_excel(
            excel_file,
            sheet_name=sheet
        )

        df["source_sheet"] = sheet

        dataframes.append(df)

    merged_df = pd.concat(
        dataframes,
        ignore_index=True
    )

    return merged_df, data_sheets


def validate_vehicle_data(df):
    """
    Vérifie la présence des colonnes obligatoires.
    """

    missing_columns = [
        column
        for column in REQUIRED_COLUMNS
        if column not in df.columns
    ]

    return missing_columns


def clean_vehicle_data(df):
    """
    Nettoyage minimal des données.
    """

    cleaned = df.copy()

    # Conversion de l'année
    cleaned["Year"] = pd.to_numeric(
        cleaned["Year"],
        errors="coerce"
    )

    # Conversion de la masse / valeur
    cleaned["Value"] = pd.to_numeric(
        cleaned["Value"],
        errors="coerce"
    )

    # Suppression des lignes sans valeur
    cleaned = cleaned.dropna(
        subset=["Year", "Value"]
    )

    # Nettoyage des champs texte
    text_columns = [
        "ID_Country",
        "parent_description",
        "Layer 1",
        "Layer 2",
        "Layer 3",
        "Layer 4",
        "Unit"
    ]

    for column in text_columns:

        cleaned[column] = (
            cleaned[column]
            .astype(str)
            .str.strip()
        )

    # Suppression des doublons parfaits
    cleaned = cleaned.drop_duplicates()

    return cleaned.reset_index(drop=True)


def get_data_summary(df):
    """
    Retourne quelques informations utiles pour l'interface.
    """

    return {
        "nombre_lignes": len(df),

        "nombre_annees": df["Year"].nunique(),

        "annee_min": int(df["Year"].min()),

        "annee_max": int(df["Year"].max()),

        "nombre_vehicules": df["Layer 1"].nunique(),

        "nombre_composants": df["Layer 2"].nunique(),

        "nombre_materiaux": df["Layer 3"].nunique(),

        "nombre_elements": df["Layer 4"].nunique(),
    }