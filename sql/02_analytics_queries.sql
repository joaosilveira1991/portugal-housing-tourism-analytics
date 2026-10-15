-- Query 1: Year-over-Year (YoY) Growth for Housing vs Tourism

WITH consolidated_metrics AS (

    SELECT
        g.municipality,
        t.year,
        t.quarter,
        h.median_price_sqm,
        tm.overnight_stays,
        LAG(h.median_price_sqm, 4) OVER (
            PARTITION BY g.municipality ORDER BY t.year, t.quarter
        ) AS prev_year_price_sqm,
        LAG(tm.overnight_stays, 4) OVER (
            PARTITION BY g.municipality ORDER BY t.year, t.quarter -- a clause used in SQL Window Functions to divide your data into distinct groups (or "partitions") before performing a calculation
        )  AS prev_year_overnight_stays

        FROM fact_housing h
        JOIN fact_tourism tm ON h.geo_id = tm.geo_id AND h.time_id = tm.time_id
        JOIN dim_geography g ON h.geo_id = g.geo_id
        JOIN dim_time t ON h.time_id = t.time_id

)

SELECT
    municipality,
    year,
    quarter,
    median_price_sqm,
    ROUND(((median_price_sqm - prev_year_price_sqm)/ NULLIF(prev_year_price_sqm, 0)) * 100, 2) AS housing_price_yoy_pct,
    ROUND(((overnight_stays - prev_year_overnight_stays)::NUMERIC / NULLIF(prev_year_overnight_stays, 0)) * 100, 2) AS tourism_stays_yoy_pct
FROM consolidated_metrics
WHERE prev_year_price_sqm IS NOT NULL
ORDER BY municipality. year DESC, quarter DESC;

-- Query 2: Regional Tourism Exposure & Housing Pressure Ranking (2024 Summary)

SELECT
    g.municipality,
    g.nuts_ii,
    ROUND(AVG(h.median_price_sqm), 2) AS avg_price_sqm_2024,
    SUM(tm.overnight_stays) AS total_overnight_stays_2024,
    ROUND(SUM(tm.total_revenue_eur),2) AS total_tourism_rev_eur_2024,
    DENSE_RANK() OVER (ORDER BY AVG(h.median_price_sqm) DESC) AS price_rank,
    DENSE_RANK() OVER (ORDER BY SUM(tm.overnight_stays) DESC) AS tourism_rank
FROM fact_housing h
JOIN fact_tourism tm ON h.geo_id = tm.geo_id AND h.time_id = tm.time_id
JOIN dim_geography g ON h.geo_id = g.geo_id
JOIN dim_time t ON h.time_id = t.time_id
WHERE t.year = 2024
GROUP BY g.municipality, g.nuts_ii
ORDER BY price_rank;