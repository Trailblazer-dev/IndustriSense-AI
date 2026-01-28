# Jupyter Notebook Structure Standards for IndustriSense-AI Project

## Overview
This document defines the structural standard for all Jupyter notebooks in the IndustriSense-AI project. The structure enforces discipline through the **Reflection Cell Rule**: every code cell must be followed by a markdown cell for post-execution observations.

---

## Core Principles

1. **Separation of Execution and Interpretation**: Code cells execute; markdown cells (reflection) interpret results
2. **Intentional Incompleteness**: Reflection cells are templates—users must fill them after running code
3. **Logical Flow**: Markdown guides reader; code implements; reflection documents findings
4. **Reusability**: Structure enables reproduction and knowledge transfer

---

## Reflection Cell Rule (MANDATORY)

### After Every Code Cell
A markdown cell titled **"Post-Execution Notes (To Be Filled After Running This Cell)"** MUST follow, containing:

```markdown
### Post-Execution Notes (To Be Filled After Running This Cell)

- **What was expected:**  
- **What actually happened:**  
- **Key observations:**  
- **Issues / warnings:**  
- **Decisions / next steps:**  
```

**Purpose**: Forces deliberate observation and documentation of code outcomes before moving forward.

---

## Generic Notebook Structure (Template)

```
[MARKDOWN CELL] Title & Objectives
# Notebook Title
- Project context
- Objectives
- Dependencies/Data

[CODE CELL] Dependencies & Setup
- Import libraries
- Set configurations
- Define paths

[MARKDOWN CELL] Post-Execution Notes

[MARKDOWN CELL] Section 1: Data Loading & Exploration
- What this section does
- Expected outputs

[CODE CELL] Load Data
- Read CSV/API/etc
- Display shape, basic info

[MARKDOWN CELL] Post-Execution Notes

[CODE CELL] Initial Data Overview
- First rows, dtypes
- Missing values check

[MARKDOWN CELL] Post-Execution Notes

...
[Repeat for each logical section]
...

[MARKDOWN CELL] Summary & Next Steps
- Key findings
- Assumptions
- What comes next
```

---

## Notebook-Specific Structures

### 1. EDA Notebook (1_EDA.ipynb)
**Status**: Already executed with outputs

**Structure**:
1. Title & Objectives
2. Data Loading & Imports
3. Data Quality Assessment (missing values, duplicates, descriptive stats)
4. Feature Engineering (Stress Index, Temperature Differential)
5. Failure Distribution Analysis
6. Correlation & Multicollinearity Analysis
7. Anomaly Detection (Isolation Forest)
8. Feature Validation & Statistical Testing
9. Dataset Structure Limitations (Phase 2 requirements)
10. Training Data Readiness Checklist
11. Summary & Recommendations

**Note**: Since this notebook has been run and has outputs, reflection cells may contain *observations written after execution* rather than templates. The structure still applies for any new cells added.

---

### 2. Feature Engineering Notebook (2_Feature_Engineering.ipynb)
**Status**: To be created/structured

**Structure**:
```
[MARKDOWN] Title & Objectives
- Feature engineering strategy
- Source of features (EDA insights)

[CODE] Load EDA data & define features
[MARKDOWN] Post-Execution Notes

[MARKDOWN] Section: Stress Index Engineering
- Physical rationale
- Validation approach

[CODE] Create & validate Stress Index
[MARKDOWN] Post-Execution Notes

[CODE] Calculate effect sizes (Cohen's d)
[MARKDOWN] Post-Execution Notes

[MARKDOWN] Section: Temperature Differential Engineering
[CODE] Create & validate Temp Diff
[MARKDOWN] Post-Execution Notes

[MARKDOWN] Section: Anomaly Score Engineering
[CODE] Isolation Forest anomaly detection
[MARKDOWN] Post-Execution Notes

[MARKDOWN] Section: Feature Interactions (if applicable)
[CODE] Explore interaction terms
[MARKDOWN] Post-Execution Notes

[MARKDOWN] Summary: Feature Set Ready for Modeling
[CODE] Save engineered features to file
[MARKDOWN] Post-Execution Notes
```

