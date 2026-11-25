# Validation Results

## Check 1

```
         tbl       n
fact_flights 2303556
 dim_airline      15
 dim_airport     346
    dim_date     335
   dim_route    6584
```

## Check 2

```
           dim  orphans
       airline        0
origin_airport        0
  dest_airport        0
          date        0
         route        0
```

## Check 3

```
flight_status  flights   pct
    Completed  2279635 98.96
    Cancelled    18528  0.80
     Diverted     5393  0.23
```

## Check 4

```
 cancelled_with_delay  completed_missing_delay  same_origin_dest  flag_mismatch  cause_without_delay
                  0.0                      0.0               0.0            0.0                  0.0
```

## Check 5

```
Empty DataFrame
Columns: [date_key, airline_code, flight_number, origin_airport, dest_airport, crs_dep_ts, tail_number, n]
Index: []
```

## Check 6

```
 cause_sum_mismatch
                  0
```

## Check 7

```
 min_dep_delay  max_dep_delay  min_arr_delay  max_arr_delay  min_distance  max_distance
         -96.0         3274.0         -126.0         3241.0          31.0        5095.0
```
