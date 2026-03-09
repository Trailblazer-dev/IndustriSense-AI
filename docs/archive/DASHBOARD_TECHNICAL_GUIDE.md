# Machine Maintenance Dashboard: Technical Guide

## Overview

This document explains how the IndustriSense-AI dashboard calculates and displays **Tool Wear** and **RUL (Remaining Useful Life)** values. It's designed for anyone who needs to understand the mechanics, from developers to stakeholders.

---

## The Problem We Solved

### What Was Broken Before

The dashboard was showing the same tool wear value (5.3 min) and RUL (248 min) for **all 10 machines**. This didn't make sense because:

- Different machines have different levels of wear
- Some machines should have more remaining life than others
- The values were unrealistic

### Why It Was Broken

The problem came down to **two pieces of data that didn't match**:

```
Scaled Data (what ML models use)
Tool Wear values: 1.41, -0.10, 0.14, -1.47, 0.33, ...
                  ↑ These are NORMALIZED numbers (not real minutes)

Raw Data (what humans understand)
Tool Wear values: 198, 101, 117, 14, 129, ...
                  ↑ These are REAL minutes
```

The dashboard was accidentally mixing these two:
- Getting scaled values (1.41, -0.10...) from the database
- Treating them as real minutes (telling users "Tool Wear: 1 min")
- Calculating RUL as: 253 - 1 = **252 min** (wrong!)

---

## How Data Gets Prepared

### Step 1: Raw Data Collection

**What is raw data?**

Raw data is the original, unmodified numbers from sensors:

```
Machine #6252:
- Air Temperature: 298.2 K
- Process Temperature: 310.5 K
- Rotational Speed: 850 rpm
- Torque: 42.3 Nm
- Tool Wear: 198 minutes  ← Actual measurement
- Stress Index: 8,357 (Torque × Tool Wear)
```

**Files:** `data/processed/features_engineered_raw.csv`

### Step 2: Scaling (Normalization)

**Why does this happen?**

Machine learning algorithms work better when numbers are on similar scales. For example:
- Temperature: 298 K
- Torque: 42 Nm
- Speed: 850 rpm

These numbers are very different sizes, which confuses ML models. So we **normalize** them:

```
Formula: Scaled Value = (Original Value - Average) / Standard Deviation

Example for Tool Wear:
- Original: 198 minutes
- Dataset Average: 120 minutes
- Dataset Std Dev: 55 minutes
- Scaled = (198 - 120) / 55 = 1.41

Example for another machine:
- Original: 14 minutes
- Scaled = (14 - 120) / 55 = -1.47
```

**Result:**
```
Scaled Tool Wear values: 1.41, -0.10, 0.14, -1.47, 0.33, ...
```

**File:** `data/processed/features_engineered_scaled.csv`

### Step 3: Model Training

**What happens:**

The XGBoost models learn using **scaled data**:

```
ML Model sees:
Input features (all scaled):  [0.41, -0.95, 1.23, 0.88, 1.41, ...]
Output prediction:           Failure probability (0-1) or Wear estimate

Model learns: "When scaled features look like [0.41, -0.95, ...], 
              the machine is likely to fail with 0.73 probability"
```

**Why scaled?**
- Prevents large numbers (like 850 rpm) from dominating small numbers (like 42 Nm)
- Helps algorithms converge faster
- Improves accuracy

---

## How the Dashboard Works

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      DASHBOARD REQUEST                      │
│                    (User visits /dashboard)                 │
└────────────────────────┬────────────────────────────────────┘
                         │
        ┌────────────────┴────────────────┐
        ▼                                 ▼
    LOAD SCALED DATA              LOAD RAW DATA
    (for ML models)               (for display)
    
    df.iloc[6252]                 df_raw.iloc[6252]
    [0.41, -0.95, 1.41...]        [298.2, 310.5, 198, ...]
        │                               │
        ▼                               ▼
    PREDICT FAILURE RISK          GET ACTUAL VALUES
    failure_prob =                tool_wear = 198
    classifier.predict()          rul = 253 - 198 = 55
        │                               │
        └───────────────┬───────────────┘
                        ▼
                  COMBINE RESULTS
                  {
                    id: 6252,
                    failure_risk: 73.2%,
                    tool_wear: 198.0 min,
                    rul: 55 min,
                    status: CRITICAL
                  }
                        │
                        ▼
                  SHOW ON WEBPAGE
