# CSC BCSH Homogeneous Stage1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Refactor `adjust_convert_mat()` to homogeneous-matrix form first, keep `RK CSC` behavior correct, then validate and create a stage-1 git commit.

**Architecture:** Keep the public CSC flow unchanged and only rewrite the BCSH matrix composition inside `get_csc_coefs.py`. Represent contrast, brightness, hue, saturation, RGB gain, and RGB offset as 4x4 homogeneous transforms so the same composition path can later support `eVideo CSC fix` and `rgbOnHsv_*` routing without reworking the CSC pipeline again.

**Tech Stack:** Python, NumPy, argparse, git

---

### Task 1: Write The Stage-1 Refactor Plan Into Code

**Files:**
- Modify: `g:\Codes\bucket_projects\hwpq_verify\script\csc\get_csc_coefs.py`

- [ ] **Step 1: Rewrite BCSH transform construction as homogeneous matrices**

```python
def _make_homo(mat3, ofs3):
    quad = np.eye(4, dtype=np.float32)
    quad[:3, :3] = mat3
    quad[:3, 3] = ofs3
    return quad
```

- [ ] **Step 2: Build independent YUV and RGB domain transforms**

```python
hue_sat_quad = _make_homo(hue_matrix @ saturation_matrix, np.zeros(3, dtype=np.float32))
rgb_gain_quad = _make_homo(gain_matrix, np.zeros(3, dtype=np.float32))
contrast_rgb_quad = _make_homo(contrast_mat_rgb, contrast_ofs_rgb)
contrast_yuv_quad = _make_homo(contrast_mat_yuv, contrast_ofs_yuv + np.array([brightness, 0, 0], dtype=np.float32))
rgb_offset_quad = _make_homo(np.eye(3, dtype=np.float32), np.array([r_offset, g_offset, b_offset], dtype=np.float32))
```

- [ ] **Step 3: Compose per-mode output-domain transforms without changing current `RK CSC` semantics**

```python
if mode.is_input_yuv and mode.is_output_yuv:
    quad = _make_homo(out_mat, out_vec) @ hue_sat_quad @ _make_homo(r2y_matrix, np.zeros(3, dtype=np.float32)) @ (rgb_gain_quad @ contrast_rgb_quad) @ _make_homo(y2r_matrix, np.zeros(3, dtype=np.float32))
elif mode.is_input_yuv and not mode.is_output_yuv:
    quad = (rgb_offset_quad @ rgb_gain_quad @ contrast_rgb_quad) @ _make_homo(out_mat, out_vec) @ hue_sat_quad
elif not mode.is_input_yuv and mode.is_output_yuv:
    quad = hue_sat_quad @ _make_homo(out_mat, out_vec) @ (rgb_gain_quad @ contrast_rgb_quad)
else:
    quad = _make_homo(out_mat, out_vec) @ (rgb_offset_quad @ rgb_gain_quad @ contrast_rgb_quad) @ _make_homo(y2r_matrix, np.zeros(3, dtype=np.float32)) @ hue_sat_quad @ _make_homo(r2y_matrix, np.zeros(3, dtype=np.float32))
```

- [ ] **Step 4: Return the decomposed 3x3 matrix and 3x1 offset**

```python
out_mat = quad[:3, :3]
out_vec = quad[:3, 3]
return out_mat, out_vec, diagonal_ratio
```

### Task 2: Validate `RK CSC` Does Not Regress

**Files:**
- Modify: `g:\Codes\bucket_projects\hwpq_verify\script\csc\get_csc_coefs.py`
- Verify: `g:\Codes\bucket_projects\hwpq_verify\script\csc\run_csc.py`

- [ ] **Step 1: Keep `config.algo_type == "RK CSC"` on the current semantic path**

```python
if config.algo_type == "RK CSC":
    final_mat, range_ofs_o, diagonal_ratio = adjust_convert_mat(config, bcsh_cfg, final_mat, range_ofs_o)
```

- [ ] **Step 2: Run syntax validation**

Run: `python -m py_compile script\csc\get_csc_coefs.py script\csc\run_csc.py script\csc\get_csc_coef_hsv.py`
Expected: command exits with no output

- [ ] **Step 3: Run a spot coefficient dump for smoke testing**

Run: `python script\csc\get_csc_coefs.py -M 709f_to_709f -P 10 -D 10`
Expected: prints one CSC matrix and offset without traceback

### Task 3: Commit Stage 1

**Files:**
- Modify: `g:\Codes\bucket_projects\hwpq_verify\script\csc\get_csc_coefs.py`
- Create: `g:\Codes\bucket_projects\hwpq_verify\docs\superpowers\plans\2026-05-15-csc-bcsh-homogeneous-stage1.md`

- [ ] **Step 1: Review diff**

Run: `git diff -- script/csc/get_csc_coefs.py docs/superpowers/plans/2026-05-15-csc-bcsh-homogeneous-stage1.md`
Expected: diff only shows the stage-1 homogeneous-matrix refactor and plan file

- [ ] **Step 2: Commit stage-1 work**

```bash
git add script/csc/get_csc_coefs.py docs/superpowers/plans/2026-05-15-csc-bcsh-homogeneous-stage1.md
git commit -m "refactor(csc): convert bcsh adjustment to homogeneous matrix form"
```
