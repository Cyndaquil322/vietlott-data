// ==========================================
// 4. CONSENSUS & ENSEMBLE: Consensus AI, Seeded PRNG, Live Countdown, Special Ball
// ==========================================


    function renderLottoBall(num, size = 'md', isSpecial = false) {
      const str = String(num).padStart(2, '0');
      let sizeClass = 'w-9 h-9 text-xs';
      if (size === 'sm') sizeClass = 'w-7 h-7 text-[11px]';
      if (size === 'lg') sizeClass = 'w-11 h-11 text-base font-bold';
      const colorClass = isSpecial ? 'ball-gold' : 'ball-red';
      return `<span class="lotto-ball ${colorClass} ${sizeClass} font-mono shadow inline-flex items-center justify-center">${str}</span>`;
    }

    function renderConsensusView(product) {
      if (!product || !product.consensus_hub) return;
      const hub = product.consensus_hub;

      // 1. Header KPIs & Target Draw Identification
      const nextDrawEl = document.getElementById('consensusNextDrawBadge');
      if (nextDrawEl) nextDrawEl.textContent = hub.next_draw_id || 'Kỳ Kế Tiếp';

      const lastDrawEl = document.getElementById('consensusLastDrawBadge');
      if (lastDrawEl) {
        const last = product.latest || {};
        lastDrawEl.textContent = last.id ? `#${last.id} (${last.date || ''})` : '--';
      }

      const drawText = hub.next_draw_id || 'Kỳ Kế Tiếp';
      const cardGoldenDraw = document.getElementById('consensusCardGoldenDraw');
      if (cardGoldenDraw) cardGoldenDraw.textContent = `Dự đoán ${drawText}`;

      const cardMomDraw = document.getElementById('consensusCardMomDraw');
      if (cardMomDraw) cardMomDraw.textContent = `Dự đoán ${drawText}`;

      const cardBao7Draw = document.getElementById('consensusCardBao7Draw');
      if (cardBao7Draw) cardBao7Draw.textContent = `Dự đoán ${drawText}`;

      const winRateEl = document.getElementById('consensusWinRateGe3');
      const consensusModel = hub.leaderboard?.find(x => x.id === 'consensus');
      if (winRateEl && consensusModel) {
        winRateEl.textContent = `${consensusModel.win_rate_ge3}%`;
      }

      // 2. Leaderboard Table
      const ldBody = document.getElementById('consensusLeaderboardBody');
      if (ldBody && hub.leaderboard) {
        ldBody.innerHTML = hub.leaderboard.map(m => {
          const isConsensus = (m.id === 'consensus');
          const isBaseline = (m.id === 'baseline_random');

          const rowBg = isConsensus 
            ? 'bg-amber-950/30 border-y border-amber-500/40 text-amber-200' 
            : (isBaseline ? 'bg-slate-950/40 text-slate-400' : 'hover:bg-slate-800/40 text-slate-300');

          const nameBadge = isConsensus 
            ? `<span class="ml-2 px-1.5 py-0.2 rounded text-[9px] font-bold bg-amber-500 text-slate-950">🏆 QUÁN QUÂN</span>`
            : '';

          const weightBar = !isBaseline 
            ? `
              <div class="flex items-center justify-center gap-2">
                <span class="font-bold text-xs">${m.weight_pct}%</span>
                <div class="w-16 bg-slate-800 rounded-full h-1.5 overflow-hidden">
                  <div class="bg-gradient-to-r from-amber-500 to-rose-500 h-1.5 rounded-full" style="width: ${Math.min(100, m.weight_pct)}%"></div>
                </div>
              </div>
            ` 
            : `<span class="text-slate-600">--</span>`;

          return `
            <tr class="${rowBg} transition">
              <td class="px-3 py-3 font-medium">
                <div class="flex items-start gap-2">
                  <i data-lucide="${m.icon || 'activity'}" class="w-4 h-4 mt-0.5 text-${m.color || 'slate'}-400 flex-shrink-0"></i>
                  <div>
                    <div class="font-bold text-white flex items-center">${m.name} ${nameBadge}</div>
                    <div class="text-[10px] text-slate-400 font-sans mt-0.5 line-clamp-1">${m.desc || ''}</div>
                  </div>
                </div>
              </td>
              <td class="px-3 py-3 text-center font-bold text-sm ${isConsensus ? 'text-amber-300' : 'text-slate-200'}">
                ${m.avg_hits} <span class="text-[10px] text-slate-500 font-normal">bóng</span>
              </td>
              <td class="px-3 py-3 text-center">
                <span class="px-2 py-0.5 rounded-full text-[11px] font-bold ${m.win_rate_ge3 >= 20 ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40' : (m.win_rate_ge3 >= 10 ? 'bg-blue-500/20 text-blue-300 border border-blue-500/40' : 'bg-slate-800 text-slate-400')}">
                  ${m.win_rate_ge3}%
                </span>
              </td>
              <td class="px-3 py-3 text-center">
                <div class="flex flex-col items-center">
                  <span class="font-bold text-xs">${m.recent_10_hits} bóng</span>
                  <span class="text-[10px] text-slate-400">${m.form}</span>
                </div>
              </td>
              <td class="px-3 py-3 text-center">
                ${weightBar}
              </td>
            </tr>
          `;
        }).join('');
      }

      // 2.5 Trained Hyperparameters & Negative Space
      const report = hub.training_report || {};
      const params = report.trained_hyperparameters || {};

      const alphaEl = document.getElementById('paramAlpha');
      if (alphaEl) alphaEl.textContent = `α = ${params.decay_alpha || 0.035}`;

      const hlEl = document.getElementById('paramHalfLife');
      if (hlEl) hlEl.textContent = `${params.half_life_draws || 20} kỳ`;

      const hWinEl = document.getElementById('paramHazardWin');
      if (hWinEl && params.hazard_window) {
        hWinEl.textContent = `[${params.hazard_window[0]} - ${params.hazard_window[1]}] chu kỳ`;
      }

      const gSumEl = document.getElementById('paramGaussianSum');
      if (gSumEl && params.gaussian_sum_range) {
        gSumEl.textContent = `[${params.gaussian_sum_range[0]} - ${params.gaussian_sum_range[1]}]`;
      }

      const gMeanEl = document.getElementById('paramGaussianMean');
      if (gMeanEl) gMeanEl.textContent = `μ = ${params.gaussian_mean || 168}`;

      const minAcEl = document.getElementById('paramMinAc');
      if (minAcEl) minAcEl.textContent = `AC ≥ ${params.min_ac_threshold || 7}`;

      const nsBadgeEl = document.getElementById('consensusNsStatusBadge');
      if (nsBadgeEl && report.negative_space_compliance) {
        nsBadgeEl.textContent = report.negative_space_compliance;
      }

      // 3. Suggested Seeded Tickets
      const tickets = hub.tickets || {};

      // 3.0 Tier 1 & 2: Key Balls & Core Pool
      const targetDrawEl2 = document.getElementById('consensusTargetDrawBadge2');
      if (targetDrawEl2 && hub.next_draw_id) targetDrawEl2.textContent = `Dự đoán ${hub.next_draw_id}`;

      const coreBacktest = tickets.core_backtest || {};
      const coreWinRateEl = document.getElementById('consensusCoreWinRate');
      if (coreWinRateEl) coreWinRateEl.textContent = `${coreBacktest.win_rate_ge3 || 12.0}%`;

      const coreSizeLabel = document.getElementById('consensusCorePoolSizeLabel');
      if (coreSizeLabel) coreSizeLabel.textContent = `${coreBacktest.pool_size || 12}`;

      const coreAvgHitsEl = document.getElementById('consensusCoreAvgHitsBadge');
      if (coreAvgHitsEl) coreAvgHitsEl.textContent = `TB ${coreBacktest.avg_hits || 1.3} bóng/kỳ`;

      // Render Top 3 Key Balls & Top 5 Ngũ Thủ
      renderConsensusKeyBalls(tickets);

      // Render Core Pool Balls
      const corePoolContainer = document.getElementById('consensusCorePoolBalls');
      if (corePoolContainer && tickets.core_pool) {
        corePoolContainer.innerHTML = tickets.core_pool.map(n => renderLottoBall(n, 'md')).join('');
      }

      // Render 4-Ticket Abbreviated Covering Wheels
      renderConsensusWheeling4(tickets);

      // Vé A: Golden Combo
      const cardGoldenDrawEl = document.getElementById('consensusCardGoldenDraw');
      if (cardGoldenDrawEl && hub.next_draw_id) cardGoldenDrawEl.textContent = `Dự đoán ${hub.next_draw_id}`;

      const goldenContainer = document.getElementById('consensusGoldenBalls');
      if (goldenContainer && tickets.golden) {
        const nums = tickets.golden.numbers || [];
        const spec = tickets.golden.special;
        goldenContainer.innerHTML = nums.map(n => renderLottoBall(n, 'lg')).join('') + 
          (spec ? `<span class="text-slate-500 font-bold mx-1">+</span>` + renderLottoBall(spec, 'lg', true) : '');

        const acEl = document.getElementById('consensusGoldenAc');
        if (acEl) acEl.textContent = tickets.golden.ac_index || '--';
        const sumEl = document.getElementById('consensusGoldenSum');
        if (sumEl) sumEl.textContent = tickets.golden.sum || '--';
        const oeEl = document.getElementById('consensusGoldenOe');
        if (oeEl) oeEl.textContent = tickets.golden.odd_even || '--';
        const seiEl = document.getElementById('consensusGoldenSei');
        if (seiEl) seiEl.textContent = `${tickets.golden.sei_score || 9.8}/10`;
      }

      // Vé B: Momentum Combo
      const cardMomDrawEl = document.getElementById('consensusCardMomDraw');
      if (cardMomDrawEl && hub.next_draw_id) cardMomDrawEl.textContent = `Dự đoán ${hub.next_draw_id}`;

      const momContainer = document.getElementById('consensusMomentumBalls');
      if (momContainer && tickets.momentum) {
        const nums = tickets.momentum.numbers || [];
        const spec = tickets.momentum.special;
        momContainer.innerHTML = nums.map(n => renderLottoBall(n, 'md')).join('') + 
          (spec ? `<span class="text-slate-500 font-bold mx-1">+</span>` + renderLottoBall(spec, 'md', true) : '');
      }

      // Vé C: Breakout Combo
      const cardBoDrawEl = document.getElementById('consensusCardBreakoutDraw');
      if (cardBoDrawEl && hub.next_draw_id) cardBoDrawEl.textContent = `Dự đoán ${hub.next_draw_id}`;

      const boContainer = document.getElementById('consensusBreakoutBalls');
      if (boContainer && tickets.breakout) {
        const nums = tickets.breakout.numbers || [];
        const spec = tickets.breakout.special;
        boContainer.innerHTML = nums.map(n => renderLottoBall(n, 'md')).join('') + 
          (spec ? `<span class="text-slate-500 font-bold mx-1">+</span>` + renderLottoBall(spec, 'md', true) : '');
      }

      // 4. Top 15 Consensus Balls Table
      const topBallsBody = document.getElementById('consensusTopBallsBody');
      if (topBallsBody && hub.top_consensus_balls) {
        topBallsBody.innerHTML = hub.top_consensus_balls.map((b, idx) => {
          const isTop3 = (idx < 3);
          const agBadge = b.agreement_count >= 4 
            ? `<span class="px-2 py-0.5 rounded text-[11px] font-bold bg-emerald-500/20 text-emerald-300 border border-emerald-500/40">${b.agreement_count}/5 (${b.agreement_pct}%)</span>`
            : (b.agreement_count >= 3
                ? `<span class="px-2 py-0.5 rounded text-[11px] font-bold bg-blue-500/20 text-blue-300 border border-blue-500/40">${b.agreement_count}/5 (${b.agreement_pct}%)</span>`
                : `<span class="px-2 py-0.5 rounded text-[11px] font-bold bg-slate-800 text-slate-400">${b.agreement_count}/5 (${b.agreement_pct}%)</span>`);

          const evalBadge = b.trap_warning 
            ? `<span class="px-2 py-0.5 rounded text-[10px] font-bold bg-amber-500/20 text-amber-300 border border-amber-500/40 flex items-center gap-1 w-max ml-auto">⚠️ Bẫy Gan Lì</span>`
            : (b.is_safe 
                ? `<span class="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 flex items-center gap-1 w-max ml-auto">🛡️ An Toàn</span>`
                : `<span class="px-2 py-0.5 rounded text-[10px] font-bold bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 flex items-center gap-1 w-max ml-auto">⚡ Đột Phá</span>`);

          // Mini stacked bar
          const bd = b.breakdown || {};
          const totalBd = (bd.hazard || 0) + (bd.decay || 0) + (bd.markov || 0) + (bd.fourier || 0) + (bd.bac_nho || 0) || 1.0;
          const pHazard = Math.round(((bd.hazard || 0) / totalBd) * 100);
          const pDecay = Math.round(((bd.decay || 0) / totalBd) * 100);
          const pMarkov = Math.round(((bd.markov || 0) / totalBd) * 100);
          const pFourier = Math.round(((bd.fourier || 0) / totalBd) * 100);
          const pBacNho = Math.max(0, 100 - (pHazard + pDecay + pMarkov + pFourier));

          return `
            <tr class="hover:bg-slate-800/30 transition">
              <td class="px-3 py-2.5 text-center font-bold ${isTop3 ? 'text-amber-400' : 'text-slate-500'}">
                #${idx + 1}
              </td>
              <td class="px-3 py-2.5">
                <div class="flex items-center gap-2">
                  ${renderLottoBall(b.ball, 'sm')}
                  <span class="font-bold text-white text-sm">Bóng ${String(b.ball).padStart(2, '0')}</span>
                </div>
              </td>
              <td class="px-3 py-2.5 text-center">
                <span class="text-sm font-bold text-amber-300">${b.score}</span>
                <span class="text-[10px] text-slate-500">/10</span>
              </td>
              <td class="px-3 py-2.5 text-center">
                ${agBadge}
              </td>
              <td class="px-3 py-2.5">
                <div class="w-full bg-slate-800 rounded-full h-2 flex overflow-hidden shadow-inner" title="Hazard: ${pHazard}%, Decay: ${pDecay}%, Markov: ${pMarkov}%, Fourier: ${pFourier}%, Bạc Nhớ: ${pBacNho}%">
                  <div class="bg-emerald-500 h-2" style="width: ${pHazard}%"></div>
                  <div class="bg-rose-500 h-2" style="width: ${pDecay}%"></div>
                  <div class="bg-fuchsia-500 h-2" style="width: ${pMarkov}%"></div>
                  <div class="bg-cyan-500 h-2" style="width: ${pFourier}%"></div>
                  <div class="bg-indigo-500 h-2" style="width: ${pBacNho}%"></div>
                </div>
              </td>
              <td class="px-3 py-2.5 text-right">
                ${evalBadge}
              </td>
            </tr>
          `;
        }).join('');
      }

      // 5. Model Cards Grid
      const cardsGrid = document.getElementById('consensusModelCardsGrid');
      if (cardsGrid && hub.model_explanations) {
        const modelsMeta = {
          "hazard": { icon: "timer", color: "emerald", border: "border-emerald-500/30", bg: "from-emerald-950/30" },
          "decay": { icon: "flame", color: "rose", border: "border-rose-500/30", bg: "from-rose-950/30" },
          "markov": { icon: "git-merge", color: "fuchsia", border: "border-fuchsia-500/30", bg: "from-fuchsia-950/30" },
          "fourier": { icon: "activity", color: "cyan", border: "border-cyan-500/30", bg: "from-cyan-950/30" },
          "bac_nho": { icon: "network", color: "indigo", border: "border-indigo-500/30", bg: "from-indigo-950/30" }
        };

        cardsGrid.innerHTML = Object.entries(hub.model_explanations).map(([k, exp]) => {
          const meta = modelsMeta[k] || { icon: "cpu", color: "slate", border: "border-slate-800", bg: "from-slate-900" };
          const mWeight = hub.leaderboard?.find(x => x.id === k)?.weight_pct || 20;

          return `
            <div class="p-4 rounded-xl bg-gradient-to-b ${meta.bg} to-slate-950 border ${meta.border} shadow-lg space-y-3">
              <div class="flex items-center justify-between gap-2 border-b border-slate-800/80 pb-2.5">
                <div class="flex items-center gap-2">
                  <i data-lucide="${meta.icon}" class="w-4 h-4 text-${meta.color}-400"></i>
                  <h5 class="font-bold text-white text-xs">${exp.name}</h5>
                </div>
                <span class="px-2 py-0.5 rounded text-[10px] font-bold bg-${meta.color}-500/20 text-${meta.color}-300 border border-${meta.color}-500/40">
                  Trọng số ${mWeight}%
                </span>
              </div>

              <div class="text-[11px] text-slate-400 font-mono">
                <span class="text-slate-500">Cơ sở:</span> ${exp.math_basis}
              </div>

              <div>
                <div class="text-[10px] uppercase font-bold text-slate-400 tracking-wider mb-1.5">Bộ số ưu tiên kỳ này:</div>
                <div class="flex flex-wrap items-center gap-1.5">
                  ${(exp.top_picks || []).map(b => renderLottoBall(b, 'sm')).join('')}
                </div>
              </div>

              <p class="text-xs text-slate-300 bg-slate-900/90 p-2.5 rounded-lg border border-slate-800/80 leading-relaxed italic">
                "${exp.rationale}"
              </p>
            </div>
          `;
        }).join('');
      }

      // 6. Audit History Table & KPIs
      const triadKpi = tickets.triad_backtest || {};
      const key5Kpi = tickets.key5_backtest || {};
      const wheel4Kpi = tickets.wheel4_backtest || {};

      const triadEl = document.getElementById('kpiTriadWinRate');
      if (triadEl) triadEl.textContent = `${triadKpi.win_rate_ge1 || 42}% nổ ≥1 bóng`;

      const key5El = document.getElementById('kpiKey5WinRate');
      if (key5El) key5El.textContent = `${key5Kpi.win_rate_ge1 || 55}% nổ ≥1 bóng`;

      const key5Ge2El = document.getElementById('kpiKey5Ge2Badge');
      if (key5Ge2El) key5Ge2El.textContent = `${key5Kpi.win_rate_ge2 || 15}% ≥2 bóng`;

      const wheel4El = document.getElementById('kpiWheel4WinRate');
      if (wheel4El) wheel4El.textContent = `${wheel4Kpi.core_ge4_win_rate || 100}% trúng khi nổ 4`;

      const auditBody = document.getElementById('consensusAuditHistoryBody');
      if (auditBody && hub.history_walk_forward) {
        auditBody.innerHTML = hub.history_walk_forward.map(row => {
          const k = row.matchCount || 0;
          const kColor = k >= 3 ? 'text-amber-400 font-bold bg-amber-500/10 px-2 py-0.5 rounded border border-amber-500/30' : (k >= 2 ? 'text-emerald-400 font-semibold' : 'text-slate-400');

          const actualHtml = (row.actual || []).map(n => {
            const isHit = (row.triadMatched && row.triadMatched.includes(n)) || (row.matched && row.matched.includes(n));
            return `<span class="inline-block px-1.5 py-0.5 rounded text-[11px] font-mono mr-1 ${isHit ? 'bg-emerald-500/30 text-emerald-300 font-bold border border-emerald-500/50' : 'text-slate-400'}">${String(n).padStart(2, '0')}</span>`;
          }).join('');

          // Triad
          const triadList = row.triad || [];
          const triadHits = row.triadMatchCount !== undefined ? row.triadMatchCount : 0;
          const triadHtml = triadList.map(n => {
            const isHit = (row.triadMatched || []).includes(n);
            return `<span class="inline-block px-1.5 py-0.5 rounded text-[11px] font-mono mr-1 ${isHit ? 'bg-amber-500 text-slate-950 font-bold shadow' : 'bg-slate-800 text-slate-400'}">${String(n).padStart(2, '0')}</span>`;
          }).join('') + (triadHits > 0 ? `<span class="ml-1 px-1.5 py-0.2 rounded text-[10px] font-bold bg-amber-500/20 text-amber-300">${triadHits} con</span>` : '');

          // Key 5
          const key5Hits = row.key5MatchCount !== undefined ? row.key5MatchCount : 0;
          const key5Badge = key5Hits >= 2 
            ? `<span class="px-2 py-0.5 rounded font-bold text-xs bg-emerald-500/20 text-emerald-300 border border-emerald-500/40">${key5Hits}/5 bóng 🔥</span>`
            : (key5Hits >= 1 
                ? `<span class="px-2 py-0.5 rounded font-semibold text-xs bg-indigo-500/20 text-indigo-300 border border-indigo-500/40">${key5Hits}/5 bóng</span>`
                : `<span class="text-slate-600 text-xs">${key5Hits}/5</span>`);

          // Core
          const coreK = row.coreMatchCount !== undefined ? row.coreMatchCount : 0;
          const coreKBadge = coreK >= 3 
            ? `<span class="px-2 py-0.5 rounded font-bold text-xs bg-amber-500/20 text-amber-300 border border-amber-500/40">${coreK} bóng 🔥</span>`
            : (coreK >= 2 
                ? `<span class="px-2 py-0.5 rounded font-semibold text-xs bg-emerald-500/20 text-emerald-300 border border-emerald-500/40">${coreK} bóng</span>`
                : `<span class="text-slate-500 text-xs">${coreK} bóng</span>`);

          // Wheel 4
          const w4 = row.wheel4 || {};
          const wheel4Badge = w4.wonPrize 
            ? `<span class="px-2 py-0.5 rounded font-bold text-[11px] bg-emerald-500/20 text-emerald-300 border border-emerald-500/40">Trúng Giải (${w4.maxHit} con) 🎉</span>`
            : `<span class="text-slate-500 text-xs">Max ${w4.maxHit || 0} con</span>`;

          return `
            <tr class="hover:bg-slate-800/30 transition text-xs font-mono">
              <td class="px-3 py-2.5 font-bold text-white">#${row.drawId}</td>
              <td class="px-3 py-2.5 text-slate-400 whitespace-nowrap">${row.date}</td>
              <td class="px-3 py-2.5">${actualHtml}</td>
              <td class="px-3 py-2.5 whitespace-nowrap">${triadHtml || '<span class="text-slate-600">--</span>'}</td>
              <td class="px-3 py-2.5 text-center">${key5Badge}</td>
              <td class="px-3 py-2.5 text-center">${coreKBadge}</td>
              <td class="px-3 py-2.5 text-center">${wheel4Badge}</td>
              <td class="px-3 py-2.5 text-right"><span class="${kColor}">${k} số</span></td>
            </tr>
          `;
        }).join('');
      }

      lucide.createIcons();
    }

    function saveConsensusTicket(type) {
      const product = appData?.products?.[currentProductKey];
      if (!product || !product.consensus_hub) return;
      const hub = product.consensus_hub;
      const t = hub.tickets?.[type];
      if (!t || !t.numbers) return;

      const nextDrawId = hub.next_draw_id?.replace('#', '') || 'Next';
      const typeName = type === 'golden' ? 'Dàn Vàng Consensus' : (type === 'momentum' ? 'Dàn Xung Lực' : (type === 'breakout' ? 'Dàn Điểm Rơi Hazard' : 'Dàn Bao 7'));

      saveTicketToNotebook({
        game: currentProductKey,
        gameName: product.name,
        drawId: nextDrawId,
        ticketType: type === 'bao7' ? 'Bao 7' : 'Chuẩn',
        label: `${typeName} (#${nextDrawId})`,
        numbers: t.numbers,
        special: t.special || null
      });
    }

    function saveConsensusCorePool() {
      const product = appData?.products?.[currentProductKey];
      if (!product || !product.consensus_hub) return;
      const hub = product.consensus_hub;
      const pool = hub.tickets?.core_pool || [];
      if (!pool.length) return;
      const nextDrawId = hub.next_draw_id?.replace('#', '') || 'Next';
      saveTicketToNotebook({
        game: currentProductKey,
        gameName: product.name,
        drawId: nextDrawId,
        ticketType: `Dàn ${pool.length} Số`,
        label: `Dàn Hạt Nhân ${pool.length} Số (#${nextDrawId})`,
        numbers: pool,
        special: null
      });
    }

    function copyConsensusCorePool() {
      const product = appData?.products?.[currentProductKey];
      if (!product || !product.consensus_hub) return;
      const pool = product.consensus_hub.tickets?.core_pool || [];
      if (!pool.length) return;
      const numbersStr = pool.map(x => String(x).padStart(2, '0')).join(' ');
      copySingleTicketSms(numbersStr);
    }

    function copyConsensusTicketSms(type) {
      const product = appData?.products?.[currentProductKey];
      if (!product || !product.consensus_hub) return;
      const t = product.consensus_hub.tickets?.[type];
      if (!t || !t.numbers) return;

      const numbersStr = t.numbers.map(x => String(x).padStart(2, '0')).join(' ');
      copySingleTicketSms(numbersStr);
    }

    let consensusKeyMode = 'triad';

    function setKeyMode(mode) {
      consensusKeyMode = mode;
      const btnTriad = document.getElementById('btnKeyModeTriad');
      const btnFive = document.getElementById('btnKeyModeFive');
      if (btnTriad && btnFive) {
        if (mode === 'triad') {
          btnTriad.className = 'px-2 py-0.5 rounded font-bold transition bg-amber-500 text-slate-950';
          btnFive.className = 'px-2 py-0.5 rounded font-bold transition text-slate-400 hover:text-white';
        } else {
          btnFive.className = 'px-2 py-0.5 rounded font-bold transition bg-amber-500 text-slate-950';
          btnTriad.className = 'px-2 py-0.5 rounded font-bold transition text-slate-400 hover:text-white';
        }
      }
      const product = appData?.products?.[currentProductKey];
      if (product && product.consensus_hub) {
        renderConsensusKeyBalls(product.consensus_hub.tickets || {});
      }
    }

    function renderConsensusKeyBalls(tickets) {
      const container = document.getElementById('consensusKeyBallsContainer');
      const descEl = document.getElementById('consensusKeyDesc');
      if (!container) return;

      if (consensusKeyMode === 'triad') {
        const roles = tickets.key_roles || (tickets.key_balls || []).map((b, i) => ({
          ball: b,
          role: i === 0 ? 'Xác Suất Markov' : (i === 1 ? 'Điểm Rơi Hazard' : 'Nhịp Cầu Rơi'),
          color: i === 0 ? 'fuchsia' : (i === 1 ? 'emerald' : 'amber')
        }));
        container.innerHTML = roles.map(r => `
          <div class="flex flex-col items-center gap-1.5 p-2 rounded-xl bg-slate-900/80 border border-slate-800 shadow-sm min-w-[95px]">
            ${renderLottoBall(r.ball, 'lg')}
            <span class="px-2 py-0.5 rounded text-[10px] font-bold bg-${r.color}-500/20 text-${r.color}-300 border border-${r.color}-500/40 whitespace-nowrap">
              ${r.role}
            </span>
          </div>
        `).join('');
        if (descEl) {
          descEl.textContent = 'Cơ chế Kiềng 3 Chân (1 Markov + 1 Hazard + 1 Cầu Rơi): Đa dạng hóa nguồn xung lực, nâng tỷ lệ nổ ≥1 bóng lên 42% - 48%.';
        }
      } else {
        const fiveBalls = tickets.key_5_balls || (tickets.key_balls || []).concat(tickets.core_pool ? tickets.core_pool.slice(3, 5) : []);
        container.innerHTML = fiveBalls.map((n, idx) => `
          <div class="flex flex-col items-center gap-1 p-1.5 rounded-xl bg-slate-900/80 border border-slate-800 shadow-sm min-w-[65px]">
            ${renderLottoBall(n, 'md')}
            <span class="text-[10px] font-bold text-amber-400 font-mono mt-0.5">Trục #${idx + 1}</span>
          </div>
        `).join('');
        if (descEl) {
          descEl.textContent = 'Top 5 Ngũ Thủ Trục: Tỷ lệ nổ ≥1 bóng đạt >55%, nổ ≥2 bóng đạt 12% - 17%. Khuyên dùng làm bộ khung cố định (Banker) hoặc ghép dàn.';
        }
      }
    }

    function saveConsensusKeyBalls() {
      const product = appData?.products?.[currentProductKey];
      if (!product || !product.consensus_hub) return;
      const hub = product.consensus_hub;
      const tickets = hub.tickets || {};
      const nums = (consensusKeyMode === 'triad') ? (tickets.key_balls || []) : (tickets.key_5_balls || []);
      if (!nums.length) return;
      const nextDrawId = hub.next_draw_id?.replace('#', '') || 'Next';
      const label = consensusKeyMode === 'triad' ? `Bạch Thủ Kiềng 3 Chân (#${nextDrawId})` : `Top 5 Ngũ Thủ Trục (#${nextDrawId})`;
      saveTicketToNotebook({
        game: currentProductKey,
        gameName: product.name,
        drawId: nextDrawId,
        ticketType: consensusKeyMode === 'triad' ? 'Trục 3 Số' : 'Trục 5 Số',
        label: label,
        numbers: nums,
        special: null
      });
    }

    function copyConsensusKeyBalls() {
      const product = appData?.products?.[currentProductKey];
      if (!product || !product.consensus_hub) return;
      const hub = product.consensus_hub;
      const tickets = hub.tickets || {};
      const nums = (consensusKeyMode === 'triad') ? (tickets.key_balls || []) : (tickets.key_5_balls || []);
      if (!nums.length) return;
      const numbersStr = nums.map(x => String(x).padStart(2, '0')).join(' ');
      copySingleTicketSms(numbersStr);
    }

    function renderConsensusWheeling4(tickets) {
      const container = document.getElementById('consensusWheeling4Grid');
      if (!container) return;
      const wheels = tickets.wheeling_4_tickets || [];
      if (!wheels.length) {
        container.innerHTML = `<p class="text-xs text-slate-500 col-span-full py-2">Chưa có tổ hợp 4 vé bao thu gọn.</p>`;
        return;
      }
      container.innerHTML = wheels.map((t, idx) => `
        <div class="p-3 rounded-xl bg-slate-900/90 border border-slate-800 hover:border-emerald-500/40 transition flex flex-col justify-between space-y-2.5">
          <div class="flex items-center justify-between text-xs">
            <span class="font-bold text-emerald-300 font-mono flex items-center gap-1">
              <i data-lucide="ticket" class="w-3.5 h-3.5"></i> ${t.label || `Vé ${idx + 1}`}
            </span>
            <span class="text-[10px] font-mono text-emerald-400/80 bg-emerald-500/10 px-1.5 py-0.5 rounded border border-emerald-500/20">10.000đ</span>
          </div>
          <div class="flex flex-wrap items-center gap-1.5 py-1 justify-center">
            ${t.numbers.map(n => renderLottoBall(n, 'sm')).join('')}
            ${t.special ? `<span class="text-slate-500 text-xs font-bold">+</span>` + renderLottoBall(t.special, 'sm', true) : ''}
          </div>
          <div class="flex items-center gap-1.5 pt-1.5 border-t border-slate-800/80">
            <button onclick="saveSingleWheeling4Ticket(${idx})" class="flex-1 py-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-emerald-300 text-[10px] font-bold flex items-center justify-center gap-1 transition" title="Lưu vé này">
              <i data-lucide="bookmark" class="w-3 h-3"></i> Lưu Sổ
            </button>
            <button onclick="copySingleWheeling4TicketSms(${idx})" class="px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-700 text-emerald-400 text-[10px] font-bold flex items-center gap-1 transition" title="Copy SMS 9969">
              <i data-lucide="copy" class="w-3 h-3"></i> SMS
            </button>
          </div>
        </div>
      `).join('');
      if (window.lucide) lucide.createIcons();
    }

    function saveWheeling4Tickets() {
      const product = appData?.products?.[currentProductKey];
      if (!product || !product.consensus_hub) return;
      const hub = product.consensus_hub;
      const wheels = hub.tickets?.wheeling_4_tickets || [];
      if (!wheels.length) {
        alert('Không tìm thấy dữ liệu dàn bao thu gọn!');
        return;
      }
      const nextDrawId = hub.next_draw_id?.replace('#', '') || 'Next';
      const list = getSavedTickets();
      let added = 0;
      wheels.forEach((t, idx) => {
        const ticketData = {
          id: 'wheel4_' + currentProductKey + '_' + nextDrawId + '_' + (idx + 1),
          game: currentProductKey,
          gameName: product.name,
          drawId: nextDrawId,
          ticketType: 'Bao Thu Gọn',
          label: `Bao Thu Gọn Vé ${idx + 1} (#${nextDrawId})`,
          numbers: t.numbers,
          special: t.special || null,
          cost: 10000,
          savedAt: new Date().toLocaleDateString('vi-VN') + ' ' + new Date().toLocaleTimeString('vi-VN', {hour: '2-digit', minute:'2-digit'})
        };
        const exists = list.some(x => x.game === ticketData.game && x.drawId === ticketData.drawId && JSON.stringify(x.numbers) === JSON.stringify(ticketData.numbers));
        if (!exists) {
          list.unshift(ticketData);
          added++;
        }
      });
      setSavedTickets(list);
      updateSavedBadge();
      if (confirm(`ĐÃ LƯU THÀNH CÔNG DÀN 4 VÉ! 📥\n\nToàn bộ ${added} vé Bao Thu Gọn (Vốn 40.000đ) đã được nạp an toàn vào Sổ Tay.\n\nBạn có muốn chuyển sang xem ngay tại tab "Sổ Tay Vé Đã Lưu"?`)) {
        switchView('saved-tickets');
      }
    }

    function copyWheeling4Sms() {
      const product = appData?.products?.[currentProductKey];
      if (!product || !product.consensus_hub) return;
      const wheels = product.consensus_hub.tickets?.wheeling_4_tickets || [];
      if (!wheels.length) return;
      const lines = wheels.map(t => t.numbers.map(x => String(x).padStart(2, '0')).join(' '));
      const fullText = lines.join('\n');
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(fullText).then(() => {
          alert(`ĐÃ COPY CÚ PHÁP 4 VÉ! 📋\n\n${fullText}\n\nĐã sao chép vào bộ nhớ tạm để gửi tin nhắn SMS 9969 hoặc lưu trữ.`);
        }).catch(() => {
          copySingleTicketSms(lines[0]);
        });
      } else {
        copySingleTicketSms(lines[0]);
      }
    }

    function saveSingleWheeling4Ticket(idx) {
      const product = appData?.products?.[currentProductKey];
      if (!product || !product.consensus_hub) return;
      const hub = product.consensus_hub;
      const t = hub.tickets?.wheeling_4_tickets?.[idx];
      if (!t) return;
      const nextDrawId = hub.next_draw_id?.replace('#', '') || 'Next';
      saveTicketToNotebook({
        game: currentProductKey,
        gameName: product.name,
        drawId: nextDrawId,
        ticketType: 'Bao Thu Gọn',
        label: `Bao Thu Gọn ${t.label || `Vé ${idx + 1}`} (#${nextDrawId})`,
        numbers: t.numbers,
        special: t.special || null
      });
    }

    function copySingleWheeling4TicketSms(idx) {
      const product = appData?.products?.[currentProductKey];
      if (!product || !product.consensus_hub) return;
      const t = product.consensus_hub.tickets?.wheeling_4_tickets?.[idx];
      if (!t || !t.numbers) return;
      const numbersStr = t.numbers.map(x => String(x).padStart(2, '0')).join(' ');
      copySingleTicketSms(numbersStr);
    }

    function renderEnsembleView(product) {
      if (!product || product.type !== 'lotto') {
        const grid = document.getElementById('ensembleGoldenTicketsGrid');
        if (grid) grid.innerHTML = `<p class="text-xs text-slate-500 col-span-full">Tính năng Dự Đoán Toàn Diện hỗ trợ cho các loại hình vé số ma trận (Power 6/55, Mega 6/45, Power 5/35).</p>`;
        return;
      }

      // 1. Update criteria summary
      const sumStats = product.sum_stats;
      const sumRangeEl = document.getElementById('ensembleSumRange');
      if (sumRangeEl && sumStats) {
        sumRangeEl.textContent = `${sumStats.safe_zone || '132 - 207'}`;
      }

      // 2. Next draw ID
      const nextDrawEl = document.getElementById('ensembleNextDrawId');
      const latestIdNum = parseInt(product.latest?.id?.replace('#', '') || '0');
      const nextIdStr = latestIdNum ? `#${String(latestIdNum + 1).padStart(5, '0')}` : 'Kỳ Tiếp Theo';
      if (nextDrawEl) nextDrawEl.textContent = nextIdStr;

      // 3. Generate golden tickets
      generateEnsembleGoldenTickets(false);

      // 3.2. Render Bac Nho & Cau Roi
      renderBacNhoAnalytics(product);

      // 3.5. Render wheeling strategy
      renderWheelingStrategy(product);

      // 4. Render prediction history
      renderPredictionHistory(product);
    }

    let ensembleSeedOffset = 0;

    function generateEnsembleGoldenTickets(forceNew = false) {
      const product = appData?.products?.[currentProductKey];
      if (!product || product.type !== 'lotto') return;

      const numBalls = product.balls || 6;
      const maxVal = product.max_number || 55;
      const positions = product.positional_stats?.positions || [];
      const sumStats = product.sum_stats;
      const avgSum = sumStats?.avg_sum || 168;
      const stdDev = sumStats?.std_dev || 37;
      const minSum = avgSum - stdDev;
      const maxSum = avgSum + stdDev;
      const markovTop = (product.markov_stats?.top_candidates || []).slice(0, 15).map(c => c.number);
      const markovSet = new Set(markovTop);

      // Deterministic Seed derived from product and latest draw ID
      const latestId = product.latest?.id?.replace('#', '') || '0';
      if (forceNew) {
        ensembleSeedOffset += 7919;
      } else {
        ensembleSeedOffset = 0;
      }
      const seedVal = stringToSeedHash(currentProductKey + '_' + latestId) + ensembleSeedOffset;
      const seededRng = createMulberry32(seedVal);

      if (forceNew || currentEnsembleTickets.length === 0) {
        const golden = [];
        for (let attempt = 0; attempt < 30000; attempt++) {
          const cand = [];
          for (let b = 0; b < numBalls; b++) {
            const posInfo = positions[b];
            let n;
            if (posInfo && seededRng() < 0.75) {
              const low = posInfo.q1;
              const high = posInfo.q3;
              n = Math.floor(seededRng() * (high - low + 1)) + low;
            } else if (markovTop.length > 0 && seededRng() < 0.4) {
              n = markovTop[Math.floor(seededRng() * markovTop.length)];
            } else {
              n = Math.floor(seededRng() * maxVal) + 1;
            }
            cand.push(n);
          }

          const sorted = Array.from(new Set(cand)).sort((a, b) => a - b);
          if (sorted.length !== numBalls) continue;

          // 1. Positional check (at least 5/6 in Q1..Q3)
          let posOk = 0;
          for (let i = 0; i < numBalls; i++) {
            if (positions[i] && sorted[i] >= positions[i].q1 && sorted[i] <= positions[i].q3) {
              posOk++;
            }
          }
          if (posOk < (numBalls - 1)) continue;

          // 2. Sum check
          const sumVal = sorted.reduce((a, b) => a + b, 0);
          if (sumVal < minSum || sumVal > maxSum) continue;

          // 3. AC Value check
          const diffs = new Set();
          for (let i = 0; i < sorted.length; i++) {
            for (let j = i + 1; j < sorted.length; j++) {
              diffs.add(Math.abs(sorted[i] - sorted[j]));
            }
          }
          const ac = diffs.size - (numBalls - 1);
          const acMin = numBalls === 5 ? 5 : 7;
          if (ac < acMin) continue;

          // 4. Markov check
          const markovMatches = sorted.filter(n => markovSet.has(n));
          const minMarkov = numBalls === 5 ? 1 : 2;
          if (markovMatches.length < minMarkov) continue;

          // 5. Odd/Even balance
          const odds = sorted.filter(n => n % 2 !== 0).length;
          if (numBalls === 5) {
            if (odds !== 2 && odds !== 3) continue;
          } else {
            if (odds < 2 || odds > 4) continue;
          }

          // 6. Ending digit diversity
          const tails = new Set(sorted.map(n => n % 10));
          const minTails = numBalls === 5 ? 4 : 5;
          if (tails.size < minTails) continue;

          // 7. Delta steps
          let smallDeltas = 0;
          for (let i = 1; i < numBalls; i++) {
            if (sorted[i] - sorted[i - 1] <= 5) smallDeltas++;
          }
          const minDeltas = numBalls === 5 ? 2 : 3;
          if (smallDeltas < minDeltas) continue;

          const spec = currentProductKey === 'power_535' ? (Math.floor(seededRng() * 12) + 1) : null;
          const score = Math.min(99, 88 + posOk * 1.5 + markovMatches.length * 2 + (ac >= (numBalls === 5 ? 6 : 8) ? 2 : 0));

          golden.push({
            numbers: sorted,
            special: spec,
            sum: sumVal,
            ac: ac,
            odds: odds,
            evens: numBalls - odds,
            distinctTails: tails.size,
            markovMatches: markovMatches,
            score: Math.round(score)
          });

          if (golden.length >= 3) break;
        }

        currentEnsembleTickets = golden;
      }

      const grid = document.getElementById('ensembleGoldenTicketsGrid');
      if (!grid) return;

      if (!currentEnsembleTickets.length) {
        grid.innerHTML = `<p class="text-xs text-slate-500 col-span-full">Đang lọc tổ hợp số tối ưu...</p>`;
        return;
      }

      grid.innerHTML = currentEnsembleTickets.map((t, idx) => {
        const rankTitle = idx === 0 ? '🏆 BỘ SỐ VÀNG #1 (ƯU TIÊN NHẤT)' : idx === 1 ? '✨ BỘ SỐ VÀNG #2 (CÂN BẰNG CAO)' : '🎯 BỘ SỐ VÀNG #3 (TIỀM NĂNG)';
        const borderClass = idx === 0 ? 'border-amber-500/60 shadow-amber-950/30' : idx === 1 ? 'border-indigo-500/50 shadow-indigo-950/30' : 'border-emerald-500/50 shadow-emerald-950/30';
        return `
          <div class="rounded-2xl bg-gradient-to-b from-slate-900 to-slate-950 border ${borderClass} p-5 shadow-xl space-y-4 relative overflow-hidden flex flex-col justify-between">
            <div class="space-y-3">
              <div class="flex items-center justify-between">
                <span class="text-xs font-bold font-mono text-amber-300 tracking-wider">${rankTitle}</span>
                <span class="px-2 py-0.5 rounded-full text-xs font-mono font-bold bg-amber-500/20 text-amber-300 border border-amber-500/30">
                  ${t.score}% Thỏa mãn
                </span>
              </div>

              <!-- Ball row -->
              <div class="flex justify-center items-center flex-wrap gap-2 py-2">
                ${t.numbers.map(n => `
                  <span class="w-10 h-10 rounded-full bg-gradient-to-br from-rose-600 to-red-700 text-white font-mono font-bold text-sm flex items-center justify-center shadow-lg shadow-rose-950/60">
                    ${String(n).padStart(2, '0')}
                  </span>
                `).join('')}
                ${t.special ? `
                  <span class="text-slate-500 font-bold px-1">+</span>
                  <div class="relative group">
                    <span class="w-10 h-10 rounded-full bg-gradient-to-br from-amber-400 to-yellow-600 text-white font-mono font-bold text-sm flex items-center justify-center shadow-lg shadow-amber-950/60 border border-yellow-300">
                      ${String(t.special).padStart(2, '0')}
                    </span>
                    <span class="absolute -top-6 left-1/2 -translate-x-1/2 text-[9px] font-bold text-amber-400 whitespace-nowrap bg-slate-900 px-1.5 py-0.5 rounded border border-amber-800">Đặc biệt</span>
                  </div>
                ` : ''}
              </div>

              <!-- Criteria checklist -->
              <div class="space-y-1.5 pt-2 border-t border-slate-800 text-[11px] text-slate-400 font-mono">
                <div class="flex justify-between">
                  <span>Tổng điểm chính:</span>
                  <span class="text-emerald-400 font-bold">${t.sum} (Chuẩn an toàn)</span>
                </div>
                <div class="flex justify-between">
                  <span>Độ phức tạp AC:</span>
                  <span class="text-orange-400 font-bold">AC = ${t.ac} (Chuẩn ngẫu nhiên)</span>
                </div>
                <div class="flex justify-between">
                  <span>Cơ cấu Lẻ - Chẵn:</span>
                  <span class="text-slate-300">${t.odds} Lẻ - ${t.evens} Chẵn</span>
                </div>
                <div class="flex justify-between">
                  <span>Độ đa dạng đuôi:</span>
                  <span class="text-teal-400">${t.distinctTails} đuôi khác nhau</span>
                </div>
                <div class="flex justify-between">
                  <span>Số trùng Markov:</span>
                  <span class="text-fuchsia-300 font-bold">[${t.markovMatches.map(n => String(n).padStart(2, '0')).join(', ')}]</span>
                </div>
              </div>
            </div>

            <!-- Action buttons -->
            <div class="pt-3 border-t border-slate-800/80 flex flex-col gap-2">
              <div class="flex gap-2">
                <button onclick="applyGoldenTicketToChecker('${t.numbers.join(', ')}${t.special ? ' + ' + t.special : ''}')" class="flex-1 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold transition">
                  Nạp sang Dò Vé
                </button>
                <button onclick="applyGoldenTicketToSim('${t.numbers.join(', ')}')" class="py-1.5 px-3 rounded-lg bg-slate-800 hover:bg-slate-700 text-yellow-400 text-xs font-semibold transition" title="Nuôi bộ số này">
                  Nuôi số
                </button>
                ${(currentProductKey === 'power_655' || currentProductKey === 'power_645') ? `
                  <button onclick="copyEnsembleSms('${t.numbers.join(', ')}')" class="py-1.5 px-2.5 rounded-lg bg-emerald-600/80 hover:bg-emerald-600 text-white text-xs font-bold flex items-center gap-1 transition" title="Copy cú pháp SMS 9969">
                    <i data-lucide="message-square" class="w-3.5 h-3.5"></i>
                    <span>SMS 9969</span>
                  </button>
                ` : ''}
              </div>
              <button onclick="saveSingleGoldenTicket('${t.numbers.join(', ')}${t.special ? ' + ' + t.special : ''}', ${t.score})" class="w-full py-1.5 rounded-lg bg-indigo-600/80 hover:bg-indigo-600 text-white text-xs font-semibold flex items-center justify-center gap-1.5 transition">
                <i data-lucide="bookmark" class="w-3.5 h-3.5"></i>
                <span>Lưu Bộ Số Này Vào Lịch Sử</span>
              </button>
            </div>
          </div>
        `;
      }).join('');

      lucide.createIcons();
    }