```

### The Code Explained

#### Loading Data

```python
# Load SCALED data (for ML predictions)
df = pd.read_csv('data/processed/features_engineered_scaled.csv')
# Now df contains: [0.41, -0.95, 1.41, -1.47, ...]

# Load RAW data (for human-readable display)
df_raw = pd.read_csv('data/processed/features_engineered_raw.csv')
# Now df_raw contains: [298.2, 310.5, 198, 42.3, ...]
```

**Why two datasets?**
- ML models need **scaled** (it's what they learned on)
- Humans understand **raw** (actual minutes, Kelvin, rpm)

#### Displaying a Machine

```python
# Get the scaled data for this machine
row_scaled = df.iloc[6252]  
# Contains: [0.41, -0.95, 1.23, 0.88, 1.41, ...]

# Step 1: Predict failure risk (uses scaled data)
X_classifier = row_scaled[FEATURE_COLS].values.reshape(1, -1)
# Give the scaled features to the model
failure_prob = classifier.predict_proba(X_classifier)[0][1] * 100
# Model says: 73.2% chance of failure

# Step 2: Get actual tool wear (uses raw data)
row_raw = df_raw.iloc[6252]
# Contains: [298.2, 310.5, 850, 42.3, 198, ...]
tool_wear = float(row_raw['Tool wear [min]'])
# Get the actual measurement: 198 minutes

# Step 3: Calculate RUL
rul = max(0, 253 - int(tool_wear))
# RUL = 253 - 198 = 55 minutes remaining

# Step 4: Display
{
    'id': 6252,
    'failure_risk': 73.2,      # From ML prediction (scaled input)
    'tool_wear': 198.0,        # Actual measurement (raw data)
    'rul': 55,                 # 253 - actual wear
    'status': 'CRITICAL'       # Because 73.2% > 95%? No, because 73% > 50%
}
```

---

## Understanding Tool Wear & RUL

### What is Tool Wear?

**Definition:** The amount of degradation in the cutting/rotating component over time.

**Real-world example:**
```
Day 1:  Tool Wear = 0 min     (brand new)
Day 50: Tool Wear = 150 min   (50% degraded)
Day 100: Tool Wear = 253 min  (100% worn, needs replacement)
```

**In our data:**
- Minimum tool wear: 0 minutes (new tool)
- Maximum tool wear: 254 minutes (end of life)
- Average tool wear: ~120 minutes (midway)

### What is RUL (Remaining Useful Life)?

**Definition:** How many more minutes until the tool needs replacement.

**Formula:**
```
RUL = Maximum Tool Life (253) - Current Tool Wear

Examples:
- If tool_wear = 198 min, then RUL = 253 - 198 = 55 min remaining
- If tool_wear = 14 min, then RUL = 253 - 14 = 239 min remaining
- If tool_wear = 253 min, then RUL = 253 - 253 = 0 min (REPLACE NOW!)
```

**Why 253?**
- Looking at the historical data, the worst-case tool wear we saw was 253 minutes
- We use this as the "end of life" threshold
- If a machine reaches 253 min of wear, it should be replaced immediately

### Example Dashboard Display

```
Machine #6252:
  Failure Risk: 73.2%
  Tool Wear: 198.0 min
  RUL: 55 min
  Status: CRITICAL

Machine #4742:
  Failure Risk: 5.8%
  Tool Wear: 14.0 min
  RUL: 239 min
  Status: NORMAL
