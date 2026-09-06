// ==========================================
// 5. NOTEBOOK & BAO 7: Saved Tickets Notebook, Bao 7 Strategy, SMS 9969
// ==========================================

    // ==========================================
    // 5. SAVED TICKETS NOTEBOOK (SỔ TAY CÁ NHÂN)
    // ==========================================

    function getSavedTickets() {
      const raw = localStorage.getItem('vietlott_user_notebook_tickets');
      if (raw) {
        try {
          const list = JSON.parse(raw);
          if (Array.isArray(list)) return list;
        } catch (e) {}
      }
      return [];
    }

    function setSavedTickets(list) {
      localStorage.setItem('vietlott_user_notebook_tickets', JSON.stringify(list));
      updateSavedBadge();
    }

    function updateSavedBadge() {
      const badge = document.getElementById('savedTicketsBadge');
      if (badge) {
        const list = getSavedTickets();
        badge.textContent = list.length;
        if (list.length > 0) {
          badge.className = 'ml-1 px-1.5 py-0.2 rounded-full text-[10px] font-bold bg-violet-500 text-white font-mono shadow-sm';
        } else {
          badge.className = 'ml-1 px-1.5 py-0.2 rounded-full text-[10px] font-bold bg-slate-700 text-slate-400 font-mono';
        }
      }
    }

    function saveTicketToNotebook(ticketData) {
      const list = getSavedTickets();
      // Check duplicate
      const exists = list.some(x => x.game === ticketData.game && x.drawId === ticketData.drawId && JSON.stringify(x.numbers) === JSON.stringify(ticketData.numbers));
      if (exists) {
        alert('Bộ số này đã có trong Sổ Tay Vé Đã Lưu của bạn!');
        return;
      }
      list.unshift({
        id: 't_' + Date.now(),
        savedAt: new Date().toLocaleDateString('vi-VN') + ' ' + new Date().toLocaleTimeString('vi-VN', {hour: '2-digit', minute:'2-digit'}),
        ...ticketData
      });
      setSavedTickets(list);
      updateSavedBadge();
      
      if (confirm(`ĐÃ LƯU VÉ VÀO SỔ TAY THÀNH CÔNG! 🎉\n\n• Game: ${ticketData.gameName}\n• Kỳ quay: #${ticketData.drawId}\n• Dãy số: [${ticketData.numbers.join(', ')}]\n\nBạn có muốn chuyển sang xem ngay tại tab "Sổ Tay Vé Đã Lưu"?`)) {
        switchView('saved-tickets');
      }
    }

    function deleteSavedTicket(ticketId) {
      if (confirm('Bạn có chắc chắn muốn xóa vé này khỏi Sổ Tay?')) {
        let list = getSavedTickets();
        list = list.filter(x => x.id !== ticketId);
        setSavedTickets(list);
        renderSavedTicketsView();
      }
    }

    function clearAllSavedTickets() {
      if (confirm('Bạn có chắc chắn muốn xóa TOÀN BỘ vé trong Sổ Tay?')) {
        setSavedTickets([]);
        renderSavedTicketsView();
      }
    }

    function filterSavedTickets(gameKey) {
      currentSavedFilter = gameKey;
      document.querySelectorAll('.st-filter-btn').forEach(btn => {
        btn.className = 'st-filter-btn px-2.5 py-1 rounded-lg bg-slate-800 text-slate-300';
      });
      const active = document.getElementById(`stFilter-${gameKey}`);
      if (active) active.className = 'st-filter-btn px-2.5 py-1 rounded-lg bg-violet-600 text-white font-bold';
      renderSavedTicketsView();
    }

    async function refreshLiveSummaryData() {
      const btn = event?.currentTarget;
      if (btn) btn.innerHTML = '<i data-lucide="loader" class="w-3.5 h-3.5 animate-spin"></i> Đang tải...';
      await loadData();
      renderSavedTicketsView();
      alert('Đã đồng bộ và cập nhật dữ liệu kết quả mới nhất từ máy chủ!');
      if (btn) btn.innerHTML = '<i data-lucide="refresh-cw" class="w-3.5 h-3.5"></i> Cập Nhật KQ Mới Nhất';
      lucide.createIcons();
    }


    // Cross-Device Sync & Git Integration
    function getAllMergedSavedTickets() {
      const localList = getSavedTickets();
      const localIds = new Set(localList.map(x => x.id || (x.game + '_' + x.drawId)));
      const merged = [...localList];
      
      if (Array.isArray(gitSavedTickets)) {
        gitSavedTickets.forEach(gt => {
          const key = gt.id || (gt.game + '_' + gt.drawId);
          if (!localIds.has(key)) {
            merged.push({ ...gt, isFromGit: true });
          }
        });
      }
      return merged;
    }

    function createShareSyncLink() {
      const list = getSavedTickets();
      if (!list.length) {
        alert('Sổ tay của bạn hiện đang trống! Hãy lưu ít nhất 1 vé trước khi tạo link đồng bộ.');
        return;
      }
      const dataStr = JSON.stringify(list);
      const encoded = btoa(encodeURIComponent(dataStr));
      const syncUrl = `${window.location.origin}${window.location.pathname}?sync=${encoded}`;
      
      navigator.clipboard.writeText(syncUrl).then(() => {
        alert(`ĐÃ TẠO VÀ COPY LINK ĐỒNG BỘ THÀNH CÔNG! 🔗\n\nBạn chỉ cần gửi link này qua Zalo / Telegram / iMessage sang máy tính hoặc điện thoại khác, mở lên là hệ thống sẽ tự động nạp toàn bộ ${list.length} vé vào Sổ Tay của thiết bị đó!`);
      }).catch(() => {
        prompt('Copy link đồng bộ dưới đây để mở trên thiết bị khác:', syncUrl);
      });
    }

    function checkUrlSyncParams() {
      const params = new URLSearchParams(window.location.search);
      const syncData = params.get('sync');
      if (syncData) {
        try {
          const decoded = decodeURIComponent(atob(syncData));
          const incomingTickets = JSON.parse(decoded);
          if (Array.isArray(incomingTickets) && incomingTickets.length > 0) {
            if (confirm(`PHÁT HIỆN LIÊN KẾT ĐỒNG BỘ! 📲\n\nBạn nhận được ${incomingTickets.length} vé từ thiết bị khác. Bạn có muốn nạp toàn bộ vé này vào Sổ Tay trên máy này không?`)) {
              const current = getSavedTickets();
              const currentIds = new Set(current.map(x => x.game + '_' + x.drawId + '_' + JSON.stringify(x.numbers)));
              let added = 0;
              incomingTickets.forEach(t => {
                const key = t.game + '_' + t.drawId + '_' + JSON.stringify(t.numbers);
                if (!currentIds.has(key)) {
                  current.unshift({ ...t, id: 'sync_' + Date.now() + '_' + Math.random().toString(36).substr(2, 4) });
                  currentIds.add(key);
                  added++;
                }
              });
              setSavedTickets(current);
              alert(`Đã nạp thành công +${added} vé mới vào Sổ Tay!`);
              // Clean URL without refresh
              const cleanUrl = window.location.origin + window.location.pathname;
              window.history.replaceState({}, document.title, cleanUrl);
              switchView('saved-tickets');
            }
          }
        } catch (err) {
          console.error('Sync parse error:', err);
        }
      }
    }

    function exportTicketsJson() {
      const list = getSavedTickets();
      if (!list.length) {
        alert('Sổ tay trống, không có vé để xuất file!');
        return;
      }
      const blob = new Blob([JSON.stringify(list, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `vietlott_so_tay_backup_${new Date().toISOString().slice(0, 10)}.json`;
      a.click();
      URL.revokeObjectURL(url);
    }

    function importTicketsJson(event) {
      const file = event.target.files[0];
      if (!file) return;
      const reader = new FileReader();
      reader.onload = (e) => {
        try {
          const imported = JSON.parse(e.target.result);
          if (Array.isArray(imported) && imported.length > 0) {
            const current = getSavedTickets();
            const currentIds = new Set(current.map(x => x.game + '_' + x.drawId + '_' + JSON.stringify(x.numbers)));
            let count = 0;
            imported.forEach(t => {
              const key = t.game + '_' + t.drawId + '_' + JSON.stringify(t.numbers);
              if (!currentIds.has(key)) {
                current.unshift({ ...t, id: 'imp_' + Date.now() + '_' + Math.random().toString(36).substr(2, 4) });
                currentIds.add(key);
                count++;
              }
            });
            setSavedTickets(current);
            renderSavedTicketsView();
            alert(`Đã nạp thành công +${count} vé từ file vào Sổ Tay!`);
          } else {
            alert('File không hợp lệ hoặc không có dữ liệu vé!');
          }
        } catch (err) {
          alert('Lỗi đọc file JSON: ' + err.message);
        }
      };
      reader.readAsText(file);
      event.target.value = '';
    }

    function renderSavedTicketsView() {
      const container = document.getElementById('savedTicketsContainer');
      if (!container) return;

      let list = getAllMergedSavedTickets();
      if (currentSavedFilter !== 'all') {
        list = list.filter(x => x.game === currentSavedFilter);
      }

      const allTickets = getAllMergedSavedTickets();
      let totalCost = 0;
      let totalWinnings = 0;
      let pendingCount = 0;

      // Evaluate each ticket against current live data in appData
      const evaluatedList = list.map(item => {
        const prod = appData?.products?.[item.game];
        let actual = null;
        let isPending = true;

        if (prod) {
          // Check if latest id matches or history matches
          if (prod.latest && (prod.latest.id === item.drawId || parseInt(prod.latest.id) >= parseInt(item.drawId))) {
            // Find draw in history or latest
            if (prod.latest.id === item.drawId) {
              actual = prod.latest.result;
              isPending = false;
            } else if (prod.history) {
              const h = prod.history.find(x => x.id === item.drawId);
              if (h) {
                actual = h.result;
                isPending = false;
              }
            }
          }
        }

        const cost = item.cost || (item.type === 'bao6' ? 60000 : item.type === 'bao7' ? 70000 : 10000);
        totalCost += cost;

        let winAmount = 0;
        let winTitle = '';
        let matchText = '';

        if (isPending) {
          pendingCount++;
          winTitle = '⏳ Đang chờ mở thưởng';
        } else if (actual) {
          const is535 = item.game === 'power_535';
          const is655 = item.game === 'power_655';
          const mainLimit = (item.type === 'bao7') ? 7 : (item.type === 'bao6') ? 6 : (is535 ? 5 : 6);
          const predMain = item.numbers.slice(0, mainLimit);
          const actualMainCount = is535 ? 5 : 6;
          const actualMain = actual.slice(0, actualMainCount);
          const actualMainSet = new Set(actualMain);
          const matchMain = predMain.filter(n => actualMainSet.has(n)).length;

          let matchSpec = false;
          if (is535) {
            const predSpec = item.numbers[mainLimit];
            const actSpec = actual[5];
            matchSpec = predSpec !== undefined && actSpec !== undefined && predSpec === actSpec;
          } else if (is655) {
            const predSpec = item.numbers[mainLimit];
            const actSpec = actual[6];
            matchSpec = predSpec !== undefined && actSpec !== undefined && predSpec === actSpec;
          }

          matchText = is535 || is655 ? `Trúng ${matchMain} chính${matchSpec ? ' + Cầu ĐB' : ''}` : `Trúng ${matchMain} số`;

          // Prize calculator
          if (item.type === 'bao7') {
            if (item.game === 'power_655') {
              if (matchMain === 6) { winAmount = 240000000; winTitle = '🏆 JACKPOT 1 + 240tr'; }
              else if (matchMain === 5 && matchSpec) { winAmount = 42500000; winTitle = '💎 JACKPOT 2 + 42.5tr'; }
              else if (matchMain === 5) { winAmount = 82500000; winTitle = '🥈 2 Giải Nhất (80tr)'; }
              else if (matchMain === 4) { winAmount = 1700000; winTitle = '🥉 3 Giải Nhì + 4 Giải Ba'; }
              else if (matchMain === 3) { winAmount = 200000; winTitle = '🎖️ 4 Giải Ba (200k)'; }
              else { winAmount = 0; winTitle = 'Không trúng'; }
            } else {
              // 6/45
              if (matchMain === 6) { winAmount = 60000000; winTitle = '🏆 JACKPOT + 60tr'; }
              else if (matchMain === 5) { winAmount = 21500000; winTitle = '🥈 2 Nhất (20tr) + 5 Nhì'; }
              else if (matchMain === 4) { winAmount = 1020000; winTitle = '🥉 3 Nhì + 4 Ba (1.02tr)'; }
              else if (matchMain === 3) { winAmount = 120000; winTitle = '🎖️ 4 Giải Ba (120k)'; }
              else { winAmount = 0; winTitle = 'Không trúng'; }
            }
          } else if (item.type === 'bao6' && item.game === 'power_535') {
            if (matchMain === 5 && matchSpec) { winAmount = 2500000; winTitle = '🏆 ĐỘC ĐẮC + 2.5tr'; }
            else if (matchMain === 5) { winAmount = 40250000; winTitle = '🥈 1 Nhất (40tr) + 5 Ba'; }
            else if (matchMain === 4 && matchSpec) { winAmount = 1200000; winTitle = '🥉 2 Nhì + 4 Tư (1.2tr)'; }
            else if (matchMain === 4) { winAmount = 100000; winTitle = '🥉 2 Giải Ba (100k)'; }
            else if (matchMain === 3 && matchSpec) { winAmount = 180000; winTitle = '🎖️ 3 Tư + 3 KK (180k)'; }
            else if (matchMain === 3) { winAmount = 90000; winTitle = '🎖️ 3 Giải Năm (90k)'; }
            else if (matchSpec) { winAmount = 60000; winTitle = '⭐ 6 Giải KK (Hòa vốn 60k)'; }
            else { winAmount = 0; winTitle = 'Không trúng'; }
          } else {
            // Vé đơn 10k
            if (item.game === 'power_655') {
              if (matchMain === 6) { winAmount = 30000000000; winTitle = '🏆 JACKPOT 1'; }
              else if (matchMain === 5 && matchSpec) { winAmount = 3500000000; winTitle = '💎 JACKPOT 2'; }
              else if (matchMain === 5) { winAmount = 40000000; winTitle = '🥈 Giải Nhất (40tr)'; }
              else if (matchMain === 4) { winAmount = 500000; winTitle = '🥉 Giải Nhì (500k)'; }
              else if (matchMain === 3) { winAmount = 50000; winTitle = '🎖️ Giải Ba (50k)'; }
            } else if (item.game === 'power_645') {
              if (matchMain === 6) { winAmount = 12000000000; winTitle = '🏆 JACKPOT'; }
              else if (matchMain === 5) { winAmount = 10000000; winTitle = '🥈 Giải Nhất (10tr)'; }
              else if (matchMain === 4) { winAmount = 300000; winTitle = '🥉 Giải Nhì (300k)'; }
              else if (matchMain === 3) { winAmount = 30000; winTitle = '🎖️ Giải Ba (30k)'; }
            } else if (item.game === 'power_535') {
              if (matchMain === 5 && matchSpec) { winAmount = 6000000000; winTitle = '🏆 ĐỘC ĐẮC'; }
              else if (matchMain === 5) { winAmount = 40000000; winTitle = '🥈 Giải Nhất (40tr)'; }
              else if (matchMain === 4 && matchSpec) { winAmount = 500000; winTitle = '🥉 Giải Nhì (500k)'; }
              else if (matchMain === 4) { winAmount = 50000; winTitle = '🥉 Giải Ba (50k)'; }
              else if (matchMain === 3 && matchSpec) { winAmount = 50000; winTitle = '🎖️ Giải Tư (50k)'; }
              else if (matchMain === 3) { winAmount = 30000; winTitle = '🎖️ Giải Năm (30k)'; }
              else if (matchSpec) { winAmount = 10000; winTitle = '⭐ Giải KK (10k)'; }
            }
          }
        }

        totalWinnings += winAmount;

        return {
          ...item,
          actual,
          isPending,
          winAmount,
          winTitle,
          matchText,
          netProfit: winAmount - cost
        };
      });

      // Update metrics
      document.getElementById('st-totalTickets').textContent = allTickets.length;
      document.getElementById('st-pendingTickets').textContent = pendingCount;
      document.getElementById('st-totalWinnings').textContent = totalWinnings.toLocaleString() + ' đ';
      const net = totalWinnings - totalCost;
      const netEl = document.getElementById('st-netProfit');
      if (netEl) {
        netEl.textContent = (net >= 0 ? '+' : '') + net.toLocaleString() + ' đ';
        netEl.className = net >= 0 ? 'text-emerald-400 font-black text-lg mt-0.5 block' : 'text-rose-400 font-black text-lg mt-0.5 block';
      }

      if (!evaluatedList.length) {
        container.innerHTML = `
          <div class="text-center py-12 bg-slate-950/60 rounded-xl border border-dashed border-slate-800 space-y-3">
            <i data-lucide="ticket" class="w-10 h-10 text-slate-600 mx-auto"></i>
            <p class="text-sm text-slate-400">Chưa có vé nào được lưu trong Sổ Tay.</p>
            <p class="text-xs text-slate-500">Hãy sang tab <strong>Dự Đoán Toàn Diện</strong> hoặc <strong>Chiến Lược Bao 7</strong> rồi bấm nút <strong>"Lưu Vé Này"</strong> để bắt đầu theo dõi!</p>
          </div>
        `;
        lucide.createIcons();
        return;
      }

      container.innerHTML = evaluatedList.map(item => {
        const gameLabel = item.game === 'power_655' ? 'Power 6/55' : item.game === 'power_645' ? 'Mega 6/45' : 'Power 5/35';
        const gameBg = item.game === 'power_655' ? 'bg-rose-500/20 text-rose-300 border-rose-500/30' : item.game === 'power_645' ? 'bg-blue-500/20 text-blue-300 border-blue-500/30' : 'bg-emerald-500/20 text-emerald-300 border-emerald-500/30';
        
        let smsSyntax = '';
        if (item.game === 'power_655') {
          smsSyntax = item.type === 'bao7' ? `655 K1 B7 S ${item.numbers.slice(0, 7).map(n => String(n).padStart(2, '0')).join(' ')}` : `655 K1 S ${item.numbers.slice(0, 6).map(n => String(n).padStart(2, '0')).join(' ')}`;
        } else if (item.game === 'power_645') {
          smsSyntax = item.type === 'bao7' ? `645 K1 B7 S ${item.numbers.slice(0, 7).map(n => String(n).padStart(2, '0')).join(' ')}` : `645 K1 S ${item.numbers.slice(0, 6).map(n => String(n).padStart(2, '0')).join(' ')}`;
        }

        const isBao = item.type === 'bao7' || item.type === 'bao6';

        return `
          <div class="rounded-xl bg-slate-950 border border-slate-800 p-4 space-y-3 transition hover:border-slate-700">
            <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-800/80 pb-3">
              <div class="flex items-center gap-2 flex-wrap">
                <span class="px-2.5 py-0.5 rounded-full text-xs font-bold border ${gameBg}">
                  ${gameLabel}
                </span>
                <span class="text-xs font-mono font-bold text-amber-400">Kỳ #${item.drawId}</span>
                <span class="px-2 py-0.5 rounded text-[11px] font-bold bg-slate-800 text-slate-300">
                  ${item.type === 'bao7' ? 'Chiến Lược Bao 7' : item.type === 'bao6' ? 'Chiến Lược Bao 6' : 'Vé Vàng Dự Đoán'}
                </span>
                ${item.isFromGit ? '<span class="px-2 py-0.5 rounded-full text-[10px] font-bold bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 flex items-center gap-1">☁️ Đồng Bộ Git</span>' : ''}
                <span class="text-[11px] text-slate-500">Lưu lúc: ${item.savedAt}</span>
              </div>

              <div class="flex items-center gap-2">
                <span class="text-xs font-mono text-slate-400">Vốn: <strong>${(item.cost || 70000).toLocaleString()}đ</strong></span>
                <button onclick="deleteSavedTicket('${item.id}')" class="text-slate-500 hover:text-rose-400 transition p-1" title="Xóa vé này">
                  <i data-lucide="trash" class="w-4 h-4"></i>
                </button>
              </div>
            </div>

            <div class="grid grid-cols-1 lg:grid-cols-12 gap-4 items-center">
              <div class="lg:col-span-6 space-y-1.5">
                <div class="text-[11px] text-slate-400">Dàn số bạn chọn:</div>
                <div class="overflow-x-auto py-1">
                  ${renderBallsWithSpecial(item.numbers, item.actual, isBao, item.game)}
                </div>
              </div>

              <div class="lg:col-span-6 space-y-1.5">
                <div class="text-[11px] text-slate-400">Kết quả thực tế từ Vietlott:</div>
                <div class="overflow-x-auto py-1">
                  ${item.actual ? renderActualBallsWithSpecial(item.actual, item.game) : '<span class="text-xs text-amber-400/80 italic font-mono flex items-center gap-1"><i data-lucide="clock" class="w-3.5 h-3.5 inline"></i> Đang chờ quay thưởng...</span>'}
                </div>
              </div>
            </div>

            <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pt-3 border-t border-slate-800/80 text-xs">
              <div class="flex items-center gap-2 flex-wrap">
                <span class="font-bold ${item.isPending ? 'text-amber-400' : item.winAmount > 0 ? 'text-emerald-400' : 'text-slate-500'}">
                  ${item.winTitle}
                </span>
                ${item.matchText ? `<span class="px-2 py-0.5 rounded-full bg-slate-900 border border-slate-800 text-slate-300 font-mono text-[11px]">${item.matchText}</span>` : ''}
                ${!item.isPending ? `
                  <span class="font-mono font-bold ${item.netProfit >= 0 ? 'text-emerald-400' : 'text-rose-400'}">
                    (${item.netProfit >= 0 ? '+' : ''}${item.netProfit.toLocaleString()} VNĐ)
                  </span>
                ` : ''}
              </div>

              <div class="flex items-center gap-2">
                ${smsSyntax ? `
                  <button onclick="navigator.clipboard.writeText('${smsSyntax}').then(() => alert('Đã chép: ' + '${smsSyntax}'))" class="px-2.5 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 font-bold text-xs flex items-center gap-1 transition">
                    <i data-lucide="copy" class="w-3.5 h-3.5"></i> Copy SMS
                  </button>
                  <button onclick="openSmsUrl('${smsSyntax}')" class="px-2.5 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs flex items-center gap-1 transition shadow-sm">
                    <i data-lucide="send" class="w-3.5 h-3.5"></i> Gửi 9969
                  </button>
                ` : ''}
              </div>
            </div>
          </div>
        `;
      }).join('');

      lucide.createIcons();
    }

    // ==========================================
    // 4. VIETLOTT SMS 9969 SYNTAX LOGIC (6/55 & 6/45)
    // ==========================================
    function getBao7SmsSyntax() {
      if (!currentBao7Ticket || !currentBao7Ticket.numbers) return '';
      const nums = currentBao7Ticket.numbers.map(n => String(n).padStart(2, '0')).slice(0, 7).join(' ');
      if (currentProductKey === 'power_655') {
        return `655 K1 B7 S ${nums}`;
      }
      if (currentProductKey === 'power_645') {
        return `645 K1 B7 S ${nums}`;
      }
      return '';
    }

    function copyBao7SmsSyntax() {
      const syntax = getBao7SmsSyntax();
      if (!syntax) {
        alert('Cú pháp SMS chuẩn hiện áp dụng cho Power 6/55 và Mega 6/45.');
        return;
      }
      navigator.clipboard.writeText(syntax).then(() => {
        alert(`ĐÃ SAO CHÉP CÚ PHÁP SMS:

${syntax}

👉 Bạn chỉ cần dán (Paste) vào tin nhắn gửi tới 9969 để đặt vé ngay!`);
      }).catch(() => {
        const ta = document.createElement('textarea');
        ta.value = syntax;
        document.body.appendChild(ta);
        ta.select();
        document.execCommand('copy');
        document.body.removeChild(ta);
        alert(`ĐÃ SAO CHÉP CÚ PHÁP SMS:

${syntax}

👉 Bạn chỉ cần dán (Paste) vào tin nhắn gửi tới 9969 để đặt vé ngay!`);
      });
    }

    function openSmsUrl(syntax) {
      if (!syntax) return;
      const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent) && !window.MSStream;
      const separator = isIOS ? '&' : '?';
      window.location.href = `sms:9969${separator}body=${encodeURIComponent(syntax)}`;
    }

    function openBao7SmsApp() {
      const syntax = getBao7SmsSyntax();
      if (!syntax) {
        alert('Cú pháp SMS chuẩn hiện áp dụng cho Power 6/55 và Mega 6/45.');
        return;
      }
      openSmsUrl(syntax);
    }

    function copyEnsembleSms(ticketNumbersStr, prodKey = currentProductKey) {
      if (prodKey !== 'power_655' && prodKey !== 'power_645') {
        alert('Cú pháp SMS chuẩn hiện áp dụng cho Power 6/55 và Mega 6/45.');
        return;
      }
      const nums = ticketNumbersStr.split(/[\s,]+/).map(n => String(parseInt(n)).padStart(2, '0')).slice(0, 6).join(' ');
      const prefix = prodKey === 'power_655' ? '655' : '645';
      const syntax = `${prefix} K1 S ${nums}`;
      
      navigator.clipboard.writeText(syntax).then(() => {
        alert(`ĐÃ SAO CHÉP CÚ PHÁP SMS:

${syntax}

👉 Gửi tin nhắn tới 9969 để đặt vé!`);
      }).catch(() => {
        const ta = document.createElement('textarea');
        ta.value = syntax;
        document.body.appendChild(ta);
        ta.select();
        document.execCommand('copy');
        document.body.removeChild(ta);
        alert(`ĐÃ SAO CHÉP CÚ PHÁP SMS:

${syntax}

👉 Gửi tin nhắn tới 9969 để đặt vé!`);
      });
    }

    function renderBao7View(product) {
      if (!product) return;

      const badgeEl = document.getElementById('bao7ProductBadge');
      const titleEl = document.getElementById('bao7Title');
      const descEl = document.getElementById('bao7Desc');
      const costBadge = document.getElementById('bao7CostBadge');
      const sumRangeEl = document.getElementById('bao7SumRange');
      const antiCrowdEl = document.getElementById('bao7AntiCrowd');
      const oddEvenEl = document.getElementById('bao7OddEven');
      const tailsEl = document.getElementById('bao7Tails');
      const payoutEl = document.getElementById('bao7PayoutTable');
      const breakdownCostEl = document.getElementById('bao7BreakdownCost');

      if (badgeEl) badgeEl.textContent = product.name;

      // Adapt to product
      if (currentProductKey === 'power_655') {
        if (titleEl) titleEl.innerHTML = `<i data-lucide="layers" class="w-5 h-5 text-emerald-400"></i> CHIẾN LƯỢC BAO 7 (POWER 6/55) - ĐÒN BẨY VỐN 70K`;
        if (descEl) descEl.textContent = `Tối ưu trên 100 kỳ gần nhất: Tỷ lệ trúng tăng 7 lần, chỉ cần trúng 3/7 số ăn ngay 4 Giải Ba (Lãi vốn 185%).`;
        if (costBadge) costBadge.textContent = `Vốn đầu tư: 70.000 VNĐ (7 vé đơn)`;
        if (sumRangeEl) sumRangeEl.textContent = `155 - 240`;
        if (antiCrowdEl) antiCrowdEl.textContent = `2 - 4 số ≥ 32`;
        if (oddEvenEl) oddEvenEl.textContent = `3L - 4C / 4L - 3C`;
        if (tailsEl) tailsEl.textContent = `≥ 5 Đuôi Phân Biệt`;
        if (breakdownCostEl) breakdownCostEl.textContent = `7 vé x 10k = 70.000đ`;
        if (payoutEl) {
          payoutEl.innerHTML = `
            <div class="space-y-2">
              <div class="p-2.5 rounded-lg bg-slate-950 border border-slate-800 flex flex-col sm:flex-row sm:items-center justify-between gap-1">
                <span class="font-bold text-slate-300">Trùng 3 số:</span>
                <span class="text-xs text-slate-400">4 giải Ba (50.000đ)</span>
                <span class="text-blue-400 font-bold">200.000 VNĐ (Lời +130.000đ)</span>
              </div>
              <div class="p-2.5 rounded-lg bg-slate-950 border border-slate-800 flex flex-col sm:flex-row sm:items-center justify-between gap-1">
                <span class="font-bold text-slate-300">Trùng 4 số:</span>
                <span class="text-xs text-slate-400">3 giải Nhì (500k) + 4 giải Ba (50k)</span>
                <span class="text-emerald-400 font-bold">1.700.000 VNĐ (Lời +1.630.000đ)</span>
              </div>
              <div class="p-2.5 rounded-lg bg-slate-950 border border-slate-800 flex flex-col sm:flex-row sm:items-center justify-between gap-1">
                <span class="font-bold text-slate-300">Trùng 5 số:</span>
                <span class="text-xs text-slate-400">2 giải Nhất (40tr) + 5 giải Nhì (500k)</span>
                <span class="text-rose-400 font-bold">82.500.000 VNĐ (Lời +82.430.000đ)</span>
              </div>
              <div class="p-2.5 rounded-lg bg-slate-900 border border-amber-500/30 flex flex-col sm:flex-row sm:items-center justify-between gap-1 text-amber-300">
                <span class="font-bold">Trùng 5 số + Cầu Vàng:</span>
                <span class="text-xs text-amber-200/80">1 Jackpot 2 + 1 giải Nhất + 5 giải Nhì</span>
                <span class="font-extrabold">Jackpot 2 + 42.500.000 VNĐ</span>
              </div>
              <div class="p-2.5 rounded-lg bg-slate-900 border border-amber-500/40 flex flex-col sm:flex-row sm:items-center justify-between gap-1 text-amber-300">
                <span class="font-bold">Trùng 6 số:</span>
                <span class="text-xs text-amber-200/80">1 Jackpot 1 + 6 giải Nhất (40tr)</span>
                <span class="font-extrabold">Jackpot 1 + 240.000.000 VNĐ</span>
              </div>
              <div class="p-2.5 rounded-lg bg-slate-900 border border-amber-500/60 flex flex-col sm:flex-row sm:items-center justify-between gap-1 text-amber-300">
                <span class="font-bold">Trùng 6 số + Cầu Vàng:</span>
                <span class="text-xs text-amber-200/80">1 Jackpot 1 + 1 Jackpot 2 + 5 giải Nhất</span>
                <span class="font-extrabold">Jackpot 1 + Jackpot 2 + 200.000.000đ</span>
              </div>
              <p class="text-[10px] text-slate-500 italic pt-1 text-right">
                * Lưu ý: Mức thưởng trên 10 triệu đồng đối với mỗi giải con chịu thuế TNCN 10% phần vượt trên 10 triệu đồng.
              </p>
            </div>
          `;
        }
      } else if (currentProductKey === 'power_645') {
        if (titleEl) titleEl.innerHTML = `<i data-lucide="layers" class="w-5 h-5 text-emerald-400"></i> CHIẾN LƯỢC BAO 7 (MEGA 6/45) - ĐÒN BẨY VỐN 70K`;
        if (descEl) descEl.textContent = `Tối ưu trên 100 kỳ Mega 6/45: Trúng 3/7 số ăn ngay 4 Giải Ba (120k), trúng 4 số ăn 1.020.000 VNĐ.`;
        if (costBadge) costBadge.textContent = `Vốn đầu tư: 70.000 VNĐ (7 vé đơn)`;
        if (sumRangeEl) sumRangeEl.textContent = `125 - 198`;
        if (antiCrowdEl) antiCrowdEl.textContent = `1 - 3 số ≥ 32`;
        if (oddEvenEl) oddEvenEl.textContent = `3L - 4C / 4L - 3C`;
        if (tailsEl) tailsEl.textContent = `≥ 5 Đuôi Phân Biệt`;
        if (breakdownCostEl) breakdownCostEl.textContent = `7 vé x 10k = 70.000đ`;
        if (payoutEl) {
          payoutEl.innerHTML = `
            <div class="space-y-2">
              <div class="p-2.5 rounded-lg bg-slate-950 border border-slate-800 flex flex-col sm:flex-row sm:items-center justify-between gap-1">
                <span class="font-bold text-slate-300">Trùng 3 số:</span>
                <span class="text-xs text-slate-400">4 giải Ba (30.000đ)</span>
                <span class="text-blue-400 font-bold">120.000 VNĐ (Lời +50.000đ)</span>
              </div>
              <div class="p-2.5 rounded-lg bg-slate-950 border border-slate-800 flex flex-col sm:flex-row sm:items-center justify-between gap-1">
                <span class="font-bold text-slate-300">Trùng 4 số:</span>
                <span class="text-xs text-slate-400">3 giải Nhì (300k) + 4 giải Ba (30k)</span>
                <span class="text-emerald-400 font-bold">1.020.000 VNĐ (Lời +950.000đ)</span>
              </div>
              <div class="p-2.5 rounded-lg bg-slate-950 border border-slate-800 flex flex-col sm:flex-row sm:items-center justify-between gap-1">
                <span class="font-bold text-slate-300">Trùng 5 số:</span>
                <span class="text-xs text-slate-400">2 giải Nhất (10tr) + 5 giải Nhì (300k)</span>
                <span class="text-rose-400 font-bold">21.500.000 VNĐ (Lời +21.430.000đ)</span>
              </div>
              <div class="p-2.5 rounded-lg bg-slate-900 border border-amber-500/40 flex flex-col sm:flex-row sm:items-center justify-between gap-1 text-amber-300">
                <span class="font-bold">Trùng 6 số:</span>
                <span class="text-xs text-amber-200/80">1 giải Jackpot + 6 giải Nhất (10tr)</span>
                <span class="font-extrabold">Jackpot (12+ Tỷ) + 60.000.000 VNĐ</span>
              </div>
              <p class="text-[10px] text-slate-500 italic pt-1 text-right">
                * Lưu ý: Mức thưởng trên 10 triệu đồng đối với mỗi giải con chịu thuế TNCN 10% phần vượt trên 10 triệu đồng.
              </p>
            </div>
          `;
        }
      } else if (currentProductKey === 'power_535') {
        if (titleEl) titleEl.innerHTML = `<i data-lucide="layers" class="w-5 h-5 text-emerald-400"></i> CHIẾN LƯỢC BAO 6 CHÍNH (POWER 5/35) - VỐN 60K`;
        if (descEl) descEl.textContent = `Lotto 5/35 gồm 5 số chính (01 - 35) + 1 số đặc biệt (01 - 12). Chơi Bao 6 gồm 6 số chính + 1 số đặc biệt = 6 vé đơn (60.000đ), chỉ cần trúng 3 số chính là có lãi ngay!`;
        if (costBadge) costBadge.textContent = `Vốn đầu tư: 60.000 VNĐ (6 vé đơn)`;
        if (sumRangeEl) sumRangeEl.textContent = `85 - 145`;
        if (antiCrowdEl) antiCrowdEl.textContent = `1 - 2 số ≥ 25`;
        if (oddEvenEl) oddEvenEl.textContent = `3L - 3C / 4L - 2C`;
        if (tailsEl) tailsEl.textContent = `≥ 4 Đuôi Phân Biệt`;
        if (breakdownCostEl) breakdownCostEl.textContent = `6 vé x 10k = 60.000đ`;
        if (payoutEl) {
          payoutEl.innerHTML = `
            <div class="space-y-2">
              <div class="p-2.5 rounded-lg bg-slate-900 border border-emerald-500/40 flex flex-col sm:flex-row sm:items-center justify-between gap-1 text-emerald-300">
                <span class="font-bold">Chỉ trúng Cầu Đặc Biệt (0-2 chính):</span>
                <span class="text-xs text-emerald-200/80">6 giải Khuyến khích (6 x 10k)</span>
                <span class="font-bold text-emerald-400">60.000 VNĐ (Bảo hiểm hòa vốn 100%)</span>
              </div>
              <div class="p-2.5 rounded-lg bg-slate-950 border border-slate-800 flex flex-col sm:flex-row sm:items-center justify-between gap-1">
                <span class="font-bold text-slate-300">Trùng 3 chính (không cầu ĐB):</span>
                <span class="text-xs text-slate-400">3 giải Năm (3 x 30k)</span>
                <span class="text-blue-400 font-bold">90.000 VNĐ (Lời +30.000đ)</span>
              </div>
              <div class="p-2.5 rounded-lg bg-slate-950 border border-slate-800 flex flex-col sm:flex-row sm:items-center justify-between gap-1">
                <span class="font-bold text-slate-300">Trùng 3 chính + Cầu ĐB:</span>
                <span class="text-xs text-slate-400">3 giải Tư (300k) + 3 giải Khuyến khích</span>
                <span class="text-blue-400 font-bold">330.000 VNĐ (Lời +270.000đ)</span>
              </div>
              <div class="p-2.5 rounded-lg bg-slate-950 border border-slate-800 flex flex-col sm:flex-row sm:items-center justify-between gap-1">
                <span class="font-bold text-slate-300">Trùng 4 chính (không cầu ĐB):</span>
                <span class="text-xs text-slate-400">2 giải Ba (1tr) + 4 giải Năm (120k)</span>
                <span class="text-emerald-400 font-bold">1.120.000 VNĐ (Gấp 19 lần vốn)</span>
              </div>
              <div class="p-2.5 rounded-lg bg-slate-950 border border-slate-800 flex flex-col sm:flex-row sm:items-center justify-between gap-1">
                <span class="font-bold text-slate-300">Trùng 4 chính + Cầu ĐB:</span>
                <span class="text-xs text-slate-400">2 giải Nhì (10tr) + 4 giải Tư (400k)</span>
                <span class="text-emerald-400 font-bold">10.400.000 VNĐ (Gấp 173 lần vốn)</span>
              </div>
              <div class="p-2.5 rounded-lg bg-slate-950 border border-slate-800 flex flex-col sm:flex-row sm:items-center justify-between gap-1">
                <span class="font-bold text-slate-300">Trùng 5 chính (không cầu ĐB):</span>
                <span class="text-xs text-slate-400">1 giải Nhất (10tr) + 5 giải Ba (2.5tr)</span>
                <span class="text-rose-400 font-bold">12.500.000 VNĐ</span>
              </div>
              <div class="p-2.5 rounded-lg bg-slate-900 border border-amber-500/50 flex flex-col sm:flex-row sm:items-center justify-between gap-1 text-amber-300">
                <span class="font-bold">Trùng 5 chính + Cầu ĐB:</span>
                <span class="text-xs text-amber-200/80">1 Độc Đắc + 5 giải Nhì (25tr)</span>
                <span class="font-extrabold">Jackpot (6+ Tỷ) + 25.000.000 VNĐ</span>
              </div>
              <p class="text-[10px] text-amber-400/80 italic pt-1 text-right">
                ⚡ Cơ chế Rolldown: Khi Độc Đắc vượt 12 Tỷ chưa nổ, số tiền vượt được chia đều cho các giải Nhất, Nhì, Ba, Tư, Năm!
              </p>
            </div>
          `;
        }
      } else {
        // Max 3D, Keno...
        if (titleEl) titleEl.innerHTML = `<i data-lucide="layers" class="w-5 h-5 text-emerald-400"></i> CHIẾN LƯỢC DÀN SỐ TỐI ƯU (${product.name})`;
        if (descEl) descEl.textContent = `Dàn số được chọn lọc dựa trên chu kỳ gan và tần suất 100 kỳ gần nhất.`;
        if (costBadge) costBadge.textContent = `Vốn linh hoạt`;
        if (sumRangeEl) sumRangeEl.textContent = `--`;
        if (antiCrowdEl) antiCrowdEl.textContent = `--`;
        if (oddEvenEl) oddEvenEl.textContent = `--`;
        if (tailsEl) tailsEl.textContent = `--`;
        if (breakdownCostEl) breakdownCostEl.textContent = `Dàn số tiềm năng`;
        if (payoutEl) {
          payoutEl.innerHTML = `
            <div class="p-2.5 rounded-lg bg-slate-950 border border-slate-800 flex justify-between items-center">
              <span>Chiến lược:</span>
              <span class="text-emerald-400 font-bold">Bao đảo bộ số tăng tỷ lệ trúng</span>
            </div>
          `;
        }
      }

      generateBao7Ticket(false);
      renderBao7History();
      lucide.createIcons();
    }

    let bao7SeedOffset = 0;

    function generateBao7Ticket(forceNew = false) {
      const product = appData?.products?.[currentProductKey];
      if (!product) return;

      const maxVal = product.max_number || (currentProductKey === 'power_645' ? 45 : 55);
      const isMega = currentProductKey === 'power_645';
      const is535 = currentProductKey === 'power_535';
      const targetBalls = is535 ? 6 : 7;
      const minSum = isMega ? 125 : is535 ? 85 : 155;
      const maxSum = isMega ? 198 : is535 ? 145 : 240;
      const bigMin = isMega ? 32 : is535 ? 25 : 32;
      const minBigs = isMega ? 1 : is535 ? 1 : 2;
      const maxBigs = isMega ? 3 : is535 ? 2 : 4;
      const markovTop = (product.markov_stats?.top_candidates || []).slice(0, 15).map(c => c.number);
      const markovSet = new Set(markovTop);

      // Check locked numbers
      const lockInput = document.getElementById('bao7LockedInput')?.value || '';
      const lockedNums = lockInput.split(/[\s,]+/)
        .map(x => parseInt(x.trim()))
        .filter(x => !isNaN(x) && x >= 1 && x <= maxVal);
      const uniqueLocked = Array.from(new Set(lockedNums)).slice(0, 2);

      // Deterministic Seeded PRNG for Bao 7
      const latestId = product.latest?.id?.replace('#', '') || '0';
      if (forceNew) {
        bao7SeedOffset += 9973;
      } else {
        bao7SeedOffset = 0;
      }
      const seedVal = stringToSeedHash('bao7_' + currentProductKey + '_' + latestId) + bao7SeedOffset;
      const seededRng = createMulberry32(seedVal);

      if (forceNew || !currentBao7Ticket) {
        let bestTicket = null;
        let bestScore = 0;

        for (let attempt = 0; attempt < 30000; attempt++) {
          const cand = [...uniqueLocked];
          while (cand.length < targetBalls) {
            let n;
            if (markovTop.length > 0 && seededRng() < 0.45) {
              n = markovTop[Math.floor(seededRng() * markovTop.length)];
            } else {
              n = Math.floor(seededRng() * maxVal) + 1;
            }
            if (!cand.includes(n) && n <= maxVal) {
              cand.push(n);
            }
          }

          const sorted = cand.sort((a, b) => a - b);
          const sumVal = sorted.reduce((a, b) => a + b, 0);
          if (sumVal < minSum || sumVal > maxSum) continue;

          // Odd / even
          const odds = sorted.filter(n => n % 2 !== 0).length;
          if (targetBalls === 7 && odds !== 3 && odds !== 4) continue;
          if (targetBalls === 6 && odds !== 3 && odds !== 2 && odds !== 4) continue;

          // Big numbers >= 32 (or 25 for 535)
          const bigCount = sorted.filter(n => n >= bigMin).length;
          if (bigCount < minBigs || bigCount > maxBigs) continue;

          // Distinct tails
          const tails = new Set(sorted.map(n => n % 10));
          if (tails.size < 5 && targetBalls === 7) continue;
          if (tails.size < 4 && targetBalls === 6) continue;

          // AC
          const diffs = new Set();
          for (let i = 0; i < sorted.length; i++) {
            for (let j = i + 1; j < sorted.length; j++) {
              diffs.add(Math.abs(sorted[i] - sorted[j]));
            }
          }
          const ac = diffs.size - (targetBalls - 1);
          if (ac < (is535 ? 6 : 8)) continue;

          const markovMatches = sorted.filter(n => markovSet.has(n));
          const score = Math.min(99, 88 + markovMatches.length * 2 + (ac >= 10 ? 3 : 0));
          const spec = is535 ? (Math.floor(Math.random() * 12) + 1) : null;

          bestTicket = {
            numbers: sorted,
            special: spec,
            sum: sumVal,
            ac: ac,
            odds: odds,
            evens: targetBalls - odds,
            bigCount: bigCount,
            distinctTails: tails.size,
            markovMatches: markovMatches,
            score: Math.round(score)
          };
          break;
        }

        currentBao7Ticket = bestTicket || {
          numbers: isMega ? [5, 12, 18, 27, 34, 39, 43] : is535 ? [3, 8, 14, 20, 27, 34] : [8, 16, 22, 35, 39, 42, 53],
          special: is535 ? 7 : null,
          sum: isMega ? 178 : is535 ? 106 : 215,
          ac: is535 ? 8 : 10,
          odds: is535 ? 3 : 4,
          evens: 3,
          bigCount: isMega ? 3 : is535 ? 2 : 4,
          distinctTails: is535 ? 5 : 6,
          markovMatches: isMega ? [18, 34] : is535 ? [14, 27] : [22, 42],
          score: 96
        };
      }

      const t = currentBao7Ticket;
      const ballsContainer = document.getElementById('bao7BallsContainer');
      const checklistContainer = document.getElementById('bao7ChecklistContainer');
      const scoreBadge = document.getElementById('bao7ScoreBadge');

      if (scoreBadge) scoreBadge.textContent = `${t.score}% Thỏa Mãn`;

      if (ballsContainer) {
        let ballsHtml = t.numbers.map(n => {
          const isLocked = uniqueLocked.includes(n);
          const ringCls = isLocked ? 'ring-4 ring-amber-400' : '';
          return `
            <div class="flex flex-col items-center">
              <span class="w-11 h-11 rounded-full bg-gradient-to-br from-emerald-600 to-teal-700 text-white font-mono font-bold text-base flex items-center justify-center shadow-lg shadow-emerald-950/60 ${ringCls}">
                ${String(n).padStart(2, '0')}
              </span>
              ${isLocked ? '<span class="text-[9px] text-amber-400 font-bold mt-1">ĐÃ KHÓA</span>' : ''}
            </div>
          `;
        }).join('');

        if (t.special) {
          ballsHtml += `
            <div class="flex items-center text-slate-500 font-bold text-xl px-1">+</div>
            <div class="flex flex-col items-center">
              <span class="w-11 h-11 rounded-full bg-gradient-to-br from-amber-400 to-yellow-600 text-white font-mono font-bold text-base flex items-center justify-center shadow-lg shadow-amber-950/60 border border-yellow-300">
                ${String(t.special).padStart(2, '0')}
              </span>
              <span class="text-[9px] text-amber-400 font-bold mt-1">ĐẶC BIỆT</span>
            </div>
          `;
        }
        ballsContainer.innerHTML = ballsHtml;
      }

      
      const smsBox = document.getElementById('baoSmsBox');
      const smsDisplay = document.getElementById('baoSmsSyntaxDisplay');
      if (currentProductKey === 'power_655' || currentProductKey === 'power_645') {
        if (smsBox) smsBox.classList.remove('hidden');
        if (smsDisplay) smsDisplay.textContent = getBao7SmsSyntax();
      } else {
        if (smsBox) smsBox.classList.add('hidden');
      }

      if (checklistContainer) {
        checklistContainer.innerHTML = `
          <div class="flex justify-between">
            <span>Tổng điểm ${targetBalls} số:</span>
            <span class="text-emerald-400 font-bold">${t.sum} (Trong dải ${minSum} - ${maxSum})</span>
          </div>
          <div class="flex justify-between">
            <span>Số ngoài dải sinh nhật (≥ ${bigMin}):</span>
            <span class="text-blue-400 font-bold">${t.bigCount} số (Chuẩn chống đám đông)</span>
          </div>
          <div class="flex justify-between">
            <span>Cơ cấu Lẻ - Chẵn:</span>
            <span class="text-amber-400 font-bold">${t.odds} Lẻ - ${t.evens} Chẵn (Tỷ lệ vàng)</span>
          </div>
          <div class="flex justify-between">
            <span>Độ đa dạng đuôi số:</span>
            <span class="text-teal-400 font-bold">${t.distinctTails} đuôi khác nhau</span>
          </div>
          <div class="flex justify-between">
            <span>Trùng ma trận Markov:</span>
            <span class="text-fuchsia-300 font-bold">[${t.markovMatches.map(n => String(n).padStart(2, '0')).join(', ')}]</span>
          </div>
        `;
      }

      // Generate breakdown tickets (omit 1 number at each index)
      const breakdownList = document.getElementById('bao7TicketsBreakdownList');
      if (breakdownList) {
        const tickets = [];
        for (let i = 0; i < t.numbers.length; i++) {
          const sub = t.numbers.filter((_, idx) => idx !== i);
          tickets.push(sub);
        }
        breakdownList.innerHTML = tickets.map((subTicket, idx) => `
          <div class="p-2.5 rounded-xl bg-slate-950 border border-slate-800 flex items-center justify-between hover:border-emerald-500/40 transition">
            <div class="flex items-center gap-2">
              <span class="w-6 h-6 rounded-full bg-slate-800 text-slate-300 text-xs font-mono font-bold flex items-center justify-center">
                #${idx + 1}
              </span>
              <div class="flex items-center gap-1.5 flex-wrap font-mono text-xs">
                ${subTicket.map(n => `
                  <span class="px-1.5 py-0.5 rounded bg-slate-900 text-slate-200 border border-slate-700 font-bold">
                    ${String(n).padStart(2, '0')}
                  </span>
                `).join('')}
                ${t.special ? `
                  <span class="text-slate-500 font-bold">+</span>
                  <span class="px-1.5 py-0.5 rounded bg-amber-950/80 text-amber-300 border border-amber-800 font-bold">
                    ${String(t.special).padStart(2, '0')}
                  </span>
                ` : ''}
              </div>
            </div>
            <button onclick="applyGoldenTicketToChecker('${subTicket.join(', ')}${t.special ? ' + ' + t.special : ''}')" class="px-2 py-1 bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white text-[10px] rounded font-semibold transition">
              Dò vé
            </button>
          </div>
        `).join('');
      }

      lucide.createIcons();
    }

function getStoredBao7Predictions(productKey) {
      const prod = appData?.products?.[productKey];
      if (prod?.bao7_backtest_data?.records) return prod.bao7_backtest_data.records;
      if (prod && Array.isArray(prod.bao7_backtest_history) && prod.bao7_backtest_history.length > 0) {
        return prod.bao7_backtest_history;
      }
      if (productKey === 'power_655') return [{"drawId": "01394", "date": "K\u1ef3 K\u1ebf Ti\u1ebfp", "predicted": [2, 8, 23, 25, 41, 45, 48], "special": 39, "actual": null, "matched": [], "matchCount": 0, "specMatched": false, "cost": 70000, "payout": 0, "netProfit": 0, "prizeDetail": "\u0110ang ch\u1edd quay", "status": "pending"}, {"drawId": "01393", "date": "2026-09-03", "predicted": [5, 14, 27, 33, 38, 39, 41], "special": 8, "actual": [8, 9, 16, 42, 46, 47, 11], "matched": [], "matchCount": 0, "specMatched": false, "cost": 70000, "payout": 0, "netProfit": -70000, "prizeDetail": "Kh\u00f4ng tr\u00fang", "status": "completed"}, {"drawId": "01392", "date": "2026-09-01", "predicted": [5, 8, 27, 28, 39, 45, 49], "special": 14, "actual": [1, 17, 41, 44, 49, 55, 45], "matched": [49], "matchCount": 1, "specMatched": false, "cost": 70000, "payout": 0, "netProfit": -70000, "prizeDetail": "Kh\u00f4ng tr\u00fang", "status": "completed"}, {"drawId": "01391", "date": "2026-08-29", "predicted": [2, 8, 27, 28, 38, 40, 49], "special": 39, "actual": [5, 10, 15, 29, 34, 45, 24], "matched": [], "matchCount": 0, "specMatched": false, "cost": 70000, "payout": 0, "netProfit": -70000, "prizeDetail": "Kh\u00f4ng tr\u00fang", "status": "completed"}, {"drawId": "01390", "date": "2026-08-27", "predicted": [1, 14, 18, 33, 38, 44, 45], "special": 8, "actual": [1, 3, 11, 21, 26, 44, 10], "matched": [1, 44], "matchCount": 2, "specMatched": false, "cost": 70000, "payout": 0, "netProfit": -70000, "prizeDetail": "Kh\u00f4ng tr\u00fang", "status": "completed"}, {"drawId": "01389", "date": "2026-08-25", "predicted": [5, 11, 23, 24, 28, 45, 55], "special": 8, "actual": [5, 7, 13, 18, 31, 40, 14], "matched": [5], "matchCount": 1, "specMatched": false, "cost": 70000, "payout": 0, "netProfit": -70000, "prizeDetail": "Kh\u00f4ng tr\u00fang", "status": "completed"}, {"drawId": "01388", "date": "2026-08-22", "predicted": [5, 8, 22, 33, 38, 45, 53], "special": 1, "actual": [9, 18, 19, 21, 25, 36, 8], "matched": [], "matchCount": 0, "specMatched": false, "cost": 70000, "payout": 0, "netProfit": -70000, "prizeDetail": "Kh\u00f4ng tr\u00fang", "status": "completed"}, {"drawId": "01387", "date": "2026-08-20", "predicted": [1, 5, 25, 32, 33, 41, 55], "special": 8, "actual": [2, 8, 29, 38, 39, 51, 47], "matched": [], "matchCount": 0, "specMatched": false, "cost": 70000, "payout": 0, "netProfit": -70000, "prizeDetail": "Kh\u00f4ng tr\u00fang", "status": "completed"}, {"drawId": "01386", "date": "2026-08-18", "predicted": [2, 3, 17, 23, 40, 45, 48], "special": 8, "actual": [3, 15, 18, 38, 41, 48, 30], "matched": [3, 48], "matchCount": 2, "specMatched": false, "cost": 70000, "payout": 0, "netProfit": -70000, "prizeDetail": "Kh\u00f4ng tr\u00fang", "status": "completed"}, {"drawId": "01385", "date": "2026-08-15", "predicted": [2, 14, 16, 32, 33, 40, 53], "special": 8, "actual": [16, 20, 25, 27, 30, 50, 2], "matched": [16], "matchCount": 1, "specMatched": false, "cost": 70000, "payout": 0, "netProfit": -70000, "prizeDetail": "Kh\u00f4ng tr\u00fang", "status": "completed"}, {"drawId": "01384", "date": "2026-08-13", "predicted": [4, 14, 17, 28, 33, 40, 48], "special": 8, "actual": [5, 9, 27, 29, 45, 46, 42], "matched": [], "matchCount": 0, "specMatched": false, "cost": 70000, "payout": 0, "netProfit": -70000, "prizeDetail": "Kh\u00f4ng tr\u00fang", "status": "completed"}];
      if (productKey === 'power_645') return [{"drawId": "01558", "date": "K\u1ef3 K\u1ebf Ti\u1ebfp", "predicted": [2, 3, 15, 28, 30, 37, 45], "special": null, "actual": null, "matched": [], "matchCount": 0, "specMatched": false, "cost": 70000, "payout": 0, "netProfit": 0, "prizeDetail": "\u0110ang ch\u1edd quay", "status": "pending"}, {"drawId": "01557", "date": "2026-09-02", "predicted": [2, 11, 13, 16, 35, 41, 45], "special": null, "actual": [6, 9, 27, 29, 35, 44], "matched": [35], "matchCount": 1, "specMatched": false, "cost": 70000, "payout": 0, "netProfit": -70000, "prizeDetail": "Kh\u00f4ng tr\u00fang", "status": "completed"}, {"drawId": "01556", "date": "2026-08-30", "predicted": [2, 20, 22, 28, 31, 35, 45], "special": null, "actual": [1, 3, 12, 15, 37, 45], "matched": [45], "matchCount": 1, "specMatched": false, "cost": 70000, "payout": 0, "netProfit": -70000, "prizeDetail": "Kh\u00f4ng tr\u00fang", "status": "completed"}, {"drawId": "01555", "date": "2026-08-28", "predicted": [9, 11, 17, 20, 30, 31, 35], "special": null, "actual": [3, 13, 15, 22, 36, 39], "matched": [], "matchCount": 0, "specMatched": false, "cost": 70000, "payout": 0, "netProfit": -70000, "prizeDetail": "Kh\u00f4ng tr\u00fang", "status": "completed"}, {"drawId": "01554", "date": "2026-08-26", "predicted": [6, 11, 14, 17, 30, 43, 45], "special": null, "actual": [3, 10, 11, 16, 33, 40], "matched": [11], "matchCount": 1, "specMatched": false, "cost": 70000, "payout": 0, "netProfit": -70000, "prizeDetail": "Kh\u00f4ng tr\u00fang", "status": "completed"}, {"drawId": "01553", "date": "2026-08-23", "predicted": [11, 14, 16, 17, 32, 36, 43], "special": null, "actual": [4, 16, 17, 22, 32, 39], "matched": [16, 17, 32], "matchCount": 3, "specMatched": false, "cost": 70000, "payout": 120000, "netProfit": 50000, "prizeDetail": "4 Gi\u1ea3i Ba (30k)", "status": "completed"}, {"drawId": "01552", "date": "2026-08-21", "predicted": [6, 11, 13, 26, 27, 39, 45], "special": null, "actual": [7, 26, 31, 38, 43, 45], "matched": [26, 45], "matchCount": 2, "specMatched": false, "cost": 70000, "payout": 0, "netProfit": -70000, "prizeDetail": "Kh\u00f4ng tr\u00fang", "status": "completed"}, {"drawId": "01551", "date": "2026-08-19", "predicted": [3, 6, 11, 26, 36, 44, 45], "special": null, "actual": [6, 15, 18, 33, 40, 43], "matched": [6], "matchCount": 1, "specMatched": false, "cost": 70000, "payout": 0, "netProfit": -70000, "prizeDetail": "Kh\u00f4ng tr\u00fang", "status": "completed"}, {"drawId": "01550", "date": "2026-08-16", "predicted": [9, 11, 13, 17, 28, 41, 42], "special": null, "actual": [6, 7, 15, 19, 36, 41], "matched": [41], "matchCount": 1, "specMatched": false, "cost": 70000, "payout": 0, "netProfit": -70000, "prizeDetail": "Kh\u00f4ng tr\u00fang", "status": "completed"}, {"drawId": "01549", "date": "2026-08-14", "predicted": [6, 9, 14, 28, 30, 37, 41], "special": null, "actual": [7, 9, 13, 31, 35, 44], "matched": [9], "matchCount": 1, "specMatched": false, "cost": 70000, "payout": 0, "netProfit": -70000, "prizeDetail": "Kh\u00f4ng tr\u00fang", "status": "completed"}, {"drawId": "01548", "date": "2026-08-12", "predicted": [3, 6, 22, 26, 31, 32, 44], "special": null, "actual": [15, 17, 22, 29, 33, 40], "matched": [22], "matchCount": 1, "specMatched": false, "cost": 70000, "payout": 0, "netProfit": -70000, "prizeDetail": "Kh\u00f4ng tr\u00fang", "status": "completed"}];
      if (productKey === 'power_535') return [{"drawId": "00865", "date": "K\u1ef3 K\u1ebf Ti\u1ebfp", "predicted": [1, 11, 13, 18, 32, 33], "special": 9, "actual": null, "matched": [], "matchCount": 0, "specMatched": false, "cost": 60000, "payout": 0, "netProfit": 0, "prizeDetail": "\u0110ang ch\u1edd quay", "status": "pending"}, {"drawId": "00864", "date": "2026-09-03", "predicted": [1, 7, 11, 25, 30, 32], "special": 9, "actual": [7, 17, 23, 24, 27, 3], "matched": [7], "matchCount": 1, "specMatched": false, "cost": 60000, "payout": 0, "netProfit": -60000, "prizeDetail": "Kh\u00f4ng tr\u00fang", "status": "completed"}, {"drawId": "00863", "date": "2026-09-03", "predicted": [7, 11, 12, 17, 28, 30], "special": 9, "actual": [2, 15, 23, 24, 30, 12], "matched": [30], "matchCount": 1, "specMatched": false, "cost": 60000, "payout": 0, "netProfit": -60000, "prizeDetail": "Kh\u00f4ng tr\u00fang", "status": "completed"}, {"drawId": "00862", "date": "2026-09-02", "predicted": [2, 9, 19, 20, 32, 34], "special": 9, "actual": [6, 7, 9, 11, 32, 12], "matched": [9, 32], "matchCount": 2, "specMatched": false, "cost": 60000, "payout": 0, "netProfit": -60000, "prizeDetail": "Kh\u00f4ng tr\u00fang", "status": "completed"}, {"drawId": "00861", "date": "2026-09-02", "predicted": [3, 7, 8, 19, 32, 34], "special": 7, "actual": [7, 11, 18, 26, 29, 6], "matched": [7], "matchCount": 1, "specMatched": false, "cost": 60000, "payout": 0, "netProfit": -60000, "prizeDetail": "Kh\u00f4ng tr\u00fang", "status": "completed"}, {"drawId": "00860", "date": "2026-09-01", "predicted": [1, 2, 19, 22, 26, 35], "special": 7, "actual": [3, 4, 6, 15, 22, 9], "matched": [22], "matchCount": 1, "specMatched": false, "cost": 60000, "payout": 0, "netProfit": -60000, "prizeDetail": "Kh\u00f4ng tr\u00fang", "status": "completed"}, {"drawId": "00859", "date": "2026-09-01", "predicted": [2, 3, 17, 20, 28, 30], "special": 7, "actual": [9, 18, 20, 27, 34, 12], "matched": [20], "matchCount": 1, "specMatched": false, "cost": 60000, "payout": 0, "netProfit": -60000, "prizeDetail": "Kh\u00f4ng tr\u00fang", "status": "completed"}, {"drawId": "00858", "date": "2026-08-31", "predicted": [2, 10, 13, 15, 34, 35], "special": 7, "actual": [1, 5, 25, 27, 28, 12], "matched": [], "matchCount": 0, "specMatched": false, "cost": 60000, "payout": 0, "netProfit": -60000, "prizeDetail": "Kh\u00f4ng tr\u00fang", "status": "completed"}, {"drawId": "00857", "date": "2026-08-31", "predicted": [7, 12, 13, 16, 26, 33], "special": 7, "actual": [4, 11, 13, 18, 27, 1], "matched": [13], "matchCount": 1, "specMatched": false, "cost": 60000, "payout": 0, "netProfit": -60000, "prizeDetail": "Kh\u00f4ng tr\u00fang", "status": "completed"}, {"drawId": "00856", "date": "2026-08-30", "predicted": [3, 15, 19, 20, 22, 30], "special": 7, "actual": [13, 15, 17, 26, 30, 10], "matched": [15, 30], "matchCount": 2, "specMatched": false, "cost": 60000, "payout": 0, "netProfit": -60000, "prizeDetail": "Kh\u00f4ng tr\u00fang", "status": "completed"}, {"drawId": "00855", "date": "2026-08-30", "predicted": [1, 8, 10, 23, 34, 35], "special": 7, "actual": [2, 4, 12, 21, 28, 7], "matched": [], "matchCount": 0, "specMatched": true, "cost": 60000, "payout": 60000, "netProfit": 0, "prizeDetail": "6 Gi\u1ea3i KK (10k)", "status": "completed"}];
      return [];
    }

    function renderBao7History() {
      const tbody = document.getElementById('bao7HistoryTableBody');
      if (!tbody) return;

      const product = appData?.products?.[currentProductKey];
      const kpiContainer = document.getElementById('bao7BacktestKpis');
      const kpis = product?.bao7_backtest_data?.kpis;
      if (kpiContainer && kpis) {
        kpiContainer.innerHTML = `
          <div class="p-3 bg-slate-950 rounded-xl border border-slate-800">
            <span class="text-[10px] text-slate-500 block uppercase font-mono">Quy Mô Kiểm Định</span>
            <span class="text-sm font-bold text-white font-mono mt-0.5 block">${kpis.total_draws} Kỳ Bao Thật</span>
            <span class="text-[10px] text-slate-400">Walk-Forward 100%</span>
          </div>
          <div class="p-3 bg-slate-950 rounded-xl border border-emerald-500/30">
            <span class="text-[10px] text-emerald-400 block uppercase font-mono">Trúng ≥ 3 Số (4 Giải Ba)</span>
            <span class="text-sm font-bold text-emerald-400 font-mono mt-0.5 block">${kpis.hit_3_plus} Kỳ (${kpis.win_rate_pct}%)</span>
            <span class="text-[10px] text-slate-400">Lời vốn giải Ba</span>
          </div>
          <div class="p-3 bg-slate-950 rounded-xl border border-amber-500/30">
            <span class="text-[10px] text-amber-400 block uppercase font-mono">Trúng ≥ 4 Số</span>
            <span class="text-sm font-bold text-amber-400 font-mono mt-0.5 block">${kpis.hit_4_plus} Kỳ</span>
            <span class="text-[10px] text-slate-400">Ăn 3 Nhì + 4 Ba</span>
          </div>
          <div class="p-3 bg-slate-950 rounded-xl border border-slate-800">
            <span class="text-[10px] text-slate-500 block uppercase font-mono">Tổng Thu Thưởng</span>
            <span class="text-sm font-bold ${kpis.total_payout > 0 ? 'text-emerald-400' : 'text-slate-400'} font-mono mt-0.5 block">${kpis.total_payout.toLocaleString('vi-VN')} đ</span>
            <span class="text-[10px] text-slate-400">Vốn: ${(kpis.total_cost).toLocaleString('vi-VN')} đ</span>
          </div>
        `;
      }

      const list = getStoredBao7Predictions(currentProductKey);
      if (!list.length) {
        tbody.innerHTML = `<tr><td colspan="5" class="py-6 text-center text-slate-500">Chưa có bản ghi Bao 7 nào được lưu cho sản phẩm này.</td></tr>`;
        return;
      }

      const is535 = currentProductKey === 'power_535';
      const is655 = currentProductKey === 'power_655';

      tbody.innerHTML = list.map(item => {
        const isPending = !item.actual;
        let matchCount = 0;
        let matchSpecial = false;
        let prizeDesc = '';
        let profitDesc = '';

        if (!isPending) {
          // For 5/35: actual is [c1,c2,c3,c4,c5,db], predicted (bao6) is [n1..n6,db]
          // For 6/55: actual is [c1..c6,db], predicted (bao7) is [n1..n7]
          // For 6/45: actual is [c1..c6], predicted (bao7) is [n1..n7]
          const actualMainCount = is535 ? 5 : 6;
          const actualMain = item.actual.slice(0, actualMainCount);
          const actualMainSet = new Set(actualMain);

          if (is535) {
            // Bao 6: predicted has 6 main numbers + 1 special
            const predMain = item.predicted.slice(0, 6);
            matchCount = predMain.filter(n => actualMainSet.has(n)).length;
            const predSpec = item.predicted[6];
            const actualSpec = item.actual[5];
            matchSpecial = predSpec !== undefined && actualSpec !== undefined && predSpec === actualSpec;
          } else {
            // 6/55 or 6/45: predicted has 7 main numbers
            const predMain = item.predicted.slice(0, 7);
            matchCount = predMain.filter(n => actualMainSet.has(n)).length;
          }

          if (currentProductKey === 'power_655') {
            const hasSpecial = item.specialBall && item.predicted.includes(item.specialBall);
            if (matchCount === 6 && hasSpecial) {
              prizeDesc = '<span class="text-amber-400 font-bold">🏆 1 JP1 + 1 JP2 + 5 GIẢI NHẤT</span>';
              profitDesc = '<span class="text-amber-400 font-bold">JP1 + JP2 + 200 Triệu</span>';
            } else if (matchCount === 6) {
              prizeDesc = '<span class="text-amber-400 font-bold">🏆 1 JP1 + 6 GIẢI NHẤT (240tr)</span>';
              profitDesc = '<span class="text-amber-400 font-bold">JP1 + 240.000.000đ</span>';
            } else if (matchCount === 5 && hasSpecial) {
              prizeDesc = '<span class="text-amber-300 font-bold">💎 1 JP2 + 1 NHẤT + 5 NHÌ</span>';
              profitDesc = '<span class="text-amber-300 font-bold">JP2 + 42.500.000đ</span>';
            } else if (matchCount === 5) {
              prizeDesc = '<span class="text-rose-400 font-bold">2 Giải Nhất (80tr) + 5 Giải Nhì</span>';
              profitDesc = '<span class="text-emerald-400 font-bold">+82.430.000 VNĐ</span>';
            } else if (matchCount === 4) {
              prizeDesc = '<span class="text-emerald-400 font-bold">3 Giải Nhì + 4 Giải Ba</span>';
              profitDesc = '<span class="text-emerald-400 font-bold">+1.630.000 VNĐ</span>';
            } else if (matchCount === 3) {
              prizeDesc = '<span class="text-blue-400 font-bold">4 Giải Ba (200.000đ)</span>';
              profitDesc = '<span class="text-emerald-400 font-bold">+130.000 VNĐ</span>';
            } else {
              prizeDesc = '<span class="text-slate-500">Không trúng</span>';
              profitDesc = '<span class="text-rose-400">-70.000 VNĐ</span>';
            }
          } else if (currentProductKey === 'power_645') {
            // Mega 6/45
            if (matchCount === 6) {
              prizeDesc = '<span class="text-amber-400 font-bold">🏆 1 JACKPOT + 6 GIẢI NHẤT</span>';
              profitDesc = '<span class="text-amber-400 font-bold">Jackpot + 60.000.000đ</span>';
            } else if (matchCount === 5) {
              prizeDesc = '<span class="text-rose-400 font-bold">2 Giải Nhất (20tr) + 5 Giải Nhì</span>';
              profitDesc = '<span class="text-emerald-400 font-bold">+21.430.000 VNĐ</span>';
            } else if (matchCount === 4) {
              prizeDesc = '<span class="text-emerald-400 font-bold">3 Giải Nhì + 4 Giải Ba</span>';
              profitDesc = '<span class="text-emerald-400 font-bold">+950.000 VNĐ</span>';
            } else if (matchCount === 3) {
              prizeDesc = '<span class="text-blue-400 font-bold">4 Giải Ba (120.000đ)</span>';
              profitDesc = '<span class="text-emerald-400 font-bold">+50.000 VNĐ</span>';
            } else {
              prizeDesc = '<span class="text-slate-500">Không trúng</span>';
              profitDesc = '<span class="text-rose-400">-70.000 VNĐ</span>';
            }
          } else {
            // Power 5/35 Bao 6 (6 số chính + 1 đặc biệt, vốn 60.000đ)
            if (matchCount === 5 && matchSpecial) {
              prizeDesc = '<span class="text-amber-400 font-bold">🏆 1 ĐỘC ĐẮC + 5 GIẢI NHÌ</span>';
              profitDesc = '<span class="text-amber-400 font-bold">Jackpot (6+ Tỷ)</span>';
            } else if (matchCount === 5) {
              prizeDesc = '<span class="text-rose-400 font-bold">1 Giải Nhất (40tr) + 5 Giải Ba</span>';
              profitDesc = '<span class="text-emerald-400 font-bold">+40.190.000 VNĐ</span>';
            } else if (matchCount === 4 && matchSpecial) {
              prizeDesc = '<span class="text-emerald-400 font-bold">2 Giải Nhì (1tr) + 4 Giải Tư</span>';
              profitDesc = '<span class="text-emerald-400 font-bold">+1.140.000 VNĐ</span>';
            } else if (matchCount === 4) {
              prizeDesc = '<span class="text-blue-400 font-bold">2 Giải Ba (2 x 50k)</span>';
              profitDesc = '<span class="text-emerald-400 font-bold">+40.000 VNĐ</span>';
            } else if (matchCount === 3 && matchSpecial) {
              prizeDesc = '<span class="text-emerald-400 font-bold">3 Giải Tư (150k) + 3 Giải KK</span>';
              profitDesc = '<span class="text-emerald-400 font-bold">+120.000 VNĐ</span>';
            } else if (matchCount === 3) {
              prizeDesc = '<span class="text-blue-400 font-bold">3 Giải Năm (3 x 30k)</span>';
              profitDesc = '<span class="text-emerald-400 font-bold">+30.000 VNĐ</span>';
            } else if (matchSpecial) {
              prizeDesc = '<span class="text-amber-300 font-bold">⭐ 6 Giải KK (Trúng Cầu ĐB)</span>';
              profitDesc = '<span class="text-emerald-400 font-bold">60.000đ (Hòa Vốn 100%)</span>';
            } else {
              prizeDesc = '<span class="text-slate-500">Không trúng</span>';
              profitDesc = '<span class="text-rose-400">-60.000 VNĐ</span>';
            }
          }
        } else {
          prizeDesc = '<span class="text-amber-400 animate-pulse font-sans">⏳ Đang chờ mở thưởng</span>';
          profitDesc = `<span class="text-slate-500">Đã chi ${is535 ? '60.000đ' : '70.000đ'}</span>`;
        }

        return `
          <tr class="hover:bg-slate-800/40 transition">
            <td class="py-3 px-4 text-amber-400 font-bold">#${item.drawId}</td>
            <td class="py-3 px-4">
              ${renderBallsWithSpecial(item.predicted, item.actual, true, currentProductKey)}
            </td>
            <td class="py-3 px-4">
              ${renderActualBallsWithSpecial(item.actual, currentProductKey)}
            </td>
            <td class="py-3 px-4 text-center">
              ${prizeDesc}
            </td>
            <td class="py-3 px-4 text-right">
              ${profitDesc}
            </td>
          </tr>
        `;
      }).join('');
    }

    function saveBao7PredictionToHistory() {
      if (!currentBao7Ticket) return;
      const product = appData?.products?.[currentProductKey];
      const latestIdNum = parseInt(product?.latest?.id?.replace('#', '') || '0');
      const nextId = latestIdNum ? String(latestIdNum + 1).padStart(5, '0') : 'Kỳ Tiếp';
      const storageKey = `vietlott_bao7_history_${currentProductKey}`;
      const list = getStoredBao7Predictions(currentProductKey);

      const toSaveNums = (currentProductKey === 'power_535' && currentBao7Ticket.special)
        ? [...currentBao7Ticket.numbers, currentBao7Ticket.special]
        : currentBao7Ticket.numbers;

      const existingIdx = list.findIndex(item => item.drawId === nextId);
      if (existingIdx !== -1) {
        list[existingIdx].predicted = toSaveNums;
      } else {
        list.unshift({
          drawId: nextId,
          predicted: toSaveNums,
          actual: null,
          status: 'pending'
        });
      }

      localStorage.setItem(storageKey, JSON.stringify(list));
      renderBao7History();
      
      const gameLabel = currentProductKey === 'power_655' ? 'Power 6/55' : currentProductKey === 'power_645' ? 'Mega 6/45' : 'Power 5/35';
      saveTicketToNotebook({
        game: currentProductKey,
        gameName: gameLabel,
        drawId: nextId,
        type: currentProductKey === 'power_535' ? 'bao6' : 'bao7',
        numbers: toSaveNums,
        cost: currentProductKey === 'power_535' ? 60000 : 70000
      });
    }

    function clearBao7History() {
      if (confirm("Bạn có chắc chắn muốn đặt lại lịch sử Bao 7 về mặc định?")) {
        const storageKey = `vietlott_bao7_history_${currentProductKey}`;
        localStorage.removeItem(storageKey);
        renderBao7History();
      }
    }

    function applyBao7ToSim() {
      if (!currentBao7Ticket) return;
      const ticketStr = currentBao7Ticket.numbers.slice(0, 6).join(', ');
      document.getElementById('simCustomNumbers').value = ticketStr;
      document.getElementById('simStrategySelect').value = 'fixed_ticket';
      document.getElementById('simCustomTicketWrap').classList.remove('hidden');
      switchView('simulator');
      runSimulation();
    }
