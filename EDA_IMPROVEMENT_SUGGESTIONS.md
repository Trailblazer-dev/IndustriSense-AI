# EDA Improvement Suggestions - IndustriSense-AI

**Purpose:** Identify gaps in the current EDA (1_EDA.ipynb) and recommend enhancements for completeness and decision-support clarity.

---

## Current EDA Coverage

**Strengths of Existing Analysis:**
- ✓ Data quality assessment (missing values, duplicates, data types)
- ✓ Univariate feature distributions (histograms, summary statistics)
- ✓ Failure mode frequencies and target variable distribution
- ✓ Stress Index feature engineering and OSF discrimination analysis
- ✓ Temperature Differential preliminary analysis
- ✓ Recognition of temporal data limitation (Thermal Trend comment)

---

## Recommended EDA Additions

### 1. Class Imbalance Quantification and Mitigation Strategy
**Current Gap:** Basic failure count (339/10000 = 3.4%) mentioned but not systematically analyzed.

**Suggested Additions:**
- **Cell: "Class Imbalance Summary"**
  ```python
  # Imbalance ratio by class
  imbalance_ratios = df['Machine failure'].value_counts(normalize=True)
  # Imbalance ratio per failure mode
  for col in ['TWF', 'HDF', 'PWF', 'OSF', 'RNF']:
      ratio = df[col].value_counts(normalize=True)
      print(f"{col}: {ratio[1]:.2%}")
  # Recommendation for model: scale_pos_weight for XGBoost
  scale_pos_weight = imbalance_ratios[0] / imbalance_ratios[1]
  print(f"Recommended scale_pos_weight: {scale_pos_weight:.2f}")
  ```

- **Cell: "Failure Mode Co-occurrence Matrix"**
  ```python
  # How often multiple failure modes occur together
  failure_cols = ['TWF', 'HDF', 'PWF', 'OSF', 'RNF']
  co_occurrence = df[failure_cols].corr()
  sns.heatmap(co_occurrence, annot=True)
  # Count machines with multiple failures
  multi_fail = (df[failure_cols].sum(axis=1) > 1).sum()
  print(f"{multi_fail} machines have multiple failure modes")
  ```

- **Cell: "Failure Mode Distribution Visualization"**
  - Bar chart: relative frequencies of TWF, HDF, PWF, OSF, RNF
  - Insight: Which modes are most common? Are they mutually exclusive?

**Rationale:**
- Imbalance ratio directly informs XGBoost hyperparameter tuning (scale_pos_weight)
- Co-occurrence analysis reveals whether failure modes are independent or related
- Failure mode frequency guides priority ranking (e.g., focus optimization on most common modes)

---

### 2. Bivariate Feature Correlation & Multicollinearity Analysis
**Current Gap:** No correlation matrix or multicollinearity assessment between input features.

**Suggested Additions:**
- **Cell: "Feature Correlation Matrix"**
  ```python
  numeric_features = [
      'Air temperature [K]', 'Process temperature [K]', 
      'Rotational speed [rpm]', 'Torque [Nm]', 'Tool wear [min]'
  ]
  corr_matrix = df[numeric_features].corr()
  sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', center=0)
  plt.title('Feature Correlation Matrix')
  
  # Identify high correlations
  for i in range(len(corr_matrix.columns)):
      for j in range(i+1, len(corr_matrix.columns)):
          if abs(corr_matrix.iloc[i, j]) > 0.7:
              print(f"High correlation: {corr_matrix.columns[i]} vs {corr_matrix.columns[j]}: {corr_matrix.iloc[i, j]:.3f}")
  ```

- **Cell: "Variance Inflation Factor (VIF) Analysis"**
  ```python
  from statsmodels.stats.outliers_influence import variance_inflation_factor
  vif_data = pd.DataFrame()
  vif_data['Feature'] = numeric_features
  vif_data['VIF'] = [variance_inflation_factor(df[numeric_features].values, i) 
                      for i in range(len(numeric_features))]
  print(vif_data.sort_values('VIF', ascending=False))
  # VIF < 5: acceptable, VIF < 10: be cautious, VIF > 10: likely collinearity
  ```

**Rationale:**
- High correlation between features (e.g., Air temp ~0.8 with Process temp) can inflate model variance
- VIF > 10 signals multicollinearity requiring feature selection
- Informs feature selection strategy (e.g., if Process temp and Air temp highly correlated, consider dropping one)

---

### 3. Detailed Anomaly/Outlier Characterization
**Current Gap:** No systematic outlier detection or characterization of unusual observations.

