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
            ef.recyclability_rate,
            ef.recycled_content_rate,
            ef.factor_type,
            ef.geographic_scope,
            ef.system_boundary,
            ef.source,
            ef.notes,

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


def save_recommendation_validation(
    year,
    vehicle,
    material,
    impact_kgco2e,
    share_percent,
    priority,
    recommendation,
    decision,
    comment
):

    conn = get_connection()
    cursor = conn.cursor()

    query = """
        INSERT INTO recommendation_validations (
            year,
            vehicle,
            material,
            impact_kgco2e,
            share_percent,
            priority,
            recommendation,
            decision,
            comment
        )
        VALUES (
            %s, %s, %s, %s, %s,
            %s, %s, %s, %s
        )

        ON CONFLICT (year, vehicle, material)

        DO UPDATE SET
            impact_kgco2e = EXCLUDED.impact_kgco2e,
            share_percent = EXCLUDED.share_percent,
            priority = EXCLUDED.priority,
            recommendation = EXCLUDED.recommendation,
            decision = EXCLUDED.decision,
            comment = EXCLUDED.comment,
            validated_at = CURRENT_TIMESTAMP;
    """

    cursor.execute(
        query,
        (
            year,
            vehicle,
            material,
            impact_kgco2e,
            share_percent,
            priority,
            recommendation,
            decision,
            comment
        )
    )

    conn.commit()

    cursor.close()
    conn.close()

@st.cache_data(ttl=30)
def get_recommendation_validations():

    conn = get_connection()

    query = """
        SELECT
            year,
            vehicle,
            material,
            impact_kgco2e,
            share_percent,
            priority,
            recommendation,
            decision,
            comment,
            validated_at
        FROM recommendation_validations
        ORDER BY validated_at DESC;
    """

    df = pd.read_sql(
        query,
        conn
    )

    conn.close()

    return df

@st.cache_data(ttl=3600)
def get_dashboard_kpis(year):

    conn = get_connection()

    query = """
        WITH vehicle_stats AS (
            SELECT
                COUNT(DISTINCT layer_1) AS vehicle_count,
                SUM(value) FILTER (
                    WHERE layer_2 IS NULL
                    AND layer_3 IS NULL
                    AND layer_4 IS NULL
                ) AS total_mass
            FROM vehicle_composition
            WHERE year = %s
        ),

        material_stats AS (
            SELECT
                SUM(vc.value) FILTER (
                    WHERE vc.layer_3 IS NOT NULL
                    AND vc.layer_4 IS NULL
                    AND vc.layer_3 <> 'shadowMaterial'
                ) AS identified_mass,

                SUM(vc.value) FILTER (
                    WHERE vc.layer_3 = 'shadowMaterial'
                    AND vc.layer_4 IS NULL
                ) AS unknown_mass,

                COUNT(DISTINCT vc.layer_3) FILTER (
                    WHERE vc.layer_3 IS NOT NULL
                    AND vc.layer_3 <> 'shadowMaterial'
                ) AS material_count,

                COUNT(DISTINCT vc.layer_2) FILTER (
                    WHERE vc.layer_2 IS NOT NULL
                ) AS component_count

            FROM vehicle_composition vc
            WHERE vc.year = %s
        ),

        carbon_stats AS (
            SELECT
                SUM(
                    vc.value
                    * ef.emission_factor_kgco2e_per_kg
                ) AS total_carbon

            FROM vehicle_composition vc

            INNER JOIN material_environmental_factors ef
                ON vc.layer_3 = ef.material

            WHERE vc.year = %s
              AND vc.layer_3 IS NOT NULL
              AND vc.layer_4 IS NULL
              AND vc.layer_3 <> 'shadowMaterial'
        )

        SELECT
            vehicle_stats.vehicle_count,
            vehicle_stats.total_mass,
            material_stats.identified_mass,
            material_stats.unknown_mass,
            material_stats.material_count,
            material_stats.component_count,
            carbon_stats.total_carbon

        FROM vehicle_stats
        CROSS JOIN material_stats
        CROSS JOIN carbon_stats;
    """

    df = pd.read_sql(
        query,
        conn,
        params=(year, year, year)
    )

    conn.close()

    return df.iloc[0].to_dict()

@st.cache_data(ttl=3600)
def get_dashboard_material_impact(year):

    conn = get_connection()

    query = """
        SELECT
            vc.layer_3 AS material,

            SUM(vc.value) AS mass_kg,

            ef.emission_factor_kgco2e_per_kg,

            SUM(
                vc.value
                * ef.emission_factor_kgco2e_per_kg
            ) AS impact_kgco2e

        FROM vehicle_composition vc

        INNER JOIN material_environmental_factors ef
            ON vc.layer_3 = ef.material

        WHERE vc.year = %s
          AND vc.layer_3 IS NOT NULL
          AND vc.layer_4 IS NULL
          AND vc.layer_3 <> 'shadowMaterial'

        GROUP BY
            vc.layer_3,
            ef.emission_factor_kgco2e_per_kg

        ORDER BY impact_kgco2e DESC;
    """

    df = pd.read_sql(
        query,
        conn,
        params=(year,)
    )

    conn.close()

    return df

@st.cache_data(ttl=3600)
def get_dashboard_carbon_trend():

    conn = get_connection()

    query = """
        SELECT
            vc.year,

            SUM(
                vc.value
                * ef.emission_factor_kgco2e_per_kg
            ) AS impact_kgco2e

        FROM vehicle_composition vc

        INNER JOIN material_environmental_factors ef
            ON vc.layer_3 = ef.material

        WHERE vc.layer_3 IS NOT NULL
          AND vc.layer_4 IS NULL
          AND vc.layer_3 <> 'shadowMaterial'

        GROUP BY vc.year

        ORDER BY vc.year;
    """

    df = pd.read_sql(
        query,
        conn
    )

    conn.close()

    return df

@st.cache_data(ttl=3600)
def get_vehicle_carbon_intensities(year):

    conn = get_connection()

    query = """
        SELECT
            vc.layer_1 AS vehicle,

            SUM(
                CASE
                    WHEN vc.layer_3 IS NOT NULL
                     AND vc.layer_4 IS NULL
                     AND vc.layer_3 <> 'shadowMaterial'
                    THEN vc.value
                    ELSE 0
                END
            ) AS identified_mass,

            SUM(
                CASE
                    WHEN vc.layer_3 IS NOT NULL
                     AND vc.layer_4 IS NULL
                     AND vc.layer_3 <> 'shadowMaterial'
                    THEN
                        vc.value
                        * ef.emission_factor_kgco2e_per_kg
                    ELSE 0
                END
            ) AS total_carbon

        FROM vehicle_composition vc

        LEFT JOIN material_environmental_factors ef
            ON vc.layer_3 = ef.material

        WHERE vc.year = %s

        GROUP BY vc.layer_1
    """

    df = pd.read_sql(
        query,
        conn,
        params=(year,)
    )

    conn.close()

    df = df[
        (df["identified_mass"] > 0)
        & (df["total_carbon"] > 0)
    ].copy()

    df["carbon_intensity"] = (
        df["total_carbon"]
        / df["identified_mass"]
    )

    return df

def save_aiec_report(
    vehicle,
    year,
    vehicle_description,
    aiec_score,
    aiec_level,
    pdf_data
):
    conn = get_connection()
    cursor = conn.cursor()

    # Conversion des types pandas / numpy
    vehicle = str(vehicle)
    year = int(year)
    vehicle_description = (
        str(vehicle_description)
        if vehicle_description is not None
        else None
    )

    aiec_score = (
        float(aiec_score)
        if aiec_score is not None
        else None
    )

    aiec_level = (
        str(aiec_level)
        if aiec_level is not None
        else None
    )

    # S'assurer que le PDF est bien transmis sous forme binaire
    pdf_data = bytes(pdf_data)

    query = """
        INSERT INTO aiec_reports (
            vehicle,
            year,
            vehicle_description,
            aiec_score,
            aiec_level,
            pdf_data
        )
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING id;
    """

    cursor.execute(
        query,
        (
            vehicle,
            year,
            vehicle_description,
            aiec_score,
            aiec_level,
            pdf_data
        )
    )

    report_id = cursor.fetchone()[0]

    conn.commit()
    cursor.close()
    conn.close()

    return report_id

@st.cache_data(ttl=60)
def get_aiec_reports():

    conn = get_connection()

    query = """
        SELECT
            id,
            vehicle,
            year,
            vehicle_description,
            aiec_score,
            aiec_level,
            generated_at
        FROM aiec_reports
        ORDER BY generated_at DESC;
    """

    df = pd.read_sql(
        query,
        conn
    )

    conn.close()

    return df

def get_aiec_report_pdf(report_id):

    conn = get_connection()

    cursor = conn.cursor()

    query = """
        SELECT pdf_data
        FROM aiec_reports
        WHERE id = %s;
    """

    cursor.execute(
        query,
        (report_id,)
    )

    result = cursor.fetchone()

    cursor.close()
    conn.close()

    if result is None:
        return None

    return bytes(result[0])