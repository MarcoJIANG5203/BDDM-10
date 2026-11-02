"""Independent hand-worked checks; no implementation-derived expected values."""
import json
from pathlib import Path

import numpy as np
import pytest

from src.conformal import prediction_sets, singleton_predictions
from src.metrics import evaluate, paired_bootstrap
from src.selection import batch_accept


def test_five_patient_hand_calculation():
    fixture = json.loads((Path(__file__).parents[1] / 'reviews' / 'B_hand_calculations.json').read_text())
    ids = np.asarray(fixture['patient_id'])
    y = np.asarray(fixture['y_true'])
    p = np.asarray(fixture['p_mean'])
    sets = prediction_sets(p, fixture['q'])
    assert sets[:, 0].tolist() == fixture['set_0']
    assert sets[:, 1].tolist() == fixture['set_1']
    pool, pred = singleton_predictions(sets)
    uncertainty = np.minimum(p, 1 - p)
    acc2 = batch_accept(ids, pool, uncertainty, .60)
    acc4 = batch_accept(ids, pool, fixture['p_std'], .60)
    assert set(ids[acc2]) == {'P1', 'P2', 'P5'}
    assert set(ids[acc4]) == {'P1', 'P2', 'P4'}
    m2 = evaluate(y, p, pred, sets, acc2)
    m4 = evaluate(y, p, pred, sets, acc4)
    assert m4['coverage'] == .4
    assert m4['selective_risk'] == pytest.approx(1 / 3)
    assert m2['selective_risk'] == pytest.approx(2 / 3)
    assert m4['selective_risk'] - m2['selective_risk'] == pytest.approx(-1 / 3)
    assert m4['dangerous_miss'] == .5
    assert m4['negative_residual'] == .5
    assert np.array_equal(batch_accept(ids, pool, uncertainty, .8),
                          batch_accept(ids, pool, fixture['p_std'], .8))


def test_two_patient_bootstrap_has_analytic_zero_to_one_interval():
    # Each resample has two draws and accepts one. A ranks the erroneous
    # patient first; B ranks the correct patient first. Identical draws yield
    # difference 0, mixed draws yield 1: all resamples have nonempty acceptance.
    result = paired_bootstrap(['error', 'correct'], [1, 0], [0, 0], [True, True],
                              [0, 1], [1, 0], .5, 2000, 918)
    assert result['valid'] == 2000
    assert result['invalid'] == 0
    assert result['ci_low'] == 0
    assert result['ci_high'] == 1
