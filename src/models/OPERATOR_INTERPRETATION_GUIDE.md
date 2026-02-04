
# IndustriSense-AI: Operator Interpretation Guide

## Version 1.0 (Prototype)
Date: 2026-02-02
Phase: 1 (Snapshot-based; Phase 2 requires temporal data)

## 1. Model Summary

### Failure Classification (Notebook 3)
- **Target:** Binary product failure (OSF, RNF, HDF, PWF, TWF vs. No Failure)
- **Model:** XGBoost Classifier with stratified 5-fold CV
- **Performance:** F2-Score ≈ [FROM CV RESULTS], Recall ≥ 0.95 (catches 95%+ actual failures)
- **Decision Rule:** Failure probability ≥ 0.5 → Alert maintenance

### Tool Wear Regression (Notebook 4)
- **Target:** Estimated tool wear in minutes (0-254 scale)
- **Model:** XGBoost Regressor with 5-fold CV
- **Performance:** MAE ≈ [FROM CV RESULTS] minutes, R² ≈ [FROM CV RESULTS]
- **RUL Conversion:** RUL = 254 - Predicted Wear (snapshot only, not degradation)

## 2. How to Use the Dashboard

### Color Codes
- **🔴 CRITICAL (Red):** Failure risk ≥ 70%
  - ACTION: Schedule maintenance immediately (within hours)
  - RATIONALE: Model 70%+ confident in failure prediction
  - NEXT STEP: Inspect, replace tool, verify sensor calibration

- **🟠 WARNING (Orange):** Failure risk 40-70%
  - ACTION: Monitor closely; schedule preventive maintenance (24-48 hours)
  - RATIONALE: Model suggests elevated risk; degradation may be ongoing
  - NEXT STEP: Log sensor data; plan tool replacement

- **🟢 NORMAL (Green):** Failure risk < 40%
  - ACTION: Continue normal operation; routine inspection
  - RATIONALE: Model indicates healthy operating condition
  - NEXT STEP: Maintain regular monitoring schedule

## 3. Understanding SHAP Explanations

### Global SHAP (All Machines)
- Shows which sensor features drive failure risk across entire dataset
- **Interpretation:** "Features on right → increase failure risk; features on left → decrease risk"
- **Use:** Understand which operating conditions are problematic

### Instance-Level SHAP (Individual Machine)
- Explains why THIS specific machine is at risk
- **Interpretation:** "Stress Index high + Torque elevated → failure risk +15%"
- **Use:** Communicate to operator why maintenance is recommended

## 4. Important Limitations

⚠️ **Snapshot-Based Estimation ONLY**
- Current models see ONE measurement per machine (cross-section, not time-series)
- TRUE RUL prognosis requires degradation trajectories over time
- Phase 2 infrastructure needed: Real-time logging + LSTM/CLSTM architectures

⚠️ **Training Data Assumptions**
- Model trained on 10,000 historical records
- Assumes NEW machines operate under similar conditions
- Requires periodic retraining as conditions evolve

⚠️ **Sensor Calibration Dependency**
- Predictions sensitive to sensor accuracy
- If sensors drift, model predictions become unreliable
- Recommend quarterly sensor calibration checks

## 5. Phase 2 Requirements (Future Enhancement)

To achieve TRUE RUL prognosis and temporal degradation tracking:

1. **Infrastructure:** Real-time sensor streaming (every 10-60 seconds)
2. **Data Requirements:** 
   - 20-50+ observations per machine
   - Weeks/months of operational data
   - Unique machine identifiers
   - Precise timestamps
3. **Modeling:** LSTM/CLSTM for degradation trajectory prediction
4. **Validation:** Test on held-out machines with known failure dates

## 6. Feedback Loop

To improve model performance:
1. Log operator actions ("tool replaced", "sensor cleaned", etc.)
2. Collect actual failure dates for failed machines
3. Compare model predictions vs. actual failures every month
4. Retrain models with updated data quarterly
5. Update risk thresholds based on false positive/negative rates

## 7. Contact & Support

- **Model Questions:** Data Science team
- **Operational Issues:** Maintenance supervisor
- **System Errors:** IT support

---
Document generated: 2026-02-02
IndustriSense-AI v1.0
