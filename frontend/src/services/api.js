const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

const TOKEN_KEY = "buyorwait_token";

export function getToken() {
  return localStorage.getItem(TOKEN_KEY);
}

export function setToken(token) {
  localStorage.setItem(TOKEN_KEY, token);
}

export function clearToken() {
  localStorage.removeItem(TOKEN_KEY);
}

function authHeaders() {
  const token = getToken();
  return token ? { Authorization: `Bearer ${token}` } : {};
}

async function handle(response, fallbackMessage) {
  if (!response.ok) {
    let detail = fallbackMessage;
    try {
      const body = await response.json();
      detail = body.detail || fallbackMessage;
    } catch (_) {
      // ignore parse errors
    }
    throw new Error(detail);
  }
  return response.json();
}

/* =========================================================
   AUTH API  (real login credentials)
========================================================= */

export async function registerUser(payload) {
  const response = await fetch(`${API_BASE_URL}/auth/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  return handle(response, "Failed to create account.");
}

export async function loginUser(email, password) {
  const form = new URLSearchParams();
  form.set("username", email);
  form.set("password", password);

  const response = await fetch(`${API_BASE_URL}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: form.toString(),
  });

  const data = await handle(response, "Invalid email or password.");
  setToken(data.access_token);
  return data;
}

export async function getCurrentUser() {
  const response = await fetch(`${API_BASE_URL}/auth/me`, {
    headers: { ...authHeaders() },
  });

  return handle(response, "Failed to load your account.");
}

export function logout() {
  clearToken();
}

/* =========================================================
   PURCHASE API  (agentic AI analysis)
========================================================= */

export async function analyzePurchase(purchaseData) {
  const response = await fetch(`${API_BASE_URL}/purchase/analyze`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...authHeaders(),
    },
    body: JSON.stringify(purchaseData),
  });

  return handle(response, "Failed to analyze purchase.");
}

export async function getPurchaseHistory() {
  const response = await fetch(`${API_BASE_URL}/purchase/history`, {
    headers: { ...authHeaders() },
  });

  return handle(response, "Failed to load purchase history.");
}

/* =========================================================
   FINANCIAL DATA API  (real per-user data, not static numbers)
========================================================= */

export async function getFinancialSummary() {
  const response = await fetch(`${API_BASE_URL}/financial-data/summary`, {
    headers: { ...authHeaders() },
  });

  return handle(response, "Failed to load financial summary.");
}

export async function getCashFlowForecast(days = 60) {
  const response = await fetch(
    `${API_BASE_URL}/financial-data/forecast?days=${days}`,
    { headers: { ...authHeaders() } }
  );

  return handle(response, "Failed to load cash flow forecast.");
}

/* =========================================================
   SAVINGS API
========================================================= */

export async function getSavingsSuggestions(target = 10000) {
  const response = await fetch(
    `${API_BASE_URL}/savings/suggest?target=${target}`,
    { headers: { ...authHeaders() } }
  );

  return handle(response, "Failed to generate savings suggestions.");
}

/* =========================================================
   HEALTH CHECK
========================================================= */

export async function checkBackendHealth() {
  const response = await fetch(`${API_BASE_URL}/health`);
  return handle(response, "Backend is not available.");
}
