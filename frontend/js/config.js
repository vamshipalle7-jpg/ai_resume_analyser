/**
 * Frontend Configuration
 * Connects exclusively to the FastAPI backend.
 * NO secret keys or database credentials are exposed here!
 */
const CONFIG = {
  API_BASE_URL: window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1"
    ? "http://127.0.0.1:8000"
    : "", // Relative path when served behind reverse proxy
  ENDPOINTS: {
    HEALTH: "/api/health",
    REGISTER: "/api/auth/register",
    LOGIN: "/api/auth/login",
    ME: "/api/auth/me",
    ANALYZE_UPLOAD: "/api/analyze/upload",
    ANALYZE_TEXT: "/api/analyze/text",
    SAMPLES: "/api/analyze/samples",
    HISTORY: "/api/history",
    ADMIN_STATS: "/api/admin/stats"
  }
};
