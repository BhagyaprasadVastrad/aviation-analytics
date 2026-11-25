# Power BI Dashboard Specification

Status: built. The final report has 41 measures (a few extra helpers were added during the build, such as a text version of Total Flights, a Cause table for the cause chart and late-aircraft measures), and the page layouts changed slightly from this first plan. The README describes the final pages.

Source: `powerbi/data/*.parquet` (written by `python/04_export_powerbi.py`).
Get Data > Parquet, import all five files. Delete nothing; load as is.

## 1. Data model

Relationships (all many-to-one from `fact_flights`, single direction):

| From (fact_flights) | To | Active |
|---|---|---|
| `date_key` | `dim_date[date_key]` | Yes |
| `airline_code` | `dim_airline[airline_code]` | Yes |
| `origin_airport` | `dim_airport[airport_code]` | Yes |
| `dest_airport` | `dim_airport[airport_code]` | **No** (role-playing destination, used with USERELATIONSHIP) |
| `route_key` | `dim_route[route_key]` | Yes |

Column settings:
- `dim_date[month_name]`: sort by `dim_date[month]`
- `dim_date[day_name]`: sort by `dim_date[day_of_week]`
- `dim_date[full_date]`: mark `dim_date` as the date table using this column
- `fact_flights[dep_del15]`, `arr_del15`, `cancelled`, `diverted`: summarize "Don't summarize"
- `dim_airport[city]`: data category City (the value is "City, ST", e.g. "Dallas/Fort Worth, TX")

Also import `data/processed/results/06_delay_causes_analysis__5.csv` as table `LateAircraft` for the propagation chart.

## 2. Calculated column (fact_flights)

```dax
Dep Period =
SWITCH (
    TRUE (),
    fact_flights[crs_dep_hour] < 6, "1 Night (0-5)",
    fact_flights[crs_dep_hour] < 12, "2 Morning (6-11)",
    fact_flights[crs_dep_hour] < 18, "3 Afternoon (12-17)",
    "4 Evening (18-23)"
)
```

## 3. Measures

Create a table `_Measures` (Enter Data, one blank column, then hide the column) and put every measure there.

```dax
-- Volumes
Total Flights = COUNTROWS ( fact_flights )

Completed Flights =
CALCULATE ( COUNTROWS ( fact_flights ), fact_flights[flight_status] = "Completed" )

Cancelled Flights =
CALCULATE ( COUNTROWS ( fact_flights ), fact_flights[cancelled] = 1 )

Diverted Flights =
CALCULATE ( COUNTROWS ( fact_flights ), fact_flights[diverted] = 1 )

-- Punctuality
On-Time Flights =
CALCULATE (
    COUNTROWS ( fact_flights ),
    fact_flights[flight_status] = "Completed",
    fact_flights[arr_del15] = 0
)

On-Time % = DIVIDE ( [On-Time Flights], [Completed Flights] )

Departed Late Flights =
CALCULATE ( COUNTROWS ( fact_flights ), fact_flights[dep_del15] = 1 )

Dep Delay Rate % = DIVIDE ( [Departed Late Flights], COUNT ( fact_flights[dep_del15] ) )

Arrived Late Flights =
CALCULATE ( COUNTROWS ( fact_flights ), fact_flights[arr_del15] = 1 )

Arr Delay Rate % = DIVIDE ( [Arrived Late Flights], COUNT ( fact_flights[arr_del15] ) )

Avg Dep Delay (min) = AVERAGE ( fact_flights[dep_delay] )
Avg Arr Delay (min) = AVERAGE ( fact_flights[arr_delay] )

Cancellation Rate % = DIVIDE ( [Cancelled Flights], [Total Flights] )
Diversion Rate % = DIVIDE ( [Diverted Flights], [Total Flights] )

Disruption Rate % =
DIVIDE (
    CALCULATE (
        COUNTROWS ( fact_flights ),
        FILTER (
            fact_flights,
            fact_flights[dep_del15] = 1
                || fact_flights[cancelled] = 1
                || fact_flights[diverted] = 1
        )
    ),
    [Total Flights]
)

-- Destination view (uses the inactive relationship)
Arrivals =
CALCULATE ( COUNTROWS ( fact_flights ),
    USERELATIONSHIP ( fact_flights[dest_airport], dim_airport[airport_code] ) )

Dest Arr Delay Rate % =
CALCULATE ( [Arr Delay Rate %],
    USERELATIONSHIP ( fact_flights[dest_airport], dim_airport[airport_code] ) )

-- Small-sample guards (use these on airport and route rankings)
Dep Delay Rate % (min 500) = IF ( [Total Flights] >= 500, [Dep Delay Rate %] )
Arr Delay Rate % (min 100) = IF ( [Total Flights] >= 100, [Arr Delay Rate %] )

-- Ranking
Airline Rank (On-Time) =
RANKX ( ALL ( dim_airline[airline_name] ), [On-Time %], , DESC, DENSE )

-- Delay causes (minutes exist only for flights arriving 15+ minutes late)
Carrier Delay Min = SUM ( fact_flights[carrier_delay] )
Weather Delay Min = SUM ( fact_flights[weather_delay] )
NAS Delay Min = SUM ( fact_flights[nas_delay] )
Security Delay Min = SUM ( fact_flights[security_delay] )
Late Aircraft Delay Min = SUM ( fact_flights[late_aircraft_delay] )

Total Cause Min =
[Carrier Delay Min] + [Weather Delay Min] + [NAS Delay Min]
    + [Security Delay Min] + [Late Aircraft Delay Min]

Carrier Share % = DIVIDE ( [Carrier Delay Min], [Total Cause Min] )
Weather Share % = DIVIDE ( [Weather Delay Min], [Total Cause Min] )
NAS Share % = DIVIDE ( [NAS Delay Min], [Total Cause Min] )
Security Share % = DIVIDE ( [Security Delay Min], [Total Cause Min] )
Late Aircraft Share % = DIVIDE ( [Late Aircraft Delay Min], [Total Cause Min] )

-- Cancellation reasons (code A carrier, B weather, C NAS, D security)
Cancelled: Weather =
CALCULATE ( [Cancelled Flights], fact_flights[cancellation_code] = "B" )
```

