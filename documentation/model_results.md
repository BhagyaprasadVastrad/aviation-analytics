# Delay Prediction Results

Target: departure delay of 15+ minutes. Prediction made 60 minutes before scheduled departure.
Data: 2,285,028 non-cancelled flights across 120 days in 4 calendar months (2024-02-01 to 2024-12-31).
Split: chronological (train 2024-02-01 to 2024-06-30, validation 2024-09-01 to 2024-09-30, test 2024-12-01 to 2024-12-31). Train 1,119,475 / validation 579,123 / test 586,430.
Test-set delay rate: 21.6%. Threshold chosen on validation to maximise F1, applied once to test.

| Model | ROC-AUC | PR-AUC | Precision | Recall | F1 | Threshold |
|---|---:|---:|---:|---:|---:|---:|
| Majority class (no model) | 0.500 | 0.216 | 0.000 | 0.000 | 0.000 |  |
| Baseline: origin 7-day delay rate | 0.570 | 0.259 | 0.221 | 0.965 | 0.359 | 0.12 |
| Logistic regression | 0.734 | 0.457 | 0.342 | 0.728 | 0.466 | 0.25 |
| Random forest | 0.754 | 0.492 | 0.373 | 0.706 | 0.488 | 0.22 |
| Gradient boosting | 0.764 | 0.516 | 0.414 | 0.636 | 0.501 | 0.25 |

Confusion matrices (test set):

| Model | TN | FP | FN | TP |
|---|---:|---:|---:|---:|
| Majority class (no model) | 459,556 | 0 | 126,874 | 0 |
| Baseline: origin 7-day delay rate | 27,619 | 431,937 | 4,427 | 122,447 |
| Logistic regression | 282,261 | 177,295 | 34,535 | 92,339 |
| Random forest | 308,845 | 150,711 | 37,278 | 89,596 |
| Gradient boosting | 345,265 | 114,291 | 46,176 | 80,698 |

Note: 4 calendar months of data. The test month is a season the model has not seen in training, so results show how well it carries over to a new season.
