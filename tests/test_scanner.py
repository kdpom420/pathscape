import numpy as np
from pathscape import rank_events, event_detail

def test_ranking(core):
    ranking = rank_events(core)
    assert len(ranking) == 120
    assert ranking.N_rare.between(0, 3).all()
    assert ranking.N_rare.is_monotonic_decreasing
    first = ranking.iloc[0]
    assert first.N_rare == (event_detail(core, first.year, first.month).R >= -np.log(.1)).sum()
