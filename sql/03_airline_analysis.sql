-- Business questions 1 and 7 (airline view)
-- On-time = completed flight arriving less than 15 minutes late (BTS convention).
-- Cancelled and diverted flights are reported separately, not hidden.

-- Airline scorecard
SELECT
    a.airline_name,
    COUNT(*)                                                         AS scheduled_flights,
    ROUND(100.0 * AVG(CASE WHEN f.flight_status = 'Completed' THEN 1 - f.arr_del15 END), 2) AS on_time_pct,
    ROUND(AVG(f.dep_delay), 2)                                       AS avg_dep_delay_min,
    ROUND(AVG(f.arr_delay), 2)                                       AS avg_arr_delay_min,
    ROUND(100.0 * AVG(f.dep_del15), 2)                               AS dep_delay_rate_pct,
    ROUND(100.0 * AVG(f.cancelled), 2)                               AS cancellation_rate_pct,
    ROUND(100.0 * AVG(f.diverted), 2)                                AS diversion_rate_pct
FROM fact_flights f
JOIN dim_airline a USING (airline_code)
GROUP BY a.airline_name
HAVING COUNT(*) >= 1000
ORDER BY on_time_pct DESC;

-- Airline ranking by month with rank movement
WITH m AS (
    SELECT a.airline_name, d.year, d.month,
           100.0 * AVG(CASE WHEN f.flight_status = 'Completed' THEN 1 - f.arr_del15 END) AS on_time_pct
    FROM fact_flights f
    JOIN dim_airline a USING (airline_code)
    JOIN dim_date d USING (date_key)
    GROUP BY ALL
)
SELECT *, RANK() OVER (PARTITION BY year, month ORDER BY on_time_pct DESC) AS monthly_rank
FROM m
ORDER BY year, month, monthly_rank;

-- Airline reliability by time of day (departure hour bucket)
SELECT a.airline_name,
       CASE WHEN f.crs_dep_hour < 6  THEN '1 Night (0-5)'
            WHEN f.crs_dep_hour < 12 THEN '2 Morning (6-11)'
            WHEN f.crs_dep_hour < 18 THEN '3 Afternoon (12-17)'
            ELSE '4 Evening (18-23)' END AS dep_period,
       ROUND(100.0 * AVG(f.dep_del15), 2) AS dep_delay_rate_pct,
       COUNT(*) AS flights
FROM fact_flights f JOIN dim_airline a USING (airline_code)
WHERE f.flight_status <> 'Cancelled'
GROUP BY ALL
ORDER BY a.airline_name, dep_period;