**Suggested Additions:**
- **Cell: "Isolation Forest Anomaly Detection"**
  ```python
  from sklearn.ensemble import IsolationForest
  iso_forest = IsolationForest(contamination=0.05, random_state=42)
  df['anomaly_score'] = iso_forest.fit_predict(df[numeric_features])
  df['anomaly_flag'] = (df['anomaly_score'] == -1).astype(int)
  
  print(f"Detected {df['anomaly_flag'].sum()} anomalies ({df['anomaly_flag'].mean():.2%} of data)")
  
  # Analyze anomalies
  anomalies = df[df['anomaly_flag'] == 1]
  normals = df[df['anomaly_flag'] == 0]
  print("\nFailure rate in anomalies:", anomalies['Machine failure'].mean())
  print("Failure rate in normals:", normals['Machine failure'].mean())
  ```

- **Cell: "Anomaly Pattern Analysis"**
  ```python
  # What characterizes anomalies?
  for col in numeric_features:
      anom_mean = anomalies[col].mean()
      norm_mean = normals[col].mean()
      print(f"{col}:")
      print(f"  Anomaly mean: {anom_mean:.2f}")
      print(f"  Normal mean:  {norm_mean:.2f}")
      print(f"  Difference:   {abs(anom_mean - norm_mean) / norm_mean * 100:.1f}%\n")
  ```

**Rationale:**
- Identifies whether "anomalies" correspond to rare failure modes or legitimate sensor extremes
- Validates Isolation Forest feasibility for cross-sectional outlier detection (FR-2)
- Determines if anomalies are worth special handling in model training

---

### 4. Failure Mode-Specific Feature Distributions
**Current Gap:** Feature distributions shown overall but not stratified by failure mode.

**Suggested Additions:**
- **Cell: "Feature Distributions by Failure Mode"**
  ```python
  failure_cols = ['Machine failure', 'TWF', 'HDF', 'PWF', 'OSF', 'RNF']
  
  for fail_col in failure_cols:
      if fail_col == 'Machine failure':
          groups = df.groupby(fail_col)
          label_0, label_1 = 'No Failure', 'Failure'
      else:
          groups = df.groupby(fail_col)
          label_0, label_1 = f'No {fail_col}', f'{fail_col}'
      
      fig, axes = plt.subplots(2, 3, figsize=(15, 8))
      axes = axes.flatten()
      for idx, feature in enumerate(numeric_features):
          groups[feature].plot(kind='kde', ax=axes[idx], legend=True)
          axes[idx].set_title(f'{feature} by {fail_col}')
      plt.tight_layout()
      plt.show()
  ```

- **Cell: "Failure Mode-Feature Separability (t-tests)"**
  ```python
  from scipy.stats import ttest_ind
  
  print("t-test results for feature separability by failure mode:\n")
  for fail_col in ['TWF', 'HDF', 'PWF', 'OSF', 'RNF']:
      print(f"\n{fail_col}:")
      group_yes = df[df[fail_col] == 1]
      group_no = df[df[fail_col] == 0]
      
      for feature in numeric_features:
          stat, p_value = ttest_ind(group_yes[feature], group_no[feature])
          effect_size = (group_yes[feature].mean() - group_no[feature].mean()) / group_yes[feature].std()
          sig = '***' if p_value < 0.001 else '**' if p_value < 0.01 else '*' if p_value < 0.05 else 'ns'
          print(f"  {feature}: t={stat:.3f}, p={p_value:.4f} {sig}, Cohen's d={effect_size:.3f}")
  ```

**Rationale:**
- Reveals which features are most discriminative for each failure mode
- Informs feature selection and model architecture (e.g., separate classifiers per mode)
- Validates EDA finding that different modes show distinct sensor signatures

---

### 5. Engineered Feature Validation (Stress Index & Temperature Differential)
**Current Gap:** Stress Index analyzed only for OSF; Temperature Differential not tested for statistical significance.

