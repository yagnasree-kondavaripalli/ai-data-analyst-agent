import pandas as pd

from tools import (
    calculate_total,
    group_sum,
    group_mean,
    missing_values,
    monthly_sales,
    yearly_sales,
    top_products,
)


def sample_df():
    return pd.DataFrame({
        "Order Date": ["2024-01-01", "2024-01-15", "2025-02-01", "2025-02-15"],
        "Region": ["West", "East", "West", "South"],
        "Category": ["A", "B", "A", "B"],
        "Product Name": ["P1", "P2", "P1", "P3"],
        "Sales": [100, 200, 300, 50],
    })


def test_total():
    assert calculate_total(sample_df(), "Sales")["total"] == 650.0


def test_group_sum():
    result = group_sum(sample_df(), "Region", "Sales")
    assert result["West"] == 400.0
    assert list(result)[0] == "West"


def test_group_mean():
    result = group_mean(sample_df(), "Region", "Sales")
    assert result["West"] == 200.0


def test_top_products():
    result = top_products(sample_df(), "Product Name", "Sales", 2)
    assert list(result.keys())[0] == "P1"
    assert result["P1"] == 400.0


def test_time_series():
    monthly = monthly_sales(sample_df(), "Order Date", "Sales")
    yearly = yearly_sales(sample_df(), "Order Date", "Sales")
    assert monthly["2024-01"] == 300.0
    assert yearly["2024"] == 300.0
    assert yearly["2025"] == 350.0


def test_missing_values():
    df = sample_df()
    df.loc[0, "Region"] = None
    result = missing_values(df)
    assert result["Region"] == 1
