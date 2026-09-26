/**
 * Admin Dashboard Module
 * Visualizes system-wide metrics, scan audit logs, and skill gap intelligence.
 */
const Admin = {
  stats: null,

  async load() {
    try {
      this.stats = await API.get(CONFIG.ENDPOINTS.ADMIN_STATS);
      this.render();
    } catch (err) {
      App.showToast(err.message || "Failed to load admin metrics.", "error");
    }
  },

  render() {
    if (!this.stats) return;

    // 1. Stat cards
    document.getElementById("stat-total-scans").textContent = this.stats.total_scans;
    document.getElementById("stat-total-users").textContent = this.stats.total_users;
    document.getElementById("stat-avg-score").textContent = `${this.stats.avg_ats_score}%`;
    document.getElementById("stat-pass-rate").textContent = `${this.stats.pass_rate_percent}%`;

    // 2. Score Distribution
    const dist = this.stats.score_distribution || {};
    const total = this.stats.total_scans || 1;
    this.setDistBar("dist-bar-low", (dist["0-40"] || 0), total);
    this.setDistBar("dist-bar-mid", (dist["41-60"] || 0), total);
    this.setDistBar("dist-bar-high", (dist["61-80"] || 0), total);
    this.setDistBar("dist-bar-excel", (dist["81-100"] || 0), total);

    // 3. Top Missing Skills
    const missingContainer = document.getElementById("admin-top-missing-skills");
    if (missingContainer) {
      const topSkills = this.stats.top_missing_skills || [];
      if (topSkills.length) {
        missingContainer.innerHTML = topSkills.map((item, idx) => `
          <div class="flex items-center justify-between p-2 rounded-lg bg-slate-50 border border-slate-200 text-xs">
            <div class="flex items-center gap-2">
              <span class="w-5 h-5 rounded-full bg-slate-200 text-slate-700 flex items-center justify-center font-bold text-[10px]">${idx + 1}</span>
              <span class="font-bold text-slate-800">${item.skill}</span>
            </div>
            <span class="px-2 py-0.5 font-mono text-[11px] font-semibold bg-rose-100 text-rose-800 rounded">${item.count} resumes</span>
          </div>
        `).join("");
      } else {
        missingContainer.innerHTML = '<span class="text-xs text-slate-400 italic">No missing skill patterns recorded yet.</span>';
      }
    }

    // 4. Recent Scans Table
    const recentTableBody = document.getElementById("admin-recent-scans-tbody");
    if (recentTableBody) {
      const recent = this.stats.recent_scans || [];
      if (recent.length) {
        recentTableBody.innerHTML = recent.map(scan => `
          <tr class="hover:bg-slate-50 transition-colors border-b border-slate-100 text-xs">
            <td class="py-3 px-4 font-medium text-slate-900">${scan.job_title}</td>
            <td class="py-3 px-4 text-slate-500 font-mono">${scan.filename}</td>
            <td class="py-3 px-4">
              <span class="font-bold ${scan.ats_score >= 70 ? 'text-emerald-600' : (scan.ats_score >= 50 ? 'text-amber-600' : 'text-rose-600')}">
                ${scan.ats_score}%
              </span>
            </td>
            <td class="py-3 px-4 text-slate-400">${new Date(scan.created_at).toLocaleDateString()}</td>
            <td class="py-3 px-4">
              <button onclick="History.viewDetail('${scan.id}')" class="text-indigo-600 hover:text-indigo-800 font-semibold">View</button>
            </td>
          </tr>
        `).join("");
      } else {
        recentTableBody.innerHTML = '<tr><td colspan="5" class="py-6 text-center text-slate-400">No scans logged yet.</td></tr>';
      }
    }
  },

  setDistBar(elId, count, total) {
    const el = document.getElementById(elId);
    if (!el) return;
    const pct = total > 0 ? Math.round((count / total) * 100) : 0;
    el.style.width = `${Math.max(5, pct)}%`;
    el.textContent = `${count} (${pct}%)`;
  }
};
