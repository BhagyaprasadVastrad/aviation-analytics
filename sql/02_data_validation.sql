-- Data validation checks. Every check should return 0 problem rows unless noted.

-- 1. Row counts per table
SELECT 'fact_flights' AS tbl, COUNT(*) AS n FROM fact_flights
UNION ALL SELECT 'dim_airline', COUNT(*) FROM dim_airline
UNION ALL SELECT 'dim_airport', COUNT(*) FROM dim_airport
UNION ALL SELECT 'dim_date',    COUNT(*) FROM dim_date
UNION ALL SELECT 'dim_route',   COUNT(*) FROM dim_route;

-- 2. Orphan foreign keys (expect 0 in every row)
SELECT 'airline' AS dim, COUNT(*) AS orphans FROM fact_flights f
  LEFT JOIN dim_airline d ON f.airline_code = d.airline_code WHERE d.airline_code IS NULL
UNION ALL SELECT 'origin_airport', COUNT(*) FROM fact_flights f
  LEFT JOIN dim_airport d ON f.origin_airport = d.airport_code WHERE d.airport_code IS NULL
UNION ALL SELECT 'dest_airport', COUNT(*) FROM fact_flights f
  LEFT JOIN dim_airport d ON f.dest_airport = d.airport_code WHERE d.airport_code IS NULL
UNION ALL SELECT 'date', COUNT(*) FROM fact_flights f
  LEFT JOIN dim_date d ON f.date_key = d.date_key WHERE d.date_key IS NULL
UNION ALL SELECT 'route', COUNT(*) FROM fact_flights f
  LEFT JOIN dim_route d ON f.route_key = d.route_key WHERE d.route_key IS NULL;

-- 3. Flight status distribution (informational)
SELECT flight_status, COUNT(*) AS flights,
       ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS pct
FROM fact_flights GROUP BY flight_status ORDER BY flights DESC;

-- 4. Logical consistency (expect 0)
SELECT
  SUM(CASE WHEN flight_status = 'Cancelled' AND dep_delay IS NOT NULL THEN 1 ELSE 0 END) AS cancelled_with_delay,
  SUM(CASE WHEN flight_status = 'Completed' AND (dep_delay IS NULL OR arr_delay IS NULL) THEN 1 ELSE 0 END) AS completed_missing_delay,
  SUM(CASE WHEN origin_airport = dest_airport THEN 1 ELSE 0 END) AS same_origin_dest,
  SUM(CASE WHEN dep_del15 = 1 AND dep_delay < 15 THEN 1 ELSE 0 END) AS flag_mismatch,
  SUM(CASE WHEN arr_del15 = 0 AND (carrier_delay IS NOT NULL) THEN 1 ELSE 0 END) AS cause_without_delay
FROM fact_flights;

-- 5. Duplicate flights (expect 0 rows)
SELECT date_key, airline_code, flight_number, origin_airport, dest_airport, crs_dep_ts, tail_number, COUNT(*) AS n
FROM fact_flights
GROUP BY ALL HAVING COUNT(*) > 1;

-- 6. Delay-cause minutes should not exceed arrival delay by much (BTS rounding): rows with a gap > 5 min
SELECT COUNT(*) AS cause_sum_mismatch
FROM fact_flights
WHERE arr_del15 = 1
  AND ABS(arr_delay - (carrier_delay + weather_delay + nas_delay + security_delay + late_aircraft_delay)) > 5;

-- 7. Ranges (informational)
SELECT MIN(dep_delay) AS min_dep_delay, MAX(dep_delay) AS max_dep_delay,
       MIN(arr_delay) AS min_arr_delay, MAX(arr_delay) AS max_arr_delay,
       MIN(distance)  AS min_distance,  MAX(distance)  AS max_distance
FROM fact_flights;
