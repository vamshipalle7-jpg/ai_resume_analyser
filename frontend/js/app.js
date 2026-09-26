/**
 * Main Application Orchestrator
 */
const App = {
  activeTab: "analyzer",

  init() {
    Auth.init();
    Analyzer.init();
    this.setupNavigation();
    this.setupAuthModals();
    this.checkSystemHealth();
  },

  setupNavigation() {
    const tabs = ["analyzer", "history", "admin"];
    tabs.forEach(tab => {
      const btn = document.getElementById(`nav-${tab}-btn`);
      if (btn) {
        btn.addEventListener("click", () => this.switchTab(tab));
      }
    });
  },

  switchTab(tabName) {
    this.activeTab = tabName;
    const views = {
      analyzer: document.getElementById("view-analyzer"),
      history: document.getElementById("view-history"),
      admin: document.getElementById("view-admin")
    };

    // Toggle views
    Object.keys(views).forEach(key => {
      if (views[key]) {
        if (key === tabName) {
          views[key].classList.remove("hidden");
        } else {
          views[key].classList.add("hidden");
        }
      }

      const btn = document.getElementById(`nav-${key}-btn`);
      if (btn) {
        if (key === tabName) {
          btn.className = "px-3 py-1.5 text-xs sm:text-sm font-bold text-indigo-600 bg-indigo-50 border border-indigo-200 rounded-lg transition-all";
        } else {
          btn.className = "px-3 py-1.5 text-xs sm:text-sm font-medium text-slate-600 hover:text-indigo-600 hover:bg-slate-100 rounded-lg transition-all";
        }
      }
    });

    // Trigger tab-specific loaders
    if (tabName === "history") {
      History.load();
    } else if (tabName === "admin") {
      Admin.load();
    }
  },

  setupAuthModals() {
    const authModal = document.getElementById("auth-modal");
    const openLoginBtn = document.getElementById("btn-open-login");
    const closeBtn = document.getElementById("close-auth-modal");

    if (openLoginBtn && authModal) {
      openLoginBtn.addEventListener("click", () => {
        authModal.classList.remove("hidden");
      });
    }

    if (closeBtn && authModal) {
      closeBtn.addEventListener("click", () => {
        authModal.classList.add("hidden");
      });
    }

    // Modal tabs: signin vs signup
    const tabSignin = document.getElementById("tab-signin-btn");
    const tabSignup = document.getElementById("tab-signup-btn");
    const formSignin = document.getElementById("form-signin");
    const formSignup = document.getElementById("form-signup");

    if (tabSignin && tabSignup) {
      tabSignin.addEventListener("click", () => {
        tabSignin.className = "flex-1 py-2 text-xs font-bold text-indigo-600 border-b-2 border-indigo-600";
        tabSignup.className = "flex-1 py-2 text-xs font-medium text-slate-500 hover:text-slate-800";
        formSignin.classList.remove("hidden");
        formSignup.classList.add("hidden");
      });

      tabSignup.addEventListener("click", () => {
        tabSignup.className = "flex-1 py-2 text-xs font-bold text-indigo-600 border-b-2 border-indigo-600";
        tabSignin.className = "flex-1 py-2 text-xs font-medium text-slate-500 hover:text-slate-800";
        formSignup.classList.remove("hidden");
        formSignin.classList.add("hidden");
      });
    }

    // Handle Form Submissions
    if (formSignin) {
      formSignin.addEventListener("submit", async (e) => {
        e.preventDefault();
        const email = document.getElementById("signin-email").value.trim();
        const pass = document.getElementById("signin-pass").value;
        try {
          await Auth.login(email, pass);
          authModal.classList.add("hidden");
          App.showToast("Signed in successfully!", "success");
        } catch (err) {
          App.showToast(err.message, "error");
        }
      });
    }

    if (formSignup) {
      formSignup.addEventListener("submit", async (e) => {
        e.preventDefault();
        const name = document.getElementById("signup-name").value.trim();
        const email = document.getElementById("signup-email").value.trim();
        const pass = document.getElementById("signup-pass").value;
        try {
          await Auth.register(email, pass, name);
          authModal.classList.add("hidden");
          App.showToast("Account created successfully!", "success");
        } catch (err) {
          App.showToast(err.message, "error");
        }
      });
    }
  },

  fillDemoUser(role) {
    const emailInput = document.getElementById("signin-email");
    const passInput = document.getElementById("signin-pass");
    if (role === "admin") {
      if (emailInput) emailInput.value = "admin@analyzer.ai";
      if (passInput) passInput.value = "Admin@123456";
    } else {
      if (emailInput) emailInput.value = "demo@analyzer.ai";
      if (passInput) passInput.value = "Admin@123456";
    }
    const form = document.getElementById("form-signin");
    if (form) form.dispatchEvent(new Event("submit"));
  },

  async checkSystemHealth() {
    const statusDot = document.getElementById("status-indicator-dot");
    const statusText = document.getElementById("status-indicator-text");
    const dbModeBadge = document.getElementById("db-mode-badge");

    try {
      const health = await API.checkHealth();
      if (health.status === "operational") {
        if (statusDot) statusDot.className = "w-2 h-2 rounded-full bg-emerald-500 animate-pulse";
        if (statusText) statusText.textContent = "API Online";
        if (dbModeBadge) {
          dbModeBadge.textContent = health.database_mode === "supabase" ? "Supabase Connected" : "Local Database Mode";
          dbModeBadge.className = health.database_mode === "supabase"
            ? "px-2 py-0.5 text-[10px] font-semibold bg-emerald-100 text-emerald-800 rounded-full"
            : "px-2 py-0.5 text-[10px] font-semibold bg-blue-100 text-blue-800 rounded-full cursor-pointer";
        }
      }
    } catch (_) {
      if (statusDot) statusDot.className = "w-2 h-2 rounded-full bg-rose-500";
      if (statusText) statusText.textContent = "API Offline";
    }
  },

  showToast(message, type = "info") {
    const container = document.getElementById("toast-container");
    if (!container) return;

    const toast = document.createElement("div");
    const colors = {
      success: "bg-emerald-900/90 text-emerald-100 border-emerald-700",
      error: "bg-rose-900/90 text-rose-100 border-rose-700",
      warning: "bg-amber-900/90 text-amber-100 border-amber-700",
      info: "bg-slate-900/90 text-slate-100 border-slate-700"
    }[type] || "bg-slate-900/90 text-slate-100 border-slate-700";

    toast.className = `px-4 py-3 rounded-xl border backdrop-blur-md shadow-xl text-xs sm:text-sm font-medium flex items-center gap-2 transform transition-all duration-300 translate-y-2 opacity-0 ${colors}`;
    toast.innerHTML = `
      <span>${type === 'success' ? '✓' : (type === 'error' ? '✕' : 'ℹ')}</span>
      <span>${message}</span>
    `;

    container.appendChild(toast);

    // Trigger enter animation
    requestAnimationFrame(() => {
      toast.classList.remove("translate-y-2", "opacity-0");
    });

    // Remove after 3.5s
    setTimeout(() => {
      toast.classList.add("opacity-0", "translate-y-2");
      setTimeout(() => toast.remove(), 300);
    }, 3500);
  },

  printReport() {
    window.print();
  },

  downloadJSON() {
    if (!Analyzer.currentAnalysis) {
      this.showToast("No analysis available to download.", "warning");
      return;
    }
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(Analyzer.currentAnalysis, null, 2));
    const dlAnchor = document.createElement("a");
    dlAnchor.setAttribute("href", dataStr);
    dlAnchor.setAttribute("download", `ats_analysis_${Analyzer.currentAnalysis.id.slice(0, 8)}.json`);
    dlAnchor.click();
    this.showToast("Report exported as JSON!", "success");
  },

  toggleSetupModal(show) {
    const modal = document.getElementById("setup-modal");
    if (modal) {
      if (show) modal.classList.remove("hidden");
      else modal.classList.add("hidden");
    }
  }
};

document.addEventListener("DOMContentLoaded", () => {
  App.init();
});
