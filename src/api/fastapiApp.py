import pandas as pd
from fastapi import FastAPI, HTTPException, Query


S3_BASE_PATH = "s3://mortgage-risk-api/api"

TABLE_PATHS = {"summary": f"{S3_BASE_PATH}/core_portfolio_findings",
                "business_findings": f"{S3_BASE_PATH}/final_business_findings",
                "states": f"{S3_BASE_PATH}/state_findings",
                "segments": f"{S3_BASE_PATH}/segment_findings",
                "vintages": f"{S3_BASE_PATH}/vintage_findings",
                "prepayment": f"{S3_BASE_PATH}/early_prepay_findings",
                "watchlist_30d": f"{S3_BASE_PATH}/transition_30d_watchlist",
                "watchlist_distress": f"{S3_BASE_PATH}/distress_persistence_watchlist",
                "risk_ladder_credit": f"{S3_BASE_PATH}/credit_risk_ladder",
                "risk_ladder_ltv": f"{S3_BASE_PATH}/ltv_risk_ladder",
                "risk_ladder_dti": f"{S3_BASE_PATH}/dti_risk_ladder"
}

app = FastAPI(title = "Mortgage Credit Risk and Prepayment Intelligence API",
                description = "FastAPI service reading Databricks-published Parquet outputs from S3.",
                version = "1.0.0"
)


def load_parquet_from_s3(table_key):
    path = TABLE_PATHS.get(table_key)

    if not path:
        raise HTTPException(status_code = 404, detail = f"Unknown table key : {table_key}")

    try:
        return pd.read_parquet(path)
    except Exception as exc:
        raise HTTPException(status_code = 500,
                            detail = f"Failed to load data from S3 for {table_key} : {str(exc)}"
        )


@app.get("/")
def root():
    return {"message": "Mortgage Credit Risk and Prepayment Intelligence API is running from EC2 and reading S3 parquet outputs."}

@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/summary")
def get_summary():
    df = load_parquet_from_s3("summary")
    return df.to_dict(orient = "records")

@app.get("/business-findings")
def get_business_findings():
    df = load_parquet_from_s3("business_findings")
    return df.to_dict(orient = "records")

@app.get("/vintages")
def get_vintages():
    df = load_parquet_from_s3("vintages")
    return df.to_dict(orient = "records")


@app.get("/states")
def get_states(top_n: int = Query(5, ge = 1, le = 50)):
    df = load_parquet_from_s3("states")
    df = df.sort_values("share_of_portfolio_delinquent_upb", ascending = False).head(top_n)
    return df.to_dict(orient = "records")

@app.get("/segments")
def get_segments(top_n: int = Query(10, ge = 1, le = 100)):
    df = load_parquet_from_s3("segments")
    df = df.sort_values("share_of_portfolio_delinquent_upb", ascending = False).head(top_n)
    return df.to_dict(orient = "records")


@app.get("/prepayment")
def get_prepayment(top_n: int = Query(10, ge = 1, le = 100)):
    df = load_parquet_from_s3("prepayment")
    df = df.sort_values("prepay_by_month_6_share", ascending = False).head(top_n)
    return df.to_dict(orient = "records")


@app.get("/watchlists/30d")
def get_30d_watchlist(top_n: int = Query(10, ge = 1, le = 100)):
    df = load_parquet_from_s3("watchlist_30d")
    df = df.sort_values("roll_to_60d_rate", ascending = False).head(top_n)
    return df.to_dict(orient = "records")

@app.get("/watchlists/distress")
def get_distress_watchlist(top_n: int = Query(10, ge = 1, le = 100)):
    df = load_parquet_from_s3("watchlist_distress")
    df = df.sort_values("roll_to_90d_plus_rate", ascending = False).head(top_n)
    return df.to_dict(orient = "records")


@app.get("/risk-ladders/credit")
def get_credit_risk_ladder():
    df = load_parquet_from_s3("risk_ladder_credit")
    return df.to_dict(orient = "records")

@app.get("/risk-ladders/ltv")
def get_ltv_risk_ladder():
    df = load_parquet_from_s3("risk_ladder_ltv")
    return df.to_dict(orient = "records")

@app.get("/risk-ladders/dti")
def get_dti_risk_ladder():
    df = load_parquet_from_s3("risk_ladder_dti")
    return df.to_dict(orient = "records")