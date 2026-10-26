import numpy as np
from pathscape import pathscape_trajectory, rank_transitions

def test_trajectory_identity(core):
    motion = pathscape_trajectory(core)
    assert motion.dpR.notna().sum() == 330
    assert motion.loc[motion.month == 1, "dpR"].isna().all()
    np.testing.assert_allclose(motion.dpR.dropna(),
        (motion.position_term+motion.rarity_term).dropna(), atol=1e-11)
    assert len(rank_transitions(motion)) == 110

def test_crossings_are_strict(core):
    motion = pathscape_trajectory(core)
    assert (motion.crossing == (motion.p_prev * motion.p < 0)).all()