```

**What this means:**
- Machine #6252 has worn down significantly (198/253 = 78% worn)
- It only has 55 minutes left before replacement is recommended
- Machine #4742 is almost brand new
- It has 239 minutes before needing replacement

---

## Why This Approach is Technically Correct

### ✅ Using Scaled Data for ML Predictions

**Correct because:**
```
Training: Model learned with scaled features
          Input: [0.41, -0.95, 1.23, ...]
          Output: Probability

Prediction: Model expects same format
            Input: [0.41, -0.95, 1.23, ...]  ← Must be SCALED
            Output: Probability
```

**Wrong way:**
```
Training: Model learned with scaled features [0.41, -0.95, ...]
Prediction: Give it raw features [298.2, 850, 198, ...]  ✗ MISMATCH!
Result: Predictions would be garbage
```

**Analogy:** If you trained a dog to sit when you whistle high notes, but then try to train it with low notes, the dog gets confused.

### ✅ Using Raw Data for Display

**Correct because:**
- Users don't understand normalized numbers (what is 0.41?)
- Operators think in minutes, not standard deviations
- Real-world decisions need real-world numbers

**Example:**
```
Wrong display:
  "Tool Wear: 1.41 (scaled units)"
  → What does this mean? Is that good or bad?

Correct display:
  "Tool Wear: 198 minutes"
  → Clear! Tool is 78% worn out (198/253)
```

### ✅ Calculating RUL from Actual Wear

**Correct because:**
- For historical data, we know what actually happened
- Using the actual measured value shows ground truth
- Prevents confusion with predictions

**When you'd use predictions instead:**
```
Real-time scenario:
- New sensor data comes in (no historical wear measurement)
- Use: rul = 253 - regressor.predict(features)
- Shows: "Based on current conditions, wear is ~150, so RUL ~ 103"

Historical scenario (our dashboard):
- We already have measured tool wear
- Use: rul = 253 - actual_tool_wear
- Shows: "This machine actually wore 198, so RUL was actually 55"
```

---

## The Complete Data Flow

### Step-by-Step for Machine #6252

```
1. USER VISITS DASHBOARD
   └─> /dashboard route triggered

2. LOAD DATA
   ├─ df = features_engineered_scaled.csv
   │  └─ Row 6252: [0.41, -0.95, ..., 1.41, ...]
   └─ df_raw = features_engineered_raw.csv
      └─ Row 6252: [298.2, 310.5, ..., 198, ...]

3. RANDOM SAMPLING
   ├─ np.random.seed(42)
   ├─ sample_indices = [6252, 4684, 1731, ...]  (10 machines)
   └─ Starting with machine 6252

4. PREDICT FAILURE RISK
   ├─ Take scaled features from df
   ├─ Input to classifier: [0.41, -0.95, ..., 1.41]
   ├─ Model outputs: 0.732 (Raw probability)
   └─ Display: 73.2% (Multiply by 100)

5. GET TOOL WEAR
   ├─ Take raw data from df_raw
   ├─ Extract 'Tool wear [min]': 198.0
   └─ (This is the actual measured value)

6. CALCULATE RUL
   ├─ rul = 253 - int(198)
   ├─ rul = 253 - 198
   └─ rul = 55

7. DETERMINE STATUS
   ├─ failure_prob = 73.2%
   ├─ Is 73.2 >= 95? No
   ├─ Is 73.2 >= 50? Yes
   └─ status = "WARNING"

8. CREATE MACHINE OBJECT
   └─ {
        'id': 6252,
        'failure_risk': 73.2,
        'tool_wear': 198.0,
        'rul': 55,
        'status': 'WARNING',
        'timestamp': '2026-02-12T...'
      }

9. RENDER TO HTML
   └─ User sees card with all above values
