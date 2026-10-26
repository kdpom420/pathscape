"""Provider-independent phase-conditioned monthly core."""
import numpy as np
import pandas as pd
from .validation import validate_monthly


def pathscape_core(df, variables, min_years=10):
    data = validate_monthly(df, variables, min_years)
    results = []
    for variable in variables:
        part = data[["year", "month", variable]].rename(columns={variable: "X"}).copy()
        annual = part.groupby("year")["X"]
        med = annual.transform("median")
        q25 = annual.transform(lambda x: np.quantile(x, 0.25, method="linear"))
        q75 = annual.transform(lambda x: np.quantile(x, 0.75, method="linear"))
        iqr = q75 - q25
        if (iqr <= 0).any():
            bad = part.loc[iqr <= 0, "year"].unique().tolist()
            raise ValueError(f"{variable}: zero annual IQR in {bad}")
        part["Z"] = (part.X - med) / iqr
        part["C"] = part.groupby("month")["Z"].transform("median")
        part["p"] = part.Z - part.C
        part["D"] = part.p.abs()
        part["S"] = (part.groupby("month")["D"].rank(method="max", ascending=False)
                     / part.groupby("month")["D"].transform("size"))
        part["R"] = -np.log(part.S)
        part["pR"] = part.p * part.R
        part["DR"] = part.D * part.R
        part["variable"] = variable
        results.append(part)
    return pd.concat(results, ignore_index=True)[
        ["year", "month", "variable", "X", "Z", "C", "p", "D", "S", "R", "pR", "DR"]
    ]
