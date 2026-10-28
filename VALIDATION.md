# Submission validation

Reviewed and rerun on **15 October 2026**. The professor's requested paper summary, paper contributions, paper limitations, and implementation details have explicit sections in the report. README.md maps each requirement to its evidence.

## Checks performed

- Executed all **11 notebook code cells** in order in a fresh Jupyter kernel (`jupyter nbconvert --execute`); outputs, including printed progress and completion messages, were captured from execution, not fabricated. The run completed in about 10 seconds on the available machine. Runtime elsewhere will vary.
- Validated the notebook format, execution counts 1–11, absence of error outputs, printed messages in every cell that prints, no stray return-value outputs, and presence of **three figure outputs**.
- Executed `ddi_project.py --output-dir ...` separately as a standalone process in a separate output directory, using the platform's default Matplotlib backend. Command-line runs save figures without opening plot windows and print the results summary as plain text. Both entry points completed successfully. CLI help worked, and importing the module produced no output or training.
- Compared the notebook experiment code with the body of the source function. The scientific logic is equivalent; the script adds a function boundary and CLI and changes the output-directory parameter. Documentation-string indentation is ignored in this comparison.
- Compared every exported CSV between notebook and standalone runs, and against the previous submitted results. All matched within **1e-12 absolute tolerance**. Original reported quantitative findings were preserved.
- Verified original workbook and extracted CSV SHA-256 digests, schema, shape, row order, IDs, labels, and **every numerical value** against the `5-fold CV` worksheet.
- Independently checked source/prediction alignment; 13,952 distinct held-out pairs; regenerated fold assignments; training/test pair separation; drug-overlap audit; and all seven fold, pooled and holdout metrics.
- Recalculated fold means and sample SDs and checked the ablation summary against its fold values.
- Regenerated the reserved drug set. Confirmed 8,852 training pairs, 584 test pairs, 4,516 excluded crossing pairs, and **zero drug identity overlap** between training and testing.
- Independently recomputed the paired percentile bootstrap intervals for holdout ROC-AUC (2,000 resamples of the 584 test pairs, seed 42) and matched the exported values.
- Checked pair lookup with reversed order, normalized case and whitespace, and rejection of non-string inputs, identical IDs, unknown IDs, and absent pairs.
- In the pipeline, assertions check finite and bounded features, no missing values, no repeated unordered pairs or self-pairs, one OOF score per row, and logistic-scaler means derived only from training folds.
- Checked all six report tables against the exported results. Table 4's published values were read from Figure 4 of the paper. Checked the paper's stated data, methods, results, contributions, limitations and global-prediction counts against its full text.
- Revised the Word report on 15 October 2026 (expanded summary and contributions, critical assessment, comparison with the paper, holdout bootstrap intervals and conclusion). The revised file passed Office Open XML schema validation, and each revised section was previewed; full pagination should be confirmed in Word.

## Tested environment

Python 3.14.6; NumPy 2.4.6; pandas 3.0.3; SciPy 1.18.0; scikit-learn 1.9.0; Matplotlib 3.11.0; IPython 9.15.0; openpyxl 3.1.5; nbformat 5.10.4; nbconvert 7.17.1; ipykernel 6.31.0. Additional recorded numerical dependency versions are in requirements-tested.txt. Each execution also records provenance.json.

These checks used local Python. No Google-hosted runtime was used for this verification. Dependency installation in a new virtual environment was not independently tested; the documented versions were already installed. Numerical comparisons allow tiny floating-point differences rather than requiring byte-identical CSVs.

## Remaining scientific limitations

1. This implements the paper's logistic-regression component using precomputed features; it is not a complete reproduction of HNAI or its best-performing SVM.
2. The workbook–manuscript count discrepancy remains unresolved. No source rows were silently removed.
3. Sampled negatives are not verified non-interactions. Data checks cannot establish clinical correctness.
4. Pair cross-validation reuses drug identities across training and test pairs. The additional disjoint evaluation uses only one reserved set and historical annotations.
5. Scores are not calibrated clinical probabilities; no prospective or independent clinical validation is provided.
6. Original fold assignments and full software configuration were not recovered. Comparisons with the paper's numbers are contextual, not evidence of exact numerical reproduction or superiority.

The checks validate execution, bookkeeping, data fidelity, and consistency of the report with the computed evidence. They do not remove these scientific limitations.
