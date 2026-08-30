import os
import pandas as pd
import psycopg2
import streamlit as st


DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "dbname": "aiec_db",
    "user": "postgres",
    "password": "postgres",
}


def get_connection():
    return psycopg2.connect(**DB_CONFIG)


@st.cache_data(ttl=3600)
def get_years():

    conn = get_connection()

    query = """
        SELECT DISTINCT year
        FROM vehicle_composition
        WHERE year IS NOT NULL
        ORDER BY year DESC;
    """

    df = pd.read_sql(query, conn)

    conn.close()

    return df["year"].tolist()


@st.cache_data(ttl=3600)
def get_vehicles_by_year(year):

    conn = get_connection()

    query = """
        SELECT DISTINCT
            layer_1,
            parent_description
        FROM vehicle_composition
        WHERE year = %s
        ORDER BY parent_description;
    """

    df = pd.read_sql(
        query,
        conn,
        params=(year,)
    )

    conn.close()

    return df


@st.cache_data(ttl=3600)
def get_vehicle_data(year, layer_1):

    conn = get_connection()

    query = """
        SELECT
            id_country,
            year,
            parent_description,
            layer_1,
            layer_2,
            layer_3,
            layer_4,
            value,
            unit,
            source_sheet
        FROM vehicle_composition
        WHERE year = %s
        AND layer_1 = %s;
    """

    df = pd.read_sql(
        query,
        conn,
        params=(year, layer_1)
    )

    conn.close()

    return df
    
@st.cache_data(ttl=3600)
def get_vehicle_total_mass(year, layer_1):

    conn = get_connection()

    query = """
        SELECT value
        FROM vehicle_composition
        WHERE year = %s
          AND layer_1 = %s
          AND layer_2 IS NULL
          AND layer_3 IS NULL
          AND layer_4 IS NULL
        LIMIT 1;
    """

    df = pd.read_sql(
        query,
        conn,
        params=(year, layer_1)
    )

    conn.close()

    if df.empty:
        return None

    return float(df["value"].iloc[0])

@st.cache_data(ttl=3600)
def get_material_composition(year, layer_1):

    conn = get_connection()

    query = """
        SELECT
            layer_3 AS material,
            value AS mass_kg
        FROM vehicle_composition
        WHERE year = %s
          AND layer_1 = %s
          AND layer_3 IS NOT NULL
          AND layer_4 IS NULL
          AND layer_3 <> 'shadowMaterial'
        ORDER BY value DESC;
    """

    df = pd.read_sql(
        query,
        conn,
        params=(year, layer_1)
    )

    conn.close()

    return df

@st.cache_data(ttl=3600)
def get_component_composition(year, layer_1):

    conn = get_connection()
    query = """
        SELECT
            layer_2 AS component,
            value AS mass_kg
        FROM vehicle_composition
        WHERE year = %s
          AND layer_1 = %s
          AND layer_2 IS NOT NULL
          AND layer_3 IS NULL
          AND layer_4 IS NULL
        ORDER BY value DESC;
    """
    df = pd.read_sql(
        query,
        conn,
        params=(year, layer_1)
    )
    conn.close()
    return df

@st.cache_data(ttl=3600)
def get_unknown_material_mass(year, layer_1):

    conn = get_connection()
    query = """
        SELECT COALESCE(SUM(value), 0) AS mass_kg
        FROM vehicle_composition
        WHERE year = %s
          AND layer_1 = %s
          AND layer_3 = 'shadowMaterial'
          AND layer_4 IS NULL;
    """
    df = pd.read_sql(
        query,
        conn,
        params=(year, layer_1)
    )
    conn.close()
    return float(df["mass_kg"].iloc[0])

@st.cache_data(ttl=3600)
def get_material_environmental_analysis(year, layer_1):

    conn = get_connection()

    query = """
        SELECT
            vc.layer_3 AS material,
            vc.value AS mass_kg,
            ef.emission_factor_kgco2e_per_kg,
            ef.factor_type,
            ef.source,
            (
                vc.value
                * ef.emission_factor_kgco2e_per_kg
            ) AS impact_kgco2e
        FROM vehicle_composition vc

        LEFT JOIN material_environmental_factors ef
            ON vc.layer_3 = ef.material

        WHERE vc.year = %s
          AND vc.layer_1 = %s
          AND vc.layer_3 IS NOT NULL
          AND vc.layer_4 IS NULL
          AND vc.layer_3 <> 'shadowMaterial'

        ORDER BY impact_kgco2e DESC;
    """

    df = pd.read_sql(
        query,
        conn,
        params=(year, layer_1)
    )
    conn.close()
    return df