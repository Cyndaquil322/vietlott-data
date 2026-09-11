// ==========================================
// 2. COMMON ANALYTICS: Hero, Gap, Sum, Patterns, Sim, History
// ==========================================

    function renderDiceSVG(face, size = 54) {
      const pipsMap = {
        1: [[50, 50, 'red', 11]],
        2: [[30, 30, 'black', 7], [70, 70, 'black', 7]],
        3: [[28, 28, 'black', 6.5], [50, 50, 'black', 6.5], [72, 72, 'black', 6.5]],
        4: [[30, 30, 'red', 7], [70, 30, 'red', 7], [30, 70, 'red', 7], [70, 70, 'red', 7]],
        5: [[28, 28, 'black', 6.5], [72, 28, 'black', 6.5], [50, 50, 'red', 7.5], [28, 72, 'black', 6.5], [72, 72, 'black', 6.5]],
        6: [[30, 25, 'black', 6], [30, 50, 'black', 6], [30, 75, 'black', 6], [70, 25, 'black', 6], [70, 50, 'black', 6], [70, 75, 'black', 6]]
      };
      const pips = pipsMap[face] || [[50, 50, 'black', 8]];
      return `
        <svg width="${size}" height="${size}" viewBox="0 0 100 100" class="rounded-xl shadow-md border-2 border-slate-300 bg-gradient-to-b from-white to-slate-100 flex-shrink-0">
          <rect x="3" y="3" width="94" height="94" rx="18" fill="white" stroke="#cbd5e1" stroke-width="2"/>
          ${pips.map(([cx, cy, color, r]) => `<circle cx="${cx}" cy="${cy}" r="${r}" fill="${color === 'red' ? '#ef4444' : '#0f172a'}"/>`).join('')}
        </svg>
      `;
    }

    function renderHero(product) {
      document.getElementById('heroGameBadge').textContent = product.name;
      document.getElementById('heroGameDesc').textContent = product.description;
      document.getElementById('heroTotalDraws').textContent = (product.total_draws || 0).toLocaleString();
      document.getElementById('heroFirstDate').textContent = product.first_draw || 'N/A';

      const latest = product.latest;
      if (!latest) {
        document.getElementById('heroBallsContainer').innerHTML = `<p class="text-slate-500">Chưa có kết quả.</p>`;
        return;
      }

      document.getElementById('heroDrawId').textContent = `Kỳ quay: #${latest.id || 'N/A'}`;
      document.getElementById('heroDrawDate').textContent = latest.date || '';

      const container = document.getElementById('heroBallsContainer');
      const legend = document.getElementById('ballLegend');
      legend.innerHTML = '';

      const sumEl = document.getElementById('heroSumVal');
      const sumSnapshotWrap = document.getElementById('heroSumSnapshotWrap');
      if (product.type === 'lotto' && latest && Array.isArray(latest.result)) {
        const mainCount = product.balls || 6;
        const sumVal = latest.result.slice(0, mainCount).reduce((a, b) => a + b, 0);
        if (sumEl) sumEl.textContent = sumVal;
        if (sumSnapshotWrap) sumSnapshotWrap.classList.remove('hidden');
      } else {
        if (sumSnapshotWrap) sumSnapshotWrap.classList.add('hidden');
      }

      if (product.type === 'lotto') {
        const res = latest.result || [];
        const mainCount = product.balls || 6;
        const mainBalls = res.slice(0, mainCount);
        const specialBall = (product.has_special && res.length > mainCount) ? res[mainCount] : null;

        let ballsHtml = mainBalls.map(num => `
          <div class="lotto-ball ball-red w-12 h-12 sm:w-14 sm:h-14 text-lg sm:text-xl font-mono">
            ${String(num).padStart(2, '0')}
          </div>
        `).join('');

        if (specialBall !== null) {
          const is535 = currentProductKey === 'power_535';
          const badgeText = is535 ? 'Số Đặc Biệt (01-12)' : 'Jackpot 2';
          ballsHtml += `
            <div class="flex items-center text-slate-600 font-bold text-xl px-1">+</div>
            <div class="relative group">
              <div class="lotto-ball ball-gold w-12 h-12 sm:w-14 sm:h-14 text-lg sm:text-xl font-mono">
                ${String(specialBall).padStart(2, '0')}
              </div>
              <span class="absolute -top-7 left-1/2 -translate-x-1/2 text-[10px] font-bold text-amber-400 uppercase tracking-widest whitespace-nowrap bg-amber-950/80 px-2 py-0.5 rounded border border-amber-800/60">${badgeText}</span>
            </div>
          `;
          legend.innerHTML = is535 ? `🔴 5 Số chính (01 - 35) | 🟡 Số đặc biệt (01 - 12)` : `🔴 Bóng chính | 🟡 Bóng Jackpot 2`;
        }
        container.innerHTML = ballsHtml;

      } else if (product.type === 'keno') {
        const res = latest.result || [];
        container.innerHTML = `
          <div class="grid grid-cols-5 sm:grid-cols-10 gap-2 w-full">
            ${res.map(num => `
              <div class="lotto-ball ball-blue w-9 h-9 sm:w-11 sm:h-11 text-xs sm:text-sm font-mono mx-auto">
                ${String(num).padStart(2, '0')}
              </div>
            `).join('')}
          </div>
        `;
      } else if (product.type === 'bingo18') {
        const res = latest.result || [];
        const isTriple = (res.length === 3 && res[0] === res[1] && res[1] === res[2]);
        container.innerHTML = `
          <div class="flex flex-wrap items-center gap-4 sm:gap-6">
            <div class="flex items-center gap-3">
              ${res.map(num => renderDiceSVG(num, 54)).join('')}
            </div>
            <div class="flex items-center gap-4 pl-4 sm:pl-6 border-l border-slate-800">
              <div>
                <span class="text-[11px] text-slate-400 block font-sans">Tổng điểm:</span>
                <span class="text-3xl font-black font-mono text-amber-400">${latest.total || res.reduce((a, b) => a + b, 0)}</span>
              </div>
              <div class="flex flex-col gap-1">
                <span class="text-xs font-bold px-2.5 py-1 rounded-lg font-mono inline-flex items-center gap-1 ${
                  latest.large_small === 'Lớn' 
                    ? 'bg-rose-500/20 text-rose-300 border border-rose-500/40' 
                    : (latest.large_small === 'Nhỏ' ? 'bg-sky-500/20 text-sky-300 border border-sky-500/40' : 'bg-amber-500/20 text-amber-300 border border-amber-500/40')
                }">
                  ${latest.large_small || ''}
                </span>
                ${isTriple ? `
                  <span class="text-[10px] font-bold px-2 py-0.5 rounded bg-yellow-500/20 text-yellow-300 border border-yellow-500/50 animate-pulse">
                    ⚡ BÃO NỔ
                  </span>
                ` : ''}
              </div>
            </div>
          </div>
        `;
      } else if (product.type === '3d') {
        const res = latest.result || {};
        container.innerHTML = `
          <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 w-full">
            ${Object.entries(res).map(([prizeName, nums]) => `
              <div class="bg-slate-950/90 rounded-xl p-3 border border-slate-800">
                <div class="text-[11px] uppercase font-bold text-amber-400 tracking-wider mb-2">${prizeName}</div>
                <div class="flex flex-wrap gap-1.5">
                  ${(Array.isArray(nums) ? nums : [nums]).map(n => `
                    <span class="px-2.5 py-1 rounded-lg bg-slate-800 text-slate-200 font-mono text-sm font-semibold tracking-wider border border-slate-700">
                      ${n}
                    </span>
                  `).join('')}
                </div>
              </div>
            `).join('')}
          </div>
        `;
      }
    }

    function populateDrawSelect(history) {
      const select = document.getElementById('compareDrawSelect');
      select.innerHTML = history.slice(0, 50).map((draw, idx) => `
        <option value="${idx}">Kỳ #${draw.id} (${draw.date})</option>
      `).join('');
    }

    function generateRandomTicket() {
      const product = appData.products[currentProductKey];
      if (!product) return;
      const count = product.balls || 6;
      const max = product.max_number || 55;
      const numbers = new Set();
      while (numbers.size < count) {
        numbers.add(Math.floor(Math.random() * max) + 1);
      }
      const sorted = Array.from(numbers).sort((a, b) => a - b);
      if (currentProductKey === 'power_535') {
        const special = Math.floor(Math.random() * 12) + 1;
        document.getElementById('ticketInput').value = `${sorted.join(', ')} + ${special}`;
      } else {
        document.getElementById('ticketInput').value = sorted.join(', ');
      }
      checkTicket();
    }

    function checkTicket() {
      const inputStr = document.getElementById('ticketInput').value.trim();
      const resultBox = document.getElementById('ticketResultBox');
      if (!inputStr) {
        resultBox.innerHTML = `<div class="text-slate-400 text-sm text-center">Vui lòng nhập số vé để dò!</div>`;
        return;
      }

      const product = appData.products[currentProductKey];
      const select = document.getElementById('compareDrawSelect');
      const selectedIndex = parseInt(select.value) || 0;
      const draw = (product.history && product.history[selectedIndex]) || product.latest;
      if (!draw) return;

      const userNumbers = inputStr.split(/[\s,;+-]+/).filter(Boolean).map(n => parseInt(n)).filter(n => !isNaN(n));
      const drawResult = draw.result || [];

      if (product.type === 'lotto') {
        const mainCount = product.balls || 6;
        const mainDrawBalls = drawResult.slice(0, mainCount);
        const specialBall = (product.has_special && drawResult.length > mainCount) ? drawResult[mainCount] : null;

        const matchedMain = userNumbers.filter(n => mainDrawBalls.includes(n));
        const matchedSpecial = specialBall && userNumbers.includes(specialBall);

        let prizeName = 'Không trúng giải';
        let isWin = false;
        let prizeColor = 'text-slate-400';

        if (product.name === 'Power 6/55' || currentProductKey === 'power_655') {
          if (matchedMain.length === 6) { prizeName = '🏆 TRÚNG JACKPOT 1 (Khởi điểm 30 TỶ)'; isWin = true; prizeColor = 'text-amber-400 font-extrabold'; }
          else if (matchedMain.length === 5 && matchedSpecial) { prizeName = '💎 TRÚNG JACKPOT 2 (Khởi điểm 3 TỶ)'; isWin = true; prizeColor = 'text-amber-300 font-bold'; }
          else if (matchedMain.length === 5) { prizeName = '⭐ TRÚNG GIẢI NHẤT (40.000.000đ)'; isWin = true; prizeColor = 'text-emerald-400 font-bold'; }
          else if (matchedMain.length === 4) { prizeName = '🎉 TRÚNG GIẢI NHÌ (500.000đ)'; isWin = true; prizeColor = 'text-emerald-400'; }
          else if (matchedMain.length === 3) { prizeName = '🎯 TRÚNG GIẢI BA (50.000đ)'; isWin = true; prizeColor = 'text-emerald-400'; }
        } else if (product.name === 'Mega 6/45' || currentProductKey === 'power_645') {
          if (matchedMain.length === 6) { prizeName = '🏆 TRÚNG JACKPOT (Khởi điểm 12 TỶ)'; isWin = true; prizeColor = 'text-amber-400 font-extrabold'; }
          else if (matchedMain.length === 5) { prizeName = '⭐ TRÚNG GIẢI NHẤT (10.000.000đ)'; isWin = true; prizeColor = 'text-emerald-400 font-bold'; }
          else if (matchedMain.length === 4) { prizeName = '🎉 TRÚNG GIẢI NHÌ (300.000đ)'; isWin = true; prizeColor = 'text-emerald-400'; }
          else if (matchedMain.length === 3) { prizeName = '🎯 TRÚNG GIẢI BA (30.000đ)'; isWin = true; prizeColor = 'text-emerald-400'; }
        } else if (product.name === 'Power 5/35' || currentProductKey === 'power_535') {
          if (matchedMain.length === 5 && matchedSpecial) { prizeName = '🏆 TRÚNG GIẢI ĐỘC ĐẮC (Tối thiểu 6 TỶ)'; isWin = true; prizeColor = 'text-amber-400 font-extrabold'; }
          else if (matchedMain.length === 5) { prizeName = '⭐ TRÚNG GIẢI NHẤT (10.000.000đ)'; isWin = true; prizeColor = 'text-emerald-400 font-bold'; }
          else if (matchedMain.length === 4 && matchedSpecial) { prizeName = '💎 TRÚNG GIẢI NHÌ (5.000.000đ)'; isWin = true; prizeColor = 'text-emerald-400 font-bold'; }
          else if (matchedMain.length === 4) { prizeName = '🎉 TRÚNG GIẢI BA (500.000đ)'; isWin = true; prizeColor = 'text-emerald-400'; }
          else if (matchedMain.length === 3 && matchedSpecial) { prizeName = '🎯 TRÚNG GIẢI TƯ (100.000đ)'; isWin = true; prizeColor = 'text-emerald-400'; }
          else if (matchedMain.length === 3) { prizeName = '🎖️ TRÚNG GIẢI NĂM (30.000đ)'; isWin = true; prizeColor = 'text-emerald-400'; }
          else if (matchedSpecial) { prizeName = '✨ TRÚNG GIẢI KHUYẾN KHÍCH (10.000đ)'; isWin = true; prizeColor = 'text-teal-400'; }
        } else {
          if (matchedMain.length >= 3) { prizeName = `🎯 Trùng ${matchedMain.length} số!`; isWin = true; prizeColor = 'text-emerald-400 font-bold'; }
        }

        if (isWin) {
          confetti({ particleCount: 80, spread: 60, origin: { y: 0.6 } });
        }

        resultBox.innerHTML = `
          <div class="space-y-2">
            <div class="flex items-center justify-between">
              <span class="text-xs text-slate-400">Kết quả đối chiếu (Kỳ #${draw.id}):</span>
              <span class="text-xs font-mono text-slate-300">Trùng <strong>${matchedMain.length}</strong> số</span>
            </div>
            <div class="text-base sm:text-lg ${prizeColor}">${prizeName}</div>
            <div class="flex flex-wrap gap-1.5 pt-1">
              ${userNumbers.map(n => {
                const isMatch = mainDrawBalls.includes(n);
                const isSpec = n === specialBall;
                let cls = 'bg-slate-800 text-slate-400 border-slate-700';
                if (isMatch) cls = 'bg-rose-600 text-white border-rose-400 font-bold shadow-md shadow-rose-900/40';
                else if (isSpec) cls = 'bg-amber-500 text-white border-amber-300 font-bold';
                return `<span class="px-2 py-0.5 rounded text-xs font-mono border ${cls}">${n}</span>`;
              }).join('')}
            </div>
          </div>
        `;
      }
    }

    function renderHotCold(product) {
      const hotContainer = document.getElementById('hotNumbersList');
      const coldContainer = document.getElementById('coldNumbersList');
      const hot = product.hot_numbers || [];
      const cold = product.cold_numbers || [];

      if (!hot.length) {
        hotContainer.innerHTML = '<p class="text-xs text-slate-500">Chưa có dữ liệu.</p>';
        coldContainer.innerHTML = '<p class="text-xs text-slate-500">Chưa có dữ liệu.</p>';
        return;
      }
      const maxCount = hot[0] ? hot[0].count : 1;

      hotContainer.innerHTML = hot.map(item => `
        <div class="flex items-center justify-between text-xs">
          <div class="flex items-center space-x-2.5">
            <span class="w-6 h-6 rounded-full bg-rose-500/20 text-rose-400 font-mono font-bold flex items-center justify-center text-[11px] border border-rose-500/30">
              ${item.number}
            </span>
            <span class="text-slate-300 font-medium">Xuất hiện ${item.count} lần</span>
          </div>
          <div class="flex items-center space-x-2 w-32">
            <div class="flex-1 bg-slate-800 h-2 rounded-full overflow-hidden">
              <div class="bg-gradient-to-r from-rose-500 to-amber-400 h-full rounded-full" style="width: ${(item.count / maxCount) * 100}%"></div>
            </div>
            <span class="font-mono text-slate-400 w-10 text-right">${item.pct || ''}%</span>
          </div>
        </div>
      `).join('');

      coldContainer.innerHTML = cold.map(item => `
        <div class="flex items-center justify-between text-xs">
          <div class="flex items-center space-x-2.5">
            <span class="w-6 h-6 rounded-full bg-cyan-500/20 text-cyan-400 font-mono font-bold flex items-center justify-center text-[11px] border border-cyan-500/30">
              ${item.number}
            </span>
            <span class="text-slate-300 font-medium">Xuất hiện ${item.count} lần</span>
          </div>
          <div class="flex items-center space-x-2 w-32">
            <div class="flex-1 bg-slate-800 h-2 rounded-full overflow-hidden">
              <div class="bg-cyan-500 h-full rounded-full" style="width: ${(item.count / maxCount) * 100}%"></div>
            </div>
            <span class="font-mono text-slate-400 w-10 text-right">${item.pct || ''}%</span>
          </div>
        </div>
      `).join('');
    }

    // --- 2. GAP / SKIP ANALYSIS ---
    function renderGapAnalysis(product) {
      const topCards = document.getElementById('topGanCards');
      const tableBody = document.getElementById('gapTableBody');
      const overdue = product.top_overdue || [];
      const gaps = product.gap_analysis || [];

      if (!gaps.length) {
        topCards.innerHTML = '<p class="text-xs text-slate-500 col-span-full">Loại hình này chưa có thống kê số gan.</p>';
        tableBody.innerHTML = '<tr><td colspan="7" class="py-4 text-center text-slate-500">Không có dữ liệu</td></tr>';
        return;
      }

      // Top 6 Overdue Cards
      topCards.innerHTML = overdue.slice(0, 6).map(g => {
        const isOver = g.heat_ratio >= 1.0;
        return `
          <div class="bg-slate-950 p-3 rounded-xl border ${isOver ? 'border-rose-700/60 bg-rose-950/20' : 'border-slate-800'}">
            <div class="flex items-center justify-between">
              <span class="w-7 h-7 rounded-full bg-slate-800 font-mono font-bold text-sm text-white flex items-center justify-center border border-slate-700">${g.number}</span>
              <span class="text-[10px] uppercase font-bold px-1.5 py-0.5 rounded ${isOver ? 'bg-rose-600 text-white' : 'bg-slate-800 text-slate-400'}">
                ${isOver ? 'Quá Nhịp' : 'Bình thường'}
              </span>
            </div>
            <div class="mt-2 text-xl font-mono font-extrabold text-amber-400">${g.current_gap} <span class="text-xs font-normal text-slate-400">kỳ vắng</span></div>
            <div class="text-[11px] text-slate-400 mt-1">TB: ${g.avg_gap} kỳ | Max: ${g.max_gap}</div>
          </div>
        `;
      }).join('');

      // Full Gap Table (Sorted by number)
      tableBody.innerHTML = gaps.map(g => {
        let statusBadge = '<span class="text-slate-400">Bình thường</span>';
        let barColor = 'bg-cyan-500';
        if (g.heat_ratio >= 1.5) {
          statusBadge = '<span class="text-rose-400 font-bold">🔥 Gan cực đại</span>';
          barColor = 'bg-rose-500';
        } else if (g.heat_ratio >= 1.0) {
          statusBadge = '<span class="text-amber-400 font-semibold">⚠️ Quá chu kỳ</span>';
          barColor = 'bg-amber-500';
        }

        const barPct = Math.min(Math.round((g.current_gap / g.max_gap) * 100), 100);

        return `
          <tr class="hover:bg-slate-850 transition">
            <td class="py-2.5 px-3 font-bold text-white">${String(g.number).padStart(2, '0')}</td>
            <td class="py-2.5 px-3 text-amber-400 font-bold">${g.current_gap} kỳ</td>
            <td class="py-2.5 px-3 text-slate-300">${g.avg_gap}</td>
            <td class="py-2.5 px-3 text-slate-400">${g.max_gap} kỳ</td>
            <td class="py-2.5 px-3 text-slate-300">${g.appearances}</td>
            <td class="py-2.5 px-3">
              <div class="w-24 bg-slate-800 h-2 rounded-full overflow-hidden">
                <div class="${barColor} h-full rounded-full" style="width: ${barPct}%"></div>
              </div>
            </td>
            <td class="py-2.5 px-3 text-right">${statusBadge}</td>
          </tr>
        `;
      }).join('');
    }

    let selectedMatrixBall = 8;

    function renderCooccurrence(product) {
      const ca = product?.cooccurrence_analytics;
      const maxVal = product?.max_number || (currentProductKey === 'power_645' ? 45 : 55);

      // Render Ball Grid Selector
      const ballGrid = document.getElementById('matrixBallGridSelector');
      if (ballGrid) {
        ballGrid.innerHTML = Array.from({ length: maxVal }, (_, i) => i + 1).map(num => {
          const isSelected = num === selectedMatrixBall;
          const cls = isSelected 
            ? 'bg-amber-500 text-slate-950 font-black shadow-md shadow-amber-950/50 border-amber-300 scale-105' 
            : 'bg-slate-800 text-slate-300 border-slate-700 hover:border-indigo-400 hover:text-white';
          return `
            <button onclick="selectMatrixInspectorBall(${num})" class="w-8 h-8 rounded-full font-mono text-xs flex items-center justify-center border transition ${cls}">
              ${String(num).padStart(2, '0')}
            </button>
          `;
        }).join('');
      }

      // Render Companions for current selected ball
      renderMatrixBallCompanions(product, selectedMatrixBall);

      // Render Top 15 Pairs
      const pairsContainer = document.getElementById('pairsListContainer');
      if (pairsContainer) {
        const topPairs = ca?.top_pairs || [];
        if (!topPairs.length) {
          pairsContainer.innerHTML = '<p class="text-xs text-slate-500 py-4 text-center">Chưa có dữ liệu ma trận đồng quy.</p>';
        } else {
          pairsContainer.innerHTML = topPairs.map((p, idx) => `
            <div class="flex items-center justify-between p-3 rounded-xl bg-slate-950 border border-slate-800/90 hover:border-indigo-500/40 transition">
              <div class="flex items-center space-x-3">
                <span class="text-xs font-mono font-bold text-slate-500 w-5">#${idx + 1}</span>
                <div class="flex space-x-1.5">
                  <span class="w-8 h-8 rounded-full bg-gradient-to-tr from-indigo-600 to-indigo-500 text-white font-mono font-bold text-xs flex items-center justify-center shadow">${String(p.ball1).padStart(2, '0')}</span>
                  <span class="w-8 h-8 rounded-full bg-gradient-to-tr from-indigo-600 to-indigo-500 text-white font-mono font-bold text-xs flex items-center justify-center shadow">${String(p.ball2).padStart(2, '0')}</span>
                </div>
                <div class="text-[11px] text-slate-300 font-medium">
                  Cặp Đồng Quy
                  <span class="px-1.5 py-0.5 rounded text-[9px] font-bold bg-amber-500/20 text-amber-300 border border-amber-500/30 ml-1.5">Lift ${p.lift}x</span>
                </div>
              </div>
              <div class="text-right">
                <div class="text-sm font-bold font-mono text-amber-400">${p.count} <span class="text-xs font-normal text-slate-400">kỳ nổ cùng</span></div>
                <div class="text-[10px] text-slate-500">Tỷ lệ: ${p.probability_pct}% (200 kỳ)</div>
              </div>
            </div>
          `).join('');
        }
      }

      // Render Graph Communities
      const commContainer = document.getElementById('communitiesContainer');
      if (commContainer) {
        const comms = ca?.communities || [];
        if (!comms.length) {
          commContainer.innerHTML = '<p class="text-xs text-slate-500 py-4 text-center">Chưa có phân cụm đồ thị.</p>';
        } else {
          const colors = [
            { bg: 'border-blue-500/30 bg-blue-950/20', text: 'text-blue-400', ball: 'bg-blue-600/30 border-blue-500/50 text-blue-200' },
            { bg: 'border-emerald-500/30 bg-emerald-950/20', text: 'text-emerald-400', ball: 'bg-emerald-600/30 border-emerald-500/50 text-emerald-200' },
            { bg: 'border-purple-500/30 bg-purple-950/20', text: 'text-purple-400', ball: 'bg-purple-600/30 border-purple-500/50 text-purple-200' },
            { bg: 'border-amber-500/30 bg-amber-950/20', text: 'text-amber-400', ball: 'bg-amber-600/30 border-amber-500/50 text-amber-200' },
            { bg: 'border-rose-500/30 bg-rose-950/20', text: 'text-rose-400', ball: 'bg-rose-600/30 border-rose-500/50 text-rose-200' }
          ];

          commContainer.innerHTML = comms.map((cluster, idx) => {
            const col = colors[idx % colors.length];
            return `
              <div class="p-3.5 rounded-xl border ${col.bg} space-y-2">
                <div class="flex items-center justify-between">
                  <span class="text-xs font-bold ${col.text} uppercase tracking-wider flex items-center gap-1.5">
                    <i data-lucide="layers" class="w-3.5 h-3.5"></i>
                    Cụm Đồ Thị #${idx + 1} (${cluster.length} số)
                  </span>
                  <span class="text-[10px] text-slate-400">Độ liên kết nội bộ cao</span>
                </div>
                <div class="flex flex-wrap gap-1.5">
                  ${cluster.map(num => `
                    <span class="w-7 h-7 rounded-full ${col.ball} font-mono font-bold text-xs flex items-center justify-center border">
                      ${String(num).padStart(2, '0')}
                    </span>
                  `).join('')}
                </div>
              </div>
            `;
          }).join('');
        }
      }

      lucide.createIcons();
    }

    function selectMatrixInspectorBall(num) {
      selectedMatrixBall = num;
      const product = appData?.products?.[currentProductKey];
      if (product) renderCooccurrence(product);
    }

    function renderMatrixBallCompanions(product, ballNum) {
      const ca = product?.cooccurrence_analytics;
      const labelEl = document.getElementById('selectedBallInspectorLabel');
      if (labelEl) labelEl.textContent = `Đang soi bóng: ${String(ballNum).padStart(2, '0')}`;

      const container = document.getElementById('matrixCompanionsList');
      if (!container) return;

      const companions = ca?.companions_map?.[String(ballNum)] || [];
      if (!companions.length) {
        container.innerHTML = '<p class="text-xs text-slate-500 col-span-full py-2">Không có dữ liệu cặp thân thiết cho bóng này.</p>';
        return;
      }

      container.innerHTML = companions.map(comp => `
        <div class="p-3 rounded-xl bg-slate-900 border border-slate-800 flex flex-col items-center justify-between text-center space-y-2 hover:border-amber-500/50 transition">
          <div class="flex items-center gap-1.5">
            <span class="w-7 h-7 rounded-full bg-slate-800 text-slate-400 font-mono font-bold text-xs flex items-center justify-center border border-slate-700">
              ${String(ballNum).padStart(2, '0')}
            </span>
            <i data-lucide="link" class="w-3 h-3 text-amber-400"></i>
            <span class="w-8 h-8 rounded-full bg-gradient-to-tr from-amber-500 to-yellow-600 text-slate-950 font-mono font-bold text-xs flex items-center justify-center shadow border border-yellow-300">
              ${String(comp.number).padStart(2, '0')}
            </span>
          </div>
          <div class="text-center font-mono">
            <div class="text-xs font-bold text-white">${comp.count} kỳ chung</div>
            <div class="text-[9px] text-amber-400">Lift ${comp.lift}x</div>
          </div>
          <button onclick="applyGoldenTicketToChecker('${ballNum}, ${comp.number}')" class="w-full py-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 text-[10px] font-semibold transition">
            Ghép Dò Vé
          </button>
        </div>
      `).join('');
      lucide.createIcons();
    }


    // --- 4. SUM DISTRIBUTION ---
    function renderSumStats(product) {
      const kpiContainer = document.getElementById('sumKpiCards');
      const sumStats = product.sum_stats;

      if (!sumStats || !sumStats.avg_sum) {
        kpiContainer.innerHTML = '<p class="text-xs text-slate-500 col-span-full">Chưa có dữ liệu tổng giải.</p>';
        return;
      }

      document.getElementById('sumSafeZoneBadge').textContent = `Vùng an toàn (±1 Std): ${sumStats.safe_zone}`;

      kpiContainer.innerHTML = `
        <div class="bg-slate-950 p-3.5 rounded-xl border border-slate-800">
          <div class="text-xs text-slate-400">Tổng Trung Bình</div>
          <div class="text-xl font-bold font-mono text-white mt-1">${sumStats.avg_sum}</div>
          <div class="text-[11px] text-emerald-400 mt-0.5">Kỳ vọng toán học</div>
        </div>
        <div class="bg-slate-950 p-3.5 rounded-xl border border-slate-800">
          <div class="text-xs text-slate-400">Trung Vị (Median)</div>
          <div class="text-xl font-bold font-mono text-amber-400 mt-1">${sumStats.median_sum}</div>
          <div class="text-[11px] text-slate-400 mt-0.5">Điểm cân bằng giữa</div>
        </div>
        <div class="bg-slate-950 p-3.5 rounded-xl border border-slate-800">
          <div class="text-xs text-slate-400">Độ lệch chuẩn (Std Dev)</div>
          <div class="text-xl font-bold font-mono text-cyan-400 mt-1">±${sumStats.std_dev}</div>
          <div class="text-[11px] text-slate-400 mt-0.5">Biên độ dao động</div>
        </div>
        <div class="bg-slate-950 p-3.5 rounded-xl border border-slate-800">
          <div class="text-xs text-slate-400">Kỷ Lục Min / Max</div>
          <div class="text-xl font-bold font-mono text-rose-400 mt-1">${sumStats.min_sum} - ${sumStats.max_sum}</div>
          <div class="text-[11px] text-slate-400 mt-0.5">Thấp nhất & Cao nhất</div>
        </div>
      `;

      renderSumChart();
      renderSumTrendChart();
    }

    function renderSumChart() {
      const product = appData.products[currentProductKey];
      if (!product || !product.sum_stats || !product.sum_stats.distribution) return;

      const ctx = document.getElementById('sumChart').getContext('2d');
      const dist = product.sum_stats.distribution;

      if (sumChartInstance) sumChartInstance.destroy();

      sumChartInstance = new Chart(ctx, {
        type: 'bar',
        data: {
          labels: dist.map(d => d.range),
          datasets: [{
            label: 'Tỷ lệ %',
            data: dist.map(d => d.pct),
            backgroundColor: [
              'rgba(100, 116, 139, 0.6)',
              'rgba(59, 130, 246, 0.7)',
              'rgba(16, 185, 129, 0.85)',
              'rgba(16, 185, 129, 0.85)',
              'rgba(59, 130, 246, 0.7)',
              'rgba(100, 116, 139, 0.6)'
            ],
            borderRadius: 6
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { display: false },
            tooltip: {
              callbacks: {
                label: (c) => `Tỷ lệ: ${c.raw}% (${dist[c.dataIndex].count} kỳ quay)`
              }
            }
          },
          scales: {
            x: { ticks: { color: '#94a3b8' }, grid: { display: false } },
            y: { ticks: { color: '#94a3b8' }, grid: { color: 'rgba(51, 65, 85, 0.3)' } }
          }
        }
      });
    }

    // --- STOCK-LIKE SUM TREND TIME-SERIES (MA5 + BANDS) ---
    let sumTrendChartInstance = null;
    let currentSumTrendRange = 50;

    function setSumTrendRange(range) {
      currentSumTrendRange = range;
      ['30', '50', '100'].forEach(r => {
        const btn = document.getElementById(`btnSumTrend${r}`);
        if (btn) {
          if (parseInt(r) === range) {
            btn.className = 'px-2.5 py-1 rounded-md bg-emerald-600 text-white font-bold transition font-mono';
          } else {
            btn.className = 'px-2.5 py-1 rounded-md text-slate-400 hover:text-white transition font-mono';
          }
        }
      });
      renderSumTrendChart();
    }

    function renderSumTrendChart() {
      const product = appData?.products?.[currentProductKey];
      if (!product || !product.history || !product.history.length) return;
      const canvas = document.getElementById('sumTrendChart');
      if (!canvas) return;

      const numBalls = product.balls || 6;
      const rawRecords = product.history.slice(0, currentSumTrendRange).reverse();
      if (!rawRecords.length) return;

      const labels = [];
      const sumValues = [];
      const dates = [];

      rawRecords.forEach(r => {
        labels.push(`#${r.id}`);
        dates.push(r.date || '');
        const res = (r.result || []).slice(0, numBalls);
        const s = res.reduce((a, b) => a + b, 0);
        sumValues.push(s);
      });

      const ma5Values = [];
      for (let i = 0; i < sumValues.length; i++) {
        if (i < 4) {
          const slice = sumValues.slice(0, i + 1);
          ma5Values.push(Math.round(slice.reduce((a, b) => a + b, 0) / slice.length));
        } else {
          const slice = sumValues.slice(i - 4, i + 1);
          ma5Values.push(Math.round(slice.reduce((a, b) => a + b, 0) / 5));
        }
      }

      const mean = product.sum_stats?.avg_sum || Math.round(sumValues.reduce((a, b) => a + b, 0) / sumValues.length);
      const stdDev = product.sum_stats?.std_dev || 37;
      const upperBand = Math.round(mean + stdDev);
      const lowerBand = Math.round(mean - stdDev);

      const meanLine = Array(sumValues.length).fill(mean);
      const upperLine = Array(sumValues.length).fill(upperBand);
      const lowerLine = Array(sumValues.length).fill(lowerBand);

      const latestSum = sumValues[sumValues.length - 1];
      const latestMa5 = ma5Values[ma5Values.length - 1];
      const latestRecord = rawRecords[rawRecords.length - 1];

      const idEl = document.getElementById('trendLatestId');
      if (idEl) idEl.textContent = latestRecord.id || '--';

      const sumEl = document.getElementById('trendLatestSum');
      if (sumEl) sumEl.textContent = `${latestSum}`;

      const ma5El = document.getElementById('trendMa5');
      if (ma5El) ma5El.textContent = `${latestMa5}`;

      const signalEl = document.getElementById('trendSignal');
      if (signalEl) {
        if (latestSum > upperBand) {
          signalEl.textContent = 'Quá Cao 🔻 (Xu hướng giảm ở kỳ tới)';
          signalEl.className = 'font-bold text-rose-400 text-xs';
        } else if (latestSum < lowerBand) {
          signalEl.textContent = 'Quá Thấp 🔺 (Xu hướng tăng ở kỳ tới)';
          signalEl.className = 'font-bold text-cyan-400 text-xs';
        } else {
          signalEl.textContent = 'Cân Bằng 🟢 (Trong dải an toàn)';
          signalEl.className = 'font-bold text-emerald-400 text-xs';
        }
      }

      if (sumTrendChartInstance) sumTrendChartInstance.destroy();

      const ctx = canvas.getContext('2d');
      const gradient = ctx.createLinearGradient(0, 0, 0, 300);
      gradient.addColorStop(0, 'rgba(16, 185, 129, 0.35)');
      gradient.addColorStop(1, 'rgba(16, 185, 129, 0.0)');

      sumTrendChartInstance = new Chart(ctx, {
        type: 'line',
        data: {
          labels: labels,
          datasets: [
            {
              label: 'Tổng giải kỳ quay',
              data: sumValues,
              borderColor: 'rgb(16, 185, 129)',
              backgroundColor: gradient,
              borderWidth: 2,
              fill: true,
              tension: 0.25,
              pointRadius: sumValues.length > 50 ? 2 : 3.5,
              pointHoverRadius: 6,
              pointBackgroundColor: 'rgb(16, 185, 129)',
              order: 1
            },
            {
              label: 'Đường MA5',
              data: ma5Values,
              borderColor: 'rgb(245, 158, 11)',
              borderWidth: 2,
              borderDash: [5, 4],
              fill: false,
              tension: 0.35,
              pointRadius: 0,
              order: 2
            },
            {
              label: 'Kỳ vọng (Mean)',
              data: meanLine,
              borderColor: 'rgba(6, 182, 212, 0.7)',
              borderWidth: 1.5,
              borderDash: [3, 3],
              fill: false,
              pointRadius: 0,
              order: 3
            },
            {
              label: 'Dải trần (+1σ)',
              data: upperLine,
              borderColor: 'rgba(244, 63, 94, 0.4)',
              borderWidth: 1,
              borderDash: [2, 2],
              fill: false,
              pointRadius: 0,
              order: 4
            },
            {
              label: 'Dải sàn (-1σ)',
              data: lowerLine,
              borderColor: 'rgba(59, 130, 246, 0.4)',
              borderWidth: 1,
              borderDash: [2, 2],
              fill: false,
              pointRadius: 0,
              order: 5
            }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          interaction: {
            mode: 'index',
            intersect: false
          },
          plugins: {
            legend: { display: false },
            tooltip: {
              backgroundColor: 'rgba(15, 23, 42, 0.95)',
              titleColor: '#f8fafc',
              bodyColor: '#cbd5e1',
              borderColor: '#334155',
              borderWidth: 1,
              padding: 10,
              callbacks: {
                title: (items) => {
                  const idx = items[0].dataIndex;
                  return `Kỳ quay ${labels[idx]} (${dates[idx]})`;
                },
                label: (item) => {
                  return ` ${item.dataset.label}: ${item.raw}`;
                }
              }
            }
          },
          scales: {
            x: {
              grid: { color: 'rgba(51, 65, 85, 0.2)' },
              ticks: {
                color: '#94a3b8',
                font: { size: 10 },
                maxTicksLimit: 14
              }
            },
            y: {
              grid: { color: 'rgba(51, 65, 85, 0.25)' },
              ticks: { color: '#94a3b8', font: { size: 10 } }
            }
          }
        }
      });
    }

    // --- 5. PATTERNS & DECADES ---
    function renderPatternMetrics(product) {
      const container = document.getElementById('patternMetricsContainer');
      const patterns = product.patterns;

      if (!patterns || patterns.consecutive_pct === undefined) {
        container.innerHTML = '<p class="text-xs text-slate-500">Chưa có dữ liệu mẫu hình cho loại hình này.</p>';
        return;
      }

      container.innerHTML = `
        <div class="bg-slate-950 p-4 rounded-xl border border-slate-800 space-y-2">
          <div class="flex items-center justify-between">
            <span class="text-xs font-semibold text-slate-300">Xuất hiện Cặp số liền kề (Consecutive Pairs)</span>
            <span class="text-sm font-mono font-bold text-cyan-400">${patterns.consecutive_pct}%</span>
          </div>
          <div class="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
            <div class="bg-cyan-500 h-full rounded-full" style="width: ${patterns.consecutive_pct}%"></div>
          </div>
          <p class="text-[11px] text-slate-400">Gần một nửa số kỳ quay xuất hiện ít nhất 2 số kề sát nhau (như 14-15, 32-33).</p>
        </div>

        <div class="bg-slate-950 p-4 rounded-xl border border-slate-800 space-y-2">
          <div class="flex items-center justify-between">
            <span class="text-xs font-semibold text-slate-300">Tỷ lệ Lặp lại số từ kỳ trước (Repeat Rate)</span>
            <span class="text-sm font-mono font-bold text-amber-400">${patterns.repeat_from_prev_pct}%</span>
          </div>
          <div class="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
            <div class="bg-amber-500 h-full rounded-full" style="width: ${patterns.repeat_from_prev_pct}%"></div>
          </div>
          <p class="text-[11px] text-slate-400">Trung bình có ${patterns.avg_repeat_per_draw} số của kỳ trước rơi lại ở kỳ tiếp theo.</p>
        </div>
      `;

      renderDecadeChart();
    }

    function renderDecadeChart() {
      const product = appData.products[currentProductKey];
      if (!product || !product.patterns || !product.patterns.decade_distribution) return;

      const ctx = document.getElementById('decadeChart').getContext('2d');
      const decades = product.patterns.decade_distribution;

      if (decadeChartInstance) decadeChartInstance.destroy();

      decadeChartInstance = new Chart(ctx, {
        type: 'doughnut',
        data: {
          labels: decades.map(d => `Dải ${d.decade}`),
          datasets: [{
            data: decades.map(d => d.pct),
            backgroundColor: [
              '#f43f5e', '#fb923c', '#eab308', '#22c55e', '#06b6d4', '#8b5cf6'
            ],
            borderWidth: 2,
            borderColor: '#0f172a'
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { position: 'right', labels: { color: '#94a3b8', font: { size: 11 } } },
            tooltip: {
              callbacks: {
                label: (c) => ` ${c.label}: ${c.raw}%`
              }
            }
          }
        }
      });
    }

    // --- 6. SMART TICKET GENERATOR ---
    function generateSmartTickets() {
      const product = appData.products[currentProductKey];
      if (!product || product.type !== 'lotto') {
        alert('Bộ tạo vé hiện áp dụng cho các game dãy bóng số (Power 6/55, Mega 6/45, Power 5/35).');
        return;
      }

      const minSum = parseInt(document.getElementById('genMinSum').value) || 120;
      const maxSum = parseInt(document.getElementById('genMaxSum').value) || 200;
      const oddEvenOpt = document.getElementById('genOddEven').value;
      const mixOpt = document.getElementById('genStrategyMix').value;

      const count = product.balls || 6;
      const maxVal = product.max_number || 55;

      const hotNums = (product.hot_numbers || []).map(h => h.number);
      const coldNums = (product.cold_numbers || []).map(c => c.number);

      const generatedTickets = [];
      let attempts = 0;

      while (generatedTickets.length < 4 && attempts < 2000) {
        attempts++;
        const pool = new Set();

        if (mixOpt === 'balanced') {
          // 3 hot, 2 mid, 1 cold
          while (pool.size < 3 && hotNums.length >= 3) {
            pool.add(hotNums[Math.floor(Math.random() * hotNums.length)]);
          }
          while (pool.size < 4 && coldNums.length >= 1) {
            pool.add(coldNums[Math.floor(Math.random() * coldNums.length)]);
          }
          while (pool.size < count) {
            pool.add(Math.floor(Math.random() * maxVal) + 1);
          }
        } else if (mixOpt === 'hot') {
          while (pool.size < Math.min(count, hotNums.length)) {
            pool.add(hotNums[Math.floor(Math.random() * hotNums.length)]);
          }
          while (pool.size < count) {
            pool.add(Math.floor(Math.random() * maxVal) + 1);
          }
        } else if (mixOpt === 'cold') {
          while (pool.size < Math.min(count, coldNums.length)) {
            pool.add(coldNums[Math.floor(Math.random() * coldNums.length)]);
          }
          while (pool.size < count) {
            pool.add(Math.floor(Math.random() * maxVal) + 1);
          }
        } else {
          while (pool.size < count) {
            pool.add(Math.floor(Math.random() * maxVal) + 1);
          }
        }

        const ticket = Array.from(pool).sort((a, b) => a - b);
        const s = ticket.reduce((a, b) => a + b, 0);

        // Sum filter
        if (s < minSum || s > maxSum) continue;

        // Odd Even filter
        const oddCount = ticket.filter(n => n % 2 !== 0).length;
        if (oddEvenOpt === '3_3' && oddCount !== 3) continue;
        if (oddEvenOpt === '4_2' && oddCount !== 2) continue;
        if (oddEvenOpt === '2_4' && oddCount !== 4) continue;

        const ticketStr = ticket.join(',');
        if (!generatedTickets.some(t => t.numbers.join(',') === ticketStr)) {
          const spec = currentProductKey === 'power_535' ? (Math.floor(seededRng() * 12) + 1) : null;
          generatedTickets.push({
            numbers: ticket,
            special: spec,
            sum: s,
            oddCount: oddCount,
            evenCount: count - oddCount
          });
        }
      }

      const container = document.getElementById('generatedTicketsContainer');
      container.innerHTML = generatedTickets.map((t, idx) => `
        <div class="bg-slate-950 p-4 rounded-xl border border-slate-800 space-y-3">
          <div class="flex items-center justify-between text-xs">
            <span class="font-bold text-pink-400">Gợi ý #${idx + 1}</span>
            <span class="text-slate-400">Tổng: <strong>${t.sum}</strong> (${t.oddCount} Lẻ - ${t.evenCount} Chẵn)</span>
          </div>
          <div class="flex flex-wrap items-center gap-2">
            ${t.numbers.map(n => `
              <span class="lotto-ball ball-red w-10 h-10 text-sm font-mono">${String(n).padStart(2, '0')}</span>
            `).join('')}
            ${t.special ? `
              <span class="text-slate-500 font-bold px-1">+</span>
              <div class="relative group">
                <span class="lotto-ball ball-gold w-10 h-10 text-sm font-mono">${String(t.special).padStart(2, '0')}</span>
                <span class="absolute -top-6 left-1/2 -translate-x-1/2 text-[9px] font-bold text-amber-400 whitespace-nowrap bg-slate-900 px-1.5 py-0.5 rounded border border-amber-800">Đặc biệt</span>
              </div>
            ` : ''}
          </div>
          <div class="flex items-center gap-2 pt-1">
            <button onclick="applySmartTicket('${t.numbers.join(', ')}${t.special ? ' + ' + t.special : ''}')" class="flex-1 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold transition">
              Nạp sang Dò Vé
            </button>
            <button onclick="applyToSimulator('${t.numbers.join(', ')}')" class="py-1.5 px-3 rounded-lg bg-slate-800 hover:bg-slate-700 text-yellow-400 text-xs font-semibold transition" title="Nạp vào Giả lập">
              Nuôi số này
            </button>
          </div>
        </div>
      `).join('');

      lucide.createIcons();
    }

    function applySmartTicket(str) {
      document.getElementById('ticketInput').value = str;
      switchView('overview');
      checkTicket();
    }

    function applyToSimulator(str) {
      document.getElementById('simCustomNumbers').value = str;
      document.getElementById('simStrategySelect').value = 'fixed_ticket';
      document.getElementById('simCustomTicketWrap').classList.remove('hidden');
      switchView('simulator');
      runSimulation();
    }

    // --- 7. BACKTEST SIMULATOR ---
    function runSimulation() {
      const product = appData.products[currentProductKey];
      if (!product || !product.history) return;

      const strategy = document.getElementById('simStrategySelect').value;
      const countOpt = document.getElementById('simDrawsCount').value;
      const customNumsStr = document.getElementById('simCustomNumbers').value.trim();

      let targetDraws = product.history.slice(); // already newest first
      if (countOpt !== 'all') {
        const n = parseInt(countOpt) || 100;
        targetDraws = targetDraws.slice(0, n);
      }
      // Reverse to simulate chronologically
      targetDraws = targetDraws.slice().reverse();

      const ticketPrice = 10000;
      let totalSpent = 0;
      let totalWon = 0;
      let prizeStats = { jp1: 0, jp2: 0, first: 0, second: 0, third: 0, none: 0 };
      const pnlPoints = [];
      let runningPnl = 0;

      const hotSet = (product.hot_numbers || []).slice(0, product.balls || 6).map(h => h.number);
      const coldSet = (product.cold_numbers || []).slice(0, product.balls || 6).map(c => c.number);
      const fixedNums = customNumsStr.split(/[\s,;-]+/).map(n => parseInt(n)).filter(n => !isNaN(n));

      targetDraws.forEach((draw, idx) => {
        totalSpent += ticketPrice;
        let pick = [];

        if (strategy === 'fixed_ticket') {
          pick = fixedNums;
        } else if (strategy === 'hot_numbers') {
          pick = hotSet;
        } else if (strategy === 'cold_numbers') {
          pick = coldSet;
        } else {
          // random
          const s = new Set();
          while (s.size < (product.balls || 6)) {
            s.add(Math.floor(Math.random() * (product.max_number || 55)) + 1);
          }
          pick = Array.from(s);
        }

        const res = draw.result || [];
        const mainCount = product.balls || 6;
        const mainBalls = res.slice(0, mainCount);
        const spec = (product.has_special && res.length > mainCount) ? res[mainCount] : null;

        const matchedMain = pick.filter(n => mainBalls.includes(n)).length;
        const matchedSpec = spec && pick.includes(spec);

        let prizeMoney = 0;
        if (product.name === 'Power 6/55') {
          if (matchedMain === 6) { prizeMoney = 30000000000; prizeStats.jp1++; }
          else if (matchedMain === 5 && matchedSpec) { prizeMoney = 3000000000; prizeStats.jp2++; }
          else if (matchedMain === 5) { prizeMoney = 40000000; prizeStats.first++; }
          else if (matchedMain === 4) { prizeMoney = 500000; prizeStats.second++; }
          else if (matchedMain === 3) { prizeMoney = 50000; prizeStats.third++; }
          else { prizeStats.none++; }
        } else if (product.name === 'Mega 6/45') {
          if (matchedMain === 6) { prizeMoney = 12000000000; prizeStats.jp1++; }
          else if (matchedMain === 5) { prizeMoney = 10000000; prizeStats.first++; }
          else if (matchedMain === 4) { prizeMoney = 300000; prizeStats.second++; }
          else if (matchedMain === 3) { prizeMoney = 30000; prizeStats.third++; }
          else { prizeStats.none++; }
        } else {
          if (matchedMain >= 3) { prizeMoney = 50000; prizeStats.third++; }
          else { prizeStats.none++; }
        }

        totalWon += prizeMoney;
        runningPnl += (prizeMoney - ticketPrice);
        pnlPoints.push({
          drawId: draw.id || `#${idx+1}`,
          pnl: runningPnl
        });
      });

      const netProfit = totalWon - totalSpent;
      const roi = ((netProfit / totalSpent) * 100).toFixed(1);
      const isProfit = netProfit >= 0;

      const container = document.getElementById('simResultsContainer');
      container.innerHTML = `
        <div class="grid grid-cols-2 sm:grid-cols-4 gap-4">
          <div class="bg-slate-950 p-4 rounded-xl border border-slate-800">
            <div class="text-xs text-slate-400">Tổng Vốn Mua Vé</div>
            <div class="text-lg font-bold font-mono text-white mt-1">${totalSpent.toLocaleString()} đ</div>
            <div class="text-[11px] text-slate-500">${targetDraws.length} kỳ quay</div>
          </div>
          <div class="bg-slate-950 p-4 rounded-xl border border-slate-800">
            <div class="text-xs text-slate-400">Tổng Tiền Trúng</div>
            <div class="text-lg font-bold font-mono text-amber-400 mt-1">${totalWon.toLocaleString()} đ</div>
            <div class="text-[11px] text-slate-500">${prizeStats.first + prizeStats.second + prizeStats.third} lần trúng</div>
          </div>
          <div class="bg-slate-950 p-4 rounded-xl border border-slate-800">
            <div class="text-xs text-slate-400">Lợi Nhuận Ròng (P&L)</div>
            <div class="text-lg font-bold font-mono ${isProfit ? 'text-emerald-400' : 'text-rose-400'} mt-1">
              ${isProfit ? '+' : ''}${netProfit.toLocaleString()} đ
            </div>
            <div class="text-[11px] ${isProfit ? 'text-emerald-400' : 'text-rose-400'}">ROI: ${roi}%</div>
          </div>
          <div class="bg-slate-950 p-4 rounded-xl border border-slate-800">
            <div class="text-xs text-slate-400">Cơ Cấu Giải Trúng</div>
            <div class="text-xs text-slate-300 font-mono mt-1 space-y-0.5">
              <div>Ba: <strong>${prizeStats.third}</strong> | Nhì: <strong>${prizeStats.second}</strong></div>
              <div>Nhất: <strong>${prizeStats.first}</strong> | Jackpot: <strong>${prizeStats.jp1 + prizeStats.jp2}</strong></div>
            </div>
          </div>
        </div>

        <div class="bg-slate-950 p-4 rounded-xl border border-slate-800 space-y-3">
          <div class="text-xs font-semibold text-slate-300">ĐƯỜNG CONG TĂNG TRƯỞNG VỐN / LỖ (P&L CURVE)</div>
          <div class="h-64 w-full">
            <canvas id="simPnlChart"></canvas>
          </div>
        </div>
      `;

      // Render PNL Chart
      const ctx = document.getElementById('simPnlChart').getContext('2d');
      if (simPnlChartInstance) simPnlChartInstance.destroy();

      simPnlChartInstance = new Chart(ctx, {
        type: 'line',
        data: {
          labels: pnlPoints.map(p => p.drawId),
          datasets: [{
            label: 'Lợi nhuận ròng (VNĐ)',
            data: pnlPoints.map(p => p.pnl),
            borderColor: isProfit ? '#10b981' : '#f43f5e',
            backgroundColor: isProfit ? 'rgba(16, 185, 129, 0.1)' : 'rgba(244, 63, 94, 0.1)',
            fill: true,
            tension: 0.2,
            pointRadius: 1
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            x: { ticks: { color: '#64748b', maxTicksLimit: 12 }, grid: { display: false } },
            y: { ticks: { color: '#64748b' }, grid: { color: 'rgba(51, 65, 85, 0.3)' } }
          }
        }
      });
    }

    // --- 8. FULL HISTORY TABLE ---
    function renderHistoryTable() {
      const product = appData.products[currentProductKey];
      if (!product || !product.history) return;

      const filter = document.getElementById('historySearch').value.toLowerCase().trim();
      let records = product.history;

      if (filter) {
        records = records.filter(r => 
          (r.id && String(r.id).toLowerCase().includes(filter)) ||
          (r.date && r.date.includes(filter))
        );
      }

      const totalRecords = records.length;
      const totalPages = Math.ceil(totalRecords / pageSize) || 1;
      if (currentPage > totalPages) currentPage = totalPages;
      if (currentPage < 1) currentPage = 1;

      const startIdx = (currentPage - 1) * pageSize;
      const endIdx = Math.min(startIdx + pageSize, totalRecords);
      const pageRecords = records.slice(startIdx, endIdx);

      document.getElementById('paginationInfo').textContent = totalRecords 
        ? `Hiển thị ${startIdx + 1} - ${endIdx} trong tổng số ${totalRecords} kỳ`
        : `Không tìm thấy kỳ quay nào`;
      document.getElementById('pageNumberDisplay').textContent = `${currentPage} / ${totalPages}`;
      document.getElementById('btnPrevPage').disabled = (currentPage <= 1);
      document.getElementById('btnNextPage').disabled = (currentPage >= totalPages);

      const tbody = document.getElementById('historyTableBody');
      if (!pageRecords.length) {
        tbody.innerHTML = `<tr><td colspan="4" class="py-8 text-center text-slate-500">Không có dữ liệu phù hợp</td></tr>`;
        return;
      }

      tbody.innerHTML = pageRecords.map(row => {
        let resultHtml = '';
        const res = row.result;

        if (product.type === 'lotto' && Array.isArray(res)) {
          const mainCount = product.balls || 6;
          const mainBalls = res.slice(0, mainCount);
          const spec = (product.has_special && res.length > mainCount) ? res[mainCount] : null;

          resultHtml = `
            <div class="flex items-center space-x-1.5">
              ${mainBalls.map(n => `
                <span class="w-7 h-7 rounded-full bg-rose-600/90 text-white font-mono text-xs font-bold flex items-center justify-center shadow-sm">
                  ${String(n).padStart(2, '0')}
                </span>
              `).join('')}
              ${spec !== null ? `
                <span class="text-slate-600 px-0.5">+</span>
                <span class="w-7 h-7 rounded-full bg-amber-500 text-white font-mono text-xs font-bold flex items-center justify-center border border-amber-300 shadow-sm" title="Jackpot 2">
                  ${String(spec).padStart(2, '0')}
                </span>
              ` : ''}
            </div>
          `;
        } else if (product.type === 'keno' && Array.isArray(res)) {
          resultHtml = `
            <div class="flex flex-wrap gap-1 max-w-xl">
              ${res.map(n => `<span class="px-1.5 py-0.5 rounded bg-slate-800 text-slate-200 text-xs font-mono">${n}</span>`).join('')}
            </div>
          `;
        } else if (product.type === 'bingo18' && Array.isArray(res)) {
          resultHtml = `
            <div class="flex items-center space-x-2">
              <span class="font-mono text-purple-400 font-bold text-sm">[${res.join(' - ')}]</span>
              <span class="text-xs text-slate-400">Tổng: ${row.total || ''} (${row.large_small || ''})</span>
            </div>
          `;
        } else if (product.type === '3d' && typeof res === 'object') {
          const specialPrize = (res && res['Giải Đặc biệt']) ? res['Giải Đặc biệt'].join(' - ') : JSON.stringify(res);
          resultHtml = `<span class="font-mono text-xs text-amber-300">Đặc biệt: <strong>${specialPrize}</strong></span>`;
        }

        return `
          <tr class="hover:bg-slate-800/40 transition">
            <td class="py-3 px-4 font-mono text-xs text-slate-300">${row.date || ''}</td>
            <td class="py-3 px-4 font-mono text-xs text-amber-400 font-semibold">#${row.id || ''}</td>
            <td class="py-3 px-4">${resultHtml}</td>
            <td class="py-3 px-4 text-right">
              <button onclick="inspectDraw('${row.id}')" class="text-xs text-indigo-400 hover:text-indigo-300 font-medium hover:underline">
                Xem kỳ này
              </button>
            </td>
          </tr>
        `;
      }).join('');
    }

    function inspectDraw(drawId) {
      const product = appData.products[currentProductKey];
      if (!product || !product.history) return;
      const foundIdx = product.history.findIndex(r => String(r.id) === String(drawId));
      if (foundIdx !== -1) {
        document.getElementById('compareDrawSelect').value = foundIdx;
        switchView('overview');
        window.scrollTo({ top: 0, behavior: 'smooth' });
        checkTicket();
      }
    }

    // =========================================================================
    // BINGO 18 SICBO QUANTITATIVE ANALYTICS DASHBOARD
    // =========================================================================
    function renderBingo18Dashboard(product) {
      const container = document.getElementById('bingo18Dashboard');
      if (!container) return;

      if (!product || product.type !== 'bingo18') {
        container.classList.add('hidden');
        return;
      }

      container.classList.remove('hidden');

      const sa = product.streak_analytics || {};
      const sd = product.sum_distribution || {};
      const sr = product.storm_radar || {};
      const df = product.dice_frequencies || {};

      const roadmap = sa.roadmap || [];
      const currentStreakType = sa.current_streak_type || 'Chưa có';
      const currentStreakLen = sa.current_streak_len || 0;
      const breakProb = sa.break_probability_pct || 50.0;
      const totalLarge = sa.total_large || 0;
      const totalSmall = sa.total_small || 0;
      const totalAnalyzed = sa.total_draws_analyzed || roadmap.length || 1;
      const largePct = Math.round((totalLarge / totalAnalyzed) * 100);
      const smallPct = Math.round((totalSmall / totalAnalyzed) * 100);

      const hazard = sr.hazard_level || { name: 'Bình Thường', color: 'slate', alert: false, badge: 'bg-slate-800 text-slate-300' };
      const currentStormGap = sr.current_storm_gap || 0;
      const avgStormGap = sr.average_storm_gap || 36.0;
      const tripleCounts = sr.triple_counts || {};

      const sumList = sd.distribution || [];
      const topHotSums = sd.top_hot_sums || [];
      const meanSum = sd.mean_sum || 10.5;

      const diceList = df.dice_frequencies || [];
      const topPairs = df.top_pairs || [];

      const pred = product.prediction_hub || {};
      const lsPred = pred.large_small_prediction || {};
      const sfPred = pred.single_face_prediction || {};
      const tsPred = pred.target_sum_prediction || {};
      const stPred = pred.storm_trigger || {};
      const targetDrawId = pred.target_draw_id || '#KỳKếTiếp';

      container.innerHTML = `
        <!-- BINGO 18 HEADER BANNER -->
        <div class="rounded-2xl bg-gradient-to-r from-rose-950/40 via-slate-900 to-amber-950/30 border border-rose-500/30 p-5 shadow-2xl flex flex-col md:flex-row items-center justify-between gap-4">
          <div class="flex items-center gap-3.5">
            <div class="w-12 h-12 rounded-2xl bg-gradient-to-tr from-rose-600 to-amber-500 flex items-center justify-center text-white shadow-lg shadow-rose-900/40 flex-shrink-0">
              <i data-lucide="dice-5" class="w-6 h-6"></i>
            </div>
            <div>
              <div class="flex items-center gap-2 flex-wrap">
                <span class="px-2.5 py-0.5 rounded-full text-xs font-bold bg-rose-500/20 text-rose-300 border border-rose-500/40 flex items-center gap-1.5">
                  <span class="w-2 h-2 rounded-full bg-rose-400 animate-ping"></span>
                  SICBO ĐỊNH LƯỢNG
                </span>
                <span class="text-xs font-mono text-slate-400">Quay 10 phút/kỳ (96 kỳ/ngày)</span>
              </div>
              <h3 class="text-lg font-bold text-white mt-1">SOI CẦU XÚC XẮC BINGO 18 & RADAR SĂN BÃO</h3>
            </div>
          </div>
          <div class="flex items-center gap-2 bg-slate-950/70 p-2.5 rounded-xl border border-slate-800">
            <span class="text-xs text-slate-400">Dữ liệu cào tự động:</span>
            <span class="text-xs font-bold font-mono text-amber-400">${(product.total_draws || 0).toLocaleString()} kỳ</span>
          </div>
        </div>

        <!-- BẢNG GỢI Ý DỰ ĐOÁN BINGO 18 KỲ KẾ TIẾP (SICBO QUANT PREDICTOR) -->
        <div class="rounded-2xl bg-gradient-to-br from-slate-900 via-slate-900/90 to-indigo-950/40 border border-indigo-500/40 p-6 shadow-2xl space-y-5">
          <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-800 pb-4">
            <div>
              <div class="flex items-center gap-2 flex-wrap">
                <span class="px-2.5 py-0.5 rounded-full text-xs font-bold bg-indigo-500/20 text-indigo-300 border border-indigo-500/40 flex items-center gap-1.5">
                  <i data-lucide="sparkles" class="w-3.5 h-3.5 text-amber-400"></i>
                  GỢI Ý DỰ ĐOÁN ĐỊNH LƯỢNG
                </span>
                <span class="text-xs font-mono font-bold text-amber-400 bg-slate-950 px-2.5 py-0.5 rounded-full border border-slate-800">
                  Kỳ kế tiếp: ${targetDrawId}
                </span>
              </div>
              <h4 class="text-base font-bold text-white mt-1.5">CHIẾN LƯỢC TOÁN HỌC TỐI ƯU KỲ QUAY TIẾP THEO</h4>
            </div>
            <span class="text-[11px] font-mono text-slate-400 bg-slate-950/80 px-3 py-1.5 rounded-xl border border-slate-800">
              Cập nhật trực tiếp 10 phút/kỳ
            </span>
          </div>

          <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <!-- THẺ 1: THẾ CẦU LỚN/NHỎ -->
            <div class="bg-slate-950/80 p-4 rounded-xl border border-slate-800 hover:border-indigo-500/50 transition flex flex-col justify-between space-y-3">
              <div>
                <div class="flex items-center justify-between">
                  <span class="text-[11px] font-mono uppercase text-slate-400 font-bold">1. Thế Cầu Lớn/Nhỏ</span>
                  <span class="text-[10px] font-mono text-slate-500">1 ăn 2 (50%)</span>
                </div>
                <div class="mt-2 flex items-baseline gap-2">
                  <span class="text-3xl font-black font-mono ${lsPred.predicted_choice === 'Lớn' ? 'text-rose-400' : 'text-sky-400'}">
                    ${lsPred.predicted_choice || 'Chờ nhịp'}
                  </span>
                  <span class="text-xs font-bold font-mono px-2 py-0.5 rounded ${lsPred.predicted_choice === 'Lớn' ? 'bg-rose-500/20 text-rose-300' : 'bg-sky-500/20 text-sky-300'}">
                    ${lsPred.confidence_pct || 50}%
                  </span>
                </div>
                <span class="text-[10px] px-2 py-0.5 rounded font-mono font-semibold bg-slate-800 text-amber-300 mt-1.5 inline-block">
                  ${lsPred.strategy_name || 'Bám cầu'}
                </span>
              </div>
              <p class="text-[11px] text-slate-400 font-sans leading-relaxed border-t border-slate-800/80 pt-2">
                ${lsPred.rationale || 'Đang nhận diện nhịp bệt và hồi quy.'}
              </p>
            </div>

            <!-- THẺ 2: BẠCH THỦ MẶT XÚC XẮC -->
            <div class="bg-slate-950/80 p-4 rounded-xl border border-slate-800 hover:border-amber-500/50 transition flex flex-col justify-between space-y-3">
              <div>
                <div class="flex items-center justify-between">
                  <span class="text-[11px] font-mono uppercase text-slate-400 font-bold">2. Bạch Thủ Mặt Xúc Xắc</span>
                  <span class="text-[10px] font-mono text-emerald-400 font-bold">+EV 42%</span>
                </div>
                <div class="mt-2 flex items-center gap-3">
                  ${renderDiceSVG(sfPred.best_face || 6, 46)}
                  <div>
                    <span class="text-xl font-black font-mono text-amber-400">Mặt ${sfPred.best_face || 6}</span>
                    <span class="text-[11px] block font-mono text-slate-400">Xác suất: ${sfPred.expected_hit_prob_pct || 42}%</span>
                  </div>
                </div>
              </div>
              <p class="text-[11px] text-slate-400 font-sans leading-relaxed border-t border-slate-800/80 pt-2">
                ${sfPred.rationale || 'Mặt xúc xắc có nhịp nổ thuận lợi nhất.'}
              </p>
            </div>

            <!-- THẺ 3: KHOẢNG TỔNG MỤC TIÊU GAUSSIAN -->
            <div class="bg-slate-950/80 p-4 rounded-xl border border-slate-800 hover:border-emerald-500/50 transition flex flex-col justify-between space-y-3">
              <div>
                <div class="flex items-center justify-between">
                  <span class="text-[11px] font-mono uppercase text-slate-400 font-bold">3. Tổng Mục Tiêu Gaussian</span>
                  <span class="text-[10px] font-mono text-slate-500">68% xác suất</span>
                </div>
                <div class="mt-2">
                  <span class="text-xl font-black font-mono text-emerald-400">Vùng [8 - 13]</span>
                  <div class="text-xs font-mono text-slate-300 mt-1">
                    Tổng rơi tối ưu: <span class="font-black text-amber-400 text-sm">Tổng ${tsPred.best_single_sum || 10}</span>
                  </div>
                </div>
              </div>
              <p class="text-[11px] text-slate-400 font-sans leading-relaxed border-t border-slate-800/80 pt-2">
                ${tsPred.rationale || 'Tổng nằm trong chuông phân phối chuẩn đối xứng 3d6.'}
              </p>
            </div>

            <!-- THẺ 4: RADAR SĂN BÃO X120 -->
            <div class="bg-slate-950/80 p-4 rounded-xl border border-slate-800 hover:border-rose-500/50 transition flex flex-col justify-between space-y-3">
              <div>
                <div class="flex items-center justify-between">
                  <span class="text-[11px] font-mono uppercase text-slate-400 font-bold">4. Radar Săn Bão Độc Đắc</span>
                  <span class="text-[10px] font-mono text-amber-300 font-bold">1 ăn 32 / 120</span>
                </div>
                <div class="mt-2">
                  <div class="flex items-center gap-1.5">
                    ${stPred.is_hunting_active ? '<span class="w-2.5 h-2.5 rounded-full bg-rose-500 animate-ping"></span>' : ''}
                    <span class="text-sm font-bold font-mono ${stPred.is_hunting_active ? 'text-rose-400' : 'text-slate-300'}">
                      ${stPred.status || 'Bình thường'}
                    </span>
                  </div>
                  <span class="text-[11px] text-slate-400 font-mono block mt-1">
                    Vắng bóng: <span class="text-amber-400 font-bold">${stPred.current_storm_gap || 0} kỳ</span> (chu kỳ ${stPred.average_gap || 35} kỳ)
                  </span>
                </div>
              </div>
              <p class="text-[11px] text-slate-400 font-sans leading-relaxed border-t border-slate-800/80 pt-2">
                ${stPred.rationale || 'Theo dõi chu kỳ nhịp nổ bão lý thuyết.'}
              </p>
            </div>
          </div>
        </div>

        <!-- 2 CỘT CHÍNH: CẦU LỚN/NHỎ & RADAR SĂN BÃO -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
          
          <!-- THẺ 1: BẢN ĐỒ BẮT CẦU LỚN / NHỎ (SICBO ROADMAP) -->
          <div class="rounded-2xl bg-slate-900 border border-slate-800 p-6 shadow-xl space-y-4">
            <div class="flex items-center justify-between border-b border-slate-800 pb-3">
              <div class="flex items-center gap-2">
                <i data-lucide="activity" class="w-5 h-5 text-rose-400"></i>
                <h4 class="font-bold text-white text-sm">BẢN ĐỒ BẮT CẦU LỚN / NHỎ (100 KỲ GẦN NHẤT)</h4>
              </div>
              <span class="text-xs font-mono text-slate-400">Xác suất 50/50 (1 ăn 2)</span>
            </div>

            <!-- Trạng thái nhịp bệt hiện tại -->
            <div class="grid grid-cols-2 sm:grid-cols-3 gap-3">
              <div class="bg-slate-950/80 p-3 rounded-xl border border-slate-800">
                <span class="text-[10px] text-slate-400 block uppercase font-mono">Nhịp bệt hiện tại</span>
                <span class="text-lg font-black font-mono ${currentStreakType === 'Lớn' ? 'text-rose-400' : 'text-sky-400'}">
                  ${currentStreakType} &times; ${currentStreakLen} kỳ
                </span>
              </div>
              <div class="bg-slate-950/80 p-3 rounded-xl border border-slate-800">
                <span class="text-[10px] text-slate-400 block uppercase font-mono">Xác suất bẻ cầu</span>
                <span class="text-lg font-black font-mono text-amber-400">${breakProb}%</span>
              </div>
              <div class="bg-slate-950/80 p-3 rounded-xl border border-slate-800 col-span-2 sm:col-span-1">
                <span class="text-[10px] text-slate-400 block uppercase font-mono">Tỷ lệ 100 kỳ</span>
                <span class="text-xs font-mono text-slate-300">
                  <span class="text-rose-400 font-bold">Lớn ${largePct}%</span> / <span class="text-sky-400 font-bold">Nhỏ ${smallPct}%</span>
                </span>
              </div>
            </div>

            <!-- Ma trận chấm tròn Roadmap (100 kỳ gần nhất) -->
            <div>
              <div class="text-[11px] text-slate-400 mb-2 flex items-center justify-between">
                <span>Ma trận nhịp (Trái sang phải, cũ đến mới):</span>
                <div class="flex items-center gap-3 text-[10px] font-mono">
                  <span class="flex items-center gap-1"><span class="w-2.5 h-2.5 rounded-full bg-rose-500 inline-block"></span> Lớn (11-18)</span>
                  <span class="flex items-center gap-1"><span class="w-2.5 h-2.5 rounded-full bg-sky-500 inline-block"></span> Nhỏ (3-10)</span>
                  <span class="flex items-center gap-1"><span class="w-2.5 h-2.5 rounded-full bg-amber-400 border border-amber-200 inline-block animate-pulse"></span> Bão</span>
                </div>
              </div>
              <div class="p-3 bg-slate-950/90 rounded-xl border border-slate-800 max-h-48 overflow-y-auto">
                <div class="flex flex-wrap gap-1.5 items-center">
                  ${roadmap.map((r, idx) => {
                    const isBao = r.isTriple;
                    const colorCls = isBao ? 'bg-amber-400 text-slate-950 border border-amber-200 shadow-md shadow-amber-500/30' : (r.type === 'Lớn' ? 'bg-rose-500 text-white' : 'bg-sky-500 text-white');
                    const char = isBao ? 'B' : (r.type === 'Lớn' ? 'L' : 'N');
                    return `
                      <div class="w-6 h-6 rounded-full flex items-center justify-center text-[10px] font-bold font-mono flex-shrink-0 cursor-pointer ${colorCls}" title="Kỳ #${r.drawId} (${r.date}): [${r.result.join(', ')}] = ${r.total} (${r.type})${isBao ? ' - BÃO' : ''}">
                        ${char}
                      </div>
                    `;
                  }).join('')}
                </div>
              </div>
            </div>
          </div>

          <!-- THẺ 2: RADAR CẢNH BÁO SĂN BÃO (TRIPLE / STORM RADAR) -->
          <div class="rounded-2xl bg-slate-900 border border-slate-800 p-6 shadow-xl space-y-4">
            <div class="flex items-center justify-between border-b border-slate-800 pb-3">
              <div class="flex items-center gap-2">
                <i data-lucide="zap" class="w-5 h-5 text-amber-400"></i>
                <h4 class="font-bold text-white text-sm">RADAR CẢNH BÁO SĂN BÃO (1 ĂN 32 & 1 ĂN 120)</h4>
              </div>
              <span class="text-xs font-mono text-amber-300 font-bold">Chu kỳ ~36 kỳ</span>
            </div>

            <!-- Đồng hồ đo nhịp bão -->
            <div class="bg-slate-950/80 p-4 rounded-xl border border-slate-800 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
              <div>
                <span class="text-xs text-slate-400 block font-sans">Số kỳ chưa nổ bão:</span>
                <div class="flex items-baseline gap-2 mt-1">
                  <span class="text-3xl font-black font-mono text-amber-400">${currentStormGap}</span>
                  <span class="text-xs font-mono text-slate-400">/ trung bình ${avgStormGap} kỳ</span>
                </div>
              </div>
              <div class="flex flex-col sm:items-end gap-1.5">
                <span class="px-3 py-1 rounded-lg text-xs font-bold font-mono inline-flex items-center gap-1.5 ${hazard.badge || 'bg-slate-800 text-slate-300'}">
                  ${hazard.alert ? '<span class="w-2 h-2 rounded-full bg-rose-400 animate-ping"></span>' : ''}
                  ${hazard.name}
                </span>
                <span class="text-[11px] text-slate-400 text-left sm:text-right max-w-xs">${hazard.rationale || ''}</span>
              </div>
            </div>

            <!-- Bảng đếm lịch sử 6 loại bão cụ thể (111..666) -->
            <div>
              <span class="text-[11px] text-slate-400 block uppercase font-mono mb-2">Lịch sử nổ 6 loại bão cụ thể (Toàn bộ dữ liệu):</span>
              <div class="grid grid-cols-3 sm:grid-cols-6 gap-2">
                ${[1, 2, 3, 4, 5, 6].map(face => {
                  const key = `${face}${face}${face}`;
                  const cnt = tripleCounts[key] || 0;
                  return `
                    <div class="p-2.5 rounded-xl bg-slate-950/90 border border-slate-800 text-center hover:border-amber-500/40 transition">
                      <div class="flex justify-center mb-1.5">
                        ${renderDiceSVG(face, 32)}
                      </div>
                      <span class="text-xs font-black font-mono text-white block">${key}</span>
                      <span class="text-[10px] font-mono text-amber-400">${cnt} lần</span>
                    </div>
                  `;
                }).join('')}
              </div>
            </div>
          </div>
        </div>

        <!-- THẺ 3 & THẺ 4: CHUÔNG TỔNG GAUSSIAN & TẦN SUẤT 6 MẶT -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
          
          <!-- THẺ 3: PHÂN PHỐI CHUÔNG TỔNG 3..18 -->
          <div class="rounded-2xl bg-slate-900 border border-slate-800 p-6 shadow-xl space-y-4">
            <div class="flex items-center justify-between border-b border-slate-800 pb-3">
              <div class="flex items-center gap-2">
                <i data-lucide="bell" class="w-5 h-5 text-indigo-400"></i>
                <h4 class="font-bold text-white text-sm">PHÂN PHỐI CHUÔNG TỔNG GAUSSIAN 3..18 (3D6)</h4>
              </div>
              <span class="text-xs font-mono text-emerald-400 font-bold">Tâm đối xứng: 10 & 11</span>
            </div>

            <div class="flex items-center justify-between text-xs text-slate-400 bg-slate-950/60 p-3 rounded-xl border border-slate-800">
              <div>Tổng trung bình: <span class="font-bold font-mono text-white">${meanSum}</span> (Lý thuyết: 10.5)</div>
              <div>Top 3 tổng nổ nhiều nhất: <span class="font-bold font-mono text-amber-400">${topHotSums.join(', ')}</span></div>
            </div>

            <!-- Bảng phân bố thanh tiến trình -->
            <div class="space-y-2 max-h-56 overflow-y-auto pr-1">
              ${sumList.map(s => {
                const isHot = topHotSums.includes(s.sum);
                const isCenter = (s.sum === 10 || s.sum === 11);
                return `
                  <div class="flex items-center gap-3 text-xs font-mono p-1.5 rounded-lg hover:bg-slate-800/40">
                    <span class="w-8 font-bold text-center ${isCenter ? 'text-amber-400' : 'text-slate-300'}">Tổng ${s.sum}</span>
                    <div class="flex-1 bg-slate-950 h-3 rounded-full overflow-hidden flex items-center">
                      <div class="h-full rounded-full ${isHot ? 'bg-gradient-to-r from-amber-500 to-rose-500' : 'bg-indigo-600'}" style="width: ${Math.min(100, s.empirical_pct * 7)}%"></div>
                    </div>
                    <span class="w-12 text-right text-slate-300">${s.empirical_pct}%</span>
                    <span class="w-14 text-right text-[10px] text-slate-500">(LT: ${s.theoretical_pct}%)</span>
                  </div>
                `;
              }).join('')}
            </div>
          </div>

          <!-- THẺ 4: TẦN SUẤT 6 MẶT XÚC XẮC & CẶP ĐÔI HAY NỔ CHUNG -->
          <div class="rounded-2xl bg-slate-900 border border-slate-800 p-6 shadow-xl space-y-4">
            <div class="flex items-center justify-between border-b border-slate-800 pb-3">
              <div class="flex items-center gap-2">
                <i data-lucide="layers" class="w-5 h-5 text-emerald-400"></i>
                <h4 class="font-bold text-white text-sm">TẦN SUẤT 6 MẶT XÚC XẮC & CẶP ĐÔI NỔ CHUNG</h4>
              </div>
              <span class="text-xs font-mono text-slate-400">Mẫu 500 kỳ gần nhất</span>
            </div>

            <!-- 6 thẻ mặt xúc xắc -->
            <div class="grid grid-cols-2 sm:grid-cols-3 gap-2.5">
              ${diceList.map(d => {
                const isHot = (d.status === 'Nóng');
                const isCold = (d.status === 'Lạnh');
                const statusCls = isHot ? 'text-rose-400 border-rose-500/40 bg-rose-500/10' : (isCold ? 'text-sky-400 border-sky-500/40 bg-sky-500/10' : 'text-slate-400 border-slate-800 bg-slate-950');
                return `
                  <div class="p-2.5 rounded-xl border flex items-center gap-3 ${statusCls}">
                    ${renderDiceSVG(d.face, 40)}
                    <div class="flex flex-col">
                      <div class="flex items-center gap-1.5">
                        <span class="text-xs font-bold text-white font-mono">Mặt ${d.face}</span>
                        <span class="text-[9px] px-1 rounded font-bold ${statusCls}">${d.status}</span>
                      </div>
                      <span class="text-xs font-mono text-amber-400 font-bold mt-0.5">${d.empirical_pct}%</span>
                      <span class="text-[10px] text-slate-400 font-mono">Vắng ${d.current_gap} kỳ</span>
                    </div>
                  </div>
                `;
              }).join('')}
            </div>

            <!-- Top cặp đôi hay nổ chung -->
            <div class="pt-2 border-t border-slate-800">
              <span class="text-[11px] text-slate-400 block uppercase font-mono mb-2">Top cặp xúc xắc hay đi cùng nhau:</span>
              <div class="flex flex-wrap gap-2">
                ${topPairs.map(p => `
                  <div class="px-3 py-1.5 rounded-xl bg-slate-950 border border-slate-800 flex items-center gap-2">
                    <div class="flex items-center gap-1">
                      ${renderDiceSVG(p.pair[0], 20)}
                      <span class="text-xs font-bold text-slate-500">+</span>
                      ${renderDiceSVG(p.pair[1], 20)}
                    </div>
                    <span class="text-xs font-bold font-mono text-emerald-400">${p.count} lần</span>
                  </div>
                `).join('')}
              </div>
            </div>
          </div>
        </div>
      `;

      if (window.lucide) {
        lucide.createIcons();
      }
    }
