# Model Ablation and Lead-Time Results

Gradient boosting, 2,285,028 non-cancelled flights over 120 days in 4 months, chronological split (train 2024-02-01 to 2024-06-30, validation 2024-09-01 to 2024-09-30, test 2024-12-01 to 2024-12-31), test-set delay rate 21.6%. PR-AUC of a model with no skill equals the delay rate.

## Feature ablation (prediction 60 minutes before departure)

| Feature set | ROC-AUC | PR-AUC | Precision | Recall | F1 |
|---|---:|---:|---:|---:|---:|
| Departure hour only | 0.615 | 0.278 | 0.272 | 0.654 | 0.384 |
| Schedule + airline/airports | 0.639 | 0.312 | 0.307 | 0.509 | 0.383 |
| + prior 7-day delay rates | 0.644 | 0.315 | 0.287 | 0.657 | 0.399 |
| + previous leg of same aircraft | 0.742 | 0.462 | 0.414 | 0.551 | 0.473 |
| + same-day airport conditions (last 3h) | 0.678 | 0.399 | 0.321 | 0.604 | 0.419 |
| + previous leg and same-day conditions | 0.760 | 0.510 | 0.419 | 0.603 | 0.494 |
| All features | 0.764 | 0.516 | 0.414 | 0.636 | 0.501 |

## Lead time (all features)

| Prediction made | Previous-leg feature available | ROC-AUC | PR-AUC | Precision | Recall | F1 |
|---|---:|---:|---:|---:|---:|---:|
| 60 min before departure | 57.8% | 0.764 | 0.516 | 0.414 | 0.636 | 0.501 |
| 120 min before departure | 35.7% | 0.703 | 0.423 | 0.330 | 0.652 | 0.438 |
| 180 min before departure | 27.2% | 0.682 | 0.394 | 0.307 | 0.668 | 0.420 |
