# Data Quality Report

Date range: 2024-02-01 to 2024-12-31

## Cleaning log

| Check | Rows |
|---|---:|
| rows_raw | 2,303,556 |
| invalid_flight_date | 0 |
| duplicates_removed | 0 |
| invalid_crs_dep_time | 0 |
| origin_equals_dest | 0 |
| nonpositive_distance | 0 |
| cancelled_with_dep_time | 940 |
| completed_missing_arr_delay | 0 |
| completed_missing_dep_delay | 0 |
| extreme_dep_delay_over_24h | 190 |
| cancelled_actuals_blanked | 859 |
| rows_clean | 2,303,556 |

## Flight status

| Status | Rows | Share |
|---|---:|---:|
| Completed | 2,279,635 | 98.96% |
| Cancelled | 18,528 | 0.80% |
| Diverted | 5,393 | 0.23% |

## Notes

- Delay-cause columns are only populated by BTS for flights with arrival delay of 15+ minutes; they are null otherwise.
- Cancelled flights keep their rows but all actual-performance fields (times, delays, taxi, air time) are blanked, including the BTS cases where a departure time was recorded before cancellation. Diverted flights keep departure delay but have no arrival delay.
- dep_del15 and arr_del15 are recomputed from the delay minutes so they cannot disagree.
