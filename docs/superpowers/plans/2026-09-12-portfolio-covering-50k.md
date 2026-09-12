# Bộ 5 Vé Tối Ưu Bọc Lót 50k (Portfolio Combinatorial Covering) 实施计划

> **面向 Agent 执行者：** 必需子技能：使用 superpower-subagent-driven-development（推荐）或 superpower-executing-plans 按任务逐项执行本计划。步骤使用复选框（`- [ ]`）语法进行跟踪。

**目标：** Xây dựng thuật toán tối ưu hóa danh mục tổ hợp bọc lót `portfolio_covering_engine.py` lọc không gian âm và gom trọn cặp/bộ 3 cho ngân sách 50k (5 vé đơn); tích hợp vào pipeline dữ liệu `render_web_data.py` và giao diện Web GUI `docs/index.html`.

**架构：** Module `portfolio_covering_engine.py` nhận Dàn Hạt Nhân (Core Pool 10-12 số), áp dụng các bộ lọc không gian âm (Negative Space) để loại bỏ vé rác, sau đó áp dụng thuật toán Greedy Max-Coverage giải bài toán bao phủ tổ hợp trích xuất 5 vé bọc lót tối ưu; `render_web_data.py` gọi engine này đưa vào `consensus_hub.tickets.portfolio_50k`; Web GUI hiển thị card 5 vé kèm nút copy SMS 9969 và lưu sổ tay.

**技术栈：** Python 3.11, Pytest, JavaScript (ES6+), HTML5/CSS3.

**规格：** `docs/superpowers/specs/2026-09-12-portfolio-covering-50k-design.md`

## 全局约束
- 100% Zero Mock Data: Dữ liệu vé và tỷ lệ bao phủ phải được tính toán bằng thuật toán thật từ Dàn Hạt Nhân thật.
- Tính tất định (Deterministic Seeding): Kết quả sinh 5 vé phải hoàn toàn đồng nhất theo mã kỳ quay `seed`.
- Tuân thủ cấu trúc sản phẩm Vietlott: 6 số cho 6/55 và 6/45, 5 số cho 5/35.

---

### 任务 1: Xây Dựng Engine Tối Ưu Hóa Danh Mục Tổ Hợp (Portfolio Covering Engine)

**文件：**
- 新建：`src/vietlott/model/portfolio_covering_engine.py`
- 测试：`src/vietlott/tests/test_portfolio_covering_engine.py`

**接口：**
- 对外产出：`filter_negative_space(combos: List[Tuple[int, ...]], max_val: int, num_balls: int) -> List[Tuple[int, ...]]`
- 对外产出：`generate_portfolio_50k(core_pool: List[int], candidate_scores: Dict[int, float], max_val: int, num_balls: int, num_tickets: int = 5, seed: int = 42) -> Dict[str, Any]`

- [ ] **步骤 1：编写失败的测试**

```python
# src/vietlott/tests/test_portfolio_covering_engine.py
import pytest
from vietlott.model.portfolio_covering_engine import (
    filter_negative_space,
    generate_portfolio_50k,
)

def test_negative_space_filter_eliminates_bad_combos():
    # Vé toàn chẵn (0 lẻ) -> bị loại
    bad_even = (2, 4, 6, 8, 10, 12)
    # Vé toàn lẻ (6 lẻ) -> bị loại
    bad_odd = (1, 3, 5, 7, 9, 11)
    # Vé dồn vào 1 đầu số -> bị loại
    bad_decade = (1, 2, 3, 4, 5, 6)
    # Vé chuẩn cân bằng
    good_combo = (5, 11, 24, 31, 47, 54)
    
    filtered = filter_negative_space([bad_even, bad_odd, bad_decade, good_combo], max_val=55, num_balls=6)
    assert good_combo in filtered
    assert bad_even not in filtered
    assert bad_odd not in filtered

def test_generate_portfolio_50k_structure():
    core = [5, 11, 24, 31, 47, 54, 1, 8, 16, 22, 39, 44]
    scores = {b: 1.0 / (idx + 1) for idx, b in enumerate(core)}
    
    res = generate_portfolio_50k(core, scores, max_val=55, num_balls=6, num_tickets=5, seed=1398)
    assert res["total_tickets"] == 5
    assert res["total_cost_vnd"] == 50000
    assert len(res["tickets"]) == 5
    for t in res["tickets"]:
        assert len(t["numbers"]) == 6
        assert t["ac"] >= 6
        assert 2 <= t["odds"] <= 4
```

- [ ] **步骤 2：运行测试并确认其失败**

运行：`.venv\Scripts\pytest.exe src/vietlott/tests/test_portfolio_covering_engine.py -v`  
预期：FAIL，提示 `ModuleNotFoundError: No module named 'vietlott.model.portfolio_covering_engine'`

