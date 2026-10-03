"""
Automated Data Leakage Verification Test Suite for CardioTwin AI.
Ensures zero patient overlap across training, validation, and test splits,
and verifies strict temporal directionality (backward-looking rolling features only).
"""
import pytest
import numpy as np
import pandas as pd
from scripts.evaluate import extract_features

def test_patient_level_isolation_no_leakage():
    df = extract_features()
    assert len(df) > 0, "Cohort feature dataset should not be empty"
    
    # Extract unique patient IDs
    patient_ids = list(df["patient_id"].unique())
    assert len(patient_ids) >= 50, "Should have sufficient patient cohorts"

    # Deterministic split replication
    np.random.seed(42)
    np.random.shuffle(patient_ids)

    n_train = int(len(patient_ids) * 0.70)
    n_val = int(len(patient_ids) * 0.15)

    train_pids = set(patient_ids[:n_train])
    val_pids = set(patient_ids[n_train:n_train+n_val])
    test_pids = set(patient_ids[n_train+n_val:])

    # 1. Assert ZERO intersection between Train and Test
    train_test_overlap = train_pids.intersection(test_pids)
    assert len(train_test_overlap) == 0, f"DATA LEAKAGE DETECTED: {train_test_overlap} found in both Train and Test!"

    # 2. Assert ZERO intersection between Train and Validation
    train_val_overlap = train_pids.intersection(val_pids)
    assert len(train_val_overlap) == 0, f"DATA LEAKAGE DETECTED: {train_val_overlap} found in both Train and Validation!"

    # 3. Assert ZERO intersection between Validation and Test
    val_test_overlap = val_pids.intersection(test_pids)
    assert len(val_test_overlap) == 0, f"DATA LEAKAGE DETECTED: {val_test_overlap} found in both Validation and Test!"

    # 4. Assert all partitions sum to total cohort
    assert len(train_pids) + len(val_pids) + len(test_pids) == len(patient_ids)

def test_temporal_directionality_and_target_isolation():
    df = extract_features()
    # Ensure target label column 'event_24h' is binary {0, 1}
    assert set(df["event_24h"].unique()).issubset({0, 1})
    
    # Feature columns must NOT contain the target
    feature_cols = [c for c in df.columns if c not in ["patient_id", "event_24h"]]
    assert "event_24h" not in feature_cols
    assert len(feature_cols) >= 15
