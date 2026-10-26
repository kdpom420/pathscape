import pytest
from pathscape import pathscape_core

VARS = ["TEMP", "RH", "WS"]

@pytest.mark.parametrize("change", [
    lambda x: x[x.year != 2010],
    lambda x: x[~((x.year == 2005) & (x.month == 6))],
    lambda x: __import__('pandas').concat([x, x.iloc[[0]]]),
    lambda x: x.assign(month=x.month.where(x.month != 12, 13)),
    lambda x: x.assign(TEMP=x.TEMP.where(x.month != 3, float('nan'))),
])
def test_invalid_monthly_rejected(monthly, change):
    with pytest.raises(ValueError):
        pathscape_core(change(monthly), VARS)

def test_zero_iqr_rejected(monthly):
    monthly.loc[monthly.year == 2005, "TEMP"] = 7.0
    with pytest.raises(ValueError, match="IQR"):
        pathscape_core(monthly, VARS)
