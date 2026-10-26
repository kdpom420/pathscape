# Pathscape

**Phase-conditioned path landscapes and signed rarity-weighted trajectories for monthly time series.**

Pathscape retains the original observations while building a shared, month-conditioned reference path. It describes where each observation lies relative to that path, how unusual its *distance* is among observations from the same calendar month, and how the signed, rarity-weighted position changes over time.

**Version:** 0.1.1  
**Research note:** [*Phase-Conditioned Path Landscapes and Signed Rarity-Weighted Vectors for Multivariate Time-Series Exploration*](https://doi.org/10.5281/zenodo.23588842)

> **Scope:** An exploratory, descriptive analysis toolkit—not a forecasting model, hypothesis test, or causal inference method.

## Installation

Python 3.10+ is required. From the repository root:

```bash
python -m pip install -e '.[test,nasa]'
python -m pytest -q -m 'not network'
```

For a built wheel, use its actual location:

```bash
python -m pip install dist/pathscape-0.1.1-py3-none-any.whl
```

In Google Colab, reinstall from a persistent Google Drive copy after a runtime reset:

```python
from google.colab import drive
drive.mount('/content/drive')
%pip install -q /content/drive/MyDrive/Pathscape/dist/pathscape-0.1.1-py3-none-any.whl
```

The NASA POWER adapter requires `requests` (`python -m pip install requests`) when installing only the base wheel.

## Quick start

Input is a wide monthly `pandas.DataFrame` with `year`, `month`, and one or more numeric variable columns. For example:

```python
from pathscape import (
    pathscape_core,
    rank_events,
    event_detail,
    pathscape_trajectory,
    rank_transitions,
)
from pathscape.datasets import load_nasa_gwangju

raw = load_nasa_gwangju(start=2001, end=2025)
core = pathscape_core(raw, ["TEMP", "RH", "WS"])

print(core.head())
print(rank_events(core).head(10))
print(event_detail(core, 2018, 7))

trajectory = pathscape_trajectory(core)
print(rank_transitions(trajectory).head(10))
```

`load_nasa_gwangju` is an optional convenience adapter. The mathematical Core accepts your own monthly DataFrame and does not require an internet connection.

## Method

For each variable independently, and for each year \(y\) and calendar month \(m\):

**1. Annual robust normalization**

$$
M_y = \mathrm{median}_m X_{y,m}, \qquad
IQR_y = Q_{0.75}(X_{y,\cdot}) - Q_{0.25}(X_{y,\cdot}), \qquad
Z_{y,m} = \frac{X_{y,m} - M_y}{IQR_y}.
$$

Quantiles use NumPy's default linear interpolation. Years with zero annual IQR are invalid.

**2. Shared calendar-month reference path**

$$
C_m = \mathrm{median}_y Z_{y,m}, \qquad
p_{y,m} = Z_{y,m} - C_m, \qquad
D_{y,m} = |p_{y,m}|.
$$

**3. Empirical month-conditioned rarity**

$$
S_m(d) = \frac{\#\{y: D_{y,m} \ge d\}}{N}, \qquad
R_{y,m} = -\ln S_m(D_{y,m}).
$$

Ties are included in the survival count. This version uses the same reference years for annual normalization, construction of $C_m$, and evaluation of $S_m$. Rarity is therefore **in-sample**;   
it is not an out-of-sample anomaly probability. For $N$ reference years, $0 \le R \le \ln N$.

**4. Signed and unsigned rarity-weighted position**

$$
pR_{y,m} = p_{y,m} R_{y,m}, \qquad
DR_{y,m} = D_{y,m} R_{y,m}.
$$

`pR` preserves the sign of the deviation; `DR` measures its unsigned rarity-weighted magnitude. Neither replaces the original `X`.

## Trajectory and decomposition

Transitions are calculated **within each year**, from February through December. January starts a new path; December-to-January transitions are not included in v0.1.1.

$$
\Delta p = p_t-p_{t-1},\qquad
\Delta R = R_t-R_{t-1},\qquad
\Delta(pR) = p_tR_t-p_{t-1}R_{t-1}.
$$

The following ordered algebraic identity is exact (up to floating-point precision):

$$
\Delta(pR) = R_{t-1}\Delta p + p_t\Delta R.
$$

The two terms are labeled `position_term` and `rarity_term`. They are **not independent causal effects**. Since each month has its own empirical reference distribution, changes in `R` can reflect both a change in distance and a change in calendar-month reference.

## Event scanning

`rank_events(core)` ranks year-month events by:

1. Number of variables with $R \ge -\ln(0.1)$ (default threshold);
2. Sum of `DR` across variables;
3. Sum of `R` across variables.

This is a descriptive ranking. Simultaneously large marginal `R` values do **not** establish a calibrated joint-event probability or statistical significance.

`rank_transitions(trajectory)` ranks year-month transitions by the sum across variables of `abs(dpR)`.

## Input contract

- At least **10 consecutive complete calendar years**, with all 12 months in each year.
- Exactly one observation per `(year, month)` and no missing or non-finite values in analyzed variables.
- Each analyzed variable must have a nonzero annual IQR in every year.
- The Core processes variables separately before comparing their results; their physical units and original values remain available.
- Outputs depend on the reference years selected. Changing the reference period can change `C`, `R`, `pR`, and rankings.

## Reproducibility

The v0.1.1 offline regression fixture contains NASA POWER monthly observations for Gwangju, Republic of Korea (2001–2025; `TEMP`/`RH`/`WS`, 300 months), stored at:

```text
tests/data/gwangju_2001_2025_monthly.csv
```

Frozen CSV SHA-256:

```text
72b6ba87029a49d536160367743fd9bc1a37317495738f0c12e070b767b91804
```

Regression tests compare the nine July–September 2018 variable-month cases against fixed, previously observed `p`, `R`, and `pR` values (rounded to five decimals; absolute tolerance `1e-4`). Other tests verify fixture integrity, shape, deterministic computation, and the 2018 relative-humidity sign reversal.

```bash
python -m pytest -q -m 'not network'
```

The live NASA POWER integration test is separate:

```bash
python -m pytest -q -m network
```

A live-source test may change when the provider revises data. The frozen fixture is the regression baseline; its checksum identifies the **saved CSV bytes**, not the original HTTP response.

## Data provenance

The optional adapter obtains monthly `T2M`, `RH2M`, and `WS2M` values from the [NASA POWER project](https://power.larc.nasa.gov/), for Gwangju at latitude 35.1595 and longitude 126.8526. API month `13` (annual summary) is excluded from monthly observations. Check NASA POWER's current data-use and attribution terms before distributing the fixture publicly. The source of the data should be credited independently of the software.

## Limitations

- Designed for complete, regular monthly data with annual 12-point normalization; no general missing-data or irregular-time support in this version.
- Empirical rarity resolution is limited by the number of reference years; with 25 years the largest in-sample `R` is `ln(25)`.
- Monthly conditioning controls for calendar-month phase, not for all physical drivers or long-term nonstationarity.
- A high `R` means a rare **absolute deviation from the reference path** within that calendar month; it is not a p-value, calibrated alarm probability, or evidence of causation.
- The initial package includes calculation and ranking functions, not the earlier interactive Colab heatmap dashboard.

## Citation and license

**Research publication**

Pom, K. D. (2026). Phase-Conditioned Path Landscapes and Signed Rarity-Weighted Vectors for Multivariate Time-Series Exploration (Version 1). Zenodo. https://doi.org/10.5281/zenodo.23588842

The research publication is licensed separately under **Creative Commons Attribution-NonCommercial 4.0 International (CC BY-NC 4.0)**.

**Software license**

Copyright (c) 2026 K. D. Pom

Pathscape Python source code is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for the full license text.

The MIT License permits use, modification, distribution, and commercial use, provided that the required copyright and license notices are retained.

## Test Data Attribution

The file `tests/data/gwangju_2001_2025_monthly.csv` contains monthly meteorological observations obtained from the NASA Prediction Of Worldwide Energy Resources (POWER) Project.

- **Source:** NASA Langley Research Center POWER Project
- **Location:** Gwangju, Republic of Korea (35.1595° N, 126.8526° E)
- **Period:** 2001–2025
- **Variables:** T2M, RH2M, WS2M
- **Purpose:** Frozen regression fixture for reproducibility testing of Pathscape v0.1.1
- **Data source:** [NASA POWER](https://power.larc.nasa.gov/)
- **Acquisition date and API version:** Not independently verified for the frozen fixture.

The dataset is redistributed with attribution to NASA POWER. The MIT License applies to the Pathscape software and does not claim ownership of the underlying NASA POWER observations.

NASA POWER provides guidance on acknowledging its data sources and requests notification when data are redistributed to other researchers. See the [NASA POWER Referencing Guide](https://power.larc.nasa.gov/docs/referencing/).

The frozen CSV is provided to support reproducible software testing. Its SHA-256 checksum identifies the saved file contents and does not establish an independently verified record of the original API response.
