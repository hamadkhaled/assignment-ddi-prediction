DDI project results using Cheng and Zhao (2014) published features.
pair_cv_fold_metrics.csv: one row per model and fold.
pair_cv_summary.csv: mean and sample SD across folds (two header rows).
pair_cv_predictions.csv: one held-out score per model per source row.
drug_holdout_*: single exploratory split with both drug endpoints disjoint.
ablation_*: exploratory removal of one feature at a time for logistic regression.
provenance.json: source hashes, settings, audit, runtime and versions.
Source label non-DDI means sampled negative, not clinically verified safe.