---

### 3. Classification Modeling Notebook (3_Failure_Classification_Modeling.ipynb)
**Status**: To be created/structured

**Structure**:
```
[MARKDOWN] Title & Objectives
- Binary classification task
- Evaluation metrics (F2-score, Recall)
- Data: engineered features from notebook 2

[CODE] Load engineered features & split train/test
[MARKDOWN] Post-Execution Notes

[MARKDOWN] Section: Class Imbalance Strategy
- scale_pos_weight calculation
- Stratified cross-validation approach

[CODE] Calculate class weights & setup stratified CV
[MARKDOWN] Post-Execution Notes

[MARKDOWN] Section: XGBoost Classification Model
[CODE] Define & train XGBoost classifier
[MARKDOWN] Post-Execution Notes

[CODE] Cross-validation evaluation (F2-score, Recall, Precision)
[MARKDOWN] Post-Execution Notes

[CODE] Feature importance analysis
[MARKDOWN] Post-Execution Notes

[MARKDOWN] Section: Failure Mode Classification (Multi-class)
[CODE] Train separate classifiers per failure mode (TWF, HDF, etc.)
[MARKDOWN] Post-Execution Notes

[CODE] Combine predictions into unified failure risk score
[MARKDOWN] Post-Execution Notes

[MARKDOWN] Summary: Model Performance & Readiness
[CODE] Save model artifacts (weights, scaler, feature names)
[MARKDOWN] Post-Execution Notes
```

---

### 4. RUL Prognosis Notebook (4_RUL_Prognosis_Modeling.ipynb)
**Status**: To be created/structured

**Structure**:
```
[MARKDOWN] Title & Objectives
- RUL estimation via Tool Wear regression
- Note: "Estimation" (snapshot) vs "Prognosis" (time-series)
- Phase 2 will implement true time-series CLSTM

[CODE] Load engineered features
[MARKDOWN] Post-Execution Notes

[MARKDOWN] Section: Tool Wear as RUL Proxy
- Physical justification (max tool wear ~254 min)
- Remaining Useful Life = 254 - predicted_wear

[CODE] Exploratory analysis: Tool Wear distribution
[MARKDOWN] Post-Execution Notes

[MARKDOWN] Section: XGBoost Regression Model
[CODE] Train XGBoost regressor on Tool Wear
[MARKDOWN] Post-Execution Notes

[CODE] Cross-validation evaluation (MAE, RMSE, R²)
[MARKDOWN] Post-Execution Notes

[CODE] Feature importance for wear prediction
[MARKDOWN] Post-Execution Notes

[MARKDOWN] Section: RUL Conversion
[CODE] Convert predicted wear to RUL (254 - wear)
[MARKDOWN] Post-Execution Notes

[CODE] Visualize RUL distribution
[MARKDOWN] Post-Execution Notes

[MARKDOWN] Summary: RUL Model Readiness
[CODE] Save RUL model artifacts
[MARKDOWN] Post-Execution Notes
```

---

### 5. XAI & Interpretation Notebook (5_XAI_and_Interpretation.ipynb)
**Status**: To be created/structured

**Structure**:
```
[MARKDOWN] Title & Objectives
- SHAP explanation of classification & regression models
- Operator-friendly insights from models 3 & 4

[CODE] Load trained models & SHAP libraries
[MARKDOWN] Post-Execution Notes

[MARKDOWN] Section: SHAP Summary Plots (Classification)
[CODE] Generate SHAP summary plot for failure classifier
[MARKDOWN] Post-Execution Notes

[CODE] SHAP dependence plots (key features)
[MARKDOWN] Post-Execution Notes

[MARKDOWN] Section: Instance-Level Explanations
[CODE] SHAP force plots for sample predictions
[MARKDOWN] Post-Execution Notes

[MARKDOWN] Section: SHAP for RUL Regression
[CODE] Generate SHAP explanations for Tool Wear regression
[MARKDOWN] Post-Execution Notes

[MARKDOWN] Section: Decision Dashboard Prototype
[CODE] Create mock decision outputs (probability + SHAP + RUL)
[MARKDOWN] Post-Execution Notes

[MARKDOWN] Summary: Operationalization Insights
[CODE] Export SHAP explanations to format for operator dashboards
[MARKDOWN] Post-Execution Notes
```

