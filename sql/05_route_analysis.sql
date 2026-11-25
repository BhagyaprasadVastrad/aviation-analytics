-- Business questions 3, 6 and 7: routes, seasonality, day-of-week and time-of-day

-- Most delay-prone routes (minimum volume guards against noisy small samples)
SELECT r.route_key, r.distance_mi,
       COUNT(*)                            AS flights,
       ROUND(100.0 * AVG(f.dep_del15), 2)  AS dep_delay_rate_pct,
       ROUND(100.0 * AVG(f.arr_del15), 2)  AS arr_delay_rate_pct,
       ROUND(AVG(f.arr_delay), 2)          AS avg_arr_delay_min
FROM fact_flights f
JOIN dim_route r USING (route_key)
GROUP BY ALL
HAVING COUNT(*) >= 100
ORDER BY arr_delay_rate_pct DESC
LIMIT 25;

-- Day of week
SELECT d.day_of_week, d.day_name,
       COUNT(*) AS flights,
       ROUND(100.0 * AVG(f.dep_del15), 2) AS dep_delay_rate_pct,
       ROUND(100.0 * AVG(f.cancelled), 2) AS cancellation_rate_pct
FROM fact_flights f JOIN dim_date d USING (date_key)
GROUP BY ALL ORDER BY d.day_of_week;

-- Hour of day
SELECT crs_dep_hour, COUNT(*) AS flights,
       ROUND(100.0 * AVG(dep_del15), 2) AS dep_delay_rate_pct,
       ROUND(AVG(dep_delay), 2) AS avg_dep_delay_min
FROM fact_flights
WHERE flight_status <> 'Cancelled'
GROUP BY crs_dep_hour ORDER BY crs_dep_hour;

-- Seasonality by quarter and month (each loaded month is a snapshot of its season, not a full-season average)
SELECT d.quarter, d.season, d.month, d.month_name, COUNT(*) AS flights,
       ROUND(100.0 * AVG(f.dep_del15), 2) AS dep_delay_rate_pct,
       ROUND(100.0 * AVG(f.cancelled), 2) AS cancellation_rate_pct
FROM fact_flights f JOIN dim_date d USING (date_key)
GROUP BY ALL ORDER BY d.month;

-- Distance band effect
SELECT CASE WHEN distance < 500 THEN '1 Short (<500 mi)'
            WHEN distance < 1500 THEN '2 Medium (500-1499 mi)'
            ELSE '3 Long (1500+ mi)' END AS distance_band,
       COUNT(*) AS flights,
       ROUND(100.0 * AVG(dep_del15), 2) AS dep_delay_rate_pct
FROM fact_flights WHERE flight_status <> 'Cancelled'
GROUP BY ALL ORDER BY distance_band;

-- Departure hour by month: how the daily delay build-up changes with the season
SELECT d.month, d.month_name, f.crs_dep_hour,
       COUNT(*) AS flights,
       ROUND(100.0 * AVG(f.dep_del15), 2) AS dep_delay_rate_pct
FROM fact_flights f JOIN dim_date d USING (date_key)
WHERE f.flight_status <> 'Cancelled'
GROUP BY ALL ORDER BY d.month, f.crs_dep_hour;

-- Monthly scorecard: one row per loaded month
SELECT d.quarter, d.month, d.month_name,
       COUNT(*) AS flights,
       ROUND(100.0 * AVG(CASE WHEN f.flight_status = 'Completed' THEN 1 - f.arr_del15 END), 2) AS on_time_pct,
       ROUND(AVG(f.dep_delay), 2) AS avg_dep_delay_min,
       ROUND(AVG(f.arr_delay), 2) AS avg_arr_delay_min,
       ROUND(100.0 * AVG(f.dep_del15), 2) AS dep_delay_rate_pct,
       ROUND(100.0 * AVG(f.cancelled), 2) AS cancellation_rate_pct,
       ROUND(100.0 * AVG(f.diverted), 2) AS diversion_rate_pct
FROM fact_flights f JOIN dim_date d USING (date_key)
GROUP BY ALL ORDER BY d.month;
