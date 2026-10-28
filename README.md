# Drug interaction prediction using published similarity features

This package implements the logistic-regression classification component of Cheng and Zhao (2014), using their four published similarity features. It includes a prior baseline, a Random Forest comparison, five-fold evaluation, a drug-disjoint holdout, and feature ablation.

Selected paper: Cheng F, Zhao Z. *Machine learning-based prediction of drug–drug interactions by integrating drug phenotypic, therapeutic, chemical, and genomic properties.* J Am Med Inform Assoc. 2014;21(e2):e278–e286. [DOI](https://doi.org/10.1136/amiajnl-2013-002512); [full article and supplementary data](https://pmc.ncbi.nlm.nih.gov/articles/PMC4173180/).

## What to submit

The two main deliverables are **DDI_Technical_Report.docx** and **DDI_Project_Final.ipynb**. Include **ddi_project.py** as the standalone documented source. Keep the data, results, dependency file, and validation scripts with them so the work can be inspected and rerun. The complete ZIP contains all of these files.

## Where each professor requirement is addressed

| Requirement | Evidence in the package |
|---|---|
| Well-documented source code | Notebook explanations; Python module and function docstrings, comments, command-line entry point; examples below |
| Technical report | DDI_Technical_Report.docx, an editable academic report |
| Summary of the selected paper | Report Sections 1 and 2.1, including data, the four similarity measures, all five classifiers' published results and the global predictions |
| Contributions of the selected paper | Report Section 2.2, distinguished from this project's contributions in Section 9 |
| Limitations of the selected paper | Report Section 2.3 (acknowledged by the authors) and Section 2.4 (independent critical assessment); implementation-specific limitations in Section 9.1 |
| Details of reproduction or implementation | Scope mapping in Section 2.5; data, preprocessing, models and evaluation in Sections 3–8; comparison with the paper's published results in Section 7.2 (Table 4); conclusion in Section 10; run instructions in Section 11 |
| Evidence supporting reported findings | Executed notebook; per-fold predictions and metrics; provenance; independently recalculated results in VALIDATION.md |

## Scope

This is an implementation of a selected component, not a complete numerical reproduction of every HNAI experiment. It reuses precomputed features and implements logistic regression with documented modern settings. It does not rebuild biological databases, reproduce the original folds, implement the paper's best-performing SVM, or repeat its global network and antipsychotic case study. Random Forest is a project comparison, not an original-paper method. The paper also studies feature removal; the project's ablation is an implementation-specific analysis, not a novel technique.

## Run in Google Colab

1. Upload **DDI_Project_Final.ipynb** to Colab.
2. Select a standard CPU runtime and choose **Runtime → Run all**.
3. Wait for the final completion message and inspect the evaluation tables.
4. Download `ddi_results.zip` from the runtime's Files panel, and download the executed `.ipynb` through the File menu.

The dataset is embedded. No data upload, Drive mount, API key, or GPU is required. The notebook uses standard scientific Python packages and does not install or upgrade them automatically. Saved outputs in this package are from a fresh **local** execution on 15 October 2026. No Google-hosted run was performed during this verification. Runtime versions are recorded because numerical results can vary between environments.

## Run locally

To match the submitted environment, use Python 3.14 (the test used 3.14.6). From the extracted package directory:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-tested.txt
python verify_source.py
python ddi_project.py --output-dir rerun_results
python verify_results.py --results-dir rerun_results
```

On Windows, replace the activation command with `.venv\Scripts\activate`.

The source script needs no network after dependencies are installed. It writes `rerun_results/` and `rerun_results.zip`; figures are saved to `rerun_results/figures/` without opening plot windows. A new output directory preserves the supplied results; using an existing one overwrites same-named generated files. Run normal Python, without `-O`, because the scientific checks use assertions. The dependency versions were inspected in the tested environment; installation into a new environment was not independently tested.

The module can also be imported without triggering training:

```python
from ddi_project import run_pipeline
run = run_pipeline(output_dir="my_results")
print(run["inspect_pair"]("DB00363", "DB00472"))
```

`run_pipeline` returns paths, result tables, all pair predictions, and the pair-lookup callable. The notebook contains the same experimental logic, divided into 11 executable cells. `verify_source.py` checks every original workbook value against the CSV. `verify_results.py` recalculates all seven primary metrics, regenerates splits, and reconciles exported labels and summaries; it does not refit models.

## Inspect drug pairs in the notebook

After all cells finish, run this in a new code cell:

```python
display(inspect_pair("DB00363", "DB00472"))
```

- `source_label` is the paper's annotation, not the model's prediction.
- `fold` is the held-out fold used for that row.
- `Logistic regression_oof_score` and `Random Forest_oof_score` are scores from two different classifiers. OOF means **out of fold**: the evaluated pair was excluded during fitting.
- Larger scores favor the DDI label. At the fixed threshold, **score ≥ 0.5** predicts DDI; lower scores predict the sampled-negative class.
- These are not calibrated percentages of clinical risk and do not measure severity. The source's `non-DDI` label is an unverified sampled negative.

The function looks up a pair already evaluated in the dataset. It does not predict arbitrary combinations or accept drug names. Both drugs may occur in other training pairs. To see all available input data and IDs:

```python
display(df)
display(pd.Series(drug_ids, name="DrugBank ID"))
```

## Data and principal findings

The distributed worksheet contains **13,952 pairs**: **6,946 DDI**, **7,006 sampled non-DDI**, and **730 distinct drug IDs**. Positive pairs involve 721 drugs. The worksheet has 60 more negative pairs and nine more IDs than the manuscript's stated balanced dataset. All rows are retained and this unresolved discrepancy is disclosed.

Mean five-fold ROC-AUC is **0.654 ± 0.011** for logistic regression, within 0.001 of the 0.655 reported for the same classifier in the paper, and **0.676 ± 0.015** for Random Forest (sample SD across folds). The single holdout with both drug identities excluded from training gives **0.629** (95% bootstrap interval 0.582–0.672) and **0.621** (0.575–0.665), respectively. These are descriptive evaluation results; they do not establish statistical superiority or clinical validity.

## File guide

| File or directory | Purpose |
|---|---|
| DDI_Project_Final.ipynb | Self-contained explained notebook, with actual execution outputs |
| ddi_project.py | Documented standalone implementation and `run_pipeline` function |
| DDI_Technical_Report.docx | Paper review, implementation details, results and limitations |
| data/amiajnl-2013-002512-s2.xlsx | Original Supplementary Table S1; use the `5-fold CV` worksheet |
| data/source_cv.csv | Value-preserving extraction of that worksheet |
| ddi_results/pair_cv_predictions.csv | All source pairs, labels, folds and held-out scores |
| ddi_results/pair_cv_fold_metrics.csv | Seven metrics per model and fold |
| ddi_results/pair_cv_summary.csv | Fold means and sample SDs; two header rows |
| ddi_results/drug_holdout_* | Separate experiment with disjoint drug identities |
| ddi_results/ablation_* | Logistic-regression feature-removal results |
| ddi_results/figures/ | Three evaluation and data figures |
| ddi_results/provenance.json | Source hashes, parameters, split counts, versions and timestamps |
| ddi_results.zip | Results exported by the notebook's current run |
| requirements-tested.txt | Tested versions of runtime and verification packages |
| verify_source.py; verify_results.py | Independent provenance and result checks |
| VALIDATION.md | Verification performed and remaining limitations |
| SHA256SUMS.json | File digests for the delivered package, excluding itself |

## Attribution and report format

The supplementary numerical data belong to the cited study. Notebook organization, the modern implementation, checks and additional evaluations are assignment work. No new DDI algorithm or clinical validation is claimed. The Word report uses Arial 11-point body text, numbered headings, 1.15 line spacing, one-inch margins, consistent tables and captions, numeric citations, and page numbers.
