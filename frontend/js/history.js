/**
 * History Module
 * Manages and displays the user's previous resume analyses.
 */
const History = {
  items: [],

  async load() {
    const listContainer = document.getElementById("history-list");
    const emptyState = document.getElementById("history-empty");

    if (listContainer) {
      listContainer.innerHTML = '<div class="p-8 text-center text-slate-400">Loading scan history...</div>';
    }

    try {
      this.items = await API.get(CONFIG.ENDPOINTS.HISTORY);
      this.render();
    } catch (err) {
      if (listContainer) {
        listContainer.innerHTML = `<div class="p-8 text-center text-rose-500 text-sm">Failed to load history: ${err.message}</div>`;
      }
    }
  },

  render() {
    const listContainer = document.getElementById("history-list");
    const emptyState = document.getElementById("history-empty");

    if (!listContainer) return;

    if (!this.items || this.items.length === 0) {
      listContainer.innerHTML = "";
      if (emptyState) emptyState.classList.remove("hidden");
      return;
    }

    if (emptyState) emptyState.classList.add("hidden");

    listContainer.innerHTML = this.items.map(item => {
      const score = item.ats_score;
      const scoreColor = score >= 85 ? "text-emerald-600 bg-emerald-50 border-emerald-200"
        : (score >= 70 ? "text-indigo-600 bg-indigo-50 border-indigo-200"
        : (score >= 50 ? "text-amber-600 bg-amber-50 border-amber-200" : "text-rose-600 bg-rose-50 border-rose-200"));

      const formattedDate = new Date(item.created_at).toLocaleDateString(undefined, {
        year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit'
      });

      return `
        <div class="p-4 bg-white border border-slate-200 rounded-xl shadow-sm hover:shadow-md transition-all flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div class="flex items-start gap-3">
            <div class="w-12 h-12 rounded-xl flex items-center justify-center font-bold text-lg border ${scoreColor}">
              ${score}
            </div>
            <div>
              <h4 class="text-sm font-bold text-slate-900">${item.job_title}</h4>
              <p class="text-xs text-slate-500 font-mono mt-0.5">${item.filename}</p>
              <div class="flex items-center gap-2 mt-1.5">
                <span class="text-[11px] text-slate-400">${formattedDate}</span>
                <span class="text-slate-300">•</span>
                <span class="text-[11px] font-semibold text-slate-600">${item.match_level}</span>
              </div>
            </div>
          </div>
          <div class="flex items-center gap-2 self-end sm:self-center">
            <button onclick="History.viewDetail('${item.id}')" class="px-3 py-1.5 text-xs font-semibold bg-indigo-50 hover:bg-indigo-100 text-indigo-700 rounded-lg transition-colors flex items-center gap-1.5">
              <span>View Report</span>
              <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/></svg>
            </button>
            <button onclick="History.deleteItem('${item.id}')" class="p-1.5 text-slate-400 hover:text-rose-600 hover:bg-rose-50 rounded-lg transition-colors" title="Delete Scan">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/></svg>
            </button>
          </div>
        </div>
      `;
    }).join("");
  },

  async viewDetail(id) {
    try {
      App.showToast("Loading report...", "info");
      const detail = await API.get(`${CONFIG.ENDPOINTS.HISTORY}/${id}`);
      Analyzer.currentAnalysis = detail;
      App.switchTab("analyzer");
      Analyzer.renderResults(detail);
      document.getElementById("results-section").scrollIntoView({ behavior: "smooth" });
    } catch (e) {
      App.showToast(e.message || "Could not load report details.", "error");
    }
  },

  async deleteItem(id) {
    if (!confirm("Are you sure you want to delete this scan from history?")) return;
    try {
      await API.delete(`${CONFIG.ENDPOINTS.HISTORY}/${id}`);
      App.showToast("Report deleted from history.", "info");
      this.items = this.items.filter(i => i.id !== id);
      this.render();
    } catch (e) {
      App.showToast(e.message || "Failed to delete report.", "error");
    }
  }
};