---

## Implementation Checklist

For each notebook:

- [ ] **Title & Objectives** markdown cell clearly states purpose
- [ ] **Setup** code cell imports all required libraries
- [ ] **Every code cell** is followed by a "Post-Execution Notes" markdown cell
- [ ] **Post-Execution Notes** use the standard template (5 bullet points)
- [ ] **Logical sections** separate distinct analytic phases
- [ ] **No conclusions premade**: reflection cells are templates for user to fill
- [ ] **Clear variable names**: output of code cells should be self-documenting
- [ ] **Section headers** explain "why" before code explains "how"

---

## Benefits of This Structure

| Aspect | Benefit |
|--------|---------|
| **Discipline** | Forces deliberate observation after every code execution |
| **Reproducibility** | Clear flow enables others to repeat and understand results |
| **Debugging** | Reflection cells catch unexpected outputs immediately |
| **Documentation** | Observations become inline documentation for future reference |
| **Iteration** | Templates guide experimentation without rigid conclusions |
| **Knowledge Transfer** | New team members understand not just code, but reasoning |

---

## Example: Properly Structured Section

### [MARKDOWN CELL]
```markdown
## 4. Feature Engineering: Stress Index Creation

The hypothesis from EDA: Overstrain Failure (OSF) is driven by the combination 
of high torque AND accumulated tool wear. We engineer a feature that captures 
this interaction:

**Stress Index = Torque [Nm] × Tool Wear [min]**

Expected outcome: OSF cases should show 2-3x higher Stress Index than non-OSF.
```

### [CODE CELL]
```python
# Create Stress Index feature
df['Stress Index'] = df['Torque [Nm]'] * df['Tool wear [min]']

# Validation: compare OSF vs non-OSF
osf_mean = df[df['OSF'] == 1]['Stress Index'].mean()
non_osf_mean = df[df['OSF'] == 0]['Stress Index'].mean()
ratio = osf_mean / non_osf_mean

print(f"Mean Stress Index (OSF=1): {osf_mean:.2f}")
print(f"Mean Stress Index (OSF=0): {non_osf_mean:.2f}")
print(f"Ratio (OSF/non-OSF): {ratio:.2f}x")
```

### [MARKDOWN CELL]
```markdown
### Post-Execution Notes (To Be Filled After Running This Cell)

- **What was expected:** 
  OSF cases show 2-3x higher Stress Index than non-OSF

- **What actually happened:** 
  [USER FILLS IN: e.g., "OSF mean was 12,067 vs non-OSF 4,238 → 2.85x ratio"]

- **Key observations:** 
  [USER FILLS IN: e.g., "Strong discrimination validates engineering approach"]

- **Issues / warnings:** 
  [USER FILLS IN: "None" or specific concerns]

- **Decisions / next steps:** 
  [USER FILLS IN: e.g., "Feature is statistically significant; include in model"]
```

---

## Status: EDA Notebook (1_EDA.ipynb)

The EDA notebook has been executed with outputs. Its structure aligns with this standard:
- ✓ Title & objectives clearly stated
- ✓ Logical sections from data quality → feature engineering → analysis
- ✓ Code cells produce outputs (visualizations, statistics)
- ✓ Markdown cells follow code cells with interpretations

For any new sections added to the EDA notebook, the Reflection Cell Rule applies.

---

## Next Steps

1. **Review this structure** with team members
2. **Create notebooks 2-5** using these templates
3. **Fill reflection cells** as you execute code
4. **Maintain consistency** across all notebooks

This disciplined approach transforms notebooks from ad-hoc scripts into executable documentation suitable for production ML projects.
