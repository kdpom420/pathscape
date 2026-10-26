import numpy as np
from pathscape import pathscape_core

VARS = ["TEMP", "RH", "WS"]

def test_core_invariants(core):
    assert len(core) == 360
    np.testing.assert_allclose(core.p, core.Z-core.C)
    np.testing.assert_allclose(core.D, core.p.abs())
    np.testing.assert_allclose(core.R, -np.log(core.S))
    np.testing.assert_allclose(core.pR, core.p*core.R)
    np.testing.assert_allclose(core.DR, core.D*core.R)
    assert core.S.between(0.1, 1).all()
    assert (core.R <= np.log(10)+1e-12).all()
    for (_, _), group in core.groupby(["variable", "month"]):
        assert np.isclose(group.C.iloc[0], np.median(group.Z))
        for row in group.itertuples():
            assert np.isclose(row.S, np.mean(group.D >= row.D))

def test_affine_invariance(monthly):
    a = pathscape_core(monthly, VARS)
    changed = monthly.copy()
    changed["TEMP"] = changed.TEMP*4+100
    b = pathscape_core(changed, VARS)
    aa = a[a.variable == "TEMP"].reset_index(drop=True)
    bb = b[b.variable == "TEMP"].reset_index(drop=True)
    for field in ["Z", "C", "p", "D"]:
        np.testing.assert_allclose(aa[field], bb[field], atol=1e-11)

# Exact empirical ranks can change under floating-point near-ties after affine transforms.
