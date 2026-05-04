# Mortgage Credit Risks and Prepayment Intelligence

This project studies real mortgage loan-level data to understand where portfolio risk is building up, which borrower segments are under more stress, how early those patterns show up and how the results can be delivered both to business users and downstream systems.

The final version of the project was built across **Databricks, AWS, Tableau and FastAPI**. The goal was not just to run analysis in a notebook, but to carry the work through a full analytics workflow : ingest raw mortgage files, create an analysis-ready Delta table, run structured risk and prepayment analysis, publish Tableau dashboards and expose the same outputs through a FastAPI service backed by S3 and EC2.

## Project objective

The project focuses on a practical mortgage portfolio question :

**Which parts of the portfolio are contributing most to delinquent exposure, which borrower segments are riskier than others, how do delinquency and prepayment differ across groups and how can those insights be made usable in both dashboards and APIs?**

The data includes :
- origination attributes such as credit score, LTV, DTI, channel, occupancy, property type, state and loan purpose
- monthly performance history such as delinquency status, UPB, loan age, zero-balance codes, modification flags and related servicing fields

## Final architecture

The final implementation is split into clear stages.

### 1. Databricks ingestion
Raw mortgage files were uploaded into a Databricks volume under the `mortgage_risk` catalog. The ingestion notebook reads the raw text files, applies the source column layouts, standardizes field types and writes managed Delta tables :

- `mortgage_risk.analytics.origination_2024`
- `mortgage_risk.analytics.performance_2024`
- `mortgage_risk.analytics.analysis_base_2024`

This creates one analysis-ready Delta foundation instead of repeatedly working from raw text files.

### 2. Databricks analysis
The analysis notebook reads `mortgage_risk.analytics.analysis_base_2024` and performs the main analytical workflow :
- data quality review
- cleaning and standardization
- latest-loan snapshot creation
- portfolio summaries
- state and segment analysis
- transition and roll-rate analysis
- vintage comparisons
- descriptive driver modeling
- final business findings assembly

The final outputs are written back as managed Delta tables in `mortgage_risk.analytics`.

### 3. Export from Databricks to S3
A separate notebook exports selected final analytics tables from Databricks to S3 as Parquet files. This creates a clean handoff layer between Databricks and the API layer.

### 4. FastAPI on EC2
FastAPI runs on EC2 and reads the Parquet outputs from S3. This turns the final analytical outputs into a reusable service rather than leaving them only inside notebooks and dashboards.

### 5. Tableau dashboards
The dashboard layer was built in Tableau Desktop using Databricks-backed tables. A separate extract-based version was then used to publish the final dashboards to Tableau Public for sharing.

## Repository structure

```text
deployment/
  README.md
  mortgage-risk-fastapi.service

notebooks/
  01_ingestion_pipeline.ipynb
  02_analysis_pipeline.ipynb
  03_export_to_s3.ipynb

src/
  api/
    fastapiApp.py

tableau/
  Executive Portfolio Overview.png
  Risk Drivers Dashboard.png
  Vintage and Prepayment Dashboard.png
  Distress Transition Watchlist Dashboard.png
  README.md
```

## Notebook workflow

### `01_ingestion_pipeline.ipynb`
This notebook handles the Databricks ingestion layer.

It :
- defines the raw volume path
- defines the origination and performance column layouts
- reads the quarterly raw text files
- tags each record with its source quarter
- casts dates and numeric fields into usable formats
- joins origination and performance data into an analysis-ready base table
- validates row counts and distinct loan counts
- writes the cleaned outputs to Delta tables

Saved outputs in the notebook show :
- origination row count : `1,048,407`
- performance row count : `14,226,973`
- analysis base row count : `14,226,973`
- distinct joined loans : `1,048,407`

That validation matters because it confirms the joined analysis base is behaving consistently with the underlying loan universe.

### `02_analysis_pipeline.ipynb`
This is the core analytical notebook.

It begins by loading the curated Delta table and then moves through the analysis in a structured order :
- column and schema inspection
- missing-value review
- numeric distribution review
- delinquency and zero-balance cleanup
- creation of analytical flags such as delinquent, serious delinquent, prepaid and modified
- business-friendly risk bands for credit score, LTV and DTI
- latest-loan snapshot construction
- active vs terminated segmentation
- month-6 vintage snapshots
- portfolio and segment summaries
- state concentration analysis
- transition and roll-rate analysis
- event timing analysis
- descriptive driver modeling
- final business findings and presentation tables
- managed Delta output table creation

### `03_export_to_s3.ipynb`
This notebook exports selected final Databricks output tables to S3 in Parquet format.

Those exported tables are the handoff layer used by the FastAPI service.

## Key findings

The analysis is not just descriptive charting. It combines counts, UPB exposure, segment comparisons, transitions and descriptive modeling to build a practical portfolio risk picture.

### 1. Portfolio risk is concentrated rather than broad-based
A relatively small set of states and borrower segments contributes a disproportionate share of delinquent and serious-delinquent UPB.

This matters because portfolio surveillance is more useful when it focuses on concentrated exposure pockets rather than treating the whole portfolio as uniformly risky.