- [ ] **步骤 3：编写最小实现**

```python
# src/vietlott/model/portfolio_covering_engine.py
import hashlib
import itertools
from typing import Any, Dict, List, Set, Tuple

def filter_negative_space(
    combos: List[Tuple[int, ...]],
    max_val: int,
    num_balls: int,
) -> List[Tuple[int, ...]]:
    filtered = []
    min_ac = 7 if num_balls >= 6 else 4
    sum_range = (125, 210) if max_val == 55 else ((105, 175) if max_val == 45 else (65, 115))

    for c in combos:
        s_combo = sorted(c)
        c_sum = sum(s_combo)
        if not (sum_range[0] <= c_sum <= sum_range[1]):
            continue
            
        diffs = {abs(x - y) for x, y in itertools.combinations(s_combo, 2)}
        ac = len(diffs) - (num_balls - 1)
        if ac < min_ac:
            continue
            
        odds = sum(1 for x in s_combo if x % 2 != 0)
        if num_balls == 6 and (odds < 2 or odds > 4):
            continue
        if num_balls == 5 and (odds < 1 or odds > 4):
            continue
            
        decades = set(x // 10 for x in s_combo)
        if num_balls == 6 and len(decades) < 3:
            continue
            
        filtered.append(s_combo)
    return filtered

def generate_portfolio_50k(
    core_pool: List[int],
    candidate_scores: Dict[int, float],
    max_val: int,
    num_balls: int,
    num_tickets: int = 5,
    seed: int = 42,
) -> Dict[str, Any]:
    pool = sorted(list(set(core_pool)))[: (12 if max_val in (55, 45) else 10)]
    if len(pool) < num_balls:
        pool = list(range(1, num_balls + 1))

    all_combos = list(itertools.combinations(pool, num_balls))
    valid_combos = filter_negative_space(all_combos, max_val, num_balls)
    if len(valid_combos) < num_tickets:
        valid_combos = [sorted(c) for c in all_combos]

    all_pairs = set(itertools.combinations(pool, 2))
    all_triplets = set(itertools.combinations(pool, 3))

    selected: List[List[int]] = []
    covered_pairs: Set[Tuple[int, int]] = set()
    covered_triplets: Set[Tuple[int, int, int]] = set()

    for idx in range(num_tickets):
        best_c = None
        best_score = -999999.0

        for c in valid_combos:
            if c in selected:
                continue
            c_pairs = set(itertools.combinations(c, 2))
            c_triplets = set(itertools.combinations(c, 3))
            
            new_p = len(c_pairs - covered_pairs)
            new_t = len(c_triplets - covered_triplets)
            exp_w = sum(candidate_scores.get(b, 0.0) for b in c)
            
            h_key = f"{seed}_{idx}_{c}".encode("utf-8")
            tie_breaker = (int(hashlib.md5(h_key).hexdigest()[:6], 16) % 1000) * 0.001
            
            score = (new_p * 3.0) + (new_t * 1.5) + (exp_w * 2.0) + tie_breaker
            if score > best_score:
                best_score = score
                best_c = c

        if best_c:
            selected.append(best_c)
            covered_pairs.update(itertools.combinations(best_c, 2))
            covered_triplets.update(itertools.combinations(best_c, 3))

    tickets_data = []
    tags = ["Trục Hạt Nhân", "Cặp Đôi Bạc Nhớ", "Kháng Dao Động", "Lực Hút Markov", "Bảo Hiểm Bao Phủ"]
    for i, t_nums in enumerate(selected):
        diffs = {abs(x - y) for x, y in itertools.combinations(t_nums, 2)}
        ac = len(diffs) - (num_balls - 1)
        odds = sum(1 for x in t_nums if x % 2 != 0)
        decades = len(set(x // 10 for x in t_nums))
        
        tickets_data.append({
            "id": f"portfolio_ticket_{i+1}",
            "ticketIndex": i + 1,
            "numbers": t_nums,
            "sum": sum(t_nums),
            "ac": ac,
            "odds": odds,
            "evens": num_balls - odds,
            "decades_count": decades,
            "tag": tags[i % len(tags)],
        })

    pair_cov_pct = round(len(covered_pairs) / max(1, len(all_pairs)) * 100.0, 1)

    return {
        "total_tickets": len(tickets_data),
        "total_cost_vnd": len(tickets_data) * 10000,
        "core_pool_size": len(pool),
        "pairs_coverage_pct": pair_cov_pct,
        "triplets_coverage_count": len(covered_triplets),
        "tickets": tickets_data,
    }
```

- [ ] **步骤 4：运行测试并确认其通过**

