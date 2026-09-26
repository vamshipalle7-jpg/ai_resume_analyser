/**
 * Authentication Module
 * Manages JWT tokens, user sessions, and role-based UI updates.
 */
const Auth = {
  currentUser: null,

  init() {
    const storedUser = localStorage.getItem("resumely_user");
    const token = localStorage.getItem("resumely_token");
    if (storedUser && token) {
      try {
        this.currentUser = JSON.parse(storedUser);
      } catch (e) {
        this.logout();
      }
    }
    this.updateUI();
  },

  async login(email, password) {
    const data = await API.post(CONFIG.ENDPOINTS.LOGIN, { email, password });
    this.setSession(data);
    return data.user;
  },

  async register(email, password, fullName) {
    const data = await API.post(CONFIG.ENDPOINTS.REGISTER, { email, password, full_name: fullName });
    this.setSession(data);
    return data.user;
  },

  setSession(authData) {
    localStorage.setItem("resumely_token", authData.access_token);
    localStorage.setItem("resumely_user", JSON.stringify(authData.user));
    this.currentUser = authData.user;
    this.updateUI();
  },

  logout() {
    localStorage.removeItem("resumely_token");
    localStorage.removeItem("resumely_user");
    this.currentUser = null;
    this.updateUI();
    App.showToast("Logged out successfully.", "info");
  },

  isLoggedIn() {
    return !!this.currentUser && !!localStorage.getItem("resumely_token");
  },

  isAdmin() {
    return this.currentUser && this.currentUser.role === "admin";
  },

  updateUI() {
    const authActions = document.getElementById("auth-actions");
    const userProfile = document.getElementById("user-profile");
    const userNameEl = document.getElementById("user-name");
    const userRoleBadge = document.getElementById("user-role-badge");
    const userAvatarEl = document.getElementById("user-avatar");
    const adminNavTab = document.getElementById("nav-admin-tab");

    if (this.isLoggedIn()) {
      if (authActions) authActions.classList.add("hidden");
      if (userProfile) userProfile.classList.remove("hidden");
      if (userNameEl) userNameEl.textContent = this.currentUser.full_name || this.currentUser.email;
      if (userRoleBadge) {
        userRoleBadge.textContent = this.currentUser.role.toUpperCase();
        userRoleBadge.className = this.currentUser.role === "admin" 
          ? "px-2 py-0.5 text-xs font-semibold bg-purple-100 text-purple-700 rounded-full"
          : "px-2 py-0.5 text-xs font-semibold bg-indigo-100 text-indigo-700 rounded-full";
      }
      if (userAvatarEl) {
        const initial = (this.currentUser.full_name || this.currentUser.email || "U")[0].toUpperCase();
        userAvatarEl.textContent = initial;
      }
      if (adminNavTab) {
        adminNavTab.classList.remove("hidden");
      }
    } else {
      if (authActions) authActions.classList.remove("hidden");
      if (userProfile) userProfile.classList.add("hidden");
      if (adminNavTab) {
        adminNavTab.classList.remove("hidden"); // Kept visible so users can test admin features in demo
      }
    }
  }
};
