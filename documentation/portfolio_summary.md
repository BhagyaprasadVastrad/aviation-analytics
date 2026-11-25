# Portfolio Summary

Text for the GitHub repository, LinkedIn and resume. Numbers come from the four-quarter run of 2024 BTS data.

## GitHub repository description (one line)

Analysis of 2.3M US domestic flights (BTS, four quarters of 2024): DuckDB star schema, 28 SQL queries, a five-page Power BI dashboard, seasonal findings and a model that predicts 15+ minute departure delays 60 minutes ahead.

Suggested topics: `data-analysis`, `sql`, `duckdb`, `python`, `scikit-learn`, `aviation`, `power-bi`

## Resume bullets (Project section)

**US Airline Delay Analysis and Prediction** | Python, SQL, DuckDB, Power BI, DAX, scikit-learn

- Loaded and cleaned 2.3 million US domestic flights from BTS (February, June, September, December 2024), logged data quality issues, and built a five-table star schema in DuckDB.
- Wrote 28 SQL queries covering airline, airport, route, seasonal and delay-cause analysis, plus validation checks for orphan keys, duplicates and logical consistency.
- Showed that late-arriving aircraft cause 40% of delay minutes: a previous flight arriving 15 to 59 minutes late makes the next departure late 50% of the time, against 9% when it arrives early.
- Measured seasonality: on-time arrival was 75.1% in June against 84.5% in September, and late departures rise from 7% at 6am to 30% at 8pm in every season.
- Built a gradient boosting model that predicts 15+ minute departure delays 60 minutes before takeoff. Trained on February and June, tested on December: ROC-AUC 0.764, PR-AUC 0.516, 2.4 times the no-skill baseline.

- Built a five-page Power BI dashboard on the star schema with 41 DAX measures, covering on-time performance, airline and airport rankings by season, routes and timing, and delay causes.

Shorter version (four bullets): use the first, third, fifth and sixth. For a Power BI role, lead with the dashboard bullet.

## LinkedIn project description

I analysed 2.3 million US domestic flights from the Bureau of Transportation Statistics, using one month from each quarter of 2024 to cover all four seasons. I cleaned the data in Python, built a star schema in DuckDB, and used SQL to answer ten business questions about airline performance, airport disruption, delay causes and seasonality.

Main findings: late-arriving aircraft cause about 40% of delay minutes, delays build through the day in every season, and on-time arrival drops from 84.5% in September to 75.1% in June. I also trained a model that predicts departure delays an hour ahead using only information available at that time, and tested it on a season it had not seen (ROC-AUC 0.764).

I presented the results in a five-page Power BI dashboard built on the same star schema, with DAX measures, a date table and seasonal comparisons of airlines, airports and delay causes.

Tools: Python, pandas, SQL, DuckDB, scikit-learn, Power BI, DAX.

## Interview talking points

- **Avoiding leakage.** The model uses only information known 60 minutes before departure. Actual times, taxi times and delay-cause columns are excluded, and the previous flight of the same aircraft is used only if it had already landed.
- **Honest evaluation.** The split is by whole months, so the test month (December) is a season the model never trained on. Accuracy is judged by PR-AUC against the no-skill baseline (the delay rate), because most flights are on time.
- **What drives the prediction.** An ablation showed the previous flight of the same aircraft is the biggest single gain, which matches the SQL finding that late aircraft is the largest delay cause.
- **Why four quarters.** One month per quarter captures all four seasons at a manageable size. A single month overstated several results: June alone made American look 12.3 points behind Delta, against 7.3 points across four seasons.
- **A correction made along the way.** An early draft said DFW was the most delayed hub in every season. The monthly breakdown showed it was first in June and December but sixth in February, so the finding was corrected.
- **Checking the dashboard.** Every visual was checked against the SQL results. One chart ranked airports with only a few dozen flights first because it used the plain delay rate; a minimum-volume measure (500 departures) fixed it. The same check caught a stale Top N setting and unreadable heatmap cells.
- **Data quality.** BTS records departure times for some cancelled flights. The cleaner blanks them so they do not distort delay averages (859 flights).

## Before publishing

- Keep the limitations section. It states the four-month scope and the lack of external weather data.
- Save the five dashboard pages as `screenshots/page1.png` to `page5.png` (the README links to those names), and copy `aviation_dashboard.pbix` into the `powerbi/` folder.
