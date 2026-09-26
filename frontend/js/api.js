/**
 * API Client Module
 * Handles all network requests to the FastAPI backend.
 */
const API = {
  getAuthHeader() {
    const token = localStorage.getItem("resumely_token");
    return token ? { Authorization: `Bearer ${token}` } : {};
  },

  async request(endpoint, options = {}) {
    const url = `${CONFIG.API_BASE_URL}${endpoint}`;
    const headers = {
      ...this.getAuthHeader(),
      ...(options.headers || {})
    };

    try {
      const response = await fetch(url, { ...options, headers });
      
      if (!response.ok) {
        let errorMsg = `Server error (${response.status})`;
        try {
          const errData = await response.json();
          errorMsg = errData.detail || errData.message || errorMsg;
        } catch (_) {}
        throw new Error(errorMsg);
      }

      return await response.json();
    } catch (err) {
      if (err.message.includes("Failed to fetch")) {
        throw new Error("Unable to connect to the backend server. Ensure FastAPI is running on http://127.0.0.1:8000.");
      }
      throw err;
    }
  },

  async get(endpoint) {
    return this.request(endpoint, { method: "GET" });
  },

  async post(endpoint, body) {
    return this.request(endpoint, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body)
    });
  },

  async postForm(endpoint, formData) {
    return this.request(endpoint, {
      method: "POST",
      body: formData // Content-Type is set automatically by the browser with boundary
    });
  },

  async delete(endpoint) {
    return this.request(endpoint, { method: "DELETE" });
  },

  async checkHealth() {
    try {
      return await this.get(CONFIG.ENDPOINTS.HEALTH);
    } catch (e) {
      return { status: "offline", error: e.message };
    }
  }
};
