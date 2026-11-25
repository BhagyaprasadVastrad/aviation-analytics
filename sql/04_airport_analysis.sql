-- Business question 2: which airports experience the most disruption?

-- Origin airport departure performance
SELECT
    f.origin_airport, ap.city, ap.state,
    COUNT(*)                              AS departures,
    ROUND(100.0 * AVG(f.dep_del15), 2)    AS dep_delay_rate_pct,
    ROUND(AVG(f.dep_delay), 2)            AS avg_dep_delay_min,
    ROUND(AVG(f.taxi_out), 2)             AS avg_taxi_out_min,
    ROUND(100.0 * AVG(f.cancelled), 2)    AS cancellation_rate_pct
FROM fact_flights f
JOIN dim_airport ap ON ap.airport_code = f.origin_airport
GROUP BY ALL
HAVING COUNT(*) >= 500
ORDER BY dep_delay_rate_pct DESC;

-- Destination airport arrival performance
SELECT
    f.dest_airport, ap.city, ap.state,
    COUNT(*)                              AS arrivals,
    ROUND(100.0 * AVG(f.arr_del15), 2)    AS arr_delay_rate_pct,
    ROUND(AVG(f.arr_delay), 2)            AS avg_arr_delay_min,
    ROUND(AVG(f.taxi_in), 2)              AS avg_taxi_in_min,
    ROUND(100.0 * AVG(f.diverted), 3)     AS diversion_rate_pct
FROM fact_flights f
JOIN dim_airport ap ON ap.airport_code = f.dest_airport
GROUP BY ALL
HAVING COUNT(*) >= 500
ORDER BY arr_delay_rate_pct DESC;

-- Congestion pattern: departure delay rate by airport and hour (heat-map source for Power BI)
SELECT f.origin_airport, f.crs_dep_hour,
       COUNT(*) AS departures,
       ROUND(100.0 * AVG(f.dep_del15), 2) AS dep_delay_rate_pct
FROM fact_flights f
WHERE f.flight_status <> 'Cancelled'
GROUP BY ALL
HAVING COUNT(*) >= 20
ORDER BY f.origin_airport, f.crs_dep_hour;

-- Disruption score: share of flights that were delayed 15+ min, cancelled or diverted
SELECT origin_airport,
       COUNT(*) AS departures,
       ROUND(100.0 * AVG(CASE WHEN dep_del15 = 1 OR cancelled = 1 OR diverted = 1 THEN 1 ELSE 0 END), 2) AS disruption_rate_pct
FROM fact_flights
GROUP BY origin_airport
HAVING COUNT(*) >= 500
ORDER BY disruption_rate_pct DESC;

-- Busiest 15 airports: departure delay rate by month (seasonal behaviour of the big hubs)
WITH top AS (
    SELECT origin_airport FROM fact_flights GROUP BY origin_airport ORDER BY COUNT(*) DESC LIMIT 15
)
SELECT f.origin_airport, d.month, d.month_name,
       COUNT(*) AS departures,
       ROUND(100.0 * AVG(f.dep_del15), 2) AS dep_delay_rate_pct
FROM fact_flights f JOIN dim_date d USING (date_key)
WHERE f.origin_airport IN (SELECT origin_airport FROM top)
GROUP BY ALL ORDER BY f.origin_airport, d.month;