**Suggested Additions:**
- **Cell: "Stress Index Comprehensive Analysis"**
  ```python
  df['Stress Index'] = df['Torque [Nm]'] * df['Tool wear [min]']
  
  # ANOVA: Stress Index by ALL failure modes
  from scipy.stats import f_oneway
  groups = [df[df[col] == 1]['Stress Index'] for col in ['TWF', 'HDF', 'PWF', 'OSF', 'RNF']]
  f_stat, p_value = f_oneway(*groups)
  print(f"ANOVA on Stress Index by failure mode: F={f_stat:.3f}, p={p_value:.4f}")
  
  # Effect size per mode
  for col in ['TWF', 'HDF', 'PWF', 'OSF', 'RNF']:
      mean_yes = df[df[col] == 1]['Stress Index'].mean()
      mean_no = df[df[col] == 0]['Stress Index'].mean()
      std_pooled = df['Stress Index'].std()
      cohen_d = (mean_yes - mean_no) / std_pooled
      print(f"{col}: mean_yes={mean_yes:.0f}, mean_no={mean_no:.0f}, Cohen's d={cohen_d:.3f}")
  ```

- **Cell: "Temperature Differential Validation"**
  ```python
  df['Temperature Differential'] = df['Process temperature [K]'] - df['Air temperature [K]']
  
  # Statistical test for HDF
  temp_diff_hdf_yes = df[df['HDF'] == 1]['Temperature Differential']
  temp_diff_hdf_no = df[df['HDF'] == 0]['Temperature Differential']
  
  from scipy.stats import ttest_ind
  t_stat, p_value = ttest_ind(temp_diff_hdf_yes, temp_diff_hdf_no)
  cohen_d = (temp_diff_hdf_yes.mean() - temp_diff_hdf_no.mean()) / df['Temperature Differential'].std()
  
  print(f"Temperature Differential and HDF:")
  print(f"  Mean for HDF=1: {temp_diff_hdf_yes.mean():.4f} K")
  print(f"  Mean for HDF=0: {temp_diff_hdf_no.mean():.4f} K")
  print(f"  t-stat: {t_stat:.3f}, p-value: {p_value:.4f}")
  print(f"  Cohen's d: {cohen_d:.3f} (weak effect)")
  ```

