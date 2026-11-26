# Aviation Analytics: US Airline On-Time Performance

An end-to-end aviation analytics project examining operational performance, flight delays, cancellations and delay prediction across US domestic flights. The project combines Python data preparation, SQL analytical modelling, predictive machine learning and an interactive Power BI report.

The analysis uses **2,303,556 scheduled flights** from four monthly snapshots in 2024: February, June, September and December. These months provide a view across the four seasons; they are not a continuous full-year dataset.

## Project at a glance

| Area | Details |
|---|---|
| Domain | Aviation operations and airline performance |
| Dataset | US Department of Transportation, Bureau of Transportation Statistics (BTS), Airline On-Time Performance |
| Coverage | February, June, September and December 2024 |
| Flights analysed | 2,303,556 scheduled flights |
| Analytical stack | Python, SQL and Power BI |
| Machine learning | Logistic regression, random forest and gradient boosting |
| Prediction target | Departure delay of 15 minutes or more |
| Prediction lead time | 60 minutes before scheduled departure |
| Reporting | Five-page Power BI report |

## Business problem

Flight delays affect passenger experience, airline operating costs, aircraft utilisation and the reliability of airport and route networks. Looking only at an overall delay percentage can hide important differences between carriers, airports, routes, departure times and seasons.

This project investigates where disruption is concentrated, what contributes to delay minutes, how performance changes across the sampled seasons, and whether a flight's departure-delay risk can be estimated before departure.

## Questions explored

- Which airlines have the strongest and weakest on-time arrival performance?
- Which airports and routes experience the highest disruption?
- How do delays vary by month, day of week and scheduled departure time?
- What proportion of delay minutes is attributed to late-arriving aircraft, carrier, National Aviation System, weather and security?
- How do cancellation patterns differ from delay patterns?
- How accurately can departure delays be predicted using information available before a flight departs?

## Selected findings

The following results are calculated from the four sampled months in 2024. They should be interpreted as findings from those monthly snapshots, not as a complete census of every day in 2024.

| Finding | Result | Operational interpretation |
|---|---:|---|
| Flights scheduled | 2,303,556 | Large-scale view of domestic flight operations |
| Completed flights arriving on time | About 80.5% | Roughly one in five completed flights arrived at least 15 minutes late |
| Flights cancelled | 0.80% | Cancellations were relatively infrequent but varied by season and airport |
| Delay minutes attributed to late-arriving aircraft | 39.8% | Aircraft rotation and knock-on delays are important operational factors |
| Delay minutes attributed to carrier causes | 35.4% | Carrier-controlled operations account for a substantial share |
| June on-time arrival | 75.1% | June was the most disrupted of the four sampled months |
| September on-time arrival | 84.5% | September had the strongest on-time arrival performance |

### Airline performance

On-time arrival ranged from **73.5% for Frontier to 86.6% for Republic** in the analysed sample. Among the four largest carriers examined in the business findings, Delta recorded 83.9% on-time arrival, compared with 76.6% for American.

Carrier rankings should be interpreted in the context of network structure, hub exposure, route mix and operating conditions, rather than as a standalone measure of management quality.

### Airport and route disruption

Aspen recorded a 33.1% departure-delay rate among airports meeting the minimum-volume threshold used in the analysis. Dallas/Fort Worth recorded a 25.2% rate and had the highest delay rate among the 15 busiest airports in the sample.

Several of the most delay-prone routes included Aspen or Dallas/Fort Worth, reinforcing the airport-level patterns. Route rankings use a minimum-flight threshold to reduce the influence of very small samples.

### When delays build up

The departure-delay rate increased through the day: 9.3% for departures before 9 a.m., compared with 28.7% for departures from 8 p.m. onward. This pattern is consistent with delays propagating through aircraft rotations as the operating day progresses.

### Delay prediction

The prediction task estimates whether a non-cancelled flight will depart at least 15 minutes late, using information available **60 minutes before scheduled departure**. A chronological train, validation and test split was used to reduce the risk of temporal leakage.

