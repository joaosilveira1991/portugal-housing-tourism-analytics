-- Dimensional Model DDL (Star Schema)

--Eliminated tables if exist
DROP TABLE IF EXISTS fact_tourism;
DROP TABLE IF EXISTS fact_housing;
DROP TABLE IF EXISTS dim_geography;
DROP TABLE IF EXISTS dim_time;


-- 1. Dimensions

CREATE TABLE dim_geography (
    geo_id VARCHER(10) PRIMARY KEY,
    municipality VARCHAR(100) NOT NULL,
    nuts_iii VARCHAR(100) NOT NULL, -- Nomenclature of Territorial Units for Statistics, Level 3.
    nuts_ii VARCHAR(100) NOT NULL  -- Nomenclature of Territorial Units for Statistics, Level 2.
);

CREATE TABLE dim_time (
    time_id VARCHAR(10) PRIMARY KEY,
    year INT NOT NULL
    quarter INT NOT NULL
);

-- 2. Fact Tables
CREATE TABLE fact_housing(
    geo_id VARCHAR(10) REFERENCES dim_geography dim_time(geo_id),
    time_id VARCHAR(10) REFERENCES dim_time(time_id),
    median_price_sqm NUMERIC(10, 2) --  median price per square meter of a property or location.
    transaction_count INT,
    total_volume_k_eur NUMERIC(14, 2), -- total financial volume measured in thousands of Euros
    PRIMARY KEY (geo_id, time_id)
);

CREATE TABLE fact_tourism (
    geo_id VARCHAR(10) REFERENCES dim_geography(geo_id),
    time_id VARCHAR(10) REFERENCES dim_time(time_id),
    overnight_stays BIGINT, --  data type used in SQL to store extremely large whole numbers (integers) without any decimal points.
    total_revenue_eur NUMERIC(14, 2),
    PRIMARY KEY (geo_id, time_id)
);