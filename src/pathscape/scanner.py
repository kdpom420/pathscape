"""Rare-state scanning without charts or provider dependencies."""
import numpy as np
import pandas as pd


def rank_events(core_result, r0=-np.log(0.1)):
    required = {"year", "month", "variable", "R", "DR", "pR"}
    if required - set(core_result.columns):
        raise ValueError(f"Missing fields: {sorted(required - set(core_result.columns))}")
    if core_result.duplicated(["year", "month", "variable"]).any():
        raise ValueError("Duplicate variable observations.")
    temp = core_result.copy()
    temp["rare"] = temp.R >= r0
    ranked = temp.groupby(["year", "month"], as_index=False).agg(
        N_rare=("rare", "sum"), R_sum=("R", "sum"), DR_sum=("DR", "sum"),
        Max_R=("R", "max"), Max_abs_pR=("pR", lambda x: x.abs().max()))
    return ranked.sort_values(["N_rare", "DR_sum", "R_sum"],
                              ascending=[False, False, False]).reset_index(drop=True)


def event_detail(core_result, year, month):
    return core_result.loc[(core_result.year == year) & (core_result.month == month)].copy()