```

---

## Common Questions

### Q: Why do we need TWO datasets?

**A:** Because ML and humans speak different languages:

```
ML Language (Scaled):
"This machine's features are [0.41, -0.95, 1.23, ...]"
(Good for math, bad for humans)

Human Language (Raw):
"This machine's tool is worn 198 minutes out of 253"
(Good for decisions, bad for math)
```

We use **scaled for ML predictions** and **raw for human decisions**.

### Q: Why is the maximum tool wear 253 minutes?

**A:** It's based on the actual data:
- We have 10,000 machine snapshots
- The worst wear observed was 253 minutes
- We use this as the "critical threshold" for replacement
- Any tool at 253 min should be replaced immediately

### Q: Can RUL go negative?

**A:** No, we use `max(0, 253 - tool_wear)`:
- If tool_wear = 254 min (somehow beyond max)
- Direct calculation: 253 - 254 = -1 (doesn't make sense)
- Our code: max(0, -1) = 0 (shows "replace immediately", safe default)

### Q: Why show only 10 machines on the dashboard?

**A:** Performance reasons:
- Showing 10,000 machines would make the page very slow
- Users can interact with 10 representative samples quickly
- Fixed seed (42) means same 10 machines always shown (consistency)

**To show more machines, change line 87:**
```python
# Current: Show 10 random machines
sample_indices = np.random.choice(len(df), 10, replace=False)

# To show 50:
sample_indices = np.random.choice(len(df), 50, replace=False)

# To show ALL:
sample_indices = np.arange(len(df))
```

### Q: How accurate are these values?

**Accuracy of Tool Wear & RUL:**
- 100% accurate (we're using actual measured values from the dataset)
- This is historical ground truth

**Accuracy of Failure Risk:**
- ~83% (our model's test recall)
- Means: when machine actually fails, we catch it 83% of the time
- Sometimes gives false alarms (predicts failure but doesn't happen)

---

## Summary

| Concept | What It Is | Where It Comes From | How It's Used |
|---------|-----------|-------------------|--------------|
| **Scaled Features** | Normalized (0 mean, 1 std dev) | features_engineered_scaled.csv | Input to ML models |
| **Raw Features** | Original sensor measurements | features_engineered_raw.csv | Display to users |
| **Tool Wear** | Degradation in minutes (0-253) | Actual measurement in raw data | Calculated RUL, status |
| **RUL** | 253 - actual tool wear | Derived calculation | Show time to replacement |
| **Failure Risk %** | Probability of imminent failure | ML model prediction | Determine status color |
| **Status** | CRITICAL/WARNING/NORMAL | Based on failure risk threshold | Visual indicator |

---

## For Developers

### File Locations

```
Dashboard Code:
  └─ web_app/app.py (lines 48-110)

Data Files:
  ├─ data/processed/features_engineered_scaled.csv
  │  └─ Used by: ML predictions
  └─ data/processed/features_engineered_raw.csv
     └─ Used by: Display values

HTML Templates:
  └─ web_app/templates/dashboard.html
     └─ Renders machines to screen
```

### Key Code Sections

**Loading data (line 48-63):**
```python
df = load_data()              # Load scaled
df_raw = load_raw_data()      # Load raw
```

**Dashboard route (line 81-112):**
```python
@app.route('/')
def dashboard():
    # Predict with scaled data
    # Display with raw data
    # Return rendered HTML
```

**Calculating values (line 95-103):**
```python
failure_prob = classifier.predict(scaled_features) * 100
tool_wear = df_raw['Tool wear [min]']
rul = max(0, 253 - int(tool_wear))
```

---

## Changelog

**Date:** February 12, 2026  
**Problem Fixed:** Dashboard showing same tool wear (5.3 min) for all machines  
**Solution:** Load scaled data for ML, raw data for display  
**Result:** Now shows realistic varied values (14-210 min tool wear, 43-239 min RUL)

---

**Questions?** Contact the development team or check the inline code comments in [app.py](web_app/app.py).
