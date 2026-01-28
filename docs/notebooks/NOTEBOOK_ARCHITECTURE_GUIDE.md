# Jupyter Notebook Architecture & Design Guide

## Executive Summary

This project uses **disciplined Jupyter notebook structure** enforced through the **Reflection Cell Rule**: every code cell must be immediately followed by a markdown cell for post-execution observations.

This approach transforms notebooks from ad-hoc experimentation scripts into executable documentation suitable for ML/data science projects requiring reproducibility, knowledge transfer, and iterative development.

---

## Three Key Documents

### 1. NOTEBOOK_STRUCTURE_STANDARDS.md
- **What**: Comprehensive structural guidelines for all notebooks
- **For**: Understanding the discipline behind notebook design
- **Contains**: Core principles, reflection cell rule, notebook-specific structures, benefits

### 2. NOTEBOOK_SKELETON_TEMPLATES.md
- **What**: Cell-by-cell templates for notebooks 2-5
- **For**: Implementing new notebooks from scratch
- **Contains**: Complete markdown + code cell structure for:
  - Notebook 2: Feature Engineering
  - Notebook 3: Classification Modeling
  - Notebook 4: RUL Prognosis
  - Notebook 5: XAI & Interpretation

### 3. This Document
- **What**: Quick reference and implementation checklist
- **For**: Getting started, understanding flow, managing execution

---

## Reflection Cell Rule: The Core Discipline

### What It Is
After EVERY code cell, a mandatory markdown cell titled:
```
### Post-Execution Notes (To Be Filled After Running This Cell)
```

### The Template
```markdown
- **What was expected:**  
- **What actually happened:**  
- **Key observations:**  
- **Issues / warnings:**  
- **Decisions / next steps:**
```

### Why It Works
1. **Forces deliberation**: Can't just run code and move on
2. **Catches surprises**: Unexpected outputs are immediately visible
3. **Documents reasoning**: Future readers see WHY decisions were made
4. **Enables debugging**: Issues are recorded as they occur, not recreated later
5. **Supports iteration**: Clear record of what was tried and learned

---

## Notebook Execution Flow

```
1_EDA.ipynb [COMPLETED]
    ↓ (insights validated)
    ↓
2_Feature_Engineering.ipynb [TEMPLATE PROVIDED]
    ├─ Load data from EDA
    ├─ Create Stress Index
    ├─ Create Temperature Differential
    ├─ Create Anomaly Score
    └─ Save engineered features
    ↓
3_Classification_Modeling.ipynb [TEMPLATE PROVIDED]
    ├─ Load engineered features
    ├─ Calculate class weights (handle imbalance)
    ├─ Train XGBoost binary classifier
    ├─ Stratified 5-fold cross-validation
    ├─ Feature importance analysis
    └─ Save trained model
    ↓
4_RUL_Prognosis_Modeling.ipynb [TEMPLATE PROVIDED]
    ├─ Load engineered features
    ├─ Train XGBoost wear regressor
    ├─ Cross-validation evaluation
    ├─ Convert wear to RUL (254 - wear)
    └─ Save RUL model
    ↓
5_XAI_Interpretation.ipynb [TEMPLATE PROVIDED]
    ├─ Load trained models
    ├─ Generate SHAP explanations (classification)
    ├─ Generate SHAP explanations (regression)
    ├─ Instance-level decision explanations
    └─ Operator dashboard prototype
```

---

## Key Features of Notebook 1 (EDA) - Already Completed

**Status**: ✅ Fully executed with outputs

**Structure** (following the standards):
1. Title & Objectives
2. Data Loading & Imports (code → post-notes)
3. Data Quality Assessment (4 code cells → post-notes each)
4. Feature Engineering (multiple code cells → post-notes each)
5. Failure Analysis (code → post-notes)
6. Correlation Analysis (code → post-notes)
7. Anomaly Detection (code → post-notes)
8. Readiness Checklist (code → post-notes)
9. Summary

**Key outputs**:
- ✅ Data is clean (no missing values, no duplicates)
- ✅ Stress Index shows 2.85x discrimination for OSF
- ✅ Temperature Differential predicts HDF effectively
- ✅ Anomaly detection identifies 5% outliers with 1.5-2.0x failure correlation
- ✅ Class imbalance identified: scale_pos_weight ≈ 27.7

---

## Implementation Checklist for Notebooks 2-5

