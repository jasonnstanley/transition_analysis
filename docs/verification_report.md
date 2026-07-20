# Transition Analysis Toolkit
## Independent Verification Report

**Generated:** 2026-07-17 15:11:43

**R version:** R version 4.6.1 (2026-06-24 ucrt)

**Research dataset modified:** 2026-07-13 15:56:37

**Canonical split modified:** 2026-07-14 15:04:57

**Overall verification status:** PASS

---

## Verification Status

| Component | Python | Independent R | Status |
|---|:---:|:---:|---|
| Research dataset | Yes | Yes | PASS |
| Canonical train/test split | Yes | Yes | PASS |
| Feature engineering | Yes | Yes | PASS |
| Dummy-variable encoding | Yes | Yes | PASS |
| Feature names and ordering | Yes | Yes | PASS |
| Cross-file ROC consistency | Yes | Yes | PASS |
| Decision Tree | Yes | Yes | VERIFIED PIPELINE; IMPLEMENTATION DIFFERENCE |
| Logistic Regression | Yes | No | PENDING |
| Random Forest | Yes | No | PENDING |

---

## Research Dataset Verification

- Rows: **1473**
- Columns: **19**
- Outcome variable: `current_subject_pass`

**Verification result: PASS**

---

## Canonical Train/Test Split Verification

- Training rows: **1178**
- Test rows: **295**
- Training non-passes: **236**
- Training passes: **942**
- Test non-passes: **59**
- Test passes: **236**

**Verification result: PASS**

---

## Feature Engineering Verification

- Predictors without Risk Index: **15**
- Predictors with Risk Index: **16**
- Without-risk names match Python design: **TRUE**
- With-risk names match Python design: **TRUE**

**Verification result: PASS**

---

## Cross-file ROC Verification

- Model variants checked: **4**
- CV ROC metrics matched: **TRUE**
- Test ROC metrics matched: **TRUE**

**Verification result: PASS**

---

## Independent Decision Tree Verification

### Implementations

- Python: `scikit-learn`
- R: `rpart`

Both implementations used:

- the same pseudonymised research dataset;
- the same canonical training and test observations;
- the same binary outcome;
- the same 15-predictor without-risk design;
- full dummy-variable encoding;
- information-gain splitting;
- minimum split size of 40;
- minimum terminal-node size of 5.

### Held-out Test-set Comparison

| Metric | Python | R | R minus Python |
|---|---:|---:|---:|
| Accuracy | 0.6847 | 0.8102 | +0.1254 |
| Balanced accuracy | 0.6949 | 0.6017 | -0.0932 |
| Precision | 0.9040 | 0.8358 | -0.0681 |
| Recall | 0.6780 | 0.9492 | +0.2712 |
| F1 | 0.7748 | 0.8889 | +0.1141 |
| ROC AUC | 0.7557 | 0.6855 | -0.0702 |

### Verification

The independently reconstructed R pipeline used the verified research dataset, canonical split, outcome definition, dummy-variable encoding and feature order.

**Pipeline verification result: PASS**

### Interpretation

The Python and R decision trees do not produce identical predictions. This is expected because `scikit-learn` and `rpart` use different tree-growing, stopping and pruning implementations, even when their high-level tuning constraints are aligned.

The R tree favoured the passing class more strongly, producing higher recall and overall accuracy but lower balanced accuracy and ROC AUC. The differences are therefore model-implementation differences, not evidence of inconsistent data preparation.

**Interpretation: EXPECTED IMPLEMENTATION DIFFERENCE**

---

## Pending Independent Verification

- Logistic Regression
- Random Forest

