const BASE_URL = (location.origin || "http://127.0.0.1:5000") + "/api";

function getToken() { return localStorage.getItem("dna_token"); }
function getUser() {
  try { return JSON.parse(localStorage.getItem("dna_user") || "null"); }
  catch { return null; }
}
function setAuth(token, user) {
  localStorage.setItem("dna_token", token);
  localStorage.setItem("dna_user", JSON.stringify(user));
}
function logout() {
  localStorage.removeItem("dna_token");
  localStorage.removeItem("dna_user");
  location.href = "/login.html";
}
function requireAuth(role) {
  const u = getUser();
  if (!getToken() || !u) { location.href = "/login.html"; return; }
  if (role && u.role !== role) { location.href = "/dashboard.html"; }
}
function isAdmin() { const u = getUser(); return u && u.role === "admin"; }

async function api(endpoint, options = {}) {
  const token = getToken();
  const res = await fetch(BASE_URL + endpoint, {
    method: options.method || "GET",
    headers: {
      "Content-Type": "application/json",
      ...(token && { Authorization: "Bearer " + token }),
    },
    body: options.body,
  });
  let data = null;
  try { data = await res.json(); } catch { /* ignore */ }
  if (res.status === 401 && endpoint !== "/auth/login" && endpoint !== "/auth/register") {
    logout();
    return;
  }
  if (!res.ok) {
    const err = new Error((data && (data.error || data.detail)) || `HTTP ${res.status}`);
    err.status = res.status;
    err.data = data;
    throw err;
  }
  return data;
}

function colorDNA(str) {
  return (str || "").split("").map(c =>
    "ATGC".includes(c) ? `<span class="${c}">${c}</span>` : c
  ).join("");
}

function escapeHTML(s) {
  return String(s == null ? "" : s)
    .replace(/&/g, "&amp;").replace(/</g, "&lt;")
    .replace(/>/g, "&gt;").replace(/"/g, "&quot;");
}

function renderNav(active) {
  const u = getUser();
  if (!u) return "";
  const adminLink = u.role === "admin"
    ? `<a href="/admin.html" class="${active === 'admin' ? 'active' : ''}">Audit</a>`
    : "";
  const roleBadge = `<span class="role-badge ${u.role}">${u.role}</span>`;
  return `
    <div class="nav">
      <div class="brand">🧬 DNA Secure Vault</div>
      <div class="nav-links">
        <a href="/dashboard.html" class="${active === 'dash' ? 'active' : ''}">Vault</a>
        <a href="/attack.html" class="${active === 'attack' ? 'active' : ''}">Attack Sim</a>
        <a href="/logs.html" class="${active === 'logs' ? 'active' : ''}">My Activity</a>
        ${adminLink}
        <span class="nav-user">${escapeHTML(u.username)} ${roleBadge}</span>
        <a href="#" onclick="logout();return false;" class="logout">Logout</a>
      </div>
    </div>
  `;
}

/** Render an animated double-helix SVG given a DNA string. */
function renderHelix(dna, opts = {}) {
  const max = opts.max || 60;
  const seq = (dna || "").slice(0, max);
  const W = 560, H = 140, step = W / Math.max(seq.length, 1);
  const colors = { A: "var(--A)", T: "var(--T)", G: "var(--G)", C: "var(--C)" };
  const comp = { A: "T", T: "A", G: "C", C: "G" };
  const top = [], bot = [], rungs = [];
  for (let i = 0; i < seq.length; i++) {
    const x = i * step + step / 2;
    const yT = 70 + Math.sin(i * 0.6) * 28;
    const yB = 70 - Math.sin(i * 0.6) * 28;
    top.push(`${i === 0 ? "M" : "L"} ${x.toFixed(1)} ${yT.toFixed(1)}`);
    bot.push(`${i === 0 ? "M" : "L"} ${x.toFixed(1)} ${yB.toFixed(1)}`);
    rungs.push(`<line x1="${x}" y1="${yT}" x2="${x}" y2="${yB}" stroke="rgba(255,255,255,.08)" stroke-width="1"/>`);
    rungs.push(`<circle cx="${x}" cy="${yT}" r="6" fill="${colors[seq[i]] || '#666'}"><title>${seq[i]}</title></circle>`);
    rungs.push(`<circle cx="${x}" cy="${yB}" r="6" fill="${colors[comp[seq[i]] || seq[i]] || '#666'}"><title>${comp[seq[i]] || seq[i]}</title></circle>`);
  }
  return `
    <svg class="helix" viewBox="0 0 ${W} ${H}" preserveAspectRatio="xMidYMid meet">
      <path d="${top.join(' ')}" fill="none" stroke="rgba(120,200,255,.4)" stroke-width="2"/>
      <path d="${bot.join(' ')}" fill="none" stroke="rgba(255,140,180,.4)" stroke-width="2"/>
      ${rungs.join("")}
    </svg>`;
}

/** Wrap an async button click with a loading state + error toast. */
async function withBusy(btn, fn) {
  if (!btn) return fn();
  const prev = btn.innerHTML;
  btn.classList.add("btn-loading");
  btn.innerHTML = `<span class="spinner"></span>Working...`;
  try { return await fn(); }
  finally { btn.classList.remove("btn-loading"); btn.innerHTML = prev; }
}

document.addEventListener("DOMContentLoaded", () => {
  // Disable autocomplete for all forms
  document.querySelectorAll("form").forEach(form => {
    form.setAttribute("autocomplete", "off");
  });

  // Disable for all inputs
  document.querySelectorAll("input").forEach(input => {
    input.setAttribute("autocomplete", "off");

    // Special handling for password fields
    if (input.type === "password") {
      input.setAttribute("autocomplete", "new-password");
    }
  });
});