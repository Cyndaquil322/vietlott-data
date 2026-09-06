// ==========================================
// 1. CORE: Global State, Navigation & Init
// ==========================================

    // State
    let appData = null;
    let currentProductKey = 'power_655';
    let currentView = 'consensus';
    let currentPage = 1;
    let pageSize = 25;
    let sumChartInstance = null;
    let decadeChartInstance = null;
    let simPnlChartInstance = null;
    let currentEnsembleTickets = [];
    let currentBao7Ticket = null;
    let currentSavedFilter = 'all';

    // 3 Loại Hình Xổ Số Cốt Lõi (Dropdown chọn loại hình gọn gàng)
    const PRODUCT_LIST = [
      { key: 'power_655', label: 'Power 6/55', icon: 'zap', schedule: 'Thứ 3, 5, 7 (18h)', desc: 'Jackpot 1 & 2 (100+ Tỷ)' },
      { key: 'power_645', label: 'Mega 6/45', icon: 'award', schedule: 'Thứ 4, 6, CN (18h)', desc: 'Jackpot khởi điểm 12 Tỷ' },
      { key: 'power_535', label: 'Power 5/35', icon: 'star', schedule: 'Hàng ngày (13h & 21h)', desc: 'Tỷ lệ trúng cao, 2 kỳ/ngày' }
    ];

    const VIEW_METADATA = {
      'consensus': { name: '⭐ Tổng Hợp Dự Đoán', icon: 'cpu', color: 'amber' },
      'bao7': { name: 'Dự Đoán Bao 7 / Bao 6', icon: 'layers', color: 'emerald' },
      'ensemble': { name: 'Dự Đoán Ensemble Đa Tầng', icon: 'sparkles', color: 'rose' },
      'smart-generator': { name: 'Sinh Số Thông Minh', icon: 'sliders', color: 'purple' },
      'simulator': { name: 'Giả Lập Quay Số & Lãi Lỗ', icon: 'play-circle', color: 'cyan' },
      'overview': { name: 'Kỳ Quay Mới & Dò Vé', icon: 'calendar', color: 'rose' },
      'saved-tickets': { name: 'Sổ Tay Vé Đã Lưu', icon: 'bookmark', color: 'violet' },
      'history': { name: 'Lịch Sử Toàn Bộ Kỳ Quay', icon: 'history', color: 'slate' },
      'gap': { name: 'Chu Kỳ Nhịp & Số Gan', icon: 'timer', color: 'emerald' },
      'pairs': { name: 'Cặp Đôi & Bộ Ba Hay Về', icon: 'link', color: 'blue' },
      'sum': { name: 'Phân Phối Dải Tổng Gaussian', icon: 'bell', color: 'amber' },
      'patterns': { name: 'Liền Kề, Cầu Lặp & Đầu Số', icon: 'grid', color: 'pink' },
      'markov': { name: 'Ma Trận Chuyển Trạng Thái Markov', icon: 'git-merge', color: 'fuchsia' },
      'ac-delta': { name: 'Độ Phức Tạp AC & Delta Gaps', icon: 'activity', color: 'emerald' },
      'positional': { name: 'Điểm Rơi Theo Vị Trí Bóng', icon: 'crosshair', color: 'orange' },
      'digits-ev': { name: 'Kỳ Vọng Toán Học EV & Đuôi Số', icon: 'sparkles', color: 'violet' }
    };

    document.addEventListener('DOMContentLoaded', async () => {
      lucide.createIcons();
      renderGameTabs();
      setupEventListeners();
      updateSavedBadge();
      checkUrlSyncParams();
      await loadData();
    });

    // Product Selector Dropdown Controller
    function toggleProductDropdown(e) {
      if (e) e.stopPropagation();
      const menu = document.getElementById('productDropdownMenu');
      const chevron = document.getElementById('productSelectorChevron');
      if (!menu) return;
      const isHidden = menu.classList.contains('hidden');
      if (isHidden) {
        menu.classList.remove('hidden');
        if (chevron) chevron.classList.add('rotate-180');
        renderProductDropdown();
      } else {
        closeProductDropdown();
      }
    }

    function closeProductDropdown() {
      const menu = document.getElementById('productDropdownMenu');
      const chevron = document.getElementById('productSelectorChevron');
      if (menu) menu.classList.add('hidden');
      if (chevron) chevron.classList.remove('rotate-180');
    }

    // Close on click outside or escape
    document.addEventListener('click', (e) => {
      const wrapper = document.getElementById('productSelectorWrapper');
      if (wrapper && !wrapper.contains(e.target)) {
        closeProductDropdown();
      }
    });

    function renderGameTabs() {
      const prod = PRODUCT_LIST.find(p => p.key === currentProductKey) || PRODUCT_LIST[0];
      const labelEl = document.getElementById('productSelectorLabel');
      const iconEl = document.getElementById('productSelectorIcon');

      if (labelEl) labelEl.textContent = prod.label;
      if (iconEl) iconEl.setAttribute('data-lucide', prod.icon);

      renderProductDropdown();
      lucide.createIcons();
    }

    function renderProductDropdown() {
      const listEl = document.getElementById('productDropdownList');
      if (!listEl) return;
      listEl.innerHTML = PRODUCT_LIST.map(p => {
        const isSelected = (p.key === currentProductKey);
        return `
          <button onclick="selectProductFromDropdown('${p.key}')" class="w-full text-left p-2.5 rounded-xl transition flex items-center justify-between gap-2 cursor-pointer ${
            isSelected 
              ? 'bg-rose-500/15 border border-rose-500/40 text-white' 
              : 'hover:bg-slate-800/80 text-slate-300 hover:text-white'
          }">
            <div class="flex items-center gap-2.5">
              <div class="w-7 h-7 rounded-lg flex items-center justify-center ${isSelected ? 'bg-rose-600 text-white' : 'bg-slate-800 text-slate-400'}">
                <i data-lucide="${p.icon}" class="w-3.5 h-3.5"></i>
              </div>
              <div>
                <div class="font-bold text-xs flex items-center gap-1.5">
                  <span>${p.label}</span>
                  ${isSelected ? '<span class="text-[9px] px-1.5 py-0.2 rounded bg-rose-500/30 text-rose-300 font-mono">Đang xem</span>' : ''}
                </div>
                <div class="text-[10px] text-slate-400 font-sans mt-0.5">${p.desc || ''}</div>
              </div>
            </div>
            <span class="text-[9px] font-mono text-slate-500 hidden sm:inline whitespace-nowrap">${p.schedule || ''}</span>
          </button>
        `;
      }).join('');
      lucide.createIcons();
    }

    function selectProductFromDropdown(key) {
      closeProductDropdown();
      switchProduct(key);
    }

    function switchProduct(key) {
      currentBao7Ticket = null;
      currentEnsembleTickets = [];
      currentProductKey = key;
      currentPage = 1;
      renderGameTabs();
      renderCurrentProduct();
    }

    // Sidebar Drawer Controller (Cột menu bên trái)
    function toggleSidebar() {
      const sidebar = document.getElementById('sidebarMenu');
      const overlay = document.getElementById('sidebarOverlay');
      if (!sidebar || !overlay) return;
      const isOpen = !sidebar.classList.contains('-translate-x-full');
      if (isOpen) {
        closeSidebar();
      } else {
        openSidebar();
      }
    }

    function openSidebar() {
      const sidebar = document.getElementById('sidebarMenu');
      const overlay = document.getElementById('sidebarOverlay');
      if (!sidebar || !overlay) return;
      sidebar.classList.remove('-translate-x-full');
      overlay.classList.remove('opacity-0', 'pointer-events-none');
      overlay.classList.add('opacity-100');
      document.body.classList.add('overflow-hidden');
      lucide.createIcons();
    }

    function closeSidebar() {
      const sidebar = document.getElementById('sidebarMenu');
      const overlay = document.getElementById('sidebarOverlay');
      if (!sidebar || !overlay) return;
      sidebar.classList.add('-translate-x-full');
      overlay.classList.add('opacity-0', 'pointer-events-none');
      overlay.classList.remove('opacity-100');
      document.body.classList.remove('overflow-hidden');
    }

    // Close on Escape key
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') closeSidebar();
    });

    const NAV_CATEGORIES = {
      'overview': { id: 'cat-overview', name: 'Tổng Quan & Vé', icon: 'sparkles', defaultView: 'overview' },
      'predictions': { id: 'cat-predictions', name: 'AI & Dự Đoán', icon: 'cpu', defaultView: 'consensus' },
      'stats': { id: 'cat-stats', name: 'Thống Kê Cơ Bản', icon: 'bar-chart-2', defaultView: 'gap' },
      'quant': { id: 'cat-quant', name: 'Định Lượng Sâu', icon: 'binary', defaultView: 'markov' }
    };

    let currentCategory = 'predictions';

    function findCategoryForView(viewName) {
      if (['consensus', 'bao7', 'ensemble', 'smart-generator', 'simulator'].includes(viewName)) return 'predictions';
      if (['overview', 'saved-tickets', 'history'].includes(viewName)) return 'overview';
      if (['gap', 'pairs', 'sum', 'patterns'].includes(viewName)) return 'stats';
      return 'quant';
    }

    function renderTier2Nav() {}
    function switchCategory(catKey) {
      const defaultView = NAV_CATEGORIES[catKey]?.defaultView || 'consensus';
      switchView(defaultView);
    }

    function switchView(viewName) {
      currentView = viewName;
      currentCategory = findCategoryForView(viewName);

      // Highlight active item in sidebar drawer
      document.querySelectorAll('.sidebar-nav-item').forEach(el => {
        el.classList.remove('bg-amber-500/10', 'text-amber-300', 'border', 'border-amber-500/30', 'bg-rose-500/10', 'text-rose-300', 'border-rose-500/30');
        el.classList.add('text-slate-300', 'hover:bg-slate-800/60', 'hover:text-white');
      });
      const activeSideBtn = document.getElementById(`side-${viewName}`);
      if (activeSideBtn) {
        activeSideBtn.classList.remove('text-slate-300', 'hover:bg-slate-800/60', 'hover:text-white');
        activeSideBtn.classList.add('bg-amber-500/10', 'text-amber-300', 'border', 'border-amber-500/30');
      }

      // Update Breadcrumb
      const bcEl = document.getElementById('currentViewBreadcrumb');
      if (bcEl && VIEW_METADATA[viewName]) {
        const meta = VIEW_METADATA[viewName];
        bcEl.innerHTML = `<i data-lucide="${meta.icon}" class="w-3.5 h-3.5 text-${meta.color}-400"></i><span>${meta.name}</span>`;
      }

      // Close sidebar drawer smoothly
      closeSidebar();

      // Toggle views visibility
      document.querySelectorAll('.view-content').forEach(c => c.classList.add('hidden'));
      const target = document.getElementById(`view-${viewName}-content`);
      if (target) {
        target.classList.remove('hidden');
      }

      // Re-trigger view rendering
      if (viewName === 'consensus') renderConsensusView(appData?.products?.[currentProductKey]);
      if (viewName === 'sum') {
        renderSumChart();
        renderSumTrendChart();
      }
      if (viewName === 'patterns') renderDecadeChart();
      if (viewName === 'positional') {
        renderSpanChart();
        renderSpanTrendChart();
      }
      if (viewName === 'ac-delta') renderAcChart();
      if (viewName === 'digits-ev') renderTailDivChart();
      if (viewName === 'bao7') renderBao7View(appData?.products?.[currentProductKey]);
      if (viewName === 'ensemble') renderEnsembleView(appData?.products?.[currentProductKey]);
      if (viewName === 'saved-tickets') renderSavedTicketsView();
      lucide.createIcons();
    }

    let gitSavedTickets = [];

    async function loadData() {
      const ts = Date.now();
      
      // Also fetch Git synced tickets
      const gitUrls = [
        './data/saved_tickets.json?v=' + ts,
        './docs/data/saved_tickets.json?v=' + ts,
        'data/saved_tickets.json?v=' + ts,
        'docs/data/saved_tickets.json?v=' + ts
      ];
      for (const gUrl of gitUrls) {
        try {
          const gitRes = await fetch(gUrl, { cache: 'no-store' });
          if (gitRes.ok) {
            gitSavedTickets = await gitRes.json();
            updateSavedBadge();
            break;
          }
        } catch (e) {}
      }

      const urls = [
        './data/vietlott_summary.json?v=' + ts,
        './docs/data/vietlott_summary.json?v=' + ts,
        'docs/data/vietlott_summary.json?v=' + ts,
        'data/vietlott_summary.json?v=' + ts
      ];

      for (const url of urls) {
        try {
          const res = await fetch(url, { cache: 'no-store' });
          if (res.ok) {
            appData = await res.json();
            onDataReady();
            return;
          }
        } catch (err) {}
      }

      if (window.location.protocol === 'file:') {
        document.getElementById('fileNotice').classList.remove('hidden');
      }
    }

    function onDataReady() {
      if (!appData) return;
      document.getElementById('fileNotice').classList.add('hidden');
      if (appData.meta && appData.meta.generated_at) {
        document.getElementById('updateTimeText').textContent = `Cập nhật: ${appData.meta.generated_at}`;
      }
      renderCurrentProduct();
      updateSavedBadge();
      switchView(currentView || 'consensus');
    }

    // ==========================================
    // MATHEMATICAL UTILITIES (PRNG & HASHING)
    // ==========================================
    function createMulberry32(seed) {
      return function() {
        let t = seed += 0x6D2B79F5;
        t = Math.imul(t ^ (t >>> 15), t | 1);
        t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
        return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
      };
    }

    function stringToSeedHash(str) {
      let hash = 0;
      for (let i = 0; i < str.length; i++) {
        hash = Math.imul(31, hash) + str.charCodeAt(i) | 0;
      }
      return Math.abs(hash);
    }

    function setupEventListeners() {
      const manualInput = document.getElementById('manualJsonInput');
      if (manualInput) {
        manualInput.addEventListener('change', (e) => {
          const file = e.target.files[0];
          if (!file) return;
          const reader = new FileReader();
          reader.onload = (event) => {
            try {
              appData = JSON.parse(event.target.result);
              onDataReady();
            } catch (err) {
              alert("Lỗi đọc file JSON: " + err.message);
            }
          };
          reader.readAsText(file);
        });
      }

      document.getElementById('btnCheckTicket').addEventListener('click', checkTicket);
      document.getElementById('btnRandomTicket').addEventListener('click', generateRandomTicket);
      document.getElementById('compareDrawSelect').addEventListener('change', checkTicket);
      document.getElementById('btnGenerateSmartTicket').addEventListener('click', generateSmartTickets);
      document.getElementById('btnRunSimulation').addEventListener('click', runSimulation);
      document.getElementById('btnCheckAc').addEventListener('click', checkAcValidator);
      document.getElementById('btnGenerateDeltaTicket').addEventListener('click', generateDeltaTicket);
      document.getElementById('btnLoadMarkovToTicket').addEventListener('click', loadMarkovToTicket);
      document.getElementById('btnRegenerateEnsemble').addEventListener('click', () => generateEnsembleGoldenTickets(true));
      document.getElementById('btnSaveCurrentPrediction').addEventListener('click', saveCurrentPredictionToHistory);
      document.getElementById('btnClearPredictionHistory').addEventListener('click', clearPredictionHistory);
      document.getElementById('btnRegenerateBao7').addEventListener('click', () => generateBao7Ticket(true));
      document.getElementById('btnApplyLockedNumbers').addEventListener('click', () => generateBao7Ticket(true));
      document.getElementById('btnSaveBao7Prediction').addEventListener('click', saveBao7PredictionToHistory);
      document.getElementById('btnClearBao7History').addEventListener('click', clearBao7History);

      document.getElementById('simStrategySelect').addEventListener('change', (e) => {
        const wrap = document.getElementById('simCustomTicketWrap');
        if (e.target.value === 'fixed_ticket') {
          wrap.classList.remove('hidden');
        } else {
          wrap.classList.add('hidden');
        }
      });

      document.getElementById('historySearch').addEventListener('input', () => {
        currentPage = 1;
        renderHistoryTable();
      });
      document.getElementById('pageSizeSelect').addEventListener('change', (e) => {
        pageSize = parseInt(e.target.value);
        currentPage = 1;
        renderHistoryTable();
      });
      document.getElementById('btnPrevPage').addEventListener('click', () => {
        if (currentPage > 1) {
          currentPage--;
          renderHistoryTable();
        }
      });
      document.getElementById('btnNextPage').addEventListener('click', () => {
        currentPage++;
        renderHistoryTable();
      });
    }

    function renderCurrentProduct() {
      if (!appData || !appData.products || !appData.products[currentProductKey]) return;
      const product = appData.products[currentProductKey];

      // 1. Overview & Hero
      renderHero(product);
      populateDrawSelect(product.history || []);
      renderHotCold(product);

      // 2. Gap Analysis
      renderGapAnalysis(product);

      // 3. Pairs & Triples
      renderCooccurrence(product);

      // 4. Sum Distribution
      renderSumStats(product);

      // 5. Patterns
      renderPatternMetrics(product);

      // 6. 4 Advanced Modules + Ensemble Multi-Model Predictor + Bao 7 Strategy
      renderPositionalView(product);
      renderAcDeltaView(product);
      renderMarkovView(product);
      renderDigitsEvView(product);
      renderConsensusView(product);
      renderEnsembleView(product);
      renderBao7View(product);

      // 7. History Table
      renderHistoryTable();

      // 8. Live Countdown Timer & Special Ball Tracker
      startLiveCountdown();
      renderSpecialBallTracker(product);

      lucide.createIcons();
    }


// Register Service Worker for PWA Support
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('./sw.js').catch(() => {});
  });
}
