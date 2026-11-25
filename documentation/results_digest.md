# Results Digest

Generated from data/processed/results/*.csv. Rates are percentages. On-time = completed flight arriving less than 15 minutes late.

## Airline scorecard (sorted by on-time %)

| airline_name | scheduled_flights | on_time_pct | avg_dep_delay_min | avg_arr_delay_min | dep_delay_rate_pct | cancellation_rate_pct | diversion_rate_pct |
|---|---|---|---|---|---|---|---|
| Republic Airways | 98,810 | 86.63 | 3.01 | -3.01 | 11.02 | 1.35 | 0.16 |
| Endeavor Air | 65,567 | 85.08 | 6.97 | -0.22 | 14.15 | 1.44 | 0.2 |
| Hawaiian Airlines | 25,813 | 84.91 | 5.32 | 4.18 | 12.74 | 0.69 | 0.1 |
| Delta Air Lines | 328,111 | 83.86 | 8.56 | 1.49 | 16.28 | 0.21 | 0.21 |
| United Airlines | 248,081 | 81.92 | 9.92 | 3.53 | 17.29 | 0.72 | 0.24 |
| SkyWest Airlines | 246,412 | 80.83 | 11.53 | 7.18 | 17.43 | 0.91 | 0.33 |
| Southwest Airlines | 457,861 | 80.73 | 10.91 | 3.98 | 22.29 | 0.42 | 0.2 |
| Envoy Air | 91,410 | 80.65 | 9.11 | 4.83 | 17.61 | 0.97 | 0.21 |
| PSA Airlines | 75,028 | 79.39 | 12.91 | 8.35 | 19.15 | 1.2 | 0.21 |
| Alaska Airlines | 80,604 | 78.57 | 7.01 | 3.6 | 19.49 | 0.69 | 0.26 |
| Spirit Airlines | 82,427 | 77.7 | 13.41 | 6.33 | 23.75 | 1.3 | 0.16 |
| Allegiant Air | 38,688 | 77.39 | 15.59 | 11.18 | 22.55 | 1.21 | 0.35 |
| American Airlines | 318,897 | 76.6 | 17.51 | 11.3 | 23.27 | 1.06 | 0.26 |
| JetBlue Airways | 78,259 | 74.52 | 16.77 | 10.43 | 25.51 | 1.36 | 0.37 |
| Frontier Airlines | 67,588 | 73.49 | 15.81 | 11.93 | 25.24 | 1.61 | 0.14 |

## Origin airports: 10 worst by departure delay rate (min 500 departures)

| origin_airport | city | departures | dep_delay_rate_pct | avg_dep_delay_min | avg_taxi_out_min | cancellation_rate_pct |
|---|---|---|---|---|---|---|
| ASE | Aspen, CO | 2,916 | 33.11 | 30.75 | 22.53 | 6.89 |
| BQN | Aguadilla, PR | 781 | 27.99 | 22.49 | 13.24 | 1.66 |
| FLL | Fort Lauderdale, FL | 29,657 | 26.22 | 15.67 | 17.94 | 1.42 |
| SFB | Sanford, FL | 3,152 | 26.17 | 14.54 | 15.09 | 0.7 |
| MIA | Miami, FL | 35,641 | 25.75 | 17.7 | 21.58 | 1.47 |
| COU | Columbia, MO | 567 | 25.62 | 17.92 | 15.11 | 0.88 |
| DFW | Dallas/Fort Worth, TX | 102,381 | 25.24 | 16.06 | 19.73 | 1.11 |
| BWI | Baltimore, MD | 31,854 | 25.24 | 12.44 | 14.65 | 0.57 |
| HDN | Hayden, CO | 940 | 24.27 | 14.04 | 24.15 | 0.96 |
| DAL | Dallas, TX | 23,627 | 24.06 | 13.53 | 13.02 | 0.39 |

## Origin airports: 10 best

| origin_airport | city | departures | dep_delay_rate_pct | avg_dep_delay_min | avg_taxi_out_min | cancellation_rate_pct |
|---|---|---|---|---|---|---|
| ITO | Hilo, HI | 2,197 | 8.22 | 0.49 | 10.1 | 0.36 |
| SGU | St. George, UT | 980 | 9.51 | 4.06 | 18.98 | 0.2 |
| GTF | Great Falls, MT | 785 | 9.86 | 7.76 | 16.29 | 0.51 |
| OGG | Kahului, HI | 8,721 | 10.61 | 3.0 | 10.82 | 0.54 |
| LIH | Lihue, HI | 5,223 | 10.67 | 3.25 | 10.47 | 0.59 |
| HLN | Helena, MT | 506 | 10.69 | 7.6 | 19.88 | 0.2 |
| KOA | Kona, HI | 5,407 | 10.88 | 3.4 | 12.54 | 0.68 |
| BIL | Billings, MT | 1,391 | 11.26 | 3.47 | 16.54 | 0.36 |
| SUN | Sun Valley/Hailey/Ketchum, ID | 715 | 11.44 | 8.22 | 22.85 | 0.98 |
| OAJ | Jacksonville/Camp Lejeune, NC | 596 | 11.8 | 8.39 | 18.73 | 0.5 |

## 15 busiest origin airports

| origin_airport | city | departures | dep_delay_rate_pct | avg_dep_delay_min | avg_taxi_out_min | cancellation_rate_pct |
|---|---|---|---|---|---|---|
| ATL | Atlanta, GA | 111,443 | 18.08 | 8.97 | 16.17 | 0.42 |
| DFW | Dallas/Fort Worth, TX | 102,381 | 25.24 | 16.06 | 19.73 | 1.11 |
| DEN | Denver, CO | 101,395 | 22.01 | 12.21 | 18.4 | 0.55 |
| ORD | Chicago, IL | 91,275 | 20.28 | 12.92 | 23.51 | 0.66 |
| CLT | Charlotte, NC | 70,970 | 23.83 | 15.27 | 21.51 | 1.08 |
| LAX | Los Angeles, CA | 63,294 | 17.85 | 9.76 | 18.55 | 0.42 |
| PHX | Phoenix, AZ | 62,572 | 18.7 | 9.22 | 15.98 | 0.29 |
| LAS | Las Vegas, NV | 61,022 | 22.6 | 11.85 | 18.09 | 0.54 |
| SEA | Seattle, WA | 53,686 | 20.31 | 9.04 | 21.59 | 0.4 |
| LGA | New York, NY | 52,760 | 17.13 | 9.23 | 23.31 | 1.58 |
| MCO | Orlando, FL | 51,137 | 22.44 | 13.7 | 17.99 | 0.56 |
| BOS | Boston, MA | 46,823 | 19.74 | 11.49 | 20.66 | 1.11 |
| DCA | Washington, DC | 45,647 | 18.17 | 10.17 | 20.61 | 0.88 |
| SFO | San Francisco, CA | 43,752 | 22.72 | 14.5 | 20.26 | 0.85 |
| DTW | Detroit, MI | 42,768 | 17.39 | 9.8 | 17.54 | 0.41 |

## Routes: 15 worst by arrival delay rate (min 100 flights)

| route_key | distance_mi | flights | dep_delay_rate_pct | arr_delay_rate_pct | avg_arr_delay_min |
|---|---|---|---|---|---|
| DFW-ALB | 1435.0 | 113 | 47.79 | 50.89 | 33.56 |
| SFO-ASE | 848.0 | 123 | 52.59 | 47.75 | 46.23 |
| MIA-PDX | 2700.0 | 146 | 38.36 | 47.26 | 23.18 |
| ASE-SFO | 848.0 | 123 | 43.24 | 46.85 | 47.92 |
| DFW-SYR | 1336.0 | 113 | 41.96 | 45.54 | 38.26 |
| MSY-SAN | 1599.0 | 104 | 43.27 | 45.19 | 21.14 |
| ASE-ATL | 1304.0 | 160 | 47.06 | 44.3 | 45.74 |
| FLL-SAN | 2269.0 | 154 | 34.21 | 43.62 | 21.28 |
| ASE-IAH | 913.0 | 252 | 41.81 | 42.61 | 38.17 |
| SEA-SIT | 861.0 | 121 | 38.33 | 42.37 | 18.64 |
| JFK-BQN | 1576.0 | 195 | 41.58 | 42.33 | 20.63 |
| SJU-BDL | 1666.0 | 321 | 35.74 | 42.32 | 35.81 |
| DFW-BDL | 1471.0 | 171 | 45.51 | 41.92 | 24.31 |
| DEN-MLI | 752.0 | 121 | 35.83 | 41.18 | 33.34 |
| EYW-DFW | 1089.0 | 148 | 34.97 | 40.85 | 23.62 |

## Day of week

| day_of_week | day_name | flights | dep_delay_rate_pct | cancellation_rate_pct |
|---|---|---|---|---|
| 1 | Monday | 363,955 | 18.91 | 0.42 |
| 2 | Tuesday | 305,354 | 16.34 | 0.74 |
| 3 | Wednesday | 291,720 | 17.36 | 0.94 |
| 4 | Thursday | 341,097 | 19.68 | 1.12 |
| 5 | Friday | 323,440 | 21.05 | 0.76 |
| 6 | Saturday | 296,494 | 20.55 | 0.7 |
| 7 | Sunday | 381,496 | 22.27 | 0.96 |

## Scheduled departure hour

| crs_dep_hour | flights | dep_delay_rate_pct | avg_dep_delay_min |
|---|---|---|---|
| 0 | 3,885 | 21.39 | 12.42 |
| 1 | 1,197 | 18.3 | 11.01 |
| 2 | 456 | 25.22 | 12.54 |
| 3 | 329 | 19.76 | 10.7 |
| 4 | 196 | 25.0 | 22.21 |
| 5 | 64,092 | 7.52 | 4.59 |
| 6 | 159,892 | 7.39 | 3.69 |
| 7 | 159,238 | 9.45 | 4.39 |
| 8 | 156,731 | 11.54 | 5.25 |
| 9 | 129,270 | 13.84 | 6.76 |
| 10 | 141,243 | 15.64 | 7.82 |
| 11 | 145,208 | 17.18 | 9.19 |
| 12 | 135,927 | 18.61 | 10.46 |
| 13 | 137,155 | 20.53 | 11.59 |
| 14 | 132,985 | 22.27 | 12.82 |
| 15 | 131,627 | 23.95 | 14.05 |
| 16 | 133,117 | 25.4 | 15.2 |
| 17 | 142,889 | 25.64 | 15.9 |
| 18 | 140,155 | 27.87 | 17.51 |
| 19 | 123,615 | 29.27 | 18.49 |
| 20 | 101,689 | 30.46 | 19.03 |
| 21 | 73,922 | 28.65 | 18.16 |
| 22 | 51,682 | 27.54 | 17.54 |
| 23 | 18,528 | 22.37 | 12.81 |

## Distance band

| distance_band | flights | dep_delay_rate_pct |
|---|---|---|
| 1 Short (<500 mi) | 780,350 | 18.1 |
| 2 Medium (500-1499 mi) | 1,207,456 | 20.31 |
| 3 Long (1500+ mi) | 297,222 | 20.29 |

## Delay cause share of delay minutes (flights 15+ min late on arrival)

| cause | delay_min | pct_of_delay_minutes |
|---|---|---|
| Late aircraft | 12184034.0 | 39.79 |
| Carrier | 10836150.0 | 35.39 |
| NAS | 5677743.0 | 18.54 |
| Weather | 1869746.0 | 6.11 |
| Security | 54557.0 | 0.18 |

## Cause mix by airline

| airline_name | delayed_flights | carrier_pct | weather_pct | nas_pct | late_aircraft_pct |
|---|---|---|---|---|---|
| Southwest Airlines | 87,656 | 28.4 | 2.3 | 17.1 | 51.9 |
| American Airlines | 73,641 | 34.9 | 5.2 | 12.7 | 47.0 |
| Delta Air Lines | 52,744 | 47.3 | 4.7 | 19.3 | 28.7 |
| SkyWest Airlines | 46,656 | 51.1 | 15.8 | 13.9 | 19.0 |
| United Airlines | 44,416 | 29.9 | 5.2 | 24.6 | 40.3 |
| JetBlue Airways | 19,598 | 37.8 | 2.9 | 19.7 | 39.5 |
| Spirit Airlines | 18,111 | 27.0 | 2.5 | 39.8 | 30.0 |
| Frontier Airlines | 17,607 | 27.2 | 1.9 | 18.1 | 52.8 |
| Envoy Air | 17,479 | 24.2 | 10.2 | 19.6 | 45.8 |
| Alaska Airlines | 17,110 | 28.6 | 4.1 | 27.9 | 38.9 |
| PSA Airlines | 15,244 | 28.7 | 7.2 | 12.5 | 51.4 |
| Republic Airways | 13,016 | 26.3 | 8.1 | 32.6 | 32.9 |
| Endeavor Air | 9,625 | 31.2 | 6.4 | 21.9 | 40.4 |
| Allegiant Air | 8,612 | 36.0 | 10.9 | 15.5 | 37.3 |
| Hawaiian Airlines | 3,865 | 63.1 | 2.1 | 3.4 | 31.1 |

## Cancellation reasons

| reason | cancellations | pct |
|---|---|---|
| Weather | 11,529 | 62.22 |
| Carrier | 4,020 | 21.7 |
| NAS | 2,979 | 16.08 |

## Late-aircraft propagation (next departure by inbound status of same aircraft)

| inbound_status | next_flights | avg_next_dep_delay_min | next_dep_delay_rate_pct |
|---|---|---|---|
| 1 Early inbound | 1,382,124 | 1.92 | 8.91 |
| 2 On-time inbound | 376,467 | 7.68 | 17.14 |
| 3 Late inbound (15-59) | 283,281 | 22.09 | 50.18 |
| 4 Very late inbound (60+) | 133,144 | 68.48 | 62.53 |

# Seasonal Comparison

## Monthly scorecard

| quarter | month | month_name | flights | on_time_pct | avg_dep_delay_min | avg_arr_delay_min | dep_delay_rate_pct | cancellation_rate_pct | diversion_rate_pct |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 2 | February | 519,221 | 84.08 | 7.44 | 0.59 | 15.49 | 0.58 | 0.18 |
| 2 | 6 | June | 611,132 | 75.06 | 16.9 | 11.81 | 25.31 | 1.29 | 0.32 |
| 3 | 9 | September | 582,622 | 84.49 | 6.64 | 1.0 | 15.07 | 0.6 | 0.15 |
| 4 | 12 | December | 590,581 | 78.85 | 13.53 | 7.12 | 21.63 | 0.7 | 0.27 |

## Departure delay rate by scheduled hour and month (%)

| crs_dep_hour | February | June | September | December |
|---|---|---|---|---|
| 0 | 15.31 | 31.8 | 16.52 | 18.18 |
| 1 | 11.89 | 24.6 | 15.56 | 18.97 |
| 2 | 23.57 | 26.92 | 15.0 | 30.16 |
| 3 | 18.81 | 22.54 | 16.22 | 20.0 |
| 4 | 21.13 | 18.18 | 0.0 | 33.77 |
| 5 | 5.77 | 8.43 | 5.56 | 9.43 |
| 6 | 5.73 | 8.58 | 5.58 | 9.44 |
| 7 | 7.56 | 11.51 | 6.84 | 11.59 |
| 8 | 9.05 | 14.09 | 8.67 | 14.04 |
| 9 | 11.68 | 16.16 | 10.4 | 16.87 |
| 10 | 12.93 | 18.17 | 11.94 | 19.47 |
| 11 | 14.56 | 20.78 | 13.24 | 19.96 |
| 12 | 15.27 | 22.46 | 13.89 | 22.43 |
| 13 | 17.72 | 25.44 | 15.72 | 23.08 |
| 14 | 18.37 | 28.31 | 17.51 | 24.7 |
| 15 | 19.66 | 31.1 | 18.67 | 25.81 |
| 16 | 20.75 | 33.71 | 20.23 | 26.73 |
| 17 | 19.95 | 34.67 | 20.57 | 26.67 |
| 18 | 20.7 | 38.06 | 22.7 | 29.18 |
| 19 | 23.62 | 39.63 | 22.68 | 29.51 |
| 20 | 22.79 | 40.27 | 24.07 | 32.01 |
| 21 | 19.06 | 39.88 | 20.62 | 30.82 |
| 22 | 18.2 | 37.42 | 19.83 | 28.65 |
| 23 | 17.88 | 31.75 | 16.16 | 20.0 |

## Airline on-time arrival % by month

| airline_name | Feb | Jun | Sep | Dec |
|---|---|---|---|---|
| Alaska Airlines | 82.79 | 74.54 | 79.76 | 78.21 |
| Allegiant Air | 82.29 | 74.53 | 82.98 | 73.26 |
| American Airlines | 81.29 | 67.82 | 80.66 | 77.32 |
| Delta Air Lines | 88.74 | 80.15 | 87.1 | 80.35 |
| Endeavor Air | 89.68 | 80.47 | 90.31 | 80.49 |
| Envoy Air | 87.71 | 71.71 | 84.7 | 79.93 |
| Frontier Airlines | 80.09 | 63.68 | 76.13 | 75.66 |
| Hawaiian Airlines | 80.96 | 84.19 | 90.12 | 84.14 |
| JetBlue Airways | 75.48 | 71.95 | 82.1 | 69.3 |
| PSA Airlines | 86.33 | 81.71 | 78.89 | 72.56 |
| Republic Airways | 92.23 | 83.8 | 89.91 | 81.62 |
| SkyWest Airlines | 83.26 | 77.52 | 84.6 | 78.26 |
| Southwest Airlines | 83.55 | 74.2 | 85.49 | 80.54 |
| Spirit Airlines | 78.43 | 72.82 | 82.65 | 77.55 |
| United Airlines | 83.96 | 75.84 | 86.75 | 81.19 |

## Airline rank by month (1 = best on-time %)

| airline_name | Feb | Jun | Sep | Dec |
|---|---|---|---|---|
| Alaska Airlines | 9 | 8 | 13 | 9 |
| Allegiant Air | 10 | 9 | 9 | 13 |
| American Airlines | 11 | 14 | 12 | 11 |
| Delta Air Lines | 3 | 5 | 4 | 6 |
| Endeavor Air | 2 | 4 | 1 | 5 |
| Envoy Air | 4 | 13 | 7 | 7 |
| Frontier Airlines | 13 | 15 | 15 | 12 |
| Hawaiian Airlines | 12 | 1 | 2 | 1 |
| JetBlue Airways | 15 | 12 | 11 | 15 |
| PSA Airlines | 5 | 3 | 14 | 14 |
| Republic Airways | 1 | 2 | 3 | 2 |
| SkyWest Airlines | 8 | 6 | 8 | 8 |
| Southwest Airlines | 7 | 10 | 6 | 4 |
| Spirit Airlines | 14 | 11 | 10 | 10 |
| United Airlines | 6 | 7 | 5 | 3 |

## Busiest 15 airports: departure delay rate by month (%)

| origin_airport | February | June | September | December |
|---|---|---|---|---|
| ATL | 11.99 | 21.12 | 15.58 | 22.66 |
| BOS | 14.95 | 23.59 | 16.1 | 23.63 |
| CLT | 16.5 | 31.01 | 22.08 | 24.67 |
| DCA | 13.34 | 21.52 | 13.56 | 24.34 |
| DEN | 23.2 | 29.82 | 16.55 | 18.26 |
| DFW | 17.09 | 36.2 | 19.57 | 26.61 |
| DTW | 11.28 | 22.64 | 11.95 | 22.49 |
| LAS | 21.18 | 29.0 | 20.26 | 19.78 |
| LAX | 17.87 | 22.41 | 12.99 | 17.96 |
| LGA | 14.3 | 21.54 | 10.78 | 21.99 |
| MCO | 19.05 | 30.51 | 15.78 | 23.34 |
| ORD | 12.88 | 29.22 | 16.04 | 21.88 |
| PHX | 15.74 | 24.94 | 14.88 | 19.04 |
| SEA | 13.56 | 26.83 | 18.62 | 20.39 |
| SFO | 27.47 | 25.65 | 16.58 | 22.51 |

## Delay cause mix by month (share of delay minutes, %)

| month | month_name | weather_pct | late_aircraft_pct |
|---|---|---|---|
| 2 | February | 5.3 | 36.9 |
| 6 | June | 6.0 | 41.5 |
| 9 | September | 4.8 | 38.4 |
| 12 | December | 7.5 | 40.2 |

## Cancellations by reason and month

| reason | February | June | September | December |
|---|---|---|---|---|
| Carrier | 711 | 1,935 | 637 | 737 |
| NAS | 387 | 2,018 | 282 | 292 |
| Weather | 1,904 | 3,923 | 2,580 | 3,122 |
