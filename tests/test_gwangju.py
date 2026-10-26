"""Optional online smoke/regression test; not a frozen-data reproducibility guarantee."""
import numpy as np
import pytest
from pathscape import pathscape_core, rank_events, pathscape_trajectory
from pathscape.datasets import load_nasa_gwangju

@pytest.mark.network
def test_gwangju_2018_online():
    raw = load_nasa_gwangju()
    core = pathscape_core(raw, ["TEMP", "RH", "WS"])
    assert len(raw) == 300 and len(core) == 900
    july = core[(core.year == 2018) & (core.month == 7)].set_index("variable")
    assert (july.R >= -np.log(.1)).all()
    assert (july.p.loc[["TEMP", "RH"]] > 0).all()
    assert july.p.loc["WS"] < 0
    rh = core[(core.year == 2018) & core.month.isin([7, 8, 9]) & (core.variable == "RH")]
    assert np.array_equal(np.sign(rh.pR), [1, -1, 1])
    assert len(rank_events(core)) == 300
    assert pathscape_trajectory(core).dpR.notna().sum() == 825