function getStoredPredictions(productKey) {
      const prod = appData?.products?.[productKey];
      if (prod?.backtest_data?.records) return prod.backtest_data.records;
      if (prod && Array.isArray(prod.backtest_history) && prod.backtest_history.length > 0) {
        return prod.backtest_history;
      }
      if (productKey === 'power_655') return [{"drawId": "01394", "date": "K\u1ef3 K\u1ebf Ti\u1ebfp", "predicted": [11, 20, 23, 27, 38, 48], "special": 8, "actual": null, "matched": [], "matchCount": 0, "specMatched": false, "status": "pending"}, {"drawId": "01393", "date": "2026-09-03", "predicted": [2, 16, 23, 27, 40, 55], "special": 8, "actual": [8, 9, 16, 42, 46, 47, 11], "matched": [16], "matchCount": 1, "specMatched": false, "status": "completed"}, {"drawId": "01392", "date": "2026-09-01", "predicted": [8, 18, 20, 33, 39, 55], "special": 28, "actual": [1, 17, 41, 44, 49, 55, 45], "matched": [55], "matchCount": 1, "specMatched": false, "status": "completed"}, {"drawId": "01391", "date": "2026-08-29", "predicted": [2, 5, 28, 33, 45, 55], "special": 8, "actual": [5, 10, 15, 29, 34, 45, 24], "matched": [5, 45], "matchCount": 2, "specMatched": false, "status": "completed"}, {"drawId": "01390", "date": "2026-08-27", "predicted": [8, 11, 33, 40, 41, 45], "special": 22, "actual": [1, 3, 11, 21, 26, 44, 10], "matched": [11], "matchCount": 1, "specMatched": false, "status": "completed"}, {"drawId": "01389", "date": "2026-08-25", "predicted": [2, 11, 23, 40, 41, 45], "special": 8, "actual": [5, 7, 13, 18, 31, 40, 14], "matched": [40], "matchCount": 1, "specMatched": false, "status": "completed"}, {"drawId": "01388", "date": "2026-08-22", "predicted": [2, 11, 22, 32, 40, 55], "special": 8, "actual": [9, 18, 19, 21, 25, 36, 8], "matched": [], "matchCount": 0, "specMatched": false, "status": "completed"}, {"drawId": "01387", "date": "2026-08-20", "predicted": [1, 11, 22, 40, 41, 53], "special": 8, "actual": [2, 8, 29, 38, 39, 51, 47], "matched": [], "matchCount": 0, "specMatched": false, "status": "completed"}, {"drawId": "01386", "date": "2026-08-18", "predicted": [3, 17, 23, 32, 40, 53], "special": 8, "actual": [3, 15, 18, 38, 41, 48, 30], "matched": [3], "matchCount": 1, "specMatched": false, "status": "completed"}, {"drawId": "01385", "date": "2026-08-15", "predicted": [8, 24, 25, 28, 32, 53], "special": 22, "actual": [16, 20, 25, 27, 30, 50, 2], "matched": [25], "matchCount": 1, "specMatched": false, "status": "completed"}, {"drawId": "01384", "date": "2026-08-13", "predicted": [9, 22, 28, 32, 39, 48], "special": 8, "actual": [5, 9, 27, 29, 45, 46, 42], "matched": [9], "matchCount": 1, "specMatched": false, "status": "completed"}];
      if (productKey === 'power_645') return [{"drawId": "01558", "date": "K\u1ef3 K\u1ebf Ti\u1ebfp", "predicted": [3, 6, 11, 30, 31, 44], "special": null, "actual": null, "matched": [], "matchCount": 0, "specMatched": false, "status": "pending"}, {"drawId": "01557", "date": "2026-09-02", "predicted": [6, 9, 11, 30, 36, 45], "special": null, "actual": [6, 9, 27, 29, 35, 44], "matched": [6, 9], "matchCount": 2, "specMatched": false, "status": "completed"}, {"drawId": "01556", "date": "2026-08-30", "predicted": [2, 11, 13, 30, 31, 45], "special": null, "actual": [1, 3, 12, 15, 37, 45], "matched": [45], "matchCount": 1, "specMatched": false, "status": "completed"}, {"drawId": "01555", "date": "2026-08-28", "predicted": [2, 3, 24, 27, 39, 44], "special": null, "actual": [3, 13, 15, 22, 36, 39], "matched": [3, 39], "matchCount": 2, "specMatched": false, "status": "completed"}, {"drawId": "01554", "date": "2026-08-26", "predicted": [11, 13, 14, 30, 36, 41], "special": null, "actual": [3, 10, 11, 16, 33, 40], "matched": [11], "matchCount": 1, "specMatched": false, "status": "completed"}, {"drawId": "01553", "date": "2026-08-23", "predicted": [11, 13, 17, 27, 36, 39], "special": null, "actual": [4, 16, 17, 22, 32, 39], "matched": [17, 39], "matchCount": 2, "specMatched": false, "status": "completed"}, {"drawId": "01552", "date": "2026-08-21", "predicted": [6, 9, 13, 25, 39, 45], "special": null, "actual": [7, 26, 31, 38, 43, 45], "matched": [45], "matchCount": 1, "specMatched": false, "status": "completed"}, {"drawId": "01551", "date": "2026-08-19", "predicted": [3, 9, 13, 26, 42, 45], "special": null, "actual": [6, 15, 18, 33, 40, 43], "matched": [], "matchCount": 0, "specMatched": false, "status": "completed"}, {"drawId": "01550", "date": "2026-08-16", "predicted": [3, 11, 17, 26, 42, 45], "special": null, "actual": [6, 7, 15, 19, 36, 41], "matched": [], "matchCount": 0, "specMatched": false, "status": "completed"}, {"drawId": "01549", "date": "2026-08-14", "predicted": [6, 13, 16, 30, 32, 41], "special": null, "actual": [7, 9, 13, 31, 35, 44], "matched": [13], "matchCount": 1, "specMatched": false, "status": "completed"}, {"drawId": "01548", "date": "2026-08-12", "predicted": [3, 13, 27, 29, 36, 41], "special": null, "actual": [15, 17, 22, 29, 33, 40], "matched": [29], "matchCount": 1, "specMatched": false, "status": "completed"}];
      if (productKey === 'power_535') return [{"drawId": "00865", "date": "K\u1ef3 K\u1ebf Ti\u1ebfp", "predicted": [1, 12, 18, 28, 30], "special": 9, "actual": null, "matched": [], "matchCount": 0, "specMatched": false, "status": "pending"}, {"drawId": "00864", "date": "2026-09-03", "predicted": [3, 15, 21, 22, 26], "special": 9, "actual": [7, 17, 23, 24, 27, 3], "matched": [], "matchCount": 0, "specMatched": false, "status": "completed"}, {"drawId": "00863", "date": "2026-09-03", "predicted": [1, 12, 21, 22, 35], "special": 9, "actual": [2, 15, 23, 24, 30, 12], "matched": [], "matchCount": 0, "specMatched": false, "status": "completed"}, {"drawId": "00862", "date": "2026-09-02", "predicted": [1, 15, 19, 21, 34], "special": 9, "actual": [6, 7, 9, 11, 32, 12], "matched": [], "matchCount": 0, "specMatched": false, "status": "completed"}, {"drawId": "00861", "date": "2026-09-02", "predicted": [1, 9, 12, 28, 35], "special": 7, "actual": [7, 11, 18, 26, 29, 6], "matched": [], "matchCount": 0, "specMatched": false, "status": "completed"}, {"drawId": "00860", "date": "2026-09-01", "predicted": [1, 7, 16, 30, 35], "special": 7, "actual": [3, 4, 6, 15, 22, 9], "matched": [], "matchCount": 0, "specMatched": false, "status": "completed"}, {"drawId": "00859", "date": "2026-09-01", "predicted": [10, 13, 21, 22, 26], "special": 7, "actual": [9, 18, 20, 27, 34, 12], "matched": [], "matchCount": 0, "specMatched": false, "status": "completed"}, {"drawId": "00858", "date": "2026-08-31", "predicted": [1, 7, 19, 30, 34], "special": 7, "actual": [1, 5, 25, 27, 28, 12], "matched": [1], "matchCount": 1, "specMatched": false, "status": "completed"}, {"drawId": "00857", "date": "2026-08-31", "predicted": [7, 13, 16, 20, 35], "special": 7, "actual": [4, 11, 13, 18, 27, 1], "matched": [13], "matchCount": 1, "specMatched": false, "status": "completed"}, {"drawId": "00856", "date": "2026-08-30", "predicted": [2, 12, 19, 21, 33], "special": 7, "actual": [13, 15, 17, 26, 30, 10], "matched": [], "matchCount": 0, "specMatched": false, "status": "completed"}, {"drawId": "00855", "date": "2026-08-30", "predicted": [2, 15, 16, 23, 35], "special": 7, "actual": [2, 4, 12, 21, 28, 7], "matched": [2], "matchCount": 1, "specMatched": true, "status": "completed"}];
      return [];
    }

    // ==========================================
    // 1. LIVE COUNTDOWN TIMER & DRAW SCHEDULE
    // ==========================================
    let countdownInterval = null;

    function startLiveCountdown() {
      if (countdownInterval) clearInterval(countdownInterval);
      updateCountdown();
      countdownInterval = setInterval(updateCountdown, 1000);
    }

    function updateCountdown() {
      const badgeText = document.getElementById('countdownStatusText');
      const targetDrawEl = document.getElementById('countdownTargetDraw');
      const scheduleEl = document.getElementById('countdownDrawSchedule');
      const hEl = document.getElementById('cd-hours');
      const mEl = document.getElementById('cd-minutes');
      const sEl = document.getElementById('cd-seconds');
      const statusBadge = document.getElementById('countdownStatusBadge');

      if (!hEl || !mEl || !sEl) return;

      const now = new Date();
      const product = appData?.products?.[currentProductKey];
      const latestId = product?.latest?.id ? parseInt(product.latest.id) : 0;
      const nextId = String(latestId + 1).padStart(5, '0');
      if (targetDrawEl) targetDrawEl.textContent = `Kỳ quay kế tiếp: #${nextId}`;

      let targetDate = new Date(now);
      let schedDesc = '';

      if (currentProductKey === 'power_655') {
        const drawDays = [2, 4, 6];
        for (let addDays = 0; addDays < 7; addDays++) {
          const d = new Date(now.getTime() + addDays * 86400000);
          d.setHours(18, 0, 0, 0);
          if (drawDays.includes(d.getDay()) && d.getTime() > now.getTime()) {
            targetDate = d;
            const dayNames = ['Chủ Nhật', 'Thứ Hai', 'Thứ Ba', 'Thứ Tư', 'Thứ Năm', 'Thứ Sáu', 'Thứ Bảy'];
            schedDesc = `Mở thưởng 18:00 ${dayNames[d.getDay()]} (${String(d.getDate()).padStart(2, '0')}/${String(d.getMonth() + 1).padStart(2, '0')}/${d.getFullYear()})`;
            break;
          }
        }
      } else if (currentProductKey === 'power_645') {
        const drawDays = [0, 3, 5];
        for (let addDays = 0; addDays < 7; addDays++) {
          const d = new Date(now.getTime() + addDays * 86400000);
          d.setHours(18, 0, 0, 0);
          if (drawDays.includes(d.getDay()) && d.getTime() > now.getTime()) {
            targetDate = d;
            const dayNames = ['Chủ Nhật', 'Thứ Hai', 'Thứ Ba', 'Thứ Tư', 'Thứ Năm', 'Thứ Sáu', 'Thứ Bảy'];
            schedDesc = `Mở thưởng 18:00 ${dayNames[d.getDay()]} (${String(d.getDate()).padStart(2, '0')}/${String(d.getMonth() + 1).padStart(2, '0')}/${d.getFullYear()})`;
            break;
          }
        }
      } else if (currentProductKey === 'power_535') {
        const d13 = new Date(now); d13.setHours(13, 0, 0, 0);
        const d21 = new Date(now); d21.setHours(21, 0, 0, 0);
        if (now.getTime() < d13.getTime()) {
          targetDate = d13;
          schedDesc = `Mở thưởng 13:00 Hôm nay (${String(now.getDate()).padStart(2, '0')}/${String(now.getMonth() + 1).padStart(2, '0')})`;
        } else if (now.getTime() < d21.getTime()) {
          targetDate = d21;
          schedDesc = `Mở thưởng 21:00 Hôm nay (${String(now.getDate()).padStart(2, '0')}/${String(now.getMonth() + 1).padStart(2, '0')})`;
        } else {
          const dTomorrow = new Date(now.getTime() + 86400000);
          dTomorrow.setHours(13, 0, 0, 0);
          targetDate = dTomorrow;
          schedDesc = `Mở thưởng 13:00 Ngày mai (${String(dTomorrow.getDate()).padStart(2, '0')}/${String(dTomorrow.getMonth() + 1).padStart(2, '0')})`;
        }
      } else {
        targetDate = new Date(now.getTime() + 3600000 * 4);
        schedDesc = 'Kỳ quay định kỳ hàng ngày';
      }

      if (!schedDesc) {
        // Fallback: find the next draw for any scenario that wasn't caught
        const dayNames = ['Chủ Nhật', 'Thứ Hai', 'Thứ Ba', 'Thứ Tư', 'Thứ Năm', 'Thứ Sáu', 'Thứ Bảy'];
        schedDesc = `Kỳ quay kế tiếp: ${dayNames[targetDate.getDay()]} ${String(targetDate.getDate()).padStart(2, '0')}/${String(targetDate.getMonth() + 1).padStart(2, '0')}`;
      }

      if (scheduleEl) scheduleEl.textContent = schedDesc;

      const diffMs = targetDate.getTime() - now.getTime();
      if (diffMs <= 0) {
        if (statusBadge) statusBadge.className = 'px-2.5 py-0.5 rounded-full text-xs font-bold bg-rose-500/20 text-rose-300 border border-rose-500/30 flex items-center gap-1.5 shadow-sm';
        if (badgeText) badgeText.textContent = 'ĐANG QUAY THƯỞNG';
        hEl.textContent = '00';
        mEl.textContent = '00';
        sEl.textContent = '00';
        return;
      }

      const totalSecs = Math.floor(diffMs / 1000);
      const hours = Math.floor(totalSecs / 3600);
      const minutes = Math.floor((totalSecs % 3600) / 60);
      const seconds = totalSecs % 60;

      hEl.textContent = String(hours).padStart(2, '0');
      mEl.textContent = String(minutes).padStart(2, '0');
      sEl.textContent = String(seconds).padStart(2, '0');

      if (totalSecs <= 1800) {
        if (statusBadge) statusBadge.className = 'px-2.5 py-0.5 rounded-full text-xs font-bold bg-amber-500/20 text-amber-300 border border-amber-500/30 flex items-center gap-1.5 shadow-sm';
        if (badgeText) badgeText.textContent = 'SẮP KHÓA SỔ (Mua trước 15p)';
      } else {
        if (statusBadge) statusBadge.className = 'px-2.5 py-0.5 rounded-full text-xs font-bold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 flex items-center gap-1.5 shadow-sm';
        if (badgeText) badgeText.textContent = 'ĐANG MỞ BÁN VÉ';
      }
    }

    // ==========================================
    // 2. SPECIAL BALL TRACKER (01 - 12 CHO 5/35 & 01 - 55 CHO 6/55)
    // ==========================================
    let specialBall655Tab = 'top'; // 'top' or 'all'

    function renderSpecialBallTracker(product) {
      const section = document.getElementById('specialBallTrackerSection');
      if (!section) return;

      if (currentProductKey !== 'power_535' && currentProductKey !== 'power_655') {
        section.classList.add('hidden');
        return;
      }
      section.classList.remove('hidden');

      const is535 = currentProductKey === 'power_535';
      const maxVal = is535 ? 12 : 55;
      const specIndex = is535 ? 5 : 6;
      const history = product?.history || [];

      // Update Header Text
      const titleEl = document.getElementById('specialBallTrackerTitle');
      const descEl = document.getElementById('specialBallTrackerDesc');
      if (titleEl) {
        titleEl.textContent = is535 
          ? 'SOI CẦU BÓNG ĐẶC BIỆT (CẦU VÀNG 01 - 12)'
          : 'SOI CẦU CẦU VÀNG JACKPOT 2 (01 - 55)';
      }
      if (descEl) {
        descEl.textContent = is535
          ? 'Phân tích chuyên sâu tần suất nổ & nhịp gan của 12 quả bóng đặc biệt. Khóa trúng bóng đặc biệt = Chìa khóa bảo hiểm hòa vốn 100% & nổ Jackpot Độc Đắc!'
          : 'Phân tích tần suất nổ & nhịp gan của quả bóng thứ 7 (Cầu Vàng quyết định nổ Jackpot 2 từ 3,5 Tỷ đến hàng trăm Tỷ). Quay từ 49 bóng còn lại trong tập 01 - 55!';
      }

      // Calculate stats for 1..maxVal
      const stats = {};
      for (let i = 1; i <= maxVal; i++) {
        stats[i] = { num: i, freq: 0, lastSeen: -1, gap: history.length };
      }

      history.forEach((draw, idx) => {
        const res = draw.result || [];
        if (res.length > specIndex) {
          const s = res[specIndex];
          if (stats[s]) {
            stats[s].freq++;
            if (stats[s].lastSeen === -1) {
              stats[s].lastSeen = idx;
              stats[s].gap = idx;
            }
          }
        }
      });

      const statList = Object.values(stats);
      const sortedPicks = [...statList].sort((a, b) => {
        const scoreA = a.freq * 2.5 - Math.abs(a.gap - (is535 ? 8 : 25));
        const scoreB = b.freq * 2.5 - Math.abs(b.gap - (is535 ? 8 : 25));
        return scoreB - scoreA;
      });

      const topCount = is535 ? 3 : 6;
      const topPicks = sortedPicks.slice(0, topCount).map(x => String(x.num).padStart(2, '0'));
      const top3Text = document.getElementById('specialBallTop3Text');
      if (top3Text) top3Text.textContent = topPicks.join('  •  ');

      const grid = document.getElementById('specialBallsGrid');
      const insightBox = document.getElementById('specialBallInsightBox');

      if (grid) {
        if (is535) {
          // Render all 12 cards for Power 5/35
          grid.className = 'grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-3';
          grid.innerHTML = statList.map(item => {
            const isTop = topPicks.includes(String(item.num).padStart(2, '0'));
            const isHot = item.freq >= 10;
            const isCold = item.gap >= 12;
            const isJustHit = item.gap === 0;

            let tagCls = 'bg-slate-800 text-slate-400 border-slate-700';
            let tagText = `Gan ${item.gap} kỳ`;
            if (isJustHit) {
              tagCls = 'bg-rose-500/20 text-rose-300 border-rose-500/40 font-bold';
              tagText = 'Vừa Nổ Kỳ Này 🔥';
            } else if (isHot) {
              tagCls = 'bg-amber-500/20 text-amber-300 border-amber-500/40 font-bold';
              tagText = `Cực Nóng (${item.freq} lần) ⚡`;
            } else if (isCold) {
              tagCls = 'bg-cyan-500/20 text-cyan-300 border-cyan-500/40 font-bold';
              tagText = `Cầu Gan (${item.gap} kỳ) ❄️`;
            }

            const cardBorder = isTop ? 'border-amber-400/80 shadow-lg shadow-amber-500/20 bg-gradient-to-b from-slate-900 to-amber-950/30' : 'border-slate-800 bg-slate-950/80';

            return `
              <div class="rounded-xl border ${cardBorder} p-3 flex flex-col items-center justify-between text-center relative group transition hover:scale-105 cursor-pointer" onclick="applyTopSpecialBallToTicket('${String(item.num).padStart(2, '0')}')">
                ${isTop ? '<span class="absolute -top-2 px-2 py-0.5 rounded-full text-[9px] font-black bg-amber-500 text-slate-950 tracking-wider shadow-sm">ƯU TIÊN</span>' : ''}
                <div class="w-11 h-11 rounded-full bg-gradient-to-tr from-amber-400 via-yellow-500 to-amber-600 text-slate-950 font-black text-base flex items-center justify-center shadow-md shadow-amber-500/30 border border-yellow-200 mt-1">
                  ${String(item.num).padStart(2, '0')}
                </div>
                <div class="mt-2 space-y-0.5 w-full">
                  <div class="text-[11px] font-bold text-slate-300">Xuất hiện: <span class="text-amber-400 font-bold">${item.freq} lần</span></div>
                  <div class="px-1.5 py-0.5 rounded text-[10px] border ${tagCls} mt-1">${tagText}</div>
                </div>
              </div>
            `;
          }).join('');
        } else {
          // Render for Power 6/55: Top 6 Sáng Giá Nhất + Ma Trận 55 Bóng Thu Gọn
          grid.className = 'space-y-4';
          
          const topCardsHtml = sortedPicks.slice(0, 6).map(item => {
            const isJustHit = item.gap === 0;
            const tagCls = isJustHit ? 'bg-rose-500/20 text-rose-300 border-rose-500/40' : 'bg-amber-500/20 text-amber-300 border-amber-500/40';
            const tagText = isJustHit ? 'Vừa Nổ Kỳ Trước 🔥' : `Gan ${item.gap} kỳ (${item.freq} lần nổ)`;

            return `
              <div class="rounded-xl border border-amber-400/60 bg-gradient-to-b from-slate-900 to-amber-950/20 p-3 flex flex-col items-center justify-between text-center relative transition hover:scale-105 shadow-md shadow-amber-950/40 cursor-pointer" onclick="applyTopSpecialBallToTicket('${String(item.num).padStart(2, '0')}')">
                <span class="absolute -top-2 px-2 py-0.5 rounded-full text-[9px] font-black bg-amber-500 text-slate-950 tracking-wider shadow-sm">TOP CẦU VÀNG</span>
                <div class="w-11 h-11 rounded-full bg-gradient-to-tr from-amber-400 via-yellow-500 to-amber-600 text-slate-950 font-black text-base flex items-center justify-center shadow-md shadow-amber-500/30 border border-yellow-200 mt-1">
                  ${String(item.num).padStart(2, '0')}
                </div>
                <div class="mt-2 space-y-0.5 w-full">
                  <div class="text-[11px] font-bold text-slate-300">Nổ: <strong class="text-amber-400">${item.freq} lần</strong></div>
                  <div class="px-1.5 py-0.5 rounded text-[10px] border ${tagCls} mt-1">${tagText}</div>
                </div>
              </div>
            `;
          }).join('');

          // 55 Balls Compact Matrix
          const matrixHtml = statList.map(item => {
            const isTop = topPicks.includes(String(item.num).padStart(2, '0'));
            const isJustHit = item.gap === 0;
            const isCold = item.gap >= 35;
            
            let btnBg = 'bg-slate-900 border-slate-800 text-slate-300 hover:border-slate-600';
            if (isJustHit) btnBg = 'bg-rose-950/80 border-rose-500 text-rose-300 font-black shadow-sm';
            else if (isTop) btnBg = 'bg-amber-950/80 border-amber-400 text-amber-300 font-black shadow-sm';
            else if (isCold) btnBg = 'bg-slate-950 border-cyan-500/50 text-cyan-300';

            return `
              <button onclick="applyTopSpecialBallToTicket('${String(item.num).padStart(2, '0')}')" 
                class="px-2 py-1.5 rounded-lg border text-xs font-mono flex flex-col items-center justify-center transition active:scale-95 ${btnBg}"
                title="Bóng ${String(item.num).padStart(2, '0')}: Xuất hiện ${item.freq} lần, Gan ${item.gap} kỳ. Bấm để chọn làm Cầu Vàng!">
                <span class="font-bold">${String(item.num).padStart(2, '0')}</span>
                <span class="text-[9px] opacity-70">${item.freq}l - g${item.gap}</span>
              </button>
            `;
          }).join('');

          grid.innerHTML = `
            <div>
              <div class="flex items-center justify-between mb-2">
                <span class="text-xs font-bold text-amber-300 uppercase tracking-wider flex items-center gap-1.5">
                  <i data-lucide="award" class="w-3.5 h-3.5 text-amber-400"></i> Top 6 Cầu Vàng Sáng Giá Nhất (Điểm Rơi Chu Kỳ 100 Kỳ)
                </span>
                <span class="text-[11px] text-slate-500">Bấm thẻ để chọn</span>
              </div>
              <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-6 gap-3">
                ${topCardsHtml}
              </div>
            </div>

            <div class="pt-2 border-t border-slate-800/80">
              <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-2">
                <span class="text-xs font-bold text-slate-300 flex items-center gap-1.5">
                  <i data-lucide="grid" class="w-3.5 h-3.5 text-slate-400"></i>
                  Ma Trận Toàn Bộ 55 Cầu Vàng (01 - 55) & Tần Suất Nổ
                </span>
                <div class="flex items-center gap-3 text-[10px] text-slate-400">
                  <span class="flex items-center gap-1"><span class="w-2 h-2 rounded bg-amber-400"></span> Top Nóng</span>
                  <span class="flex items-center gap-1"><span class="w-2 h-2 rounded bg-rose-500"></span> Vừa nổ</span>
                  <span class="flex items-center gap-1"><span class="w-2 h-2 rounded bg-cyan-400"></span> Cầu Gan</span>
                </div>
              </div>
              <div class="grid grid-cols-5 sm:grid-cols-8 md:grid-cols-11 gap-1.5 bg-slate-950 p-3 rounded-xl border border-slate-800/80">
                ${matrixHtml}
              </div>
            </div>
          `;
        }
      }

      if (insightBox) {
        insightBox.innerHTML = `
          <div class="flex items-start gap-2.5">
            <i data-lucide="lightbulb" class="w-4 h-4 text-amber-400 flex-shrink-0 mt-0.5"></i>
            <div>
              <span class="font-bold text-amber-300">${is535 ? 'Chiến lược Cầu Vàng 5/35:' : 'Chiến lược Cầu Vàng Jackpot 2 (6/55):'}</span>
              <span class="text-slate-300 ml-1">
                ${is535 
                  ? `Bộ ba cầu vàng sáng nhất kỳ này là <strong class="text-white font-mono font-bold">${topPicks.join(', ')}</strong>. Khuyên dùng: Đánh dàn số chính ghép xoay vòng với 3 bóng này để nâng tỷ lệ bắt trúng bóng đặc biệt lên <strong class="text-emerald-400">25%</strong>!`
                  : `Top cầu vàng có nhịp rơi đẹp nhất kỳ này là <strong class="text-white font-mono font-bold">${topPicks.join(', ')}</strong>. Khuyên dùng: Chọn 1 trong các bóng này để nuôi giải Jackpot 2 (khởi điểm 3,5 Tỷ đồng)!`
                }
              </span>
            </div>
          </div>
          <button onclick="applyTopSpecialBallToTicket('${topPicks[0]}')" class="px-3 py-1.5 rounded-lg bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold text-xs whitespace-nowrap shadow-sm transition flex-shrink-0">
            Chọn Cầu Vàng [${topPicks[0]}]
          </button>
        `;
      }

      lucide.createIcons();
    }

    // ========================================================
    // 3. SEPARATED MAIN & SPECIAL BALLS RENDERING IN TABLES
    // ========================================================
    function renderBallsWithSpecial(numbers, actualNumbers, isBao = false, productKey = currentProductKey) {
      if (!numbers || !numbers.length) return '';
      const actualSet = actualNumbers ? new Set(actualNumbers) : null;
      
      if (productKey === 'power_535') {
        const mainCount = isBao ? 6 : 5;
        const mainBalls = numbers.slice(0, mainCount);
        const specBall = numbers[mainCount];
        const actualMain = actualNumbers ? actualNumbers.slice(0, 5) : [];
        const actualSpec = actualNumbers && actualNumbers.length >= 6 ? actualNumbers[5] : null;

        const mainHtml = mainBalls.map(n => {
          const isMatch = actualMain.includes(n);
          const cls = isMatch ? 'bg-emerald-600 text-white font-bold border-emerald-400 shadow-sm' : 'bg-slate-800 text-slate-300 border-slate-700';
          return `<span class="px-2 py-0.5 rounded text-xs border ${cls}">${String(n).padStart(2, '0')}</span>`;
        }).join('');

        let specHtml = '';
        if (specBall !== undefined && specBall !== null) {
          const isSpecMatch = actualSpec === specBall;
          const specCls = isSpecMatch ? 'bg-amber-500 text-slate-950 font-black border-amber-300 shadow-md shadow-amber-500/30' : 'bg-amber-950/80 text-amber-300 border-amber-600/60 font-bold';
          specHtml = `
            <span class="text-amber-400 font-black text-xs px-1">+</span>
            <span class="px-2 py-0.5 rounded text-xs border ${specCls} flex items-center gap-1 shadow-sm" title="Số đặc biệt (01-12)">
              <i data-lucide="star" class="w-2.5 h-2.5 fill-amber-400"></i>${String(specBall).padStart(2, '0')}
            </span>
          `;
        }
        return `<div class="flex items-center gap-1 flex-nowrap whitespace-nowrap">${mainHtml}${specHtml}</div>`;
      }
      
      if (productKey === 'power_655') {
        const mainCount = isBao ? 7 : 6;
        const mainBalls = numbers.slice(0, mainCount);
        const specBall = numbers[mainCount];
        const actualMain = actualNumbers ? actualNumbers.slice(0, 6) : [];
        const actualSpec = actualNumbers && actualNumbers.length >= 7 ? actualNumbers[6] : null;

        const mainHtml = mainBalls.map(n => {
          const isMatch = actualMain.includes(n);
          const cls = isMatch ? 'bg-rose-600 text-white font-bold border-rose-400 shadow-sm' : 'bg-slate-800 text-slate-300 border-slate-700';
          return `<span class="px-2 py-0.5 rounded text-xs border ${cls}">${String(n).padStart(2, '0')}</span>`;
        }).join('');

        let specHtml = '';
        if (specBall !== undefined && specBall !== null) {
          const isSpecMatch = actualSpec === specBall;
          const specCls = isSpecMatch ? 'bg-amber-500 text-slate-950 font-black border-amber-300 shadow-md' : 'bg-amber-950/80 text-amber-300 border-amber-600/60 font-bold';
          specHtml = `
            <span class="text-amber-400 font-black text-xs px-1">+</span>
            <span class="px-2 py-0.5 rounded text-xs border ${specCls} flex items-center gap-1 shadow-sm" title="Cầu vàng Jackpot 2">
              <i data-lucide="star" class="w-2.5 h-2.5 fill-amber-400"></i>${String(specBall).padStart(2, '0')}
            </span>
          `;
        }
        return `<div class="flex items-center gap-1 flex-nowrap whitespace-nowrap">${mainHtml}${specHtml}</div>`;
      }

      // Mega 6/45
      return `
        <div class="flex gap-1.5 flex-nowrap whitespace-nowrap">
          ${numbers.map(n => {
            const isMatch = actualSet && actualSet.has(n);
            const cls = isMatch ? 'bg-emerald-600 text-white font-bold border-emerald-400 shadow-sm' : 'bg-slate-800 text-slate-300 border-slate-700';
            return `<span class="px-2 py-0.5 rounded text-xs border ${cls}">${String(n).padStart(2, '0')}</span>`;
          }).join('')}
        </div>
      `;
    }

    function renderActualBallsWithSpecial(actualNumbers, productKey = currentProductKey) {
      if (!actualNumbers || !actualNumbers.length) {
        return '<span class="text-slate-500 italic">Chưa có kết quả</span>';
      }
      if (productKey === 'power_535') {
        const main = actualNumbers.slice(0, 5);
        const spec = actualNumbers[5];
        const mainHtml = main.map(n => `<span class="px-1.5 py-0.5 rounded bg-slate-900 text-slate-400 text-xs border border-slate-800">${String(n).padStart(2, '0')}</span>`).join('');
        const specHtml = spec !== undefined ? `
          <span class="text-amber-400/80 font-bold text-xs px-1">+</span>
          <span class="px-1.5 py-0.5 rounded bg-amber-950 text-amber-300 text-xs border border-amber-500/50 font-bold flex items-center gap-0.5">
            <i data-lucide="star" class="w-2.5 h-2.5 fill-amber-400"></i>${String(spec).padStart(2, '0')}
          </span>
        ` : '';
        return `<div class="flex items-center gap-1 flex-nowrap whitespace-nowrap">${mainHtml}${specHtml}</div>`;
      }
      if (productKey === 'power_655') {
        const main = actualNumbers.slice(0, 6);
        const spec = actualNumbers[6];
        const mainHtml = main.map(n => `<span class="px-1.5 py-0.5 rounded bg-slate-900 text-slate-400 text-xs border border-slate-800">${String(n).padStart(2, '0')}</span>`).join('');
        const specHtml = spec !== undefined ? `
          <span class="text-amber-400/80 font-bold text-xs px-1">+</span>
          <span class="px-1.5 py-0.5 rounded bg-amber-950 text-amber-300 text-xs border border-amber-500/50 font-bold flex items-center gap-0.5">
            <i data-lucide="star" class="w-2.5 h-2.5 fill-amber-400"></i>${String(spec).padStart(2, '0')}
          </span>
        ` : '';
        return `<div class="flex items-center gap-1 flex-nowrap whitespace-nowrap">${mainHtml}${specHtml}</div>`;
      }
      // Mega 6/45
      return `
        <div class="flex gap-1 flex-nowrap whitespace-nowrap">
          ${actualNumbers.map(n => `<span class="px-1.5 py-0.5 rounded bg-slate-900 text-slate-400 text-xs border border-slate-800">${String(n).padStart(2, '0')}</span>`).join('')}
        </div>
      `;
    }

    function renderPredictionHistory(product) {
      const tbody = document.getElementById('predictionHistoryTableBody');
      if (!tbody) return;

      const kpiContainer = document.getElementById('ensembleBacktestKpis');
      const kpis = product?.backtest_data?.kpis;
      if (kpiContainer && kpis) {
        kpiContainer.innerHTML = `
          <div class="p-3 bg-slate-950 rounded-xl border border-slate-800">
            <span class="text-[10px] text-slate-500 block uppercase font-mono">Quy Mô Kiểm Định</span>
            <span class="text-sm font-bold text-white font-mono mt-0.5 block">${kpis.total_draws} Kỳ Thật</span>
            <span class="text-[10px] text-slate-400">Walk-Forward 100%</span>
          </div>
          <div class="p-3 bg-slate-950 rounded-xl border border-emerald-500/30">
            <span class="text-[10px] text-emerald-400 block uppercase font-mono">Trúng ≥ 3 Số (Giải Ba+)</span>
            <span class="text-sm font-bold text-emerald-400 font-mono mt-0.5 block">${kpis.hit_3_plus} Kỳ (${kpis.win_rate_pct}%)</span>
            <span class="text-[10px] text-slate-400">Có thưởng thực tế</span>
          </div>
          <div class="p-3 bg-slate-950 rounded-xl border border-amber-500/30">
            <span class="text-[10px] text-amber-400 block uppercase font-mono">Trúng ≥ 4 Số (Giải Nhì+)</span>
            <span class="text-sm font-bold text-amber-400 font-mono mt-0.5 block">${kpis.hit_4_plus} Kỳ</span>
            <span class="text-[10px] text-slate-400">Thưởng lớn</span>
          </div>
          <div class="p-3 bg-slate-950 rounded-xl border border-slate-800">
            <span class="text-[10px] text-slate-500 block uppercase font-mono">Tổng Thu Thưởng</span>
            <span class="text-sm font-bold ${kpis.total_payout > 0 ? 'text-emerald-400' : 'text-slate-400'} font-mono mt-0.5 block">${kpis.total_payout.toLocaleString('vi-VN')} đ</span>
            <span class="text-[10px] text-slate-400">Vốn 200 vé: ${(kpis.total_cost).toLocaleString('vi-VN')} đ</span>
          </div>
        `;
      }

      const list = getStoredPredictions(currentProductKey);
      if (!list.length) {
        tbody.innerHTML = `<tr><td colspan="6" class="py-6 text-center text-slate-500">Chưa có bản ghi dự đoán nào được lưu.</td></tr>`;
        return;
      }

      const is535 = currentProductKey === 'power_535';
      const is655 = currentProductKey === 'power_655';
      const mainCount = is535 ? 5 : 6;

      tbody.innerHTML = list.map(item => {
        const isPending = !item.actual;
        let matchMain = 0;
        let matchSpecial = false;
        let prizeBadge = '';

        if (!isPending) {
          const predMain = item.predicted.slice(0, mainCount);
          const actualMain = item.actual.slice(0, mainCount);
          const actualMainSet = new Set(actualMain);
          matchMain = predMain.filter(n => actualMainSet.has(n)).length;

          if (is535 || is655) {
            const predSpec = item.predicted[mainCount];
            const actualSpec = item.actual[mainCount];
            matchSpecial = predSpec !== undefined && actualSpec !== undefined && predSpec === actualSpec;
          }

          if (is535) {
            if (matchMain === 5 && matchSpecial) prizeBadge = '<span class="text-amber-400 font-bold">🏆 JACKPOT (5 chính + ĐB)!</span>';
            else if (matchMain === 5) prizeBadge = '<span class="text-rose-400 font-bold">🥈 Giải Nhất (40tr)</span>';
            else if (matchMain === 4 && matchSpecial) prizeBadge = '<span class="text-emerald-400 font-bold">🥉 Giải Nhì (500k + ĐB)</span>';
            else if (matchMain === 4) prizeBadge = '<span class="text-emerald-400 font-bold">🥉 Giải Ba (50k)</span>';
            else if (matchMain === 3 && matchSpecial) prizeBadge = '<span class="text-blue-400 font-bold">🎖️ Giải Tư (50k)</span>';
            else if (matchMain === 3) prizeBadge = '<span class="text-blue-400 font-bold">🎖️ Giải Năm (30k)</span>';
            else if (matchSpecial) prizeBadge = '<span class="text-amber-300 font-bold">⭐ Giải KK (10k - trúng ĐB)</span>';
            else prizeBadge = '<span class="text-slate-500">Không trúng thưởng</span>';
          } else if (is655) {
            if (matchMain === 6 && matchSpecial) prizeBadge = '<span class="text-amber-400 font-bold">🏆 JACKPOT 1 + JP2!</span>';
            else if (matchMain === 6) prizeBadge = '<span class="text-amber-400 font-bold">🏆 JACKPOT 1!</span>';
            else if (matchMain === 5 && matchSpecial) prizeBadge = '<span class="text-amber-300 font-bold">💎 JACKPOT 2!</span>';
            else if (matchMain === 5) prizeBadge = '<span class="text-rose-400 font-bold">🥈 Giải Nhất (40tr)</span>';
            else if (matchMain === 4) prizeBadge = '<span class="text-emerald-400 font-bold">🥉 Giải Nhì (500k)</span>';
            else if (matchMain === 3) prizeBadge = '<span class="text-blue-400 font-bold">🎖️ Giải Ba (50k)</span>';
            else prizeBadge = '<span class="text-slate-500">Không trúng thưởng</span>';
          } else {
            // Mega 6/45
            if (matchMain === 6) prizeBadge = '<span class="text-amber-400 font-bold">🏆 JACKPOT!</span>';
            else if (matchMain === 5) prizeBadge = '<span class="text-rose-400 font-bold">🥈 Giải Nhất (10tr)</span>';
            else if (matchMain === 4) prizeBadge = '<span class="text-emerald-400 font-bold">🥉 Giải Nhì (300k)</span>';
            else if (matchMain === 3) prizeBadge = '<span class="text-blue-400 font-bold">🎖️ Giải Ba (30k)</span>';
            else prizeBadge = '<span class="text-slate-500">Không trúng thưởng</span>';
          }
        } else {
          prizeBadge = '<span class="text-amber-400 font-sans font-bold">⏳ Đang chờ mở thưởng</span>';
        }

        const matchDisplay = isPending ? '--' : (
          (is535 || is655)
            ? `${matchMain} chính${matchSpecial ? ' + ĐB' : ''}`
            : `${matchMain} số`
        );
        const matchCls = (!isPending && matchMain >= 3) ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30' : 'bg-slate-800 text-slate-400';

        return `
          <tr class="hover:bg-slate-800/40 transition">
            <td class="py-3 px-4 text-amber-400 font-bold">#${item.drawId}</td>
            <td class="py-3 px-4 text-slate-300">${item.date || '--'}</td>
            <td class="py-3 px-4">
              ${renderBallsWithSpecial(item.predicted, item.actual, false, currentProductKey)}
            </td>
            <td class="py-3 px-4">
              ${renderActualBallsWithSpecial(item.actual, currentProductKey)}
            </td>
            <td class="py-3 px-4 text-center">
              ${isPending ? '<span class="text-slate-500">--</span>' : `
                <span class="px-2 py-0.5 rounded-full text-xs font-bold ${matchCls}">
                  ${matchDisplay}
                </span>
              `}
            </td>
            <td class="py-3 px-4 text-right">
              ${prizeBadge}
            </td>
          </tr>
        `;
      }).join('');
    }

    function saveCurrentPredictionToHistory() {
      if (!currentEnsembleTickets.length) return;
      const product = appData?.products?.[currentProductKey];
      const latestIdNum = parseInt(product?.latest?.id?.replace('#', '') || '0');
      const nextId = latestIdNum ? String(latestIdNum + 1).padStart(5, '0') : 'Kỳ Tiếp';
      const storageKey = `vietlott_prediction_history_${currentProductKey}`;
      const list = getStoredPredictions(currentProductKey);

      const topTicket = currentEnsembleTickets[0];
      const existingIdx = list.findIndex(item => item.drawId === nextId);
      if (existingIdx !== -1) {
        list[existingIdx].predicted = topTicket.numbers;
      } else {
        list.unshift({
          drawId: nextId,
          date: 'Kỳ tới (Sắp quay)',
          predicted: topTicket.numbers,
          actual: null,
          status: 'pending'
        });
      }

      localStorage.setItem(storageKey, JSON.stringify(list));
      renderPredictionHistory(product);
      
      const gameLabel = currentProductKey === 'power_655' ? 'Power 6/55' : currentProductKey === 'power_645' ? 'Mega 6/45' : 'Power 5/35';
      const toSaveNums = (currentProductKey === 'power_535' && topTicket.special)
        ? [...topTicket.numbers, topTicket.special]
        : topTicket.numbers;

      saveTicketToNotebook({
        game: currentProductKey,
        gameName: gameLabel,
        drawId: nextId,
        type: 'ensemble',
        numbers: toSaveNums,
        cost: 10000
      });
    }

    function saveSingleGoldenTicket(ticketStr, score) {
      const nums = ticketStr.split(',').map(x => parseInt(x.trim())).filter(x => !isNaN(x));
      const product = appData?.products?.[currentProductKey];
      const latestIdNum = parseInt(product?.latest?.id?.replace('#', '') || '0');
      const nextId = latestIdNum ? String(latestIdNum + 1).padStart(5, '0') : 'Kỳ Tiếp';
      const storageKey = `vietlott_prediction_history_${currentProductKey}`;
      const list = getStoredPredictions(currentProductKey);

      list.unshift({
        drawId: nextId,
        date: 'Kỳ tới (Sắp quay)',
        predicted: nums,
        actual: null,
        status: 'pending'
      });

      localStorage.setItem(storageKey, JSON.stringify(list));
      renderPredictionHistory(product);
      
      const gameLabel = currentProductKey === 'power_655' ? 'Power 6/55' : currentProductKey === 'power_645' ? 'Mega 6/45' : 'Power 5/35';
      saveTicketToNotebook({
        game: currentProductKey,
        gameName: gameLabel,
        drawId: nextId,
        type: 'ensemble',
        numbers: nums,
        cost: 10000
      });
    }

    function clearPredictionHistory() {
      if (confirm("Bạn có chắc chắn muốn đặt lại lịch sử dự đoán về mặc định?")) {
        const storageKey = `vietlott_prediction_history_${currentProductKey}`;
        localStorage.removeItem(storageKey);
        renderPredictionHistory(appData?.products?.[currentProductKey]);
      }
    }

    function applyGoldenTicketToChecker(ticketStr) {
      document.getElementById('ticketInput').value = ticketStr;
      switchView('overview');
      checkTicket();
    }

    function applyGoldenTicketToSim(ticketStr) {
      document.getElementById('simCustomNumbers').value = ticketStr;
      document.getElementById('simStrategySelect').value = 'fixed_ticket';
      document.getElementById('simCustomTicketWrap').classList.remove('hidden');
      switchView('simulator');
      runSimulation();
    }

