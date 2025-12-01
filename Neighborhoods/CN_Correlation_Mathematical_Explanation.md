# Mathematical Explanation: How CN (Neighborhood) Correlation is Built

This document explains the mathematical steps used to compute correlations between cellular neighborhoods (CNs) in the `cca_cleaned_up.ipynb` notebook.

## Overview

The CN correlation measures how similar the cell type composition patterns are between different neighborhoods across patients. It uses **Canonical Correlation Analysis (CCA)** to find the optimal linear combination of cell types that maximizes correlation between neighborhoods.

---

## Step 1: Neighborhood-Specific Cell Type Frequency (nsctf)

**Location:** Cell 4

**Mathematical Formula:**
```
nsctf(patient, neighborhood, cell_type) = log(ε + mean_frequency)
```

Where:
- `ε = 1e-3` (small constant to avoid log(0))
- `mean_frequency` = average value of each cell type column for cells belonging to that patient-neighborhood combination

**Procedure:**
1. Group cells by `(patient, neighborhood)` pairs
2. Compute the mean of each cell type feature (e.g., 'type', 'type_prob', 'color_R', etc.) within each group
3. Apply log transformation: `log(1e-3 + mean)` to handle zero values and stabilize variance

**Result:** 
A matrix where:
- **Rows:** `(neighborhood_index, patient)` tuples
- **Columns:** Cell type features (5 features in your case: type, type_prob, color_R, color_G, color_B)

**Example structure:**
```
nsctf shape: (118, 5)
Index: [neighborhood_0idx, patients]
Columns: [type, type_prob, color_R, color_G, color_B]
```

---

## Step 2: Canonical Correlation Analysis (CCA)

**Location:** Cells 6 and 9

**Purpose:** For each pair of neighborhoods `(CN_i, CN_j)`, find the optimal linear combinations of cell types that maximize correlation between the two neighborhoods.

### 2.1 Data Preparation

For neighborhoods `CN_i` and `CN_j`:

1. **Extract common patients:** Find patients that appear in both neighborhoods
   ```
   common_patients = patients_CN_i ∩ patients_CN_j ∩ group_patients
   ```

2. **Create paired datasets:**
   - **X matrix:** nsctf values for `CN_i` across common patients
   - **Y matrix:** nsctf values for `CN_j` across common patients
   
   Both matrices have:
   - **Rows:** Common patients (n patients)
   - **Columns:** Cell type features (5 features)

### 2.2 CCA Mathematical Formulation

CCA finds linear transformations **w_x** and **w_y** such that the correlation between the transformed views is maximized:

**Objective:**
```
maximize: corr(X·w_x, Y·w_y)
```

**Constraints:**
- `var(X·w_x) = 1`
- `var(Y·w_y) = 1`

**Solution:**
The canonical correlation coefficient `ρ` is the maximum correlation achieved:
```
ρ = max_wx,wy corr(X·w_x, Y·w_y)
```

**Implementation:**
```python
cca = CCA(n_components=1, max_iter=5000)
ccx, ccy = cca.fit_transform(x, y)
observed_correlation = pearsonr(ccx[:,0], ccy[:,0])[0]
```

Where:
- `ccx[:,0]` = `X·w_x` (canonical component for neighborhood i)
- `ccy[:,0]` = `Y·w_y` (canonical component for neighborhood j)
- `observed_correlation` = Pearson correlation coefficient between these components

---

## Step 3: Permutation-Based Statistical Significance

**Location:** Cells 6 and 9 (permutation loop)

**Purpose:** Determine if the observed correlation is statistically significant by comparing it to a null distribution.

### 3.1 Permutation Procedure

For each of `n_perms = 5000` iterations:

1. **Shuffle patient labels** in X matrix while keeping Y unchanged:
   ```python
   idx = np.arange(len(x))
   np.random.shuffle(idx)
   x_permuted = x[idx]  # Shuffle rows (patients)
   y_unchanged = y      # Keep original order
   ```

2. **Compute CCA on permuted data:**
   ```python
   cc_permx, cc_permy = cca.fit_transform(x_permuted, y_unchanged)
   permuted_correlation = pearsonr(cc_permx[:,0], cc_permy[:,0])[0]
   ```

3. **Store permutation result:** `arr[i] = permuted_correlation`

### 3.2 P-value Calculation

**Location:** Cell 11

The p-value is the proportion of permuted correlations that exceed the observed correlation:

```
p_value = mean(observed_correlation > permuted_correlations)
```

**Interpretation:**
- If `p_value > 0.85` (threshold), the correlation is considered statistically significant
- This means that in 85%+ of random permutations, the permuted correlation was lower than the observed one

---

## Step 4: Network Construction

**Location:** Cell 11

**Purpose:** Build a graph where nodes are neighborhoods and edges represent significant correlations.

**Procedure:**
1. For each neighborhood pair `(CN_i, CN_j)`:
   - Extract `(observed_correlation, permutation_array)`
   - Calculate `p_value = mean(observed_correlation > permutation_array)`
   
2. **Add edge if significant:**
   ```python
   if p_value > THRESHOLD (0.85):
       g.add_edge(CN_i, CN_j, weight=p_value)
   ```

3. **Visualize:**
   - Nodes = neighborhoods (labeled 1-7)
   - Edges = significant correlations
   - Edge thickness = correlation strength
   - Edge opacity = p-value (higher p-value = more opaque)

---

## Summary: The Complete Pipeline

1. **Transform data:** Compute `nsctf = log(ε + mean_frequency)` for each (patient, neighborhood, cell_type)
2. **For each neighborhood pair:**
   - Extract common patients
   - Apply CCA to find optimal linear combinations
   - Compute canonical correlation coefficient
   - Perform 5000 permutations to assess significance
3. **Filter by significance:** Keep pairs with p-value > 0.85
4. **Visualize:** Network graph showing relationships between neighborhoods

---

## Key Mathematical Concepts

### Why CCA instead of simple correlation?

- **Simple correlation:** Would require comparing individual cell types one-by-one
- **CCA advantage:** Finds the optimal combination of all cell types simultaneously, capturing multi-dimensional relationships between neighborhoods

### Why log transformation?

- Handles zero frequencies gracefully
- Stabilizes variance (common in count/frequency data)
- Makes the distribution more normal-like

### Why permutation testing?

- Provides non-parametric statistical significance
- Accounts for patient-specific effects (by shuffling patient labels)
- More robust than parametric tests when data distribution is unknown

---

## Mathematical Notation Summary

- **nsctf[CN, p, f]**: Neighborhood-specific cell type frequency for neighborhood CN, patient p, feature f
- **X**: Matrix of nsctf values for neighborhood CN_i (n patients × 5 features)
- **Y**: Matrix of nsctf values for neighborhood CN_j (n patients × 5 features)
- **w_x, w_y**: Canonical weights (5-dimensional vectors)
- **ccx, ccy**: Canonical components (n-dimensional vectors)
- **ρ**: Canonical correlation coefficient
- **p_value**: Proportion of permutations with correlation < observed correlation