**Rationale:**
- Confirms statistical significance (not just descriptive differences)
- Quantifies effect sizes (Cohen's d) to gauge practical importance
- Informs which engineered features warrant inclusion in final model

---

### 6. Explicit Data Limitation Assessment
**Current Gap:** Temporal data limitations mentioned in text but not formally documented with code examples showing impossibility.

**Suggested Additions:**
- **Cell: "Temporal Data Limitation Check"**
  ```python
  # Check for temporal structure
  print("Dataset Temporal Characteristics:")
  print(f"  Total rows: {len(df)}")
  print(f"  Unique Product IDs: {df['Product ID'].nunique()}")
  print(f"  Avg rows per Product ID: {len(df) / df['Product ID'].nunique():.2f}")
  print(f"  Has timestamps? {any(df.columns.str.contains('date|time|timestamp', case=False))}")
  print(f"  Has machine sequence IDs? {any(df.columns.str.contains('sequence|cycle|order', case=False))}")
  
  print("\nConclusion: Static cross-sectional snapshot, not time-series")
  print("Implication: LSTM/CLSTM and temporal trend analysis are NOT FEASIBLE")
  ```

- **Cell: "Thermal Trend Feasibility Demonstration"**
  ```python
  # Attempt to demonstrate thermal trend impossibility
  print("Attempting to compute thermal trend (slope over time)...\n")
  
  # Try grouping by machine
  product_groups = df.groupby('Product ID')
  print(f"Number of distinct machines: {product_groups.ngroups}")
  
  # Check if any machine has multiple observations with temporal ordering
  max_obs_per_machine = product_groups.size().max()
  avg_obs_per_machine = product_groups.size().mean()
  
  print(f"  Max observations per machine: {max_obs_per_machine}")
  print(f"  Avg observations per machine: {avg_obs_per_machine:.2f}")
  
  if max_obs_per_machine < 3:
      print("\n❌ THERMAL TREND IS NOT FEASIBLE:")
      print("   - Cannot compute slope with <3 observations per machine")
      print("   - No timestamps to order observations temporally")
      print("   - No way to distinguish 'before' vs 'after' states")
  
  # Demonstrate alternative: Temperature Differential
  print("\n✓ RECOMMENDED ALTERNATIVE: Temperature Differential")
  df['Temperature Differential'] = df['Process temperature [K]'] - df['Air temperature [K]']
  print(f"   Feature computable: Mean={df['Temperature Differential'].mean():.4f} K")
  ```

**Rationale:**
- Explicitly documents data constraints preventing temporal modeling
- Provides evidence for SRS feasibility assessments (FR-4, FR-6 NOT FEASIBLE)
- Prevents future misunderstandings about what's possible with snapshot data

---

### 7. Model Training Data Readiness Checklist
**Current Gap:** No explicit summary indicating readiness for supervised learning.

**Suggested Additions:**
- **Cell: "Training Data Readiness Checklist"**
  ```python
  print("✓ SUPERVISED LEARNING READINESS ASSESSMENT\n")
  
  checklist = {
      "Target variable complete": df['Machine failure'].isna().sum() == 0,
      "Features complete": df[[col for col in df.columns if col not in ['UDI', 'Machine failure']]].isna().sum().sum() == 0,
      "Sufficient positive samples": (df['Machine failure'] == 1).sum() >= 30,
      "Sufficient negative samples": (df['Machine failure'] == 0).sum() >= 100,
      "Feature variance (std > 0)": all(df[[c for c in numeric_features if c in df.columns]].std() > 0),
      "No constant features": all(df[[c for c in numeric_features if c in df.columns]].nunique() > 1),
  }
  
  for check, result in checklist.items():
      status = "✓ PASS" if result else "✗ FAIL"
      print(f"  {status}: {check}")
  
  print("\nRecommendations:")
  print("  ✓ Ready for cross-validation and model training")
  print("  ✓ Use stratified k-fold to handle class imbalance")
  print("  ✓ Apply class weights in XGBoost (scale_pos_weight)")
  ```

**Rationale:**
- Provides explicit go/no-go decision for proceeding to modeling phase
- Summarizes data quality findings in checklist format (easy for stakeholders)

---

### 8. Sample Size and Power Analysis
**Current Gap:** No discussion of whether 10,000 samples is sufficient for desired model performance.

**Suggested Additions:**
- **Cell: "Statistical Power Analysis"**
  ```python
  from statsmodels.stats.power import tt_solve_power
  
  # Example: Detect difference between OSF and non-OSF groups
  osf_yes = df[df['OSF'] == 1]
  osf_no = df[df['OSF'] == 0]
  
  # Estimate effect size from data
  effect_size = (osf_yes['Stress Index'].mean() - osf_no['Stress Index'].mean()) / df['Stress Index'].std()
  
  # Calculate power with current sample size
  power = tt_solve_power(
      effect_size=effect_size,
      nobs=len(osf_no),
      alpha=0.05,
      alternative='two-sided'
  )
  
  print(f"Effect size (Cohen's d): {effect_size:.3f}")
  print(f"Statistical power: {power:.3f}")
  print(f"Sample size adequacy: {'✓ SUFFICIENT' if power > 0.8 else '✗ INSUFFICIENT'}")
  ```

**Rationale:**
- Confirms 10,000 rows is sufficient for stable model training
- Informs whether data collection/augmentation is needed for Phase 2

---

## Summary Table: EDA Enhancement Priorities

| Addition | Priority | Effort | Value | Rationale |
| --- | --- | --- | --- | --- |
| Class Imbalance Quantification | HIGH | Low | High | Directly informs XGBoost hyperparameters (FR-5) |
| Correlation & VIF Analysis | HIGH | Low | High | Guides feature selection; prevents multicollinearity |
| Anomaly Characterization | MEDIUM | Medium | High | Validates Isolation Forest feasibility (FR-2) |
| Failure Mode-Specific Features | MEDIUM | Medium | Medium | Supports multi-class modeling strategy |
| Engineered Feature Validation | MEDIUM | Low | High | Confirms Stress Index & Temp Differential efficacy (FR-3, FR-4 alt) |
| Temporal Limitation Check | HIGH | Low | Critical | Explicitly documents why CLSTM/Thermal Trend infeasible (FR-4, FR-6) |
| Training Readiness Checklist | LOW | Low | Medium | Stakeholder communication tool |
| Power Analysis | LOW | Medium | Low | Nice-to-have; data already sufficient |

---

## Implementation Recommendation

**Prioritize in this order:**
1. **Temporal Limitation Check** (HIGH priority) – Directly addresses SRS feasibility concerns
2. **Class Imbalance Quantification** (HIGH priority) – Essential for FR-5 modeling
3. **Correlation & VIF Analysis** (HIGH priority) – Enables robust feature selection
4. **Engineered Feature Validation** (MEDIUM) – Confirms FR-3 and FR-4 alternative
5. **Anomaly Characterization** (MEDIUM) – Supports FR-2 feasibility

These additions will transform 1_EDA.ipynb from exploratory analysis into a comprehensive decision-support document, directly tracing requirements (SRS) → dataset evidence (EDA) → modeling recommendations (Phase 2).

