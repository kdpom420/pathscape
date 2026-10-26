import numpy as np
import pandas as pd
import pytest
from pathscape import pathscape_core

@pytest.fixture
def monthly():
    rows = []
    for year in range(2001, 2011):
        for month in range(1, 13):
            rows.append((year, month,
                         20 + 0.3*(year-2001) + 10*np.sin(month*np.pi/6) + 0.2*(year-2001)*np.cos(month),
                         60 + 12*np.cos(month*np.pi/6) + 0.7*(year-2001)*np.sin(month),
                         2 + 0.3*np.sin(month*np.pi/6) + 0.02*(year-2001)*np.cos(month)))
    return pd.DataFrame(rows, columns=["year", "month", "TEMP", "RH", "WS"])

@pytest.fixture
def core(monthly):
    return pathscape_core(monthly, ["TEMP", "RH", "WS"])