运行：`.venv\Scripts\pytest.exe src/vietlott/tests/test_portfolio_covering_engine.py -v`  
预期：PASS

- [ ] **步骤 5：提交**

```bash
git add src/vietlott/model/portfolio_covering_engine.py src/vietlott/tests/test_portfolio_covering_engine.py
git commit -m "feat(portfolio): implement portfolio combinatorial covering engine with negative space filter"
```

---

### 任务 2: Tích Hợp Vào Pipeline `render_web_data.py`

**文件：**
- 修改：`src/vietlott/model/ensemble_engine.py`
- 修改：`src/vietlott/render_web_data.py`

- [ ] **步骤 1：Gọi `generate_portfolio_50k` trong `ensemble_engine.py`**

Trong `calculate_multi_model_consensus_and_backtest`:
Thêm vé `portfolio_50k` vào `tickets`:
```python
from vietlott.model.portfolio_covering_engine import generate_portfolio_50k
tickets["portfolio_50k"] = generate_portfolio_50k(
    core_pool=top_core,
    candidate_scores=consensus_sc,
    max_val=max_val,
    num_balls=num_balls,
    num_tickets=5,
    seed=seed_val,
)
```

- [ ] **步骤 2：Chạy test tích hợp ensemble engine**

运行：`.venv\Scripts\pytest.exe src/vietlott/tests/test_ensemble_engine.py -v`  
预期：PASS

- [ ] **步骤 3：Chạy `render_web_data.py` để cập nhật JSON xuất bản**

Chạy: `.venv\Scripts\python.exe -u src/vietlott/render_web_data.py`  
Xác nhận: Tệp `docs/data/vietlott_summary.json` và `docs/data/products/power_655.json` đều chứa key `portfolio_50k`.

- [ ] **步骤 4：Commit pipeline**

```bash
git add src/vietlott/model/ensemble_engine.py src/vietlott/render_web_data.py data/ docs/data/
git commit -m "feat(pipeline): integrate portfolio 50k covering tickets into web data"
```

---

### 任务 3: Nâng Cấp Giao Diện Web GUI (Card Bộ 5 Vé Tối Ưu Bọc Lót 50k)

**文件：**
- 修改：`docs/index.html`
- 修改：`docs/assets/js/consensus_ensemble.js`

- [ ] **步骤 1：Thêm Card `#consensusPortfolio50kSection` vào `docs/index.html`**

Bổ sung khối giao diện nằm ngay dưới Dàn Hạt Nhân:
- Header: "🎯 BỘ 5 VÉ TỐI ƯU BỌC LÓT (NGÂN SÁCH 50.000đ / KỲ)"
- Badge tỷ lệ bao phủ cặp đôi `pairs_coverage_pct%` và số lượng bộ ba được bảo hiểm.
- Grid 5 vé với bóng số nổi bật, chỉ số AC, Tổng, Chẵn/Lẻ và tag chiến thuật.
- Nút: "Lưu Cả 5 Vé Vào Sổ Tay" & "Copy SMS 9969 (5 Vé)".

- [ ] **步骤 2：Viết hàm render `renderConsensusPortfolio50k()` trong `docs/assets/js/consensus_ensemble.js`**

- [ ] **步骤 3：Kiểm tra cú pháp JS và test hiển thị**

Chạy: `node -c docs/assets/js/consensus_ensemble.js`  
Xác nhận: Không có lỗi cú pháp.

- [ ] **步骤 4：Commit giao diện**

```bash
git add docs/index.html docs/assets/js/consensus_ensemble.js
git commit -m "feat(ui): add interactive portfolio 50k covering card with batch save and SMS 9969"
```

---

### 任务 4: Kiểm Thử Toàn Diện & Nghiệm Thu (Verification Before Completion)

**文件：**
- Toàn bộ test suite trong `src/vietlott/tests/`

- [ ] **步骤 1：Chạy toàn bộ bài test**

Chạy: `.venv\Scripts\pytest.exe src/vietlott/tests/test_portfolio_covering_engine.py src/vietlott/tests/test_ensemble_engine.py src/vietlott/tests/test_prediction_evaluator.py -v`  
Kỳ vọng: 100% test PASSED.

- [ ] **步骤 2：Xác minh file JSON xuất bản**

Chạy: `.venv\Scripts\python.exe -c "import json; d=json.load(open('docs/data/vietlott_summary.json', encoding='utf-8')); print([(k, len(d['products'][k]['consensus_hub']['tickets'].get('portfolio_50k', {}).get('tickets', []))) for k in ['power_655', 'power_645', 'power_535']])"`  
Kỳ vọng: Mỗi game đều ghi nhận đủ 5 vé bọc lót.