### For Each Notebook

- [ ] **Title & Objectives** cell clearly states:
  - Purpose of the notebook
  - Input data source
  - Expected outputs

- [ ] **Setup** code cell:
  - Imports all required libraries
  - Sets paths/configurations
  - Loads data
  - Prints verification messages

- [ ] **Every Code Cell** followed by **Post-Execution Notes** markdown cell with template

- [ ] **Logical Sections**:
  - Markdown header explains the section
  - 1-3 code cells implement the logic
  - Post-execution notes document findings
  - Next section clearly introduced

- [ ] **Final Summary** cell:
  - Key metrics/findings
  - What worked, what didn't
  - Transition to next notebook

- [ ] **Save artifacts**:
  - Trained models to disk
  - Processed datasets to `../data/processed/`
  - Visualizations if needed

---

## Notebook 2: Feature Engineering - Quick Start

**Purpose**: Transform raw sensor data using EDA insights

**Key engineering**:
1. **Stress Index** = Torque × Tool Wear
   - Captures mechanical stress accumulation
   - Expected: 2-3x higher for OSF cases

2. **Temperature Differential** = Process Temp - Air Temp
   - Captures thermal stress beyond ambient
   - Expected: Higher for HDF cases

3. **Anomaly Score** = Isolation Forest
   - Flags unusual sensor combinations
   - Expected: 5% anomalies, 1.5-2x failure correlation

**Outputs**:
- Engineered feature set (8 features)
- Saved as `../data/processed/engineered_features.csv`

---

## Notebook 3: Classification - Quick Start

**Purpose**: Train failure/no-failure binary classifier

**Key challenge**: Severe class imbalance (96.5% no-failure)

**Solution**:
- XGBoost with `scale_pos_weight ≈ 27.7`
- Penalize failure misclassification 27.7x more heavily
- Stratified 5-fold cross-validation
- Evaluate with F2-score (Recall 2× Precision)

**Target performance**:
- Recall ≥ 0.95 (catch 95%+ actual failures)
- Precision acceptable at lower threshold (OK to have false alarms for safety)

**Outputs**:
- Trained XGBoost classifier
- Feature importance rankings
- Cross-validation metrics

---

## Notebook 4: RUL Prognosis - Quick Start

**Purpose**: Estimate remaining useful life via tool wear prediction

**Important Note**: 
- This is **snapshot-based estimation**, NOT time-series forecasting
- Predicts current wear state → converts to RUL
- True time-series CLSTM is Phase 2 requirement

**Logic**:
```
RUL = 254 min (max capacity) - Predicted Tool Wear
```

**Example**:
- Current predicted wear: 200 min → RUL = 54 min (nearing end of life)
- Current predicted wear: 50 min → RUL = 204 min (plenty of life remaining)

**Outputs**:
- Trained XGBoost wear regressor
- RUL distribution analysis
- Model evaluation metrics (MAE, RMSE, R²)

---

## Notebook 5: XAI & Interpretation - Quick Start

**Purpose**: Explain model predictions to operators using SHAP

**Key deliverables**:
1. **Global feature importance** (mean |SHAP| values)
2. **Feature dependence plots** (how SHAP changes with feature value)
3. **Instance-level explanations** (why this prediction for this sample)
4. **Operator dashboard prototype** combining:
   - Failure probability
   - RUL estimate
   - Top 3 contributing features
   - Recommended action

**Example dashboard output**:
```
═══════════════════════════════════════
EQUIPMENT HEALTH ASSESSMENT
═══════════════════════════════════════
Health Status: ⚠️  AT RISK
Failure Probability: 72%
Remaining Useful Life: 47 minutes
───────────────────────────────────────
WHY THIS RISK LEVEL?
1. Stress Index +28% above normal (+30%)
2. Tool Wear at 84% capacity (+18%)
3. Temperature slightly elevated (+8%)
═══════════════════════════════════════
```

---

## Common Pitfalls & How to Avoid Them

| Pitfall | Solution |
|---------|----------|
| Forget to fill post-execution notes | Make it a habit before running next cell |
| Too many code cells without section headers | Add markdown explaining "why" before "how" |
| Conclusions hardcoded in code cells | Leave conclusions in post-execution notes as templates |
| No clear data flow between notebooks | Save intermediate outputs to `../data/processed/` |
| Models not saved after training | Always save trained models using joblib/pickle |
| Unclear feature sources | Document which notebook creates which feature |
| Copy-paste code duplication | Use utility functions or reference prior notebooks |

