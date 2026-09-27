import pandas as pd


def _numeric(df, column):
    if column not in df.columns:
        return None
    return pd.to_numeric(df[column], errors="coerce")


def inspect_dataset(df):
    return {
        "rows": int(len(df)),
        "columns": list(df.columns),
        "data_types": {str(k): str(v) for k, v in df.dtypes.items()},
        "missing_values": {str(k): int(v) for k, v in df.isna().sum().items()},
    }


def numeric_statistics(df, columns=None):
    numeric = df.select_dtypes(include="number")
    if columns:
        valid = [c for c in columns if c in numeric.columns]
        numeric = numeric[valid]
    if numeric.empty:
        return {"error": "No numeric columns available."}
    return numeric.describe().round(3).to_dict()


def missing_values(df):
    result = df.isna().sum().sort_values(ascending=False)
    result = result[result > 0]
    return {str(k): int(v) for k, v in result.items()}


def calculate_total(df, value_column):
    values = _numeric(df, value_column)
    if values is None:
        return {"error": f"Column '{value_column}' not found."}
    return {
        "column": value_column,
        "total": round(float(values.sum()), 2),
        "average": round(float(values.mean()), 2),
        "maximum": round(float(values.max()), 2),
        "minimum": round(float(values.min()), 2),
        "valid_values": int(values.notna().sum()),
    }


def group_sum(df, group_column, value_column, limit=20):
    if group_column not in df.columns:
        return {"error": f"Column '{group_column}' not found."}
    values = _numeric(df, value_column)
    if values is None:
        return {"error": f"Column '{value_column}' not found."}
    temp = pd.DataFrame({"group": df[group_column], "value": values})
    result = (
        temp.groupby("group", dropna=False)["value"]
        .sum()
        .sort_values(ascending=False)
        .head(limit)
    )
    return {str(k): round(float(v), 2) for k, v in result.items()}


def group_mean(df, group_column, value_column, limit=20):
    if group_column not in df.columns:
        return {"error": f"Column '{group_column}' not found."}
    values = _numeric(df, value_column)
    if values is None:
        return {"error": f"Column '{value_column}' not found."}
    temp = pd.DataFrame({"group": df[group_column], "value": values})
    result = (
        temp.groupby("group", dropna=False)["value"]
        .mean()
        .sort_values(ascending=False)
        .head(limit)
    )
    return {str(k): round(float(v), 2) for k, v in result.items()}


def top_products(df, product_column, value_column, limit=10, ascending=False):
    result = group_sum(df, product_column, value_column, limit=max(limit, 100))
    if "error" in result:
        return result
    items = sorted(result.items(), key=lambda x: x[1], reverse=not ascending)[:limit]
    return dict(items)


def time_series(df, date_column, value_column, period):
    if date_column not in df.columns:
        return {"error": f"Column '{date_column}' not found."}
    values = _numeric(df, value_column)
    if values is None:
        return {"error": f"Column '{value_column}' not found."}
    dates = pd.to_datetime(df[date_column], errors="coerce")
    temp = pd.DataFrame({"date": dates, "value": values}).dropna()
    if temp.empty:
        return {"error": "No valid dates and numeric values were found."}
    if period == "month":
        temp["period"] = temp["date"].dt.to_period("M").astype(str)
    elif period == "year":
        temp["period"] = temp["date"].dt.year.astype(str)
    else:
        return {"error": f"Unsupported period: {period}"}
    result = temp.groupby("period")["value"].sum().sort_index()
    return {str(k): round(float(v), 2) for k, v in result.items()}


def monthly_sales(df, date_column="Order Date", value_column="Sales"):
    return time_series(df, date_column, value_column, "month")


def yearly_sales(df, date_column="Order Date", value_column="Sales"):
    return time_series(df, date_column, value_column, "year")


def value_by_date(df, date_column, value_column, limit=20):
    data = time_series(df, date_column, value_column, "month")
    if "error" in data:
        return data
    return dict(sorted(data.items(), key=lambda x: x[1], reverse=True)[:limit])


def dataset_summary(df, value_column=None, date_column=None):
    summary = {
        "rows": int(len(df)),
        "columns": int(len(df.columns)),
        "column_names": list(df.columns),
        "numeric_columns": list(df.select_dtypes(include="number").columns),
        "categorical_columns": list(df.select_dtypes(include=["object", "category"]).columns),
        "missing_cells": int(df.isna().sum().sum()),
    }
    if value_column and value_column in df.columns:
        summary["value_summary"] = calculate_total(df, value_column)
    if date_column and date_column in df.columns:
        dates = pd.to_datetime(df[date_column], errors="coerce").dropna()
        if not dates.empty:
            summary["date_range"] = {
                "start": str(dates.min().date()),
                "end": str(dates.max().date()),
                "valid_dates": int(len(dates)),
            }
    for column in ["Product Name", "Customer Name", "Category", "Region", "State", "City", "Segment"]:
        if column in df.columns:
            summary[f"unique_{column.lower().replace(' ', '_')}"] = int(df[column].nunique(dropna=True))
    return summary


def correlation(df, columns=None):
    numeric = df.select_dtypes(include="number")
    if columns:
        valid = [c for c in columns if c in numeric.columns]
        numeric = numeric[valid]
    if numeric.shape[1] < 2:
        return {"error": "At least two numeric columns are required."}
    return numeric.corr().round(3).to_dict()
