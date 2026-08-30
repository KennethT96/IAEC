import io
import pandas as pd
import psycopg2


EXCEL_FILE = "data/Vehicle_composition.xlsx"

SHEETS = [
    "Vehicle_composition_1",
    "Vehicle_composition_2",
    "Vehicle_composition_3",
]


DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "dbname": "aiec_db",
    "user": "postgres",
    "password": "postgres",
}


COLUMN_MAPPING = {
    "ID_Country": "id_country",
    "Year": "year",
    "parent_description": "parent_description",
    "Layer 1": "layer_1",
    "Layer 2": "layer_2",
    "Layer 3": "layer_3",
    "Layer 4": "layer_4",
    "Value": "value",
    "Unit": "unit",
}


def prepare_dataframe(df, sheet_name):

    df = df.rename(columns=COLUMN_MAPPING)

    required_columns = list(COLUMN_MAPPING.values())

    df = df[required_columns].copy()

    df["source_sheet"] = sheet_name

    df["year"] = pd.to_numeric(
        df["year"],
        errors="coerce"
    )

    df["value"] = pd.to_numeric(
        df["value"],
        errors="coerce"
    )

    df = df.dropna(
        subset=["year", "value"]
    )

    df["year"] = df["year"].astype(int)

    return df


def copy_dataframe(cursor, df):

    buffer = io.StringIO()

    df.to_csv(
        buffer,
        index=False,
        header=False,
        sep="\t",
        na_rep="\\N"
    )

    buffer.seek(0)

    columns = [
        "id_country",
        "year",
        "parent_description",
        "layer_1",
        "layer_2",
        "layer_3",
        "layer_4",
        "value",
        "unit",
        "source_sheet",
    ]

    copy_sql = f"""
        COPY vehicle_composition
        ({", ".join(columns)})
        FROM STDIN
        WITH (
            FORMAT CSV,
            DELIMITER E'\\t',
            NULL '\\N'
        )
    """

    cursor.copy_expert(
        copy_sql,
        buffer
    )


def main():

    print("Connexion à PostgreSQL...")

    connection = psycopg2.connect(
        **DB_CONFIG
    )

    cursor = connection.cursor()

    try:

        for sheet in SHEETS:

            print()
            print("=" * 60)
            print(f"Lecture : {sheet}")

            df = pd.read_excel(
                EXCEL_FILE,
                sheet_name=sheet
            )

            print(
                f"{len(df):,} lignes lues"
            )

            df = prepare_dataframe(
                df,
                sheet
            )

            print(
                f"{len(df):,} lignes après nettoyage"
            )

            print(
                "Import dans PostgreSQL..."
            )

            copy_dataframe(
                cursor,
                df
            )

            connection.commit()

            print(
                f"{sheet} importée avec succès."
            )

        cursor.execute(
            """
            SELECT COUNT(*)
            FROM vehicle_composition;
            """
        )

        total = cursor.fetchone()[0]

        print()
        print("=" * 60)
        print("IMPORT TERMINÉ")
        print(
            f"Nombre total de lignes : {total:,}"
        )

    except Exception as e:

        connection.rollback()

        print()
        print("ERREUR :")
        print(e)

        raise

    finally:

        cursor.close()
        connection.close()


if __name__ == "__main__":
    main()