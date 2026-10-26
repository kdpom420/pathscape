"""Strict monthly input validation."""
import numpy as np
import pandas as pd


def validate_monthly(df, variables, min_years=10):
    variables = list(variables)
    if not variables or len(variables) != len(set(variables)):
        raise ValueError("Provide unique variable names (at least one).")
    required = ["year", "month", *variables]
    missing = set(required) - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns: {sorted(missing)}")
    if df.empty:
        raise ValueError("Input is empty.")
    data = df[required].copy()
    try:
        for col in required:
            data[col] = pd.to_numeric(data[col], errors="raise")
    except (ValueError, TypeError) as exc:
        raise ValueError("Non-numeric input.") from exc
    if not np.isfinite(data.to_numpy(dtype=float)).all():
        raise ValueError("Missing or non-finite values.")
    for col in ("year", "month"):
        if not (data[col] == np.floor(data[col])).all():
            raise ValueError(f"{col} must be integral.")
        data[col] = data[col].astype(int)
    if not data.month.between(1, 12).all():
        raise ValueError("Month must be 1..12.")
    if data.duplicated(["year", "month"]).any():
        raise ValueError("Duplicate year-month observations.")
    years = np.sort(data.year.unique())
    if len(years) < min_years:
        raise ValueError(f"At least {min_years} complete years required.")
    if not np.array_equal(years, np.arange(years[0], years[-1] + 1)):
        raise ValueError("Years must be consecutive.")
    for year in years:
        months = np.sort(data.loc[data.year == year, "month"].to_numpy())
        if not np.array_equal(months, np.arange(1, 13)):
            raise ValueError(f"Incomplete monthly observations: {year}.")
    return data.sort_values(["year", "month"]).reset_index(drop=True)