For the cause-share bar chart, build a small disconnected table with the five cause names and use a
`SWITCH` measure, or simply place the five share measures in one clustered bar visual.

Format: percentages to 1 decimal place, delay minutes to 1 decimal place, flight counts with thousands separators.

## 4. Pages

Common to every page: slicers for `dim_date[full_date]` (between), `dim_airline[airline_name]`,
and `dim_airport[state]`; title bar with page name; one accent colour for "worse than average"
(red-orange) and one neutral for the rest. Add a text box with the definition
"On-time = completed flight arriving less than 15 minutes late (BTS convention)".

**Page 1: Executive Aviation Overview**
- Cards: Total Flights, On-Time %, Avg Dep Delay (min), Avg Arr Delay (min), Cancellation Rate %, Departed Late Flights
- Line chart: `dim_date[full_date]` by Dep Delay Rate % and Cancellation Rate % (secondary axis). With one month per quarter loaded, the date table also spans the empty days between months; use a categorical date axis or a `dim_date[month_name]` view so the gaps do not show as breaks
- Column chart: `fact_flights[crs_dep_hour]` by Dep Delay Rate % (the headline pattern)
- Decomposition or key-influencers visual optional

**Page 2: Airline Performance**
- Bar chart: airline by On-Time %, sorted descending, with Airline Rank in the tooltip
- Table: airline, Total Flights, On-Time %, Avg Dep Delay, Avg Arr Delay, Cancellation Rate %, Diversion Rate %
- Scatter: x = Dep Delay Rate %, y = Cancellation Rate %, size = Total Flights, detail = airline
- Matrix: airline by `Dep Period`, value Dep Delay Rate % with conditional formatting

**Page 3: Airport Performance**
- Table: `dim_airport[airport_code]`, city, Total Flights, Dep Delay Rate % (min 500), Avg Dep Delay, Avg Taxi Out (add `AVERAGE(fact_flights[taxi_out])`), Cancellation Rate %, Disruption Rate %
- Bar charts: top 15 airports by Dep Delay Rate % (min 500) and by Dest Arr Delay Rate %
- Map: bubble per airport (size = Total Flights, colour = Dep Delay Rate %). Geocoding by "City, ST" can be imperfect;
  if bubbles land in the wrong place, join an airport coordinates table (for example from OurAirports) on airport code.
- Heat map matrix: origin airport by `crs_dep_hour`, value Dep Delay Rate %, top 15 airports by flights

**Page 4: Route and Delay Analysis**
- Table: `dim_route[route_key]`, distance, Total Flights, Arr Delay Rate % (min 100), Avg Arr Delay; top N filter on rate
- Column charts: day of week (`dim_date[day_name]`) and month by Dep Delay Rate %
- Line chart: hour by Dep Delay Rate %
- Slicer: distance band (create a calculated column on `fact_flights[distance]`)
- With only one month loaded, hide the month chart or mark it "needs more data"

**Page 5: Delay Causes and Operational Intelligence**
- Stacked bar (100%): airline by the five cause shares
- Donut or bar: overall cause share
- Bar chart: cancellation reasons using `cancellation_code` (map A, B, C, D to names with a small lookup table)
- Column chart from `LateAircraft`: inbound status vs next departure delay rate
- Text box with the headline: "Late-arriving aircraft is the largest cause of delay minutes"; update the figure from the data rather than hardcoding it

## 5. Checks before publishing screenshots

1. Total Flights on Page 1 equals the `fact_flights` row count in `documentation/validation_results.md`.
2. On-Time % overall equals the SQL airline scorecard weighted result (about 75% for June 2024).
3. Airline On-Time % in the table matches `03_airline_analysis__1.csv` to one decimal.
4. Save screenshots of each page to `screenshots/`.