---

## File Organization

```
IndustriSense-AI/
├── notebooks/
│   ├── 1_EDA.ipynb [COMPLETED]
│   ├── 2_Feature_Engineering.ipynb [USE TEMPLATE]
│   ├── 3_Failure_Classification_Modeling.ipynb [USE TEMPLATE]
│   ├── 4_RUL_Prognosis_Modeling.ipynb [USE TEMPLATE]
│   ├── 5_XAI_and_Interpretation.ipynb [USE TEMPLATE]
│
├── data/
│   ├── raw/
│   │   ├── ai4i2020.csv [input]
│   │   └── predictive_maintenance.csv
│   └── processed/
│       └── engineered_features.csv [created by notebook 2]
│
├── src/
│   ├── models/
│   │   ├── classification_model.py
│   │   └── rul_model.py
│   ├── features/
│   │   └── build_features.py
│   └── visualization/
│       └── visualize.py
│
├── NOTEBOOK_STRUCTURE_STANDARDS.md
├── NOTEBOOK_SKELETON_TEMPLATES.md
└── README.md
```

---

## Execution Workflow

### When Creating a New Notebook

1. **Copy cell template** from NOTEBOOK_SKELETON_TEMPLATES.md
2. **Paste into Jupyter** (manually or via notebook API)
3. **Adapt to your context** (paths, feature names, etc.)
4. **Execute each cell** one at a time
5. **Fill post-execution notes** before moving to next cell
6. **Save model artifacts** when complete

### When Debugging

1. **Re-read the post-execution notes** from the failing cell
2. **Check what was "expected"** vs **what actually happened**
3. **Review the decision** made after that cell
4. **Trace dependencies** through prior cells
5. **Update post-execution notes** with debug findings

### When Handing Off

1. **Notes already contain reasoning** - no additional documentation needed
2. **Next person can see the flow** - from code to interpretation to decision
3. **Issues are documented** - "issues/warnings" section shows what went wrong
4. **Assumptions are explicit** - all in post-execution observations

---

## Success Criteria

A well-structured project notebook has:

✅ **Clear purpose**: Title cell states objectives explicitly
✅ **Logical flow**: Each section builds on prior findings
✅ **Every code cell followed by reflection**: No exceptions
✅ **Filled notes**: Team has documented observations as code executes
✅ **Saved artifacts**: Models, features, metrics persist between notebooks
✅ **No hardcoded conclusions**: Interpretations in post-execution notes, not code
✅ **Reproducible**: Another user can follow the same steps and get same results
✅ **Transferable**: Next person understands not just code, but reasoning

---

## Quick Reference: When to Use Each Document

| Question | Answer in |
|----------|-----------|
| "What is the overall design philosophy?" | NOTEBOOK_STRUCTURE_STANDARDS.md |
| "How do I structure notebook 2?" | NOTEBOOK_SKELETON_TEMPLATES.md (Notebook 2 section) |
| "What goes in a post-execution cell?" | NOTEBOOK_STRUCTURE_STANDARDS.md (Reflection Cell Rule) |
| "What is the data flow between notebooks?" | This document (Notebook Execution Flow section) |
| "Where do trained models go?" | This document (File Organization section) |
| "What metrics should notebook 3 report?" | NOTEBOOK_SKELETON_TEMPLATES.md (Notebook 3) |

---

## Next Steps

1. **Review** NOTEBOOK_STRUCTURE_STANDARDS.md (15 min read)
2. **Study** NOTEBOOK_SKELETON_TEMPLATES.md (30 min to understand patterns)
3. **Create** notebook 2 using the template (adapt as needed)
4. **Execute** notebook 2 cell-by-cell, filling post-execution notes
5. **Validate** engineered features match EDA insights
6. **Proceed** to notebooks 3, 4, 5 in sequence

---

## Contact & Questions

If unclear about structure:
- Check NOTEBOOK_STRUCTURE_STANDARDS.md for philosophy
- Check NOTEBOOK_SKELETON_TEMPLATES.md for concrete examples
- Examine 1_EDA.ipynb for a completed reference implementation

The discipline of post-execution notes will be evident once you run your first notebook—the value of documented observations becomes clear immediately.

**Happy experimenting! Document as you go. 📓**
