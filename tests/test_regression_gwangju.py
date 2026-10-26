
import hashlib
from pathlib import Path

import numpy as np
import pandas as pd

from pathscape import pathscape_core

FIXTURE = (
    Path(__file__).parent
    / "data"
    / "gwangju_2001_2025_monthly.csv"
)

EXPECTED_SHA = (
    "72b6ba87029a49d536160367743fd9bc1a37317495738f0c12e070b767b91804"
)

VARIABLES = ["TEMP", "RH", "WS"]

# Frozen reference values from the original v0.1 output.
REFERENCE = {
    (2018, 7, "TEMP"): (0.16711, 3.21888, 0.53791),
    (2018, 8, "TEMP"): (0.22469, 2.52573, 0.56751),
    (2018, 9, "TEMP"): (0.01339, 0.08338, 0.00112),
    (2018, 7, "RH"): (0.85150, 2.52573, 2.15067),
    (2018, 8, "RH"): (-1.74656, 3.21888, -5.62197),
    (2018, 9, "RH"): (1.71307, 3.21888, 5.51416),
    (2018, 7, "WS"): (-0.68312, 3.21888, -2.19888),
    (2018, 8, "WS"): (0.26562, 0.27444, 0.07290),
    (2018, 9, "WS"): (0.27376, 0.51083, 0.13984),
}


def load_fixture():
    return pd.read_csv(FIXTURE)


def test_frozen_dataset_checksum():
    actual = hashlib.sha256(FIXTURE.read_bytes()).hexdigest()
    assert actual == EXPECTED_SHA


def test_frozen_dataset_structure():
    df = load_fixture()

    assert len(df) == 300
    assert df.year.nunique() == 25
    assert df.year.min() == 2001
    assert df.year.max() == 2025

    assert list(df.columns) == [
        "year", "month", "TEMP", "RH", "WS"
    ]

    assert not df.isna().any().any()
    assert not df.duplicated(["year", "month"]).any()

    for year, group in df.groupby("year"):
        assert sorted(group.month.tolist()) == list(range(1, 13))


def test_gwangju_core_shape():
    core = pathscape_core(load_fixture(), VARIABLES)

    assert len(core) == 900
    assert set(core.variable) == set(VARIABLES)

    assert np.isfinite(
        core[["X", "Z", "C", "p", "D", "S", "R", "pR", "DR"]]
        .to_numpy(dtype=float)
    ).all()

    assert np.allclose(
        core["D"].to_numpy(),
        np.abs(core["p"].to_numpy()),
        rtol=0,
        atol=1e-12
    )

    assert np.allclose(
        core["pR"].to_numpy(),
        (core["p"] * core["R"]).to_numpy(),
        rtol=0,
        atol=1e-12
    )


def test_gwangju_2018_regression():
    core = pathscape_core(load_fixture(), VARIABLES)

    indexed = core.set_index(
        ["year", "month", "variable"]
    )

    for key, expected in REFERENCE.items():
        actual = indexed.loc[
            key, ["p", "R", "pR"]
        ].to_numpy(dtype=float)

        np.testing.assert_allclose(
            actual,
            expected,
            rtol=0,
            atol=1e-4,
            err_msg=f"Regression mismatch: {key}"
        )


def test_gwangju_core_deterministic():
    df = load_fixture()

    a = pathscape_core(df, VARIABLES)
    b = pathscape_core(df, VARIABLES)

    pd.testing.assert_frame_equal(a, b)


def test_gwangju_2018_rh_reversal():
    core = pathscape_core(load_fixture(), VARIABLES)

    rh = (
        core[
            (core.year == 2018)
            & (core.month.isin([7, 8, 9]))
            & (core.variable == "RH")
        ]
        .sort_values("month")
    )

    assert len(rh) == 3
    assert rh["p"].tolist()[0] > 0
    assert rh["p"].tolist()[1] < 0
    assert rh["p"].tolist()[2] > 0

    assert rh["pR"].tolist()[0] > 0
    assert rh["pR"].tolist()[1] < 0
    assert rh["pR"].tolist()[2] > 0
