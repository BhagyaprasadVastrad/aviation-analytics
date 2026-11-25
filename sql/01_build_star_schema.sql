-- Star schema for the aviation analytics warehouse (DuckDB).
-- {{PARQUET}} is replaced by python/02_build_warehouse.py with the cleaned parquet path.

CREATE OR REPLACE TABLE stg_flights AS
SELECT * FROM read_parquet('{{PARQUET}}');

-- ---------------------------------------------------------------- Dim_Airline
CREATE OR REPLACE TABLE dim_airline (
    airline_code VARCHAR PRIMARY KEY,
    airline_name VARCHAR NOT NULL
);

INSERT INTO dim_airline
SELECT s.airline_code, COALESCE(n.airline_name, s.airline_code)
FROM (SELECT DISTINCT airline_code FROM stg_flights) s
LEFT JOIN (VALUES
    ('AA','American Airlines'), ('DL','Delta Air Lines'), ('UA','United Airlines'),
    ('WN','Southwest Airlines'), ('B6','JetBlue Airways'), ('AS','Alaska Airlines'),
    ('NK','Spirit Airlines'), ('F9','Frontier Airlines'), ('G4','Allegiant Air'),
    ('HA','Hawaiian Airlines'), ('YX','Republic Airways'), ('OO','SkyWest Airlines'),
    ('MQ','Envoy Air'), ('9E','Endeavor Air'), ('OH','PSA Airlines'), ('YV','Mesa Airlines'),
    ('QX','Horizon Air'), ('C5','CommuteAir'), ('G7','GoJet Airlines'), ('ZW','Air Wisconsin')
) AS n(airline_code, airline_name) ON n.airline_code = s.airline_code;

-- ---------------------------------------------------------------- Dim_Airport
CREATE OR REPLACE TABLE dim_airport (
    airport_code VARCHAR PRIMARY KEY,
    city         VARCHAR,
    state        VARCHAR
);

INSERT INTO dim_airport
SELECT airport_code, MIN(city), MIN(state)
FROM (
    SELECT origin AS airport_code, origin_city AS city, origin_state AS state FROM stg_flights
    UNION ALL
    SELECT dest, dest_city, dest_state FROM stg_flights
)
GROUP BY airport_code;

-- ---------------------------------------------------------------- Dim_Date
CREATE OR REPLACE TABLE dim_date (
    date_key     INTEGER PRIMARY KEY,   -- yyyymmdd
    full_date    DATE NOT NULL,
    year         INTEGER,
    quarter      INTEGER,
    month        INTEGER,
    month_name   VARCHAR,
    day_of_month INTEGER,
    day_of_week  INTEGER,               -- 1 = Monday ... 7 = Sunday (ISO)
    day_name     VARCHAR,
    is_weekend   BOOLEAN,
    season       VARCHAR
);

INSERT INTO dim_date
SELECT
    CAST(strftime(d, '%Y%m%d') AS INTEGER),
    CAST(d AS DATE),
    year(d), quarter(d), month(d), monthname(d), day(d),
    isodow(d), dayname(d), isodow(d) >= 6,
    CASE WHEN month(d) IN (12, 1, 2) THEN 'Winter'
         WHEN month(d) IN (3, 4, 5)  THEN 'Spring'
         WHEN month(d) IN (6, 7, 8)  THEN 'Summer'
         ELSE 'Autumn' END
FROM (
    SELECT unnest(generate_series(min_d, max_d, INTERVAL 1 DAY)) AS d
    FROM (SELECT MIN(flight_date) AS min_d, MAX(flight_date) AS max_d FROM stg_flights)
);

-- ---------------------------------------------------------------- Dim_Route
CREATE OR REPLACE TABLE dim_route (
    route_key    VARCHAR PRIMARY KEY,   -- ORIGIN-DEST
    origin       VARCHAR NOT NULL,
    dest         VARCHAR NOT NULL,
    distance_mi  DOUBLE
);

INSERT INTO dim_route
SELECT origin || '-' || dest, origin, dest, MEDIAN(distance)
FROM stg_flights
GROUP BY origin, dest;

-- ---------------------------------------------------------------- Fact_Flights
CREATE OR REPLACE TABLE fact_flights (
    flight_id           BIGINT PRIMARY KEY,
    date_key            INTEGER NOT NULL,
    airline_code        VARCHAR NOT NULL,
    origin_airport      VARCHAR NOT NULL,
    dest_airport        VARCHAR NOT NULL,
    route_key           VARCHAR NOT NULL,
    flight_number       VARCHAR,
    tail_number         VARCHAR,
    crs_dep_ts          TIMESTAMP,
    crs_dep_hour        INTEGER,
    dep_time_blk        VARCHAR,
    flight_status       VARCHAR,        -- Completed / Cancelled / Diverted
    dep_delay           DOUBLE,
    dep_del15           INTEGER,
    arr_delay           DOUBLE,
    arr_del15           INTEGER,
    taxi_out            DOUBLE,
    taxi_in             DOUBLE,
    air_time            DOUBLE,
    distance            DOUBLE,
    cancelled           INTEGER,
    cancellation_code   VARCHAR,        -- A carrier, B weather, C NAS, D security
    diverted            INTEGER,
    carrier_delay       DOUBLE,         -- cause columns: only populated when arr_del15 = 1
    weather_delay       DOUBLE,
    nas_delay           DOUBLE,
    security_delay      DOUBLE,
    late_aircraft_delay DOUBLE
);

INSERT INTO fact_flights
SELECT
    row_number() OVER (ORDER BY flight_date, crs_dep_min, airline_code, flight_number),
    CAST(strftime(flight_date, '%Y%m%d') AS INTEGER),
    airline_code, origin, dest, origin || '-' || dest,
    CAST(flight_number AS VARCHAR), tail_number,
    crs_dep_ts, crs_dep_hour, dep_time_blk, flight_status,
    dep_delay, CAST(dep_del15 AS INTEGER), arr_delay, CAST(arr_del15 AS INTEGER),
    taxi_out, taxi_in, air_time, distance,
    cancelled, cancellation_code, diverted,
    carrier_delay, weather_delay, nas_delay, security_delay, late_aircraft_delay
FROM stg_flights;

-- Indexes help the join-heavy dashboard queries
CREATE INDEX IF NOT EXISTS ix_fact_date    ON fact_flights(date_key);
CREATE INDEX IF NOT EXISTS ix_fact_airline ON fact_flights(airline_code);
CREATE INDEX IF NOT EXISTS ix_fact_origin  ON fact_flights(origin_airport);

DROP TABLE stg_flights;
