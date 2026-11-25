# Methodology

## Data
BTS Airline On-Time Performance, Reporting Carrier file. One month first to validate the pipeline,
then at least 6 to 12 months for modelling and seasonality.

## Cleaning rules
- Parse flight date; drop rows missing date, airline, origin or destination.
- Trim and upper-case airline, airport, tail number and cancellation code.
- Remove exact duplicates on date, airline, flight number, origin, destination, scheduled departure, tail number.
- Convert hhmm times to minutes after midnight; 2400 maps to 0; invalid minutes become null.
- Recompute `dep_del15` and `arr_del15` from delay minutes.
- Log anomalies (origin equals destination, non-positive distance, cancelled flights with a departure time,
  completed flights missing delays, delays over 24 hours) to `documentation/data_quality_report.md`.

## Prediction design (to be implemented)
- Target: `dep_del15` (departure delay of 15+ minutes), cancelled flights excluded.
- Split: chronological. Train on earlier months, validate and test on later months. No random split.
- Features known before departure only: scheduled departure hour, day of week, month, airline, origin,
  destination, distance, and rolling delay history computed strictly from data before each flight.
- Excluded as leakage: actual departure and arrival times, arrival delay, taxi times, air time,
  and all delay-cause columns.
- Late-aircraft signal: use the previous leg of the same tail number only when that flight landed before
  the prediction time.
- Metrics: ROC-AUC and PR-AUC as headline, plus precision, recall, F1 and confusion matrix for the delayed class,
  because roughly one flight in five is delayed and accuracy alone misleads.
- Baselines: majority class, and airline plus hour averages, before logistic regression, random forest and gradient boosting.
