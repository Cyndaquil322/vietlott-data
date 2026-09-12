# Tinh Giản & Hiện Đại Hóa Giao Diện Người Dùng (UI/UX Simplification & Modernization) 实施计划

> **面向 Agent 执行者：** 必需子技能：使用 superpower-subagent-driven-development（推荐）或 superpower-executing-plans 按任务逐项执行本计划。步骤使用复选框（`- [ ]`）语法进行跟踪。

**目标：** Tái cấu trúc giao diện Web GUI, gom gọn thanh điều hướng bên trái từ 16 tab thành 4 Không Gian Cốt Lõi, sắp xếp lại trang Dự đoán thành 3 Gói Ngân Sách Thực Tế (10k, 50k, 70k), mang lại trải nghiệm tinh gọn, chuyên nghiệp và ra quyết định trong 30 giây.

**架构：** Cập nhật `docs/assets/js/core.js` chuẩn hóa `MASTER_VIEWS` 4 không gian; tái cấu trúc `docs/index.html` gom gọn Sidebar và phân bổ 3 gói vé ngân sách trực quan; tinh chỉnh `docs/assets/js/consensus_ensemble.js` hỗ trợ layout mới và các bộ nút tiện ích SMS/Lưu vé.

**技术栈：** HTML5, Tailwind CSS, Vanilla JS (ES6+), Lucide Icons.

**规格：** `docs/superpowers/specs/2026-09-13-ui-simplification-modernization-design.md`

## 全局约束
- Bảo tồn 100% dữ liệu toán học và các tính năng dò vé/lưu sổ tay.
- Giữ vững nguyên tắc Không Mock Data, hiển thị minh bạch Nhật ký đối soát Real-time Ledger.
- Cú pháp JavaScript hợp lệ, không gây lỗi runtime trên trình duyệt.

---

### 任务 1: Tái Cấu Trúc Thanh Điều Hướng Sidebar (16 Tabs -> 4 Master Hubs)

**文件：**
- 修改：`docs/index.html` (Phần `<aside id="sidebar">`)
- 修改：`docs/assets/js/core.js` (Cập nhật `VIEW_METADATA` và điều phối chuyển view)

**接口：**
- `switchView(viewName: str)`: Hỗ trợ 4 master views: `'prediction'`, `'results'`, `'analytics'`, `'simulator'` (kèm cơ chế backward compatibility cho các sub-views cũ).

- [ ] **步骤 1：Cập nhật `VIEW_METADATA` trong `docs/assets/js/core.js`**

Định nghĩa 4 Master Views chính và duy trì alias tương thích ngược:
```javascript
const VIEW_METADATA = {
  'prediction': { name: '🎯 Trung Tâm Dự Đoán', icon: 'cpu', color: 'amber' },
  'results': { name: '📋 Kết Quả & Sổ Tay Dò Vé', icon: 'bookmark-check', color: 'emerald' },
  'analytics': { name: '🔬 Lab Phân Tích Định Lượng', icon: 'activity', color: 'indigo' },
  'simulator': { name: '🎮 Giả Lập Đầu Tư', icon: 'play-circle', color: 'cyan' },
};
```

- [ ] **步骤 2：Thiết kế lại Sidebar HTML trong `docs/index.html`**

Thay thế danh sách 16 button dài ngoằng bằng 4 button lớn với icon và badge trực quan:
1. `🎯 Trung Tâm Dự Đoán` (Có badge "Đề xuất")
2. `📋 Kết Quả & Dò Vé` (Có badge đếm vé đã lưu)
3. `🔬 Lab Phân Tích Định Lượng`
4. `🎮 Giả Lập Đầu Tư`

- [ ] **步骤 3：Kiểm tra cú pháp JS và test chuyển view**

Chạy: `node -c docs/assets/js/core.js`  
Xác nhận: Không có lỗi cú pháp.

- [ ] **步骤 4：Commit**

```bash
git add docs/index.html docs/assets/js/core.js
git commit -m "feat(ui): streamline sidebar navigation into 4 master hubs"
```

