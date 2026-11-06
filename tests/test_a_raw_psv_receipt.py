"""Exercise v1 time boundaries in the standalone receipt implementation."""
from pathlib import Path
import sys

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from verify_a_raw_psv_receipt import HEADER, inspect_hourly


def hourly_bytes(first_positive=None, start=1, end=24, omitted=None):
    rows = ["|".join(HEADER)]
    for hour in range(start, end + 1):
        if hour == omitted:
            continue
        fields = ["NaN"] * len(HEADER)
        fields[0] = str(hour)  # A different HR after hour12 detects future leakage.
        fields[34], fields[35] = "60", "1"
        fields[39] = str(hour)
        fields[40] = str(int(first_positive is not None and hour >= first_positive))
        rows.append("|".join(fields))
    return ("\n".join(rows) + "\n").encode("utf-8")


@pytest.mark.parametrize("first_positive,onset,reason,label", [
    (6, 12, "onset_at_or_before_12", None),
    (7, 13, "included", 1),
    (18, 24, "included", 1),
    (19, 25, "included", 0),
    (None, None, "included", 0),
])
def test_onset_boundaries(first_positive, onset, reason, label):
    row, _ = inspect_hourly(hourly_bytes(first_positive), "A_test", "A", "test.psv")
    assert row["recovered_onset_hour"] == onset
    assert row["reason"] == reason
    assert row["y_true"] == label


def test_first_record_positive_has_no_exact_recovered_onset():
    row, features = inspect_hourly(hourly_bytes(1), "A_test", "A", "test.psv")
    assert row["reason"] == "first_observation_positive"
    assert row["censoring_status"] == "left_censored_first_observation_positive"
    assert row["recovered_onset_hour"] is None
    assert row["y_true"] is None
    assert features is None


def test_delayed_start_remains_excluded():
    row, features = inspect_hourly(hourly_bytes(18, start=2), "A_test", "A", "test.psv")
    assert row["reason"] == "missing_initial_hours"
    assert row["first_hour"] == 2
    assert row["y_true"] is None
    assert features is None


def test_last_input_is_hour12_and_missing_is_not_imputed():
    row, features = inspect_hourly(hourly_bytes(), "A_test", "A", "test.psv")
    assert row["feature_max_source_hour"] == 12
    assert len(features) == 36
    assert features[0] == 12
    assert np.isnan(features[1])


def test_gap_is_invalid_not_repaired():
    row, features = inspect_hourly(hourly_bytes(18, omitted=6), "A_test", "A", "test.psv")
    assert row["reason"] == "invalid_hourly_records"
    assert features is None