### 2. Credit score is the strongest descriptive risk separator
Delinquent exposure falls sharply as borrower credit quality improves.

This is visible in both the risk ladders and the driver analysis and it remains one of the clearest organizing patterns in the project.

### 3. High LTV materially increases stress
Higher leverage is associated with meaningfully worse delinquent exposure, especially in the `90-100` LTV range.

This matters because leverage reduces the borrower’s margin for error and makes weaker segments more vulnerable.

### 4. High DTI adds clear payment-stress risk
As debt-to-income rises, delinquent exposure rises as well.

This supports the idea that payment burden is not just a background borrower feature; it is an active risk separator in the current portfolio.

### 5. Risk is interaction-based, not single-factor
The riskiest parts of the portfolio are not identified by one variable alone. The stronger pattern comes from combinations such as weaker credit, higher LTV and higher DTI.

This is why the project includes segment-level interaction analysis rather than stopping at one-variable summaries.

### 6. Distress persistence is meaningful once delinquency begins
The transition analysis shows that some already-stressed segments are much more likely to worsen into 90D+ delinquency than to cure.

This adds an operational monitoring layer to the project and moves the work closer to real portfolio surveillance practice.

### 7. Prepayment behaves differently from delinquency
Early prepayment is not simply the opposite of credit risk. Certain higher-credit borrower groups prepay faster, especially in the early months.

This matters because prepayment and delinquency reflect different borrower behaviors and should not be interpreted as the same type of signal.

### 8. Vintage differences need context
Quarter-to-quarter differences in early performance are real, but they should be interpreted alongside borrower-mix changes and coverage depth.

The notebook handles this carefully by checking month-3, month-6 and month-9 comparability before drawing conclusions.

### 9. The portfolio still carries meaningful active exposure at risk
The final portfolio summary shows :
- active loans : `953,299`
- active total UPB : `$308.61B`
- delinquent UPB share : `1.24%`
- serious delinquent UPB share : `0.39%`

These metrics anchor the rest of the analysis in exposure terms, not only loan counts.

## Tableau dashboards

The final Tableau layer turns the analysis into four business-facing dashboards.

### Executive Portfolio Overview
![Executive Portfolio Overview](tableau/Executive%20Portfolio%20Overview.png)

### Executive Portfolio Overview
This dashboard summarizes :
- active loans
- active total UPB
- delinquent UPB share
- serious delinquent UPB share
- top risk segments
- top states by share of portfolio delinquent UPB

### Risk Drivers Dashboard
This dashboard focuses on :
- credit risk ladder
- LTV risk ladder
- DTI risk ladder

It answers a practical question : which borrower-quality and leverage dimensions separate risk most clearly?

### Vintage and Prepayment Dashboard
This dashboard combines :
- vintage delinquency comparison
- early prepayment by credit band and loan purpose

It shows how early behavior differs across cohorts and borrower groups.

### Distress Transition Watchlist Dashboard
This dashboard surfaces :
- 30D transition watchlist
- 60D to 90D+ distress watchlist

This is the most operational dashboard in the project and is closest to a surveillance workflow.

Tableau Public :
- https://public.tableau.com/app/profile/bhavik.patwa/vizzes

## FastAPI service

The API exposes the same analytical outputs programmatically.

It runs on EC2 and reads Parquet outputs from S3.

### FastAPI App Screenshot
![FastAPI App Preview](src/api/FastAPI%20UI%20screenshot.png)

The FastAPI application in this repository is :
- `src/api/fastapiApp.py`

Available routes include :
- `/health`
- `/summary`
- `/docs`
- `/business-findings`
- `/vintages`
- `/states`
- `/segments`
- `/prepayment`
- `/watchlists/30d`
- `/watchlists/distress`
- `/risk-ladders/credit`
- `/risk-ladders/ltv`
- `/risk-ladders/dti`

Some ranked endpoints support `top_n` query parameters so the service can return shorter business-facing result sets.

## AWS and deployment

AWS is used in two practical ways in the final version.

### S3
S3 serves as the handoff layer between Databricks and FastAPI. Databricks writes selected final analytics tables to S3 as Parquet files and the API reads those Parquet outputs.

### EC2
FastAPI is hosted on EC2 and managed as a background service through systemd.

Deployment artifacts included in this repository :
- `deployment/mortgage-risk-fastapi.service`
- `deployment/README.md`

These capture the EC2-side process used to install dependencies, test the app manually and run it as a persistent service.

## Security and privacy

This repository intentionally excludes :
- private keys
- secrets
- credentials
- environment files containing sensitive values
- raw source mortgage files

The included notebooks, API code, dashboard screenshots and deployment materials are meant to demonstrate proof of work without exposing infrastructure access details.

## Why this project matters

It shows a full analytics delivery chain :
- cloud-based ingestion and curated storage
- analytical modeling and business interpretation
- dashboard delivery for non-technical users
- API delivery for downstream systems
- AWS-based operational setup for serving results

That combination is the main value of the project.

## Project links

- GitHub repository : https://github.com/Bhavik-Patwa/Mortgage-Credit-Risks-and-Prepayment-Intelligence
- Tableau Public dashboards : https://public.tableau.com/app/profile/bhavik.patwa/vizzes