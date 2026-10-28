"""Independently verify saved DDI results without fitting any model.

Run from the extracted package directory:
    python verify_results.py --results-dir ddi_results

The checks recompute metrics from predictions, regenerate the documented splits,
and reconcile exported labels and counts against the supplied source data. They
validate experiment bookkeeping, not clinical label accuracy or generalization.
Use normal Python execution: -O disables assertions and is not supported.
"""
from pathlib import Path
import argparse
import json
import numpy as np
import pandas as pd
from sklearn.metrics import (accuracy_score, average_precision_score,
                            balanced_accuracy_score, f1_score, precision_score,
                            recall_score, roc_auc_score)
from sklearn.model_selection import StratifiedKFold

ROOT = Path(__file__).resolve().parent
METRICS = ['roc_auc', 'average_precision', 'accuracy', 'balanced_accuracy',
           'precision', 'recall', 'f1']
MODELS = ['Prior baseline', 'Logistic regression', 'Random Forest']


def recalculate(labels, scores, threshold):
    """Return independent metric values in the fixed METRICS column order."""
    predicted = np.asarray(scores) >= threshold
    return [roc_auc_score(labels, scores), average_precision_score(labels, scores),
            accuracy_score(labels, predicted), balanced_accuracy_score(labels, predicted),
            precision_score(labels, predicted, zero_division=0),
            recall_score(labels, predicted, zero_division=0),
            f1_score(labels, predicted, zero_division=0)]


def check_scores(frame, suffix):
    """Reject incomplete, nonfinite or out-of-range classifier scores."""
    values = frame[[name + suffix for name in MODELS]].to_numpy()
    assert np.isfinite(values).all()
    assert ((values >= 0) & (values <= 1)).all()


def verify(results_dir):
    """Check one complete result directory against the distributed source CSV."""
    res = Path(results_dir)
    provenance = json.loads((res / 'provenance.json').read_text())
    assert provenance['seed'] == 42 and provenance['folds'] == 5
    assert provenance['threshold'] == 0.5
    threshold = provenance['threshold']
    source = pd.read_csv(ROOT / 'data/source_cv.csv', float_precision='round_trip')
    data = pd.read_csv(res / 'validated_pairs.csv', float_precision='round_trip')
    pred = pd.read_csv(res / 'pair_cv_predictions.csv', float_precision='round_trip')
    assert len(source) == len(data) == len(pred) == 13952
    assert data.row_id.tolist() == pred.row_id.tolist() == list(range(13952))
    assert pred.pair_key.nunique() == 13952 and not pred.isna().any().any()
    for old, new in [('Drug_A (Drugbank ID)', 'drug_a'), ('Drug_B (Drugbank ID)', 'drug_b'),
                     ('Class', 'source_label'), ('Structural Similarity', 'structural'),
                     ('Genomic Similarity', 'genomic'), ('Therapeutic Similarity', 'therapeutic'),
                     ('Phenotypic Similarity', 'phenotypic')]:
        np.testing.assert_array_equal(source[old], data[new])
    np.testing.assert_array_equal(data.label, source.Class.map({'DDI': 1, 'non-DDI': 0}))
    for col in ['row_id', 'drug_a', 'drug_b', 'pair_key', 'source_label', 'label']:
        np.testing.assert_array_equal(pred[col], data[col])
    expected_keys = ['|'.join(sorted(pair)) for pair in zip(data.drug_a, data.drug_b)]
    assert data.pair_key.tolist() == expected_keys
    check_scores(pred, '_oof_score')
    folds = list(StratifiedKFold(5, shuffle=True, random_state=42).split(data, data.label))
    audit = pd.read_csv(res / 'pair_cv_split_audit.csv')
    for fold, (tr, te) in enumerate(folds, 1):
        assert set(pred.loc[pred.fold.eq(fold), 'row_id']) == set(te)
        assert set(data.iloc[tr].pair_key).isdisjoint(data.iloc[te].pair_key)
        train_ids = set(data.iloc[tr][['drug_a', 'drug_b']].to_numpy().ravel())
        a = data.iloc[te].drug_a.isin(train_ids)
        b = data.iloc[te].drug_b.isin(train_ids)
        row = audit.set_index('fold').loc[fold]
        assert row.train_rows == len(tr) and row.test_rows == len(te)
        assert row.test_positive_rows == data.iloc[te].label.sum()
        assert (row.both_drugs_seen, row.one_drug_seen, row.neither_drug_seen) == (
            (a & b).sum(), (a ^ b).sum(), (~a & ~b).sum())
    fm = pd.read_csv(res / 'pair_cv_fold_metrics.csv')
    assert len(fm) == 15 and not fm.duplicated(['model', 'fold']).any()
    assert set(fm.model) == set(MODELS)
    for _, row in fm.iterrows():
        test = pred[pred.fold.eq(row.fold)]
        np.testing.assert_allclose(recalculate(test.label, test[row.model + '_oof_score'], threshold),
                                   row[METRICS].astype(float), rtol=0, atol=1e-12)
    summary = pd.read_csv(res / 'pair_cv_summary.csv', header=[0, 1], index_col=0)
    expected = fm.groupby('model', sort=False)[METRICS].agg(['mean', 'std'])
    pd.testing.assert_frame_equal(summary, expected, check_exact=False, rtol=0, atol=1e-12)
    pooled = pd.read_csv(res / 'pair_cv_pooled_metrics.csv')
    for _, row in pooled.iterrows():
        np.testing.assert_allclose(recalculate(pred.label, pred[row.model + '_oof_score'], threshold),
                                   row[METRICS].astype(float), rtol=0, atol=1e-12)
    ids = np.unique(data[['drug_a', 'drug_b']].to_numpy().ravel())
    reserved = set(json.loads((res / 'heldout_drug_ids.json').read_text()))
    expected_reserved = set(np.random.default_rng(42).choice(ids, size=int(np.ceil(.2 * len(ids))), replace=False))
    assert reserved == expected_reserved
    a, b = data.drug_a.isin(reserved), data.drug_b.isin(reserved)
    train, test, excluded = data[~a & ~b], data[a & b], data[a ^ b]
    assert (len(train), len(test), len(excluded)) == (8852, 584, 4516)
    assert set(train[['drug_a', 'drug_b']].to_numpy().ravel()).isdisjoint(
        set(test[['drug_a', 'drug_b']].to_numpy().ravel()))
    hp = pd.read_csv(res / 'drug_holdout_predictions.csv', float_precision='round_trip')
    assert hp.row_id.tolist() == test.row_id.tolist()
    for col in ['row_id', 'drug_a', 'drug_b', 'label']:
        np.testing.assert_array_equal(hp[col], test[col])
    check_scores(hp, '_score')
    hm = pd.read_csv(res / 'drug_holdout_metrics.csv')
    assert set(hm.model) == set(MODELS) and len(hm) == 3
    for _, row in hm.iterrows():
        np.testing.assert_allclose(recalculate(hp.label, hp[row.model + '_score'], threshold),
                                   row[METRICS].astype(float), rtol=0, atol=1e-12)
    boot = pd.read_csv(res / 'drug_holdout_auc_bootstrap.csv', float_precision='round_trip').set_index('quantity')
    rng = np.random.default_rng(42)
    lr, rf = hp['Logistic regression_score'].to_numpy(), hp['Random Forest_score'].to_numpy()
    labels = hp.label.to_numpy()
    draws = np.empty((2000, 2))
    for b in range(2000):
        i = rng.integers(0, len(labels), len(labels))
        draws[b] = roc_auc_score(labels[i], lr[i]), roc_auc_score(labels[i], rf[i])
    for name, values, point in [('Logistic regression', draws[:, 0], roc_auc_score(labels, lr)),
                                ('Random Forest', draws[:, 1], roc_auc_score(labels, rf)),
                                ('Logistic regression minus Random Forest', draws[:, 0] - draws[:, 1],
                                 roc_auc_score(labels, lr) - roc_auc_score(labels, rf))]:
        np.testing.assert_allclose(boot.loc[name, ['roc_auc', 'ci95_lower', 'ci95_upper']].astype(float),
                                   [point, *np.percentile(values, [2.5, 97.5])], rtol=0, atol=1e-12)
    assert len(boot) == 3
    counts = pd.read_csv(res / 'drug_holdout_counts.csv').set_index('partition')
    for name, part in [('Training', train), ('Testing', test), ('Excluded crossing pairs', excluded)]:
        assert counts.loc[name].tolist() == [len(part), int(part.label.sum()), int(part.label.eq(0).sum())]
    af = pd.read_csv(res / 'ablation_fold_metrics.csv')
    assert len(af) == 25 and not af.duplicated(['removed_feature', 'fold']).any()
    ab = pd.read_csv(res / 'ablation_summary.csv', header=[0, 1], index_col=0)
    expected_ab = af.groupby('removed_feature', sort=False)[['roc_auc', 'average_precision']].agg(['mean', 'std'])
    expected_ab[('roc_auc', 'change_from_all')] = expected_ab[('roc_auc', 'mean')] - expected_ab.loc['None (all four)', ('roc_auc', 'mean')]
    pd.testing.assert_frame_equal(ab, expected_ab, check_exact=False, rtol=0, atol=1e-12)
    print('PASS: source alignment, unique held-out rows, folds, all seven metrics, summaries, disjoint drug split, holdout bootstrap intervals and ablation aggregation.')
    print('Verified:', res.resolve())


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--results-dir', type=Path, default=ROOT / 'ddi_results')
    verify(parser.parse_args().results_dir)