---

### 任务 2: Bố Cục Lại Trang Dự Đoán Theo 3 Gói Ngân Sách (10k, 50k, 70k)

**文件：**
- 修改：`docs/index.html` (Khối `#view-consensus-content`)
- 修改：`docs/assets/js/consensus_ensemble.js`

- [ ] **步骤 1：Tái cấu trúc HTML 3 Gói Ngân Sách trong `docs/index.html`**

Đặt 3 thẻ Card nổi bật nằm song song (3-Column Responsive Grid):
- **Gói 1 (10.000đ):** Vé Vàng Markowitz (Nút Lưu Sổ + Nút SMS 9969).
- **Gói 2 (50.000đ):** Bộ 5 Vé Bọc Lót Danh Mục (Hiển thị 5 vé đan xen, nút Lưu Cả 5 Vé, nút SMS 9969 cả 5 vé).
- **Gói 3 (70.000đ):** Bao 7 / Bao 6 Pareto Tối Ưu (Nút Lưu Bao 7, nút SMS 9969).

- [ ] **步骤 2：Gom Dàn Hạt Nhân (12 số) và Dàn Bọc Lót Hỗ Trợ vào Khối Tiện Ích Rút Gọn**

Đặt Dàn Hạt Nhân làm nền tảng bên dưới 3 gói vé. Khối Dàn Banker và Bao 4 vé thu gọn được thiết kế dạng Accordion "Công Cụ Ghép Dàn Nâng Cao" (thu gọn mặc định để tránh rối mắt).

- [ ] **步骤 3：Cập nhật JS render trong `docs/assets/js/consensus_ensemble.js`**

Đảm bảo các nút tương tác và hiển thị bóng số hoạt động mượt mà.

- [ ] **步骤 4：Kiểm tra cú pháp JS**

Chạy: `node -c docs/assets/js/consensus_ensemble.js`  
Xác nhận: Không có lỗi cú pháp.

- [ ] **步骤 5：Commit**

```bash
git add docs/index.html docs/assets/js/consensus_ensemble.js
git commit -m "feat(ui): reorganize prediction hub into 3 practical budget packages (10k, 50k, 70k)"
```

---

### 任务 3: Gom Nhóm Các Biểu Đồ Chuyên Sâu Vào "Lab Phân Tích Định Lượng"

**文件：**
- 修改：`docs/index.html`
- 修改：`docs/assets/js/core.js`

- [ ] **步骤 1：Tạo View Container `#view-analytics-content` với Sub-tabs**

Trong Lab Phân Tích Định Lượng, tạo một thanh sub-tabs ngang nhỏ gọn:
`[Chu Kỳ & Số Gan] | [Cặp Đôi & Cầu Rơi] | [Dải Tổng Gaussian] | [Ma Trận Markov] | [Độ Phức Tạp AC & EV]`
Người dùng có thể chuyển đổi qua lại nhanh chóng mà không làm phình to thanh sidebar chính.

- [ ] **步骤 2：Kiểm tra chuyển sub-tab mượt mà bằng JavaScript**

- [ ] **步骤 3：Commit**

```bash
git add docs/index.html docs/assets/js/core.js
git commit -m "feat(ui): consolidate deep charts into clean sub-tabbed analytics lab"
```

---

### 任务 4: Kiểm Thử Toàn Diện & Nghiệm Thu Giao Diện

**文件：**
- Toàn bộ test suite và asset files

- [ ] **步骤 1：Chạy test suite dự án**

Chạy: `.venv\Scripts\pytest.exe src/vietlott/tests/ -v`  
Kỳ vọng: 100% test PASSED.

- [ ] **步骤 2：Kiểm tra responsive và cú pháp của toàn bộ tệp JS**

Chạy: `node -c docs/assets/js/core.js; node -c docs/assets/js/consensus_ensemble.js`  
Xác nhận: Không có bất kỳ lỗi cú pháp nào.
