"""Within-year transitions and exact ordered pR decomposition."""
import numpy as np
import pandas as pd


def pathscape_trajectory(core_result):
    required = {"year", "month", "variable", "p", "R", "pR"}
    if required - set(core_result.columns):
        raise ValueError(f"Missing fields: {sorted(required - set(core_result.columns))}")
    df = core_result.copy()
    if df.duplicated(["year", "month", "variable"]).any():
        raise ValueError("Duplicate observations.")
    df = df.sort_values(["variable", "year", "month"]).reset_index(drop=True)
    g = df.groupby(["variable", "year"])
    for col in ("p", "R", "pR"):
        df[f"{col}_prev"] = g[col].shift(1)
    df["dp"] = df.p - df.p_prev
    df["dR"] = df.R - df.R_prev
    df["dpR"] = df.pR - df.pR_prev
    df["D"] = df.p.abs()
    df["dD"] = df.D - df.p_prev.abs()
    df["position_term"] = df.R_prev * df.dp
    df["rarity_term"] = df.p * df.dR
    df["decomp_error"] = df.dpR - df.position_term - df.rarity_term
    if df.decomp_error.dropna().abs().max() > 1e-10:
        raise AssertionError("pR decomposition identity failed.")
    df["crossing"] = (df.p_prev * df.p < 0).fillna(False)
    df["motion_type"] = np.select(
        [df.p_prev.isna(), df.crossing, df.dD > 1e-10, df.dD < -1e-10],
        ["START", "CROSSING", "OUTWARD", "INWARD"], default="STABLE")
    df["rarity_type"] = np.select(
        [df.R_prev.isna(), df.dR > 1e-10, df.dR < -1e-10],
        ["START", "RARER", "COMMONER"], default="UNCHANGED")
    return df


def rank_transitions(trajectory):
    df = trajectory.loc[trajectory.dpR.notna()].copy()
    for source, target in [("dpR", "abs_dpR"), ("position_term", "abs_position_term"),
                           ("rarity_term", "abs_rarity_term")]:
        df[target] = df[source].abs()
    ranked = df.groupby(["year", "month"], as_index=False).agg(
        Total_abs_dpR=("abs_dpR", "sum"), Position_abs_sum=("abs_position_term", "sum"),
        Rarity_abs_sum=("abs_rarity_term", "sum"), Crossings=("crossing", "sum"))
    return ranked.sort_values("Total_abs_dpR", ascending=False).reset_index(drop=True)
