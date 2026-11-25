-- Business questions 4, 5 and 8: delay causes, weather, late-arriving aircraft.
-- Cause minutes exist only for flights with arr_del15 = 1, so shares are of delayed flights.

-- Cause share of total delay minutes (overall)
WITH t AS (
    SELECT SUM(carrier_delay) c, SUM(weather_delay) w, SUM(nas_delay) n,
           SUM(security_delay) s, SUM(late_aircraft_delay) l
    FROM fact_flights WHERE arr_del15 = 1
)
SELECT cause, delay_min, ROUND(100.0 * delay_min / SUM(delay_min) OVER (), 2) AS pct_of_delay_minutes
FROM (SELECT 'Carrier' AS cause, c AS delay_min FROM t UNION ALL SELECT 'Weather', w FROM t
      UNION ALL SELECT 'NAS', n FROM t UNION ALL SELECT 'Security', s FROM t
      UNION ALL SELECT 'Late aircraft', l FROM t)
ORDER BY delay_min DESC;

-- Cause mix by airline
SELECT a.airline_name,
       COUNT(*) AS delayed_flights,
       ROUND(100.0 * SUM(carrier_delay) / SUM(arr_delay), 1)       AS carrier_pct,
       ROUND(100.0 * SUM(weather_delay) / SUM(arr_delay), 1)       AS weather_pct,
       ROUND(100.0 * SUM(nas_delay) / SUM(arr_delay), 1)           AS nas_pct,
       ROUND(100.0 * SUM(late_aircraft_delay) / SUM(arr_delay), 1) AS late_aircraft_pct
FROM fact_flights f JOIN dim_airline a USING (airline_code)
WHERE f.arr_del15 = 1
GROUP BY a.airline_name ORDER BY delayed_flights DESC;

-- Cause mix by month (weather seasonality)
SELECT d.month, d.month_name,
       ROUND(100.0 * SUM(weather_delay) / SUM(arr_delay), 1) AS weather_pct,
       ROUND(100.0 * SUM(late_aircraft_delay) / SUM(arr_delay), 1) AS late_aircraft_pct
FROM fact_flights f JOIN dim_date d USING (date_key)
WHERE f.arr_del15 = 1
GROUP BY ALL ORDER BY d.month;

-- Cancellation reasons
SELECT CASE cancellation_code WHEN 'A' THEN 'Carrier' WHEN 'B' THEN 'Weather'
                              WHEN 'C' THEN 'NAS' WHEN 'D' THEN 'Security' END AS reason,
       COUNT(*) AS cancellations,
       ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS pct
FROM fact_flights WHERE cancelled = 1
GROUP BY ALL ORDER BY cancellations DESC;

-- Late-aircraft propagation: how much of the inbound delay carries into the same tail's next departure?
-- Uses only flights where the previous leg of the same tail number landed before the next scheduled departure.
WITH legs AS (
    SELECT tail_number, crs_dep_ts, dep_delay, arr_delay, dest_airport, origin_airport,
           LAG(arr_delay)    OVER w AS prev_arr_delay,
           LAG(dest_airport) OVER w AS prev_dest,
           LAG(crs_dep_ts)   OVER w AS prev_crs_dep_ts
    FROM fact_flights
    WHERE flight_status = 'Completed' AND tail_number IS NOT NULL
    WINDOW w AS (PARTITION BY tail_number ORDER BY crs_dep_ts)
)
SELECT CASE WHEN prev_arr_delay < 0  THEN '1 Early inbound'
            WHEN prev_arr_delay < 15 THEN '2 On-time inbound'
            WHEN prev_arr_delay < 60 THEN '3 Late inbound (15-59)'
            ELSE '4 Very late inbound (60+)' END AS inbound_status,
       COUNT(*) AS next_flights,
       ROUND(AVG(dep_delay), 2) AS avg_next_dep_delay_min,
       ROUND(100.0 * AVG(CASE WHEN dep_delay >= 15 THEN 1 ELSE 0 END), 2) AS next_dep_delay_rate_pct
FROM legs
WHERE prev_arr_delay IS NOT NULL
  AND prev_dest = origin_airport                       -- aircraft really did fly the previous leg into this airport
  AND prev_crs_dep_ts >= crs_dep_ts - INTERVAL 1 DAY   -- same operating day sequence
GROUP BY ALL ORDER BY inbound_status;

-- Cancellation reasons by month
SELECT d.month, d.month_name,
       CASE f.cancellation_code WHEN 'A' THEN 'Carrier' WHEN 'B' THEN 'Weather'
                                WHEN 'C' THEN 'NAS' WHEN 'D' THEN 'Security' END AS reason,
       COUNT(*) AS cancellations
FROM fact_flights f JOIN dim_date d USING (date_key)
WHERE f.cancelled = 1
GROUP BY ALL ORDER BY d.month, cancellations DESC;
