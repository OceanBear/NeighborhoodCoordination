# Detailed Explanation of the CCA (Canonical Correlation Analysis) Process

## Table of Contents
1. [What is CCA and Why Do We Use It?](#what-is-cca-and-why-do-we-use-it)
2. [Understanding the Data Structure](#understanding-the-data-structure)
3. [Step-by-Step CCA Process](#step-by-step-cca-process)
4. [Mathematical Details Explained Simply](#mathematical-details-explained-simply)
5. [Permutation Testing Explained](#permutation-testing-explained)
6. [Complete Example Walkthrough](#complete-example-walkthrough)

---

## What is CCA and Why Do We Use It?

### The Problem We're Trying to Solve

Imagine you have two neighborhoods (let's call them Neighborhood A and Neighborhood B). Each neighborhood has multiple cell types (like T cells, B cells, macrophages, etc.). 

**Question:** How similar are these two neighborhoods in terms of their cell type composition?

**The Challenge:** 
- Each neighborhood has **5 different features** (type, type_prob, color_R, color_G, color_B)
- You can't just compare one number to another number
- You need to compare **multiple features at once**

### What is CCA?

**Canonical Correlation Analysis (CCA)** is a statistical method that:
1. Takes two sets of data (each with multiple features)
2. Finds the **best way to combine** the features from each set
3. Calculates how well these combined scores match between the two sets

### Simple Analogy

Think of comparing two houses:
- **House A** has: location score, size score, price score, condition score, neighborhood score
- **House B** has: location score, size score, price score, condition score, neighborhood score

You can't just say "House A's location is better than House B's location" - that's only one aspect!

**CCA does this:**
- It finds weights for each feature (e.g., location × 0.3 + size × 0.2 + price × 0.1 + ...)
- It creates a **single overall score** for House A and a **single overall score** for House B
- It finds the weights that make these scores **most similar** (highest correlation)

---

## Understanding the Data Structure

Before we dive into CCA, let's understand what data we're working with.

### 1. Raw Cell Data

**What it is:** A table where each row represents one cell.

**Columns include:**
- `X:X`, `Y:Y`: Spatial coordinates (where the cell is located)
- `ClusterName`: What type of cell it is
- `File Name`: Which patient/sample it came from
- `neighborhood20`: Which neighborhood (1-7) the cell belongs to
- `type`, `type_prob`, `color_R`, `color_G`, `color_B`: Features describing the cell

**Example:**
```
Cell ID | X:X  | Y:Y  | ClusterName | File Name      | neighborhood20 | type  | type_prob
--------|------|------|-------------|----------------|----------------|-------|----------
1       | 100  | 200  | T_cell      | patient_001    | 1              | 0.5   | 0.8
2       | 105  | 205  | B_cell      | patient_001    | 1              | 0.3   | 0.6
3       | 150  | 250  | T_cell      | patient_001    | 2              | 0.6   | 0.9
```

### 2. nsctf (Neighborhood-Specific Cell Type Frequency)

**What it is:** A transformed version of the data that summarizes cell type information for each patient in each neighborhood.

**How it's calculated:**
1. **Group cells** by (patient, neighborhood)
2. **Calculate the mean** of each feature within each group
3. **Apply log transformation:** `nsctf = log(0.001 + mean)`

**Why log transformation?**
- Some features might be 0 (no cells of that type), and log(0) is undefined
- Adding 0.001 prevents this: log(0.001) ≈ -6.91
- Log transformation also makes the data more "normal" (statistically speaking)

**Result structure:**
```
nsctf is a table with:
- Rows: (neighborhood, patient) pairs
- Columns: type, type_prob, color_R, color_G, color_B

Example:
                    type    type_prob  color_R  color_G  color_B
(0, patient_001)    0.917   -0.263     3.487    5.280    3.822
(0, patient_002)    0.523   -0.321     3.245    4.890    3.650
(1, patient_001)    0.375   -0.299     3.779    4.824    3.811
(1, patient_002)    0.421   -0.356     3.512    4.567    3.789
```

**What each value means:**
- `nsctf[0, patient_001, 'type'] = 0.917` means: "For patient_001 in neighborhood 0, the average 'type' value (after log transformation) is 0.917"

---

## Step-by-Step CCA Process

Now let's walk through exactly what happens when we run CCA.

### Step 1: Choose Two Neighborhoods to Compare

**What happens:**
```python
for cn_i in [0, 1, 2, 3, 4, 5, 6]:
    for cn_j in [0, 1, 2, 3, 4, 5, 6]:
        if cn_i < cn_j:  # Only compare each pair once
            # Perform CCA
```

**Why nested loops?**
- We want to compare **every pair** of neighborhoods
- Neighborhood 0 vs 1, 0 vs 2, 0 vs 3, ..., 5 vs 6
- Total: 21 pairs (7 choose 2 = 21)

**Example:** Let's say we're comparing `cn_i = 0` and `cn_j = 1`

---

### Step 2: Find Common Patients

**What happens:**
```python
patients_cn_i = nsctf.loc[cn_i].index  # All patients in neighborhood 0
patients_cn_j = nsctf.loc[cn_j].index  # All patients in neighborhood 1

common_patients = list(set(patients_cn_i) & set(patients_cn_j))
```

**Why do we need common patients?**
- We can only compare neighborhoods if we have data from the **same patients** in both
- Like comparing two classes' test scores - you need the same students in both classes

**Example:**
- Neighborhood 0 has patients: [A, B, C, D]
- Neighborhood 1 has patients: [A, B, E, F]
- Common patients: [A, B]

---

### Step 3: Build X and Y Matrices

**What happens:**
```python
# Extract data for neighborhood 0 (only common patients)
x = nsctf.loc[cn_i].loc[common_patients].values
# Shape: (n patients, 5 features)

# Extract data for neighborhood 1 (only common patients)
y = nsctf.loc[cn_j].loc[common_patients].values
# Shape: (n patients, 5 features)
```

**What are X and Y?**
- **X matrix:** Data from neighborhood 0
- **Y matrix:** Data from neighborhood 1
- Both have the **same patients** (in the same order)
- Both have **5 columns** (one for each feature)

**Example:**
```
X (neighborhood 0):
Patient A:  [0.917, -0.263, 3.487, 5.280, 3.822]
Patient B:  [0.523, -0.321, 3.245, 4.890, 3.650]

Y (neighborhood 1):
Patient A:  [0.375, -0.299, 3.779, 4.824, 3.811]
Patient B:  [0.421, -0.356, 3.512, 4.567, 3.789]
```

**Visual representation:**
```
X = [Patient A's features in neighborhood 0]
    [Patient B's features in neighborhood 0]

Y = [Patient A's features in neighborhood 1]
    [Patient B's features in neighborhood 1]
```

---

### Step 4: Run CCA

**What happens:**
```python
cca = CCA(n_components=1, max_iter=5000)
ccx, ccy = cca.fit_transform(x, y)
observed_correlation = pearsonr(ccx[:,0], ccy[:,0])[0]
```

Let's break this down **very slowly**:

#### 4.1: Initialize CCA

```python
cca = CCA(n_components=1, max_iter=5000)
```

**What this does:**
- Creates a CCA object
- `n_components=1`: We only want **one** canonical component (the best one)
- `max_iter=5000`: Maximum 5000 iterations to find the solution

**What is a "component"?**
- Think of it as a "summary score"
- CCA can create multiple components (like PCA), but we only need the first (best) one

#### 4.2: Fit and Transform

```python
ccx, ccy = cca.fit_transform(x, y)
```

**What this does (step by step):**

**Step 4.2.1: CCA finds weight vectors**

CCA calculates two weight vectors:
- `w_x = [w1, w2, w3, w4, w5]` (for X matrix)
- `w_y = [w1, w2, w3, w4, w5]` (for Y matrix)

**What are weights?**
- Each weight tells us how important that feature is
- Example: `w_x = [0.3, 0.1, 0.2, 0.2, 0.2]` means:
  - Feature 1 (type) is most important (0.3)
  - Features 2-5 are less important (0.1, 0.2, 0.2, 0.2)

**Step 4.2.2: Calculate weighted scores**

For each patient, calculate:
```
Patient A's score in neighborhood 0 (ccx[A]):
  = X[A, 0] × w_x[0] + X[A, 1] × w_x[1] + X[A, 2] × w_x[2] + X[A, 3] × w_x[3] + X[A, 4] × w_x[4]
  = 0.917 × w1 + (-0.263) × w2 + 3.487 × w3 + 5.280 × w4 + 3.822 × w5

Patient A's score in neighborhood 1 (ccy[A]):
  = Y[A, 0] × w_y[0] + Y[A, 1] × w_y[1] + Y[A, 2] × w_y[2] + Y[A, 3] × w_y[3] + Y[A, 4] × w_y[4]
  = 0.375 × w1 + (-0.299) × w2 + 3.779 × w3 + 4.824 × w4 + 3.811 × w5
```

**Step 4.2.3: CCA optimizes the weights**

CCA tries different weight combinations until it finds the one that makes `ccx` and `ccy` **most correlated**.

**What does "most correlated" mean?**
- If `ccx` and `ccy` are highly correlated, when one goes up, the other goes up too
- CCA finds weights that maximize this relationship

**Result:**
```
ccx = [Patient A's score, Patient B's score, ...]  (one score per patient for neighborhood 0)
ccy = [Patient A's score, Patient B's score, ...]  (one score per patient for neighborhood 1)
```

#### 4.3: Calculate Correlation

```python
observed_correlation = pearsonr(ccx[:,0], ccy[:,0])[0]
```

**What this does:**
- `ccx[:,0]` means "all rows, column 0" = all patients' scores for neighborhood 0
- `ccy[:,0]` means "all rows, column 0" = all patients' scores for neighborhood 1
- `pearsonr()` calculates the Pearson correlation coefficient between these two score vectors

**What is Pearson correlation?**
- A number between -1 and 1
- **1.0**: Perfect positive correlation (when one goes up, the other always goes up)
- **0.0**: No correlation (no relationship)
- **-1.0**: Perfect negative correlation (when one goes up, the other always goes down)

**Example:**
```
ccx = [2.5, 1.8, 3.2, 2.1]  (scores for 4 patients in neighborhood 0)
ccy = [2.4, 1.9, 3.1, 2.0]  (scores for 4 patients in neighborhood 1)

These are very similar! Correlation ≈ 0.98 (very high)
```

---

## Mathematical Details Explained Simply

### The CCA Objective Function

**What CCA is trying to do:**

```
Maximize: correlation(X · w_x, Y · w_y)
```

**In words:**
- Find weights `w_x` and `w_y` such that when we multiply X by `w_x` and Y by `w_y`, the resulting scores are as correlated as possible

**Constraints:**
- `var(X · w_x) = 1` (variance of X scores = 1)
- `var(Y · w_y) = 1` (variance of Y scores = 1)

**Why these constraints?**
- Without constraints, we could just make the weights huge and get high correlation artificially
- Normalizing variance ensures we're finding a "real" relationship

### How CCA Solves This

**The algorithm:**
1. Start with random weights
2. Calculate correlation
3. Adjust weights slightly
4. Recalculate correlation
5. If correlation increased, keep the new weights; otherwise, try different adjustment
6. Repeat until correlation can't be improved (or max iterations reached)

**This is an iterative process** - that's why we set `max_iter=5000`

---

## Permutation Testing Explained

### Why Do We Need Permutation Testing?

**The question:** Is the correlation we found **real** or just **by chance**?

**Example:**
- We found correlation = 0.95 between neighborhoods 0 and 1
- But what if we randomly shuffled the patients and still got 0.95?
- That would mean the correlation is not meaningful!

### What is Permutation Testing?

**The idea:**
1. **Shuffle the data** randomly (break any real relationships)
2. **Calculate correlation** on shuffled data
3. **Repeat many times** (5000 times)
4. **Compare** real correlation to shuffled correlations

**If real correlation is much higher than shuffled correlations → it's real!**

### Step-by-Step Permutation Process

#### Step 1: Store Real Correlation

```python
ccx, ccy = cca.fit_transform(x, y)
observed_correlation = pearsonr(ccx[:,0], ccy[:,0])[0]
# Example: observed_correlation = 0.95
```

#### Step 2: Create Array to Store Permutation Results

```python
arr = np.zeros(5000)  # Will store 5000 correlation values
```

#### Step 3: Permutation Loop

```python
for i in range(5000):
    # Step 3.1: Create random shuffle
    idx = np.arange(len(x))  # [0, 1, 2, 3, ..., n-1]
    np.random.shuffle(idx)   # [2, 0, 3, 1, ..., n-2] (random order)
    
    # Step 3.2: Shuffle X matrix (but keep Y unchanged)
    x_permuted = x[idx]  # X rows are now in random order
    y_unchanged = y      # Y rows stay in original order
    
    # Step 3.3: Run CCA on shuffled data
    cc_permx, cc_permy = cca.fit_transform(x_permuted, y_unchanged)
    
    # Step 3.4: Calculate correlation on shuffled data
    arr[i] = pearsonr(cc_permx[:,0], cc_permy[:,0])[0]
```

**What does shuffling do?**

**Before shuffling:**
```
X (neighborhood 0):          Y (neighborhood 1):
Patient A: [0.917, ...]      Patient A: [0.375, ...]
Patient B: [0.523, ...]      Patient B: [0.421, ...]
Patient C: [0.712, ...]      Patient C: [0.698, ...]
```

**After shuffling X:**
```
X (neighborhood 0, shuffled):  Y (neighborhood 1, unchanged):
Patient C: [0.712, ...]         Patient A: [0.375, ...]
Patient A: [0.917, ...]         Patient B: [0.421, ...]
Patient B: [0.523, ...]         Patient C: [0.698, ...]
```

**What this tests:**
- "If we randomly assign patients to neighborhood 0, do we still get high correlation with neighborhood 1?"
- If yes → the neighborhoods themselves are similar (even random assignment works)
- If no → the correlation depends on specific patient-neighborhood relationships

#### Step 4: Calculate P-value

```python
p_value = np.mean(observed_correlation > arr)
```

**What this does:**
- Counts how many times `observed_correlation > arr[i]`
- Divides by total (5000) to get proportion

**Example:**
```
observed_correlation = 0.95

arr (first 10 values): [0.23, 0.18, 0.31, 0.15, 0.27, 0.19, 0.22, 0.21, 0.16, 0.24, ...]

How many times is 0.95 > value in arr?
Answer: Almost all 5000 times!

p_value = 4998 / 5000 = 0.9996
```

**Interpretation:**
- p-value = 0.9996 means: "The real correlation is higher than 99.96% of random shuffles"
- This is **very significant**!

**Threshold:**
- If `p_value > 0.85` (or 0.97 in your code), we consider the correlation **significant**
- This means the correlation is real, not by chance

---

## Complete Example Walkthrough

Let's walk through a complete example with concrete numbers.

### Setup

**Neighborhoods to compare:** 0 and 1

**Common patients:** A, B, C (3 patients)

### Step 1: Extract Data

**X matrix (neighborhood 0):**
```
        type    type_prob  color_R  color_G  color_B
A       0.917   -0.263     3.487    5.280    3.822
B       0.523   -0.321     3.245    4.890    3.650
C       0.712   -0.198     3.678    5.123    4.012
```

**Y matrix (neighborhood 1):**
```
        type    type_prob  color_R  color_G  color_B
A       0.375   -0.299     3.779    4.824    3.811
B       0.421   -0.356     3.512    4.567    3.789
C       0.698   -0.245     3.890    5.234    4.123
```

### Step 2: Run CCA

**CCA finds weights (example):**
```
w_x = [0.3, 0.1, 0.2, 0.2, 0.2]
w_y = [0.25, 0.15, 0.2, 0.2, 0.2]
```

**Calculate scores:**

**Patient A:**
```
ccx[A] = 0.917×0.3 + (-0.263)×0.1 + 3.487×0.2 + 5.280×0.2 + 3.822×0.2
       = 0.275 + (-0.026) + 0.697 + 1.056 + 0.764
       = 2.766

ccy[A] = 0.375×0.25 + (-0.299)×0.15 + 3.779×0.2 + 4.824×0.2 + 3.811×0.2
       = 0.094 + (-0.045) + 0.756 + 0.965 + 0.762
       = 2.532
```

**Patient B:**
```
ccx[B] = 0.523×0.3 + (-0.321)×0.1 + 3.245×0.2 + 4.890×0.2 + 3.650×0.2
       = 2.456

ccy[B] = 0.421×0.25 + (-0.356)×0.15 + 3.512×0.2 + 4.567×0.2 + 3.789×0.2
       = 2.387
```

**Patient C:**
```
ccx[C] = 0.712×0.3 + (-0.198)×0.1 + 3.678×0.2 + 5.123×0.2 + 4.012×0.2
       = 2.891

ccy[C] = 0.698×0.25 + (-0.245)×0.15 + 3.890×0.2 + 5.234×0.2 + 4.123×0.2
       = 2.834
```

**Result:**
```
ccx = [2.766, 2.456, 2.891]
ccy = [2.532, 2.387, 2.834]
```

**Calculate correlation:**
```
observed_correlation = pearsonr(ccx, ccy)[0] = 0.98
```

### Step 3: Permutation Test

**Permutation 1:**
```
Shuffle: [C, A, B]

X shuffled:
C: [0.712, -0.198, 3.678, 5.123, 4.012]
A: [0.917, -0.263, 3.487, 5.280, 3.822]
B: [0.523, -0.321, 3.245, 4.890, 3.650]

Y unchanged:
A: [0.375, -0.299, 3.779, 4.824, 3.811]
B: [0.421, -0.356, 3.512, 4.567, 3.789]
C: [0.698, -0.245, 3.890, 5.234, 4.123]

Run CCA → correlation = 0.23
```

**Permutation 2:**
```
Shuffle: [B, C, A]
Run CCA → correlation = 0.18
```

**... (repeat 4998 more times) ...**

**Results:**
```
arr = [0.23, 0.18, 0.31, 0.15, 0.27, ..., 0.21]  (5000 values, mostly low)
```

### Step 4: Calculate P-value

```
observed_correlation = 0.98

How many times is 0.98 > arr[i]?
Answer: 4998 out of 5000

p_value = 4998 / 5000 = 0.9996
```

### Step 5: Decision

```
if p_value > 0.97:  # 0.9996 > 0.97 ✓
    # Add edge to network graph
    g.add_edge(0, 1, weight=0.9996)
```

**Result:** Neighborhoods 0 and 1 are significantly correlated!

---

## Key Takeaways

1. **CCA finds the best way to combine multiple features** to compare two datasets
2. **It creates weighted scores** that maximize correlation between the two datasets
3. **Permutation testing verifies** that the correlation is real, not by chance
4. **High p-value** (> 0.85 or 0.97) means the correlation is statistically significant
5. **The network graph** visualizes which neighborhoods are significantly correlated

---

## Common Questions

### Q: Why not just compare each feature separately?

**A:** Because features might be related. For example, if type and color_R are correlated, comparing them separately would double-count the relationship. CCA finds the optimal combination that accounts for all features together.

### Q: Why shuffle only X, not Y?

**A:** We're testing: "If we randomly assign patients to neighborhood 0, do we still get high correlation with neighborhood 1?" Keeping Y fixed tests whether the neighborhoods themselves are similar, regardless of patient assignment.

### Q: What if p-value is low (e.g., 0.5)?

**A:** That means the real correlation is only higher than 50% of random shuffles - basically a coin flip! This suggests the correlation might be by chance, not real.

### Q: Can we use more than one canonical component?

**A:** Yes, but usually the first component captures most of the relationship. Using more components can lead to overfitting (finding patterns that don't generalize).

---

## Summary

The CCA process:
1. **Prepares data:** Calculate nsctf for each (patient, neighborhood) pair
2. **For each neighborhood pair:**
   - Extract common patients
   - Build X and Y matrices
   - Run CCA to find optimal weights
   - Calculate correlation between weighted scores
3. **Test significance:**
   - Shuffle data 5000 times
   - Calculate correlation each time
   - Compare real correlation to shuffled correlations
   - Calculate p-value
4. **Visualize:**
   - Create network graph with edges for significant correlations
   - Edge thickness = correlation strength
   - Edge opacity = p-value (significance)

This process allows us to identify which cellular neighborhoods have similar cell type composition patterns across patients!
