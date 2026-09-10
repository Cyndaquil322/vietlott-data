# Core Pool Optimal Septet Optimization & 100-Draw Walk-Forward Backtest Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement a Pareto Multi-Objective Optimization algorithm to extract the optimal 7-ball combination (Bao 7 / Bao 6) from the Consensus Core Pool (10-12 numbers) with 100-draw Walk-Forward Backtest across all 3 Vietlott games.

**Architecture:** 
- Add `extract_optimal_septet()` in `src/vietlott/model/covering_engine.py` implementing Pairwise Lift, State Harmonic Balance, and Negative Space Filtering.
- Integrate into `calculate_multi_model_consensus_and_backtest()` and `calculate_walk_forward_bao7_backtest()` in `src/vietlott/render_web_data.py` with 100-draw walk-forward tracking.
- Update UI in `docs/index.html`, `consensus_ensemble.js`, and `notebook_bao7.js` to render the optimal ticket and backtest KPIs.

**Tech Stack:** Python 3.10+, JavaScript ES6, Tailwind CSS, Playwright, Unittest.

**Spec:** [docs/superpowers/specs/2026-09-08-core-pool-septet-optimization-design.md](file:///d:/Projects/vietlott-data-master/docs/superpowers/specs/2026-09-08-core-pool-septet-optimization-design.md)

## Global Constraints
- Strictly 100% real data from `vietlott.vn`, NO mock data, NO fake win tables (AGENTS.md).
- Strict Walk-Forward Backtest: At draw $T$, only use historical data $\le T-1$. Zero Look-Ahead Bias.
- Deterministic seeded predictions: seed = `Draw ID Seed` so F5/reload produces 100% identical numbers.
- Never delete any user files. Only create or edit.
- Docs-First Rule: update `docs/architecture/MATHEMATICAL_MODELS.md` in tandem with code changes.

---

### Task 1: Mathematical Optimization Engine in `src/vietlott/model/covering_engine.py`

**Files:**
- Modify: `src/vietlott/model/covering_engine.py`
- Test: `src/vietlott/tests/test_covering_engine.py`

**Interfaces:**
- Consumes: `core_pool: List[int]`, `past_records: List[Dict]`, `max_val: int`, `num_balls: int`, `is_two_matrix: bool`, `seed: int`
- Produces: `extract_optimal_septet(...) -> Dict[str, Any]` returning `{ "numbers": List[int], "special": Optional[int], "ac_index": int, "sum": int, "odd_even": str, "alpha_score": float, "lift_score": float, "state_composition": Dict[str, int], "passed_negative_space": bool }`

- [ ] **Step 1: Write failing unit tests in `src/vietlott/tests/test_covering_engine.py`**

```python
def test_extract_optimal_septet_power655(self):
    from vietlott.model.covering_engine import extract_optimal_septet
    core_pool = [3, 8, 12, 19, 24, 27, 33, 38, 42, 45, 50, 53]
    records = [
        {"id": "01001", "result": [3, 12, 24, 33, 42, 50, 8]},
        {"id": "01002", "result": [8, 19, 27, 38, 45, 53, 12]},
        {"id": "01003", "result": [3, 8, 19, 24, 33, 50, 42]},
    ]
    res = extract_optimal_septet(
        core_pool=core_pool,
        past_records=records,
        max_val=55,
        num_balls=6,
        is_two_matrix=False,
        seed=1004
    )
    self.assertIn("numbers", res)
    self.assertEqual(len(res["numbers"]), 7)
    self.assertTrue(set(res["numbers"]).issubset(set(core_pool)))
    self.assertGreaterEqual(res["ac_index"], 10)
    self.assertIn("sum", res)
    self.assertIn("odd_even", res)

def test_extract_optimal_septet_power535(self):
    from vietlott.model.covering_engine import extract_optimal_septet
    core_pool = [2, 7, 11, 15, 18, 22, 26, 29, 31, 35]
    records = [
        {"id": "00801", "result": [2, 11, 18, 26, 31, 7]},
        {"id": "00802", "result": [7, 15, 22, 29, 35, 11]},
    ]
    res = extract_optimal_septet(
        core_pool=core_pool,
        past_records=records,
        max_val=35,
        num_balls=5,
        is_two_matrix=True,
        seed=803
    )
    self.assertEqual(len(res["numbers"]), 6)
    self.assertTrue(set(res["numbers"]).issubset(set(core_pool)))
    self.assertIsNotNone(res["special"])

def test_extract_optimal_septet_determinism(self):
    from vietlott.model.covering_engine import extract_optimal_septet
    core_pool = [1, 5, 9, 14, 18, 23, 27, 32, 36, 40, 44, 45]
    records = [{"id": "001", "result": [1, 5, 9, 14, 18, 23]}]
    res1 = extract_optimal_septet(core_pool, records, 45, 6, False, seed=999)
    res2 = extract_optimal_septet(core_pool, records, 45, 6, False, seed=999)
    self.assertEqual(res1["numbers"], res2["numbers"])
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m unittest src/vietlott/tests/test_covering_engine.py`
Expected: FAIL with `ImportError: cannot import name 'extract_optimal_septet'`

- [ ] **Step 3: Implement `extract_optimal_septet` in `src/vietlott/model/covering_engine.py`**

Implement:
- Pairwise Co-occurrence Lift matrix $L(u, v) = \frac{P(u, v)}{P(u) P(v)}$ over `past_records[-100:]`.
- Recency State distribution (Hot: gap $\le 4$, Warm: $5 \le \text{gap} \le 10$, Cold: $\text{gap} > 10$).
- Target 7-ball (or 6-ball) combinations from `core_pool`: $C(12, 7) = 792$ or $C(10, 6) = 210$.
- Comprehensive Multi-Objective scoring function:
  $$\text{Score}(S) = \text{Alpha}(S) + \gamma \cdot \text{Lift}(S) + \lambda_{\text{state}} \cdot \Psi(S) + \text{Bonus}_{\text{AC}}(S) - \text{Penalty}_{\text{Gaussian}}(S) - \text{Penalty}_{\text{Consecutive}}(S)$$
- Seed-based tie-breaking for perfect determinism.
- Return structured payload with `numbers`, `special`, `ac_index`, `sum`, `odd_even`, `lift_score`, `state_composition`.

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m unittest src/vietlott/tests/test_covering_engine.py`
Expected: PASS all tests.

---

### Task 2: Pipeline Integration in `src/vietlott/render_web_data.py`

**Files:**
- Modify: `src/vietlott/render_web_data.py`
- Test: `src/vietlott/tests/test_production_core.py`

**Interfaces:**
- Consumes: `extract_optimal_septet` from `src.vietlott.model.covering_engine`
- Produces: 
  - `consensus_hub["tickets"]["optimal_septet"]` (next draw prediction)
  - `consensus_hub["tickets"]["septet_backtest"]` (100-draw walk-forward backtest summary)
  - `consensus_hub["history_logs"][i]["optimal_septet"]` (per-draw backtest records)
  - `bao7_backtest_data` synced with the Pareto optimization engine.

- [ ] **Step 1: Write integration tests in `src/vietlott/tests/test_production_core.py`**

Test that `consensus_hub["tickets"]` contains `optimal_septet` with 7 numbers (or 6 for 5/35), valid metrics, and `septet_backtest` with 100-draw Walk-Forward statistics.

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m unittest src/vietlott/tests/test_production_core.py`
Expected: FAIL due to missing `optimal_septet` in `tickets`.

- [ ] **Step 3: Integrate Walk-Forward backtest and next-draw prediction into `render_web_data.py`**

In `calculate_multi_model_consensus_and_backtest`:
1. In the 100-draw walk-forward loop:
   - At step $i$, extract `top_core`.
   - Call `extract_optimal_septet(top_core, past, max_val, num_balls, is_two_matrix, seed=int(draw_id))`.
   - Evaluate hit count against `actual_balls`: record matches, check $\ge 3, \ge 4, \ge 5, 6, 7$ hits.
   - Calculate simulated Vietlott Bao 7 / Bao 6 payout and cost.
   - Attach to `history_logs[step]["optimal_septet"]`.
2. For Next Draw:
   - Call `extract_optimal_septet(top_core_balls, records, max_val, num_balls, is_two_matrix, seed=seed_hash)`.
   - Store in `tickets["optimal_septet"]`.
   - Aggregate 100-draw KPIs in `tickets["septet_backtest"]`.
3. In `calculate_walk_forward_bao7_backtest`:
   - Utilize `extract_optimal_septet` so both endpoints share identical mathematical rigor.

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m unittest discover -s src/vietlott/tests`
Expected: PASS all tests.

---

### Task 3: Documentation Sync (Docs-First Rule)

**Files:**
- Modify: `docs/architecture/MATHEMATICAL_MODELS.md`
- Modify: `docs/architecture/FRONTEND_COMPONENT_MAP.md`

- [ ] **Step 1: Update `MATHEMATICAL_MODELS.md`**
Document Section 11: "Mô Hình Tối Ưu Hóa Dàn Hạt Nhân Rút Gọn (Pareto Multi-Objective Septet Extraction)":
- Formulation of Pairwise Lift with Empirical Bayes Smoothing.
- State/Gap Harmonic distribution optimization (Hot:Warm:Cold ratio).
- Negative space filtering for 7-ball combinations ($AC_7 \ge 12$, Gaussian Sum interval, Span $\ge 30$).
- Walk-forward backtest protocol and deterministic seeding.

- [ ] **Step 2: Update `FRONTEND_COMPONENT_MAP.md`**
Document the new UI cards, bindings, and events for `optimal_septet` and `septet_backtest`.

---

### Task 4: UI/UX Rendering in Frontend

**Files:**
- Modify: `docs/index.html`
- Modify: `docs/assets/js/consensus_ensemble.js` (and copy to `assets/js/consensus_ensemble.js`)
- Modify: `docs/assets/js/notebook_bao7.js` (and copy to `assets/js/notebook_bao7.js`)

- [ ] **Step 1: Update `docs/index.html`**
Add card for "Bộ 7 Số Tối Ưu Toán Học (Bao 7 Pareto)" inside `view-consensus-content`:
- Ball display with special ball (for 6/55 and 5/35).
- Metric badges: AC index, Gaussian Sum, Odd/Even, State composition (Nóng/Ấm/Lạnh).
- 100-draw Walk-Forward badge: Win rate $\ge 3$ numbers, Win rate $\ge 4$ numbers, Simulated ROI.
- Quick action buttons: "Sao chép Bao 7", "Lưu vào Sổ tay".

- [ ] **Step 2: Update `docs/assets/js/consensus_ensemble.js`**
- In `renderConsensusHub()`: bind `tickets.optimal_septet` and `tickets.septet_backtest`.
- In `renderConsensusHistory()`: display the optimal septet column and hit count in the 100-draw đối soát table.
- Implement `copyOptimalSeptet()` and `saveOptimalSeptet()` helper functions.
- Mirror changes to `assets/js/consensus_ensemble.js`.

- [ ] **Step 3: Update `docs/assets/js/notebook_bao7.js`**
- Bind recommended Bao 7 ticket to `tickets.optimal_septet`.
- Mirror changes to `assets/js/notebook_bao7.js`.

---

### Task 5: End-to-End Verification & Verification Evidence

**Files:**
- Run: `src/vietlott/render_web_data.py`
- Test: Playwright headless browser check on `docs/index.html`

- [ ] **Step 1: Execute data generation pipeline**
Run: `python src/vietlott/render_web_data.py`
Verify that `data/vietlott_summary.json` and `docs/data/vietlott_summary.json` contain the new `optimal_septet` and `septet_backtest` fields for `power_655`, `power_645`, and `power_535`.

- [ ] **Step 2: Run all unit tests**
Run: `$env:PYTHONPATH="src"; python -m unittest discover -s src/vietlott/tests`
Verify: 100% PASS with 0 failures.

- [ ] **Step 3: Playwright Browser Audit**
Launch local HTTP server on port 8080 and run Playwright script to:
- Verify page loads with 0 JS errors in console.
- Switch between Power 6/55, Mega 6/45, Power 5/35.
- Confirm "Bộ 7 Số Tối Ưu" renders with valid balls, AC $\ge 12$, and 100-draw backtest stats.
- Capture verification screenshots.
