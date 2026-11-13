# Undiagnosed Diabetes Risk Model (NHANES)

A screening model that estimates the risk of **undiagnosed diabetes** in US adults, using public CDC NHANES data (2017–March 2020).

The question: from information you can collect in a short visit (age, waist, blood pressure, family history, and optionally a cholesterol test), can we find people who have diabetes but don't know it?

## Data

- **Source:** [NHANES 2017–March 2020 pre-pandemic](https://wwwn.cdc.gov/nchs/nhanes/continuousnhanes/default.aspx?Cycle=2017-2020), 12 public files (demographics, diabetes questionnaire, HbA1c, glucose, body measures, blood pressure, cholesterol, smoking, physical activity, medical conditions).
- **Target:** HbA1c ≥ 6.5% in a person who has **not** been told they have diabetes and takes no insulin or diabetes pills.
- **Sample:**

| Step | Rows |
|---|---|
| Participants with an HbA1c result | 9,737 |
| Aged 20+ | 8,081 |
| Not pregnant | 8,005 |
| Known diabetes status | 8,000 |
| **Not diagnosed (analysis sample)** | **6,644** |

237 people (3.6%) in the analysis sample have undiagnosed diabetes.

## Method

- **No leakage:** the diabetes questionnaire columns and HbA1c are not used as features.
- **Two feature sets:**
  - **Model A, no lab test:** demographics, body measures, blood pressure, history and lifestyle.
  - **Model B:** Model A plus total and HDL cholesterol (one blood test).
- **Models:** logistic regression and gradient boosting (scikit-learn pipelines with imputation, scaling and one-hot encoding).
- **Evaluation:** 80/20 stratified split. 5-fold stratified cross-validation on the training set for model choice, and the test set for final results.
- **Metrics:** ROC-AUC, PR-AUC (the baseline is the prevalence, 0.036) and the Brier score.

## Results

**Cross-validation (training set, 5 folds):**

| Model | ROC-AUC | PR-AUC |
|---|---|---|
| Logistic regression A | 0.76 ± 0.04 | 0.10 ± 0.03 |
| **Logistic regression B** | **0.80 ± 0.03** | **0.12 ± 0.04** |
| Gradient boosting A | 0.75 ± 0.03 | 0.11 ± 0.02 |
| Gradient boosting B | 0.76 ± 0.03 | 0.13 ± 0.03 |

- **Cholesterol helps:** adding one blood test raises ROC-AUC by about 0.04.
- **A more complex model didn't help:** gradient boosting was no better than logistic regression. With about 190 positive cases in training, the simple model generalizes better and is easier to explain. **Logistic regression B is the final model.**

**Test set (final model):** ROC-AUC 0.83, PR-AUC 0.14 (about 4× the baseline), Brier 0.032.

**Calibration:** predicted risks match the observed rates well (for example, a predicted risk of about 11% matches about 11% observed). Predictions only reach about 12%, and the test set has 47 positive cases, so the evidence is limited.

![Calibration plot](reports/figures/calibration_plot.png)

**Subgroups (test set, ROC-AUC):**

- **Sex:** women 0.86 and men 0.79. The groups are small (23 and 24 cases), so this difference is within noise.
- **Age:** 40–59 scored 0.83, but **60+ only 0.70**. The model is weakest in the oldest group, where most people already have several risk factors. The 20–39 group has only 4 cases, so its score is not reliable.
- **Race:** each group has 2–18 cases, which is too few to compare.

**Most important features (logistic regression B):**

![Feature importance](reports/figures/feature_importance.png)

- **HDL cholesterol is protective:** about 0.44× the odds per standard deviation.
- **Classic risk factors:** age (about 2× the odds per standard deviation, about 17 years), family history of diabetes (1.6×), waist circumference (1.5×) and diagnosed high blood pressure (1.5×).
- **"Told high cholesterol" lowers the risk** (0.68×). This is probably not biology. People with a cholesterol diagnosis see doctors more often, so their diabetes is more likely to be diagnosed already, and they leave the "undiagnosed" group.
- These are associations, not causes. Correlated features, such as BMI and waist, share their effect, so a small coefficient doesn't mean a feature is unimportant.

## Limitations

- Only 237 positive cases. Test results are based on 47 cases, so all numbers have wide uncertainty.
- The survey weights are not used. The results describe this sample, not the whole US population.
- A single HbA1c measurement. A clinical diagnosis normally needs a repeated test.
- Cross-sectional data: the model finds people who have diabetes now. It doesn't predict future diabetes.

## Project structure

```
data/raw/              NHANES .xpt files (not in git, see below)
data/processed/        analysis_sample.parquet
src/01_load_and_clean.ipynb   load, clean, merge, build target and features
src/02_model.ipynb            models, cross-validation, calibration, subgroups, feature importance
reports/figures/       saved plots
```

## How to run

1. Create an environment and install the packages:
```
pip install -r requirements.txt
```
2. Download the 12 files below into `data/raw/` from `https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2017/DataFiles/<FILE>.xpt`

   P_DEMO, P_DIQ, P_GHB, P_GLU, P_BMX, P_BPXO, P_BPQ, P_TCHOL, P_HDL, P_SMQ, P_PAQ, P_MCQ

3. Run `src/01_load_and_clean.ipynb`, then `src/02_model.ipynb`

## Stack

Python, pandas, NumPy, scikit-learn, matplotlib