| Model | ROC-AUC | PR-AUC | Precision | Recall | F1 |
|---|---:|---:|---:|---:|---:|
| Logistic regression | 0.734 | 0.457 | 0.342 | 0.728 | 0.466 |
| Random forest | 0.754 | 0.492 | 0.373 | 0.706 | 0.488 |
| Gradient boosting | **0.764** | **0.516** | **0.414** | 0.636 | **0.501** |

The gradient-boosting model produced the strongest overall test metrics among the evaluated models. The test set was December 2024, a month not used for model training. These results are an evaluation on the available sample, not a claim of production-ready airline forecasting performance.

## Methodology and workflow

1. **Data acquisition:** obtain BTS Airline On-Time Performance data for the selected months.
2. **Data preparation:** clean and standardise fields, handle flight-time values, remove exact duplicates where present, recompute delay indicators and record data-quality checks.
3. **Analytical modelling:** build a relational analytical model and use SQL to examine airline, airport, route, timing and delay-cause performance.
4. **Predictive modelling:** compare baseline approaches with logistic regression, random forest and gradient boosting using a chronological split and pre-departure features.
5. **Reporting:** bring the analytical outputs into Power BI to present operational performance and findings.

Detailed documentation is available in the [documentation folder](documentation/), including the [methodology](documentation/methodology.md), [business findings](documentation/business_findings.md), [data quality report](documentation/data_quality_report.md), [model results](documentation/model_results.md) and [ablation and lead-time results](documentation/ablation_results.md).

## Power BI dashboard

The repository includes the Power BI report file and dashboard screenshots.

| Page | Focus |
|---|---|
| 1 | Executive Aviation Overview |
| 2 | Airline Performance |
| 3 | Airport Performance |
| 4 | Route and Delay Analysis |
| 5 | Delay Causes and Operational Intelligence |

### Dashboard previews

![Power BI dashboard – Page 1](screenshots/Page%201.png)

![Power BI dashboard – Page 2](screenshots/Page%202.png)

![Power BI dashboard – Page 3](screenshots/Page%203.png)

![Power BI dashboard – Page 4](screenshots/Page%204.png)

![Power BI dashboard – Page 5](screenshots/Page%205.png)

## Technology stack

- **Python:** data acquisition, cleaning, preparation, feature engineering and machine learning.
- **SQL:** analytical data modelling, validation and operational analysis.
- **Power BI:** data modelling, DAX measures, interactive reporting and visual analysis.
- **Machine learning:** logistic regression, random forest and gradient boosting.
- **Documentation:** Markdown for methodology, data quality, findings and model evaluation.

## Repository structure

\`\`\`text
aviation-analytics/
├── data/
│   ├── raw/
│   ├── processed/
│   └── sample/
├── documentation/
│   ├── ablation_results.md
│   ├── business_findings.md
│   ├── data_quality_report.md
│   ├── methodology.md
│   └── model_results.md
├── models/
├── powerbi/
│   ├── Background Templates/
│   ├── aviation_dashboard.pbix
│   ├── aviation_theme.json
│   └── dashboard_spec.md
├── python/
├── screenshots/
├── sql/
└── README.md
\`\`\`

## Reproducibility and project files

The Python scripts, SQL scripts, Power BI report, dashboard screenshots and supporting documentation are organised in this repository. Some large source or intermediate data files are not committed to GitHub because of file-size constraints. Refer to the data availability note below if you need access to those files.

For the analytical design and implementation details, start with the methodology and dashboard specification documents. The exact data files required by individual scripts may need to be supplied separately.

## Data Availability & Access

Due to GitHub's file size limitations, certain large source data files used in this analysis have not been included in this repository.

The repository contains the project documentation, analytical workflows, code, and supporting materials necessary to understand the methodology and findings.

**Additional project data files are available upon request.**

For access or further information, please contact:

📧 **prasadvastrad220@gmail.com**
