// ==========================================
// 3. ADVANCED QUANT: Positional, AC/Delta, Markov, +EV, Wheeling, Bac Nho
// ==========================================

    // --- 8. POSITIONAL & SPAN DYNAMICS ---
    let spanChartInstance = null;
    function renderPositionalView(product) {
      const pos = product.positional_stats;
      const container = document.getElementById('positionalBallsList');
      const kpiBadge = document.getElementById('spanKpiBadge');
      if (!pos || !pos.positions || pos.positions.length === 0) {
        if (container) container.innerHTML = `<p class="text-xs text-slate-500 col-span-full">Chưa có dữ liệu phân bố vị trí cho loại hình này.</p>`;
        return;
      }

      container.innerHTML = pos.positions.map(p => {
        const maxVal = product.max_number || 55;
        const pctQ1 = Math.round((p.q1 / maxVal) * 100);
        const pctQ3 = Math.round((p.q3 / maxVal) * 100);
        const widthSafe = Math.max(10, pctQ3 - pctQ1);
        return `
          <div class="bg-slate-950 p-4 rounded-xl border border-slate-800 space-y-3">
            <div class="flex items-center justify-between">
              <span class="px-2.5 py-1 rounded-lg bg-blue-500/20 text-blue-300 font-bold text-xs border border-blue-500/30">
                Bóng Số ${p.ball_index}
              </span>
              <span class="text-xs font-mono text-emerald-400 font-bold bg-emerald-950/60 px-2 py-0.5 rounded border border-emerald-800/40">
                Dải an toàn: ${p.safe_range}
              </span>
            </div>
            <div class="grid grid-cols-4 gap-2 text-center text-xs font-mono pt-1">
              <div class="bg-slate-900/80 p-2 rounded-lg border border-slate-800">
                <span class="text-[10px] text-slate-500 block">Min</span>
                <span class="text-slate-300 font-bold">${p.min}</span>
              </div>
              <div class="bg-slate-900/80 p-2 rounded-lg border border-slate-800">
                <span class="text-[10px] text-slate-500 block">Q1 (25%)</span>
                <span class="text-blue-300 font-bold">${p.q1}</span>
              </div>
              <div class="bg-slate-900/80 p-2 rounded-lg border border-slate-800">
                <span class="text-[10px] text-slate-500 block">Trung vị</span>
                <span class="text-amber-300 font-bold">${p.median}</span>
              </div>
              <div class="bg-slate-900/80 p-2 rounded-lg border border-slate-800">
                <span class="text-[10px] text-slate-500 block">Q3 (75%)</span>
                <span class="text-blue-300 font-bold">${p.q3}</span>
              </div>
            </div>
            <div class="space-y-1">
              <div class="flex justify-between text-[10px] text-slate-500 font-mono">
                <span>01</span>
                <span>Max: ${p.max}</span>
              </div>
              <div class="w-full bg-slate-900 h-2.5 rounded-full relative overflow-hidden">
                <div class="absolute bg-gradient-to-r from-blue-500 to-cyan-400 h-2.5 rounded-full" style="left: ${pctQ1}%; width: ${widthSafe}%"></div>
              </div>
            </div>
          </div>
        `;
      }).join('');

      if (pos.span_stats && kpiBadge) {
        const s = pos.span_stats;
        kpiBadge.innerHTML = `
          <span class="bg-slate-950 px-2.5 py-1 rounded-lg border border-slate-800 text-slate-300">Min: <strong class="text-white">${s.min}</strong></span>
          <span class="bg-slate-950 px-2.5 py-1 rounded-lg border border-slate-800 text-slate-300">Trung vị: <strong class="text-amber-400">${s.median}</strong></span>
          <span class="bg-slate-950 px-2.5 py-1 rounded-lg border border-slate-800 text-slate-300">Max: <strong class="text-white">${s.max}</strong></span>
        `;
        renderSpanChart();
        renderSpanTrendChart();
      }
    }

    function renderSpanChart() {
      const product = appData?.products?.[currentProductKey];
      const spanStats = product?.positional_stats?.span_stats;
      if (!spanStats || !spanStats.distribution) return;
      const canvas = document.getElementById('spanChart');
      if (!canvas) return;

      if (spanChartInstance) spanChartInstance.destroy();

      const labels = spanStats.distribution.map(d => d.range);
      const dataValues = spanStats.distribution.map(d => d.count);

      spanChartInstance = new Chart(canvas.getContext('2d'), {
        type: 'bar',
        data: {
          labels: labels,
          datasets: [{
            label: 'Số kỳ quay',
            data: dataValues,
            backgroundColor: 'rgba(6, 182, 212, 0.75)',
            borderColor: 'rgb(6, 182, 212)',
            borderWidth: 1.5,
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
                afterLabel: (ctx) => `Tỷ lệ: ${spanStats.distribution[ctx.dataIndex].pct}%`
              }
            }
          },
          scales: {
            x: { grid: { color: 'rgba(51, 65, 85, 0.3)' }, ticks: { color: '#94a3b8', font: { size: 11 } } },
            y: { grid: { color: 'rgba(51, 65, 85, 0.3)' }, ticks: { color: '#94a3b8', font: { size: 11 } } }
          }
        }
      });
    }

    let spanTrendChartInstance = null;
    function renderSpanTrendChart() {
      const product = appData?.products?.[currentProductKey];
      if (!product || !product.history || !product.history.length) return;
      const canvas = document.getElementById('spanTrendChart');
      if (!canvas) return;

      const numBalls = product.balls || 6;
      const rawRecords = product.history.slice(0, 30).reverse();
      if (!rawRecords.length) return;

      const labels = [];
      const spanValues = [];

      rawRecords.forEach(r => {
        labels.push(`#${r.id}`);
        const res = (r.result || []).slice(0, numBalls).sort((a, b) => a - b);
        if (res.length === numBalls) {
          spanValues.push(res[res.length - 1] - res[0]);
        } else {
          spanValues.push(0);
        }
      });

      const avgSpan = product.positional_stats?.span_stats?.avg || 40;
      const avgLine = Array(spanValues.length).fill(avgSpan);

      if (spanTrendChartInstance) spanTrendChartInstance.destroy();

      const ctx = canvas.getContext('2d');
      const gradient = ctx.createLinearGradient(0, 0, 0, 250);
      gradient.addColorStop(0, 'rgba(6, 182, 212, 0.35)');
      gradient.addColorStop(1, 'rgba(6, 182, 212, 0.0)');

      spanTrendChartInstance = new Chart(ctx, {
        type: 'line',
        data: {
          labels: labels,
          datasets: [
            {
              label: 'Biên độ (Span)',
              data: spanValues,
              borderColor: 'rgb(6, 182, 212)',
              backgroundColor: gradient,
              borderWidth: 2,
              fill: true,
              tension: 0.25,
              pointRadius: 3,
              pointBackgroundColor: 'rgb(6, 182, 212)'
            },
            {
              label: 'Biên độ trung bình',
              data: avgLine,
              borderColor: 'rgba(245, 158, 11, 0.7)',
              borderWidth: 1.5,
              borderDash: [4, 4],
              fill: false,
              pointRadius: 0
            }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          interaction: { mode: 'index', intersect: false },
          plugins: {
            legend: { display: false },
            tooltip: {
              callbacks: {
                label: (ctx) => ` ${ctx.dataset.label}: ${ctx.raw}`
              }
            }
          },
          scales: {
            x: { grid: { color: 'rgba(51, 65, 85, 0.2)' }, ticks: { color: '#94a3b8', font: { size: 10 }, maxTicksLimit: 8 } },
            y: { grid: { color: 'rgba(51, 65, 85, 0.25)' }, ticks: { color: '#94a3b8', font: { size: 10 } } }
          }
        }
      });
    }

    // --- 9. ARITHMETIC COMPLEXITY & DELTA SYSTEM ---
    let acChartInstance = null;
    function renderAcDeltaView(product) {
      const acData = product.ac_stats;
      const deltaData = product.delta_stats;

      if (acData && acData.distribution) {
        const badge = document.getElementById('highAcBadge');
        if (badge) badge.textContent = `>${acData.high_ac_pct}% kỳ quay AC ≥ 7 (TB: ${acData.avg_ac || 8.1})`;
        renderAcChart();
      }

      const deltaContainer = document.getElementById('deltaStatsContainer');
      if (deltaData && deltaData.top_deltas && deltaContainer) {
        deltaContainer.innerHTML = `
          <div class="bg-slate-950 p-4 rounded-xl border border-slate-800 space-y-3">
            <div class="flex items-center justify-between text-xs">
              <span class="text-slate-400">Tỷ lệ bước nhảy nhỏ (1 - 5):</span>
              <span class="font-bold text-amber-400 font-mono">${deltaData.small_delta_pct}%</span>
            </div>
            <div class="w-full bg-slate-900 rounded-full h-2 overflow-hidden">
              <div class="bg-amber-500 h-2 rounded-full" style="width: ${deltaData.small_delta_pct}%"></div>
            </div>
            <div class="grid grid-cols-4 gap-2 pt-2">
              ${deltaData.top_deltas.slice(0, 4).map(d => `
                <div class="bg-slate-900 p-2.5 rounded-lg border border-slate-800 text-center font-mono">
                  <div class="text-xs text-slate-500">Δ = ${d.delta}</div>
                  <div class="text-sm font-bold text-white mt-0.5">${d.count}</div>
                  <div class="text-[10px] text-amber-400">${d.pct}%</div>
                </div>
              `).join('')}
            </div>
          </div>
        `;
      }
    }

    function renderAcChart() {
      const product = appData?.products?.[currentProductKey];
      const acData = product?.ac_stats;
      if (!acData || !acData.distribution) return;
      const canvas = document.getElementById('acChart');
      if (!canvas) return;

      if (acChartInstance) acChartInstance.destroy();

      const labels = acData.distribution.map(d => `AC = ${d.ac}`);
      const dataValues = acData.distribution.map(d => d.count);
      const bgColors = acData.distribution.map(d => d.ac >= 7 ? 'rgba(249, 115, 22, 0.85)' : 'rgba(148, 163, 184, 0.35)');

      acChartInstance = new Chart(canvas.getContext('2d'), {
        type: 'bar',
        data: {
          labels: labels,
          datasets: [{
            data: dataValues,
            backgroundColor: bgColors,
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
                afterLabel: (ctx) => `Tỷ lệ: ${acData.distribution[ctx.dataIndex].pct}%`
              }
            }
          },
          scales: {
            x: { grid: { color: 'rgba(51, 65, 85, 0.3)' }, ticks: { color: '#94a3b8', font: { size: 11 } } },
            y: { grid: { color: 'rgba(51, 65, 85, 0.3)' }, ticks: { color: '#94a3b8', font: { size: 11 } } }
          }
        }
      });
    }

    function checkAcValidator() {
      const input = document.getElementById('acValidatorInput').value.trim();
      const resContainer = document.getElementById('acValidatorResult');
      if (!input || !resContainer) return;

      const nums = input.split(/[\s,]+/).map(x => parseInt(x)).filter(x => !isNaN(x) && x > 0);
      if (nums.length !== 6) {
        resContainer.classList.remove('hidden');
        resContainer.className = 'p-3 rounded-lg border border-rose-800 bg-rose-950/60 text-xs font-mono text-rose-300';
        resContainer.innerHTML = '⚠️ Vui lòng nhập đúng 6 số phân biệt từ 1 đến 55.';
        return;
      }

      const sortedNums = Array.from(new Set(nums)).sort((a,b) => a - b);
      if (sortedNums.length !== 6) {
        resContainer.classList.remove('hidden');
        resContainer.className = 'p-3 rounded-lg border border-rose-800 bg-rose-950/60 text-xs font-mono text-rose-300';
        resContainer.innerHTML = '⚠️ Dãy số có số bị trùng lặp, vui lòng kiểm tra lại.';
        return;
      }

      const diffs = new Set();
      for (let i = 0; i < sortedNums.length; i++) {
        for (let j = i + 1; j < sortedNums.length; j++) {
          diffs.add(Math.abs(sortedNums[i] - sortedNums[j]));
        }
      }
      const ac = diffs.size - (sortedNums.length - 1);

      let quality = '';
      let colorClass = '';
      if (ac >= 7) {
        quality = '✅ Đạt chuẩn ngẫu nhiên thực tế (Xuất sắc - Trên 85% vé trúng lịch sử có điểm AC này)';
        colorClass = 'border-emerald-800 bg-emerald-950/60 text-emerald-300';
      } else if (ac >= 5) {
        quality = '⚠️ Độ ngẫu nhiên trung bình (Hơi trật tự - Tần suất trúng lịch sử khoảng 10%)';
        colorClass = 'border-amber-800 bg-amber-950/60 text-amber-300';
      } else {
        quality = '❌ Quá trật tự / Bất thường nhân tạo (AC ≤ 4 chỉ chiếm <2% lịch sử, nên đổi vé khác)';
        colorClass = 'border-rose-800 bg-rose-950/60 text-rose-300';
      }

      resContainer.classList.remove('hidden');
      resContainer.className = `p-3 rounded-lg border ${colorClass} text-xs font-mono space-y-1.5`;
      resContainer.innerHTML = `
        <div class="flex items-center justify-between font-bold">
          <span>Điểm AC: ${ac} / 10</span>
          <span>Số hiệu số D(X): ${diffs.size} / 15</span>
        </div>
        <p class="text-[11px] font-sans pt-1 border-t border-slate-700/50">${quality}</p>
      `;
    }

    function generateDeltaTicket() {
      const product = appData?.products?.[currentProductKey];
      const maxVal = product?.max_number || 55;
      const numBalls = product?.balls || 6;
      const resContainer = document.getElementById('deltaTicketResult');

      const smallDeltas = [1, 2, 3, 4, 5];
      const mediumDeltas = [6, 7, 8, 9, 10];

      let validTicket = null;
      for (let attempt = 0; attempt < 100; attempt++) {
        const deltas = [];
        deltas.push(Math.floor(Math.random() * 10) + 1);
        for (let i = 1; i < numBalls; i++) {
          if (Math.random() < 0.7) {
            deltas.push(smallDeltas[Math.floor(Math.random() * smallDeltas.length)]);
          } else {
            deltas.push(mediumDeltas[Math.floor(Math.random() * mediumDeltas.length)]);
          }
        }
        const nums = [];
        let acc = 0;
        for (const d of deltas) {
          acc += d;
          nums.push(acc);
        }
        if (nums[nums.length - 1] <= maxVal && new Set(nums).size === numBalls) {
          validTicket = nums;
          break;
        }
      }

      if (validTicket && resContainer) {
        resContainer.classList.remove('hidden');
        resContainer.innerHTML = `
          <div class="text-xs text-slate-400 mb-2">Bộ số sinh bởi chuỗi bước nhảy Delta tự nhiên:</div>
          <div class="flex justify-center gap-2 mb-3">
            ${validTicket.map(n => `<span class="w-8 h-8 rounded-full bg-gradient-to-br from-amber-500 to-orange-600 text-white font-bold font-mono text-xs flex items-center justify-center shadow">${String(n).padStart(2, '0')}</span>`).join('')}
          </div>
          <button onclick="applyDeltaTicket('${validTicket.join(', ')}')" class="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs rounded-lg border border-slate-700 transition">
            Nạp sang Dò Vé Số
          </button>
        `;
      }
    }

    function applyDeltaTicket(str) {
      document.getElementById('ticketInput').value = str;
      switchView('overview');
      checkTicket();
    }

    // --- 10. MARKOV NEXT-DRAW PREDICTOR ---
    function renderMarkovView(product) {
      const markov = product.markov_stats;
      const basisBadge = document.getElementById('markovBasisBadge');
      const grid = document.getElementById('markovCandidatesGrid');
      if (!markov || !markov.top_candidates || markov.top_candidates.length === 0) {
        if (grid) grid.innerHTML = `<p class="text-xs text-slate-500 col-span-full">Chưa có dữ liệu Markov cho loại hình này.</p>`;
        return;
      }

      if (markov.latest_basis && basisBadge) {
        basisBadge.innerHTML = `Kỳ quay cơ sở: <strong>[${markov.latest_basis.map(n => String(n).padStart(2, '0')).join(', ')}]</strong>`;
      }

      if (grid) {
        grid.innerHTML = markov.top_candidates.map((c, idx) => {
          const medal = idx === 0 ? '🥇' : idx === 1 ? '🥈' : idx === 2 ? '🥉' : `#${idx + 1}`;
          return `
            <div class="bg-slate-950 p-3.5 rounded-xl border border-slate-800 flex items-center justify-between gap-3">
              <div class="flex items-center gap-3">
                <span class="text-xs font-mono font-bold text-slate-500 w-5">${medal}</span>
                <span class="w-9 h-9 rounded-full bg-gradient-to-br from-fuchsia-600 to-purple-700 text-white font-bold font-mono text-sm flex items-center justify-center shadow-lg shadow-fuchsia-950/50">
                  ${String(c.number).padStart(2, '0')}
                </span>
                <div>
                  <div class="text-xs font-bold text-white">Số ${String(c.number).padStart(2, '0')}</div>
                  <div class="text-[10px] text-slate-400 font-mono">${c.score} lần chuyển tiếp</div>
                </div>
              </div>
              <div class="w-20 text-right space-y-1">
                <div class="text-xs font-mono font-bold text-fuchsia-400">${c.rel_strength}%</div>
                <div class="w-full bg-slate-800 rounded-full h-1.5 overflow-hidden">
                  <div class="bg-fuchsia-500 h-1.5 rounded-full" style="width: ${c.rel_strength}%"></div>
                </div>
              </div>
            </div>
          `;
        }).join('');
      }
    }

    function loadMarkovToTicket() {
      const product = appData?.products?.[currentProductKey];
      const markov = product?.markov_stats;
      if (!markov || !markov.top_candidates || markov.top_candidates.length < 6) return;
      const top6 = markov.top_candidates.slice(0, 6).map(c => String(c.number).padStart(2, '0'));
      document.getElementById('ticketInput').value = top6.join(', ');
      switchView('overview');
      checkTicket();
    }

    // --- 11. DIGIT DYNAMICS & EXPECTED VALUE (+EV TRACKER) ---
    let tailDivChartInstance = null;
    function renderDigitsEvView(product) {
      const dd = product.digit_dynamics;
      const ev = product.ev_metrics;

      const camTailsGrid = document.getElementById('camTailsGrid');
      if (dd && dd.cam_tails && camTailsGrid) {
        camTailsGrid.innerHTML = dd.cam_tails.sort((a,b) => a.tail - b.tail).map(t => {
          const isSilent = t.streak >= 2;
          const bg = isSilent ? 'bg-rose-950/80 border-rose-700 text-rose-300' : 'bg-slate-900 border-slate-800 text-slate-300';
          return `
            <div class="p-2 rounded-lg border ${bg}">
              <div class="text-[10px] text-slate-500">Đuôi</div>
              <div class="text-base font-bold my-0.5">${t.tail}</div>
              <div class="text-[10px] ${isSilent ? 'text-rose-400 font-bold' : 'text-slate-500'}">${t.streak} kỳ</div>
            </div>
          `;
        }).join('');
      }

      const camHeadsGrid = document.getElementById('camHeadsGrid');
      if (dd && dd.cam_heads && camHeadsGrid) {
        camHeadsGrid.innerHTML = dd.cam_heads.map(h => {
          const isSilent = h.streak >= 2;
          const bg = isSilent ? 'bg-amber-950/80 border-amber-700 text-amber-300' : 'bg-slate-900 border-slate-800 text-slate-300';
          return `
            <div class="p-2 rounded-lg border ${bg}">
              <div class="text-[10px] text-slate-500">Đầu</div>
              <div class="text-base font-bold my-0.5">${h.head}</div>
              <div class="text-[10px] ${isSilent ? 'text-amber-400 font-bold' : 'text-slate-500'}">${h.streak} kỳ</div>
            </div>
          `;
        }).join('');
      }

      if (dd && dd.tail_diversity) {
        renderTailDivChart();
      }

      if (ev && ev.current_ev) {
        const isPositive = ev.current_ev >= 10000;
        const statusBadge = document.getElementById('evStatusBadge');
        if (statusBadge) {
          statusBadge.textContent = ev.status;
          statusBadge.className = `px-2.5 py-1 rounded-full text-xs font-bold font-mono ${isPositive ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30' : 'bg-amber-500/20 text-amber-300 border border-amber-500/30'}`;
        }

        const amtEl = document.getElementById('evCurrentAmount');
        if (amtEl) amtEl.textContent = `${ev.current_ev.toLocaleString()} VNĐ (${ev.ev_pct}%)`;

        const barEl = document.getElementById('evProgressBar');
        if (barEl) barEl.style.width = `${Math.min(100, ev.ev_pct)}%`;

        const bkEl = document.getElementById('evBreakevenText');
        if (bkEl) bkEl.textContent = ev.breakeven_jackpot || '283 Tỷ VNĐ';

        const table = document.getElementById('evBreakdownTable');
        if (table) {
          table.innerHTML = `
            <div class="p-2.5 rounded-lg bg-slate-950 border border-slate-800 flex justify-between">
              <span class="text-slate-400">Giải thưởng phụ (Nhất, Nhì, Ba):</span>
              <span class="text-slate-200">~1,211 VNĐ / vé</span>
            </div>
            <div class="p-2.5 rounded-lg bg-slate-950 border border-slate-800 flex justify-between">
              <span class="text-slate-400">Đóng góp từ Jackpot 2:</span>
              <span class="text-slate-200">~684 VNĐ / vé</span>
            </div>
            <div class="p-2.5 rounded-lg bg-slate-950 border border-slate-800 flex justify-between">
              <span class="text-slate-400">Đóng góp từ Jackpot 1:</span>
              <span class="text-slate-200">~1,624 VNĐ / vé</span>
            </div>
            <div class="p-2.5 rounded-lg bg-slate-900 border border-slate-700 flex justify-between font-bold">
              <span class="text-emerald-400">Tổng Giá Trị Kỳ Vọng:</span>
              <span class="text-emerald-400">${ev.current_ev.toLocaleString()} VNĐ / 10.000 VNĐ</span>
            </div>
          `;
        }
      }
    }

    function renderTailDivChart() {
      const product = appData?.products?.[currentProductKey];
      const dd = product?.digit_dynamics;
      if (!dd || !dd.tail_diversity) return;
      const canvas = document.getElementById('tailDivChart');
      if (!canvas) return;

      if (tailDivChartInstance) tailDivChartInstance.destroy();

      const labels = dd.tail_diversity.map(d => `${d.distinct_tails} đuôi khác nhau`);
      const dataValues = dd.tail_diversity.map(d => d.count);

      tailDivChartInstance = new Chart(canvas.getContext('2d'), {
        type: 'doughnut',
        data: {
          labels: labels,
          datasets: [{
            data: dataValues,
            backgroundColor: [
              'rgba(148, 163, 184, 0.5)',
              'rgba(20, 184, 166, 0.8)',
              'rgba(6, 182, 212, 0.8)',
              'rgba(59, 130, 246, 0.8)'
            ],
            borderWidth: 1,
            borderColor: '#0f172a'
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { position: 'right', labels: { color: '#94a3b8', font: { size: 10 } } }
          }
        }
      });
    }

    // --- 12. ENSEMBLE PREDICTOR & PREDICTION HISTORY ---


    // ==========================================
    // WHEELING SYSTEM JAVASCRIPT FUNCTIONS
    // ==========================================
    function renderWheelingStrategy(product) {
      const ws = product?.wheeling_strategy;
      const section = document.getElementById('wheelingSystemSection');
      if (!section) return;

      if (!ws || !ws.tickets || !ws.tickets.length) {
        section.classList.add('hidden');
        return;
      }
      section.classList.remove('hidden');

      const coreBallsContainer = document.getElementById('wheelingCorePoolBalls');
      const coreSizeEl = document.getElementById('wheelingCorePoolSize');
      const ticketsContainer = document.getElementById('wheelingTicketsGrid');

      if (coreSizeEl) coreSizeEl.textContent = ws.core_pool_size || 14;

      if (coreBallsContainer) {
        coreBallsContainer.innerHTML = (ws.core_pool || []).map(num => `
          <span class="w-8 h-8 rounded-full bg-gradient-to-tr from-amber-500 to-yellow-600 text-slate-950 font-mono font-bold text-xs flex items-center justify-center shadow-md shadow-amber-950/40 border border-yellow-300">
            ${String(num).padStart(2, '0')}
          </span>
        `).join('');
      }

      if (ticketsContainer) {
        ticketsContainer.innerHTML = (ws.tickets || []).map((t, idx) => {
          return `
            <div class="rounded-xl bg-slate-950 p-4 border border-slate-800/90 flex flex-col justify-between space-y-3 hover:border-indigo-500/50 transition">
              <div class="flex items-center justify-between border-b border-slate-800 pb-2">
                <span class="text-xs font-bold font-mono text-indigo-300">VÉ BỌC LÓT #${t.ticketIndex || (idx + 1)}</span>
                <span class="text-[11px] font-mono text-slate-400">Tổng ${t.sum} • AC ${t.ac}</span>
              </div>
              <div class="flex items-center justify-center gap-1.5 py-1">
                ${t.numbers.map(n => `
                  <span class="w-8 h-8 rounded-full bg-slate-800 text-slate-200 font-mono font-bold text-xs flex items-center justify-center border border-slate-700">
                    ${String(n).padStart(2, '0')}
                  </span>
                `).join('')}
              </div>
              <div class="flex items-center gap-2 pt-2 border-t border-slate-800/80 text-[11px]">
                <button onclick="applyGoldenTicketToChecker('${t.numbers.join(', ')}')" class="flex-1 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 font-semibold transition">
                  Dò vé
                </button>
                <button onclick="saveSingleGoldenTicket('${t.numbers.join(', ')}', 92)" class="p-1.5 px-2.5 rounded-lg bg-indigo-600/80 hover:bg-indigo-600 text-white font-semibold transition" title="Lưu vé này vào sổ tay">
                  <i data-lucide="bookmark" class="w-3.5 h-3.5"></i>
                </button>
                <button onclick="copySingleTicketSms('${t.numbers.join(' ')}')" class="p-1.5 px-2.5 rounded-lg bg-emerald-600/80 hover:bg-emerald-600 text-white font-semibold transition" title="Copy SMS 9969">
                  <i data-lucide="message-square" class="w-3.5 h-3.5"></i>
                </button>
              </div>
            </div>
          `;
        }).join('');
      }
      lucide.createIcons();
    }

    function saveAllWheelingTickets() {
      const product = appData?.products?.[currentProductKey];
      const ws = product?.wheeling_strategy;
      if (!ws || !ws.tickets || !ws.tickets.length) {
        alert('Không tìm thấy dữ liệu dàn bọc lót!');
        return;
      }
      const nextId = product.latest?.id ? String(parseInt(product.latest.id.replace('#', '')) + 1).padStart(5, '0') : '00000';
      const list = getSavedTickets();
      let added = 0;
      ws.tickets.forEach(t => {
        const ticketData = {
          id: 'wheel_' + currentProductKey + '_' + nextId + '_' + t.ticketIndex,
          game: currentProductKey,
          gameName: product.name,
          drawId: nextId,
          type: 'wheel',
          numbers: t.numbers,
          cost: 10000,
          savedAt: new Date().toLocaleString('vi-VN')
        };
        const exists = list.some(x => x.game === ticketData.game && x.drawId === ticketData.drawId && JSON.stringify(x.numbers) === JSON.stringify(ticketData.numbers));
        if (!exists) {
          list.unshift(ticketData);
          added++;
        }
      });
      setSavedTickets(list);
      updateSavedBadge();
      alert(`ĐÃ LƯU THÀNH CÔNG DÀN 6 VÉ! 📥\n\nToàn bộ ${added} vé trong dàn bọc lót đã được nạp an toàn vào Sổ Tay của bạn.`);
    }

    function copyWheelingSms() {
      const product = appData?.products?.[currentProductKey];
      const ws = product?.wheeling_strategy;
      if (!ws || !ws.tickets || !ws.tickets.length) return;

      const code = currentProductKey === 'power_655' ? '655' : currentProductKey === 'power_645' ? '645' : '535';
      const lines = ws.tickets.map((t, idx) => {
        const letter = String.fromCharCode(65 + idx);
        const numsStr = t.numbers.map(n => String(n).padStart(2, '0')).join(' ');
        return `${code} K1 ${letter} S ${numsStr}`;
      });

      const fullMsg = lines.join('\n');
      navigator.clipboard.writeText(fullMsg).then(() => {
        alert(`ĐÃ COPY CÚ PHÁP DÀN 6 VÉ SMS 9969! 📲\n\n${fullMsg}\n\nBạn có thể gửi từng dòng hoặc gửi tin nhắn đến tổng đài 9969.`);
      }).catch(() => {
        prompt('Copy cú pháp gửi 9969:', fullMsg);
      });
    }

    function copySingleTicketSms(numsSpaceSeparated) {
      const code = currentProductKey === 'power_655' ? '655' : currentProductKey === 'power_645' ? '645' : '535';
      const formatted = numsSpaceSeparated.split(' ').map(n => n.padStart(2, '0')).join(' ');
      const syntax = `${code} K1 A S ${formatted}`;
      navigator.clipboard.writeText(syntax).then(() => {
        alert(`ĐÃ COPY CÚ PHÁP SMS 9969! 📲\n\n${syntax}\n\nNgười nhận: 9969`);
      }).catch(() => {
        prompt('Copy cú pháp gửi 9969:', syntax);
      });
    }


    // ==========================================
    // BAC NHO & CAU ROI JAVASCRIPT FUNCTIONS
    // ==========================================
    function renderBacNhoAnalytics(product) {
      const bn = product?.bac_nho_analytics;
      const section = document.getElementById('bacNhoSection');
      if (!section) return;

      if (!bn || !bn.cau_roi_analysis || !bn.cau_roi_analysis.length) {
        section.classList.add('hidden');
        return;
      }
      section.classList.remove('hidden');

      const rateEl = document.getElementById('bacNhoRepeatRate');
      if (rateEl) rateEl.textContent = `${bn.has_repeat_pct}% (200 kỳ)`;

      // Render Cau Roi Balls
      const cauRoiContainer = document.getElementById('cauRoiBallsContainer');
      const topNumbers = (bn.top_cau_roi || []).map(x => x.number);

      if (cauRoiContainer) {
        cauRoiContainer.innerHTML = (bn.cau_roi_analysis || []).map(item => {
          const isTop = topNumbers.includes(item.number);
          const bgCls = isTop 
            ? 'border-emerald-400/80 bg-gradient-to-b from-slate-900 to-emerald-950/40 text-emerald-300 shadow-md shadow-emerald-950/40' 
            : 'border-slate-800 bg-slate-900 text-slate-300';

          return `
            <div class="rounded-xl border ${bgCls} p-2.5 flex flex-col items-center justify-between text-center relative transition hover:scale-105 cursor-pointer" 
              onclick="applyGoldenTicketToChecker('${item.number}')" title="Bóng ${item.number} đã từng rơi lại ${item.past_repeats} lần trong 200 kỳ">
              ${isTop ? '<span class="absolute -top-1.5 px-1.5 py-0.2 rounded-full text-[8px] font-black bg-emerald-500 text-slate-950 tracking-wider">KHUYÊN CHỌN</span>' : ''}
              <span class="w-8 h-8 rounded-full bg-slate-800 text-white font-mono font-bold text-xs flex items-center justify-center border border-slate-700 mt-1">
                ${String(item.number).padStart(2, '0')}
              </span>
              <div class="text-[10px] text-slate-400 mt-1">
                Từng rơi: <strong class="text-emerald-400">${item.past_repeats} lần</strong>
              </div>
            </div>
          `;
        }).join('');
      }

      // Render Bac Nho Rules
      const rulesContainer = document.getElementById('bacNhoRulesContainer');
      if (rulesContainer) {
        if (!bn.triggered_bac_nho || !bn.triggered_bac_nho.length) {
          rulesContainer.innerHTML = `<p class="text-xs text-slate-500 col-span-full py-4 text-center">Chưa có cặp bạc nhớ nào vượt ngưỡng Lift 1.6x ở kỳ này.</p>`;
        } else {
          rulesContainer.innerHTML = bn.triggered_bac_nho.map(rule => `
            <div class="rounded-lg bg-slate-900 p-2.5 border border-slate-800 flex items-center justify-between hover:border-amber-500/40 transition">
              <div class="flex items-center gap-2">
                <span class="w-7 h-7 rounded-full bg-slate-800 text-slate-300 font-mono font-bold text-xs flex items-center justify-center border border-slate-700">
                  ${String(rule.from_number).padStart(2, '0')}
                </span>
                <i data-lucide="arrow-right" class="w-3.5 h-3.5 text-amber-400"></i>
                <span class="w-7 h-7 rounded-full bg-amber-500/20 text-amber-300 font-mono font-bold text-xs flex items-center justify-center border border-amber-500/40">
                  ${String(rule.to_number).padStart(2, '0')}
                </span>
              </div>
              <div class="text-right text-[11px] font-mono">
                <div class="text-amber-400 font-bold">${rule.count} lần • ${rule.probability_pct}%</div>
                <div class="text-[9px] text-slate-400">Lift ${rule.lift}x ngẫu nhiên</div>
              </div>
            </div>
          `).join('');
        }
      }

      lucide.createIcons();
    }
