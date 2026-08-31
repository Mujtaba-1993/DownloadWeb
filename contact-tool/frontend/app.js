const state = {
  page: 1,
  per_page: 50,
  sort: "name",
  order: "asc",
  q: "",
  filters: { company: "", title: "", country: "", email_status: "", favorite: "" },
};

const el = (id) => document.getElementById(id);

function debounce(fn, ms) {
  let t;
  return (...args) => {
    clearTimeout(t);
    t = setTimeout(() => fn(...args), ms);
  };
}

async function loadStats() {
  const r = await fetch("/api/stats");
  const s = await r.json();
  el("stats").textContent =
    `${s.total.toLocaleString()} contacts · ${s.companies.toLocaleString()} companies` +
    (s.last_synced_at ? ` · synced ${s.last_synced_at}` : "");
}

async function loadFacets() {
  const r = await fetch("/api/facets");
  const data = await r.json();
  fillSelect("filter-company", data.companies);
  fillSelect("filter-title", data.titles);
  fillSelect("filter-country", data.countries);
  fillSelect("filter-email_status", data.email_statuses);
}

function fillSelect(id, items) {
  const sel = el(id);
  for (const item of items) {
    const opt = document.createElement("option");
    opt.value = item.value;
    opt.textContent = `${item.value} (${item.count})`;
    sel.appendChild(opt);
  }
}

function buildQuery() {
  const params = new URLSearchParams();
  params.set("page", state.page);
  params.set("per_page", state.per_page);
  params.set("sort", state.sort);
  params.set("order", state.order);
  if (state.q) params.set("q", state.q);
  for (const [k, v] of Object.entries(state.filters)) {
    if (v) params.set(k, v);
  }
  return params.toString();
}

async function loadContacts() {
  const query = buildQuery();
  el("export-link").href = "/api/contacts.csv?" + query;
  const r = await fetch("/api/contacts?" + query);
  const data = await r.json();
  renderTable(data.contacts);
  renderPagination(data.total, data.page, data.per_page);
}

function renderTable(contacts) {
  const body = el("contacts-body");
  body.innerHTML = "";
  for (const c of contacts) {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td><span class="star ${c.is_favorite ? "" : "inactive"}" data-id="${c.apollo_id}">&#9733;</span></td>
      <td><div class="contact-name">${escapeHtml(c.full_name || "")}</div>
          <div class="contact-sub">${escapeHtml(c.linkedin_url ? "LinkedIn" : "")}</div></td>
      <td>${escapeHtml(c.title || "")}</td>
      <td>${escapeHtml(c.organization_name || "")}</td>
      <td>${escapeHtml(c.email || "")}</td>
      <td>${escapeHtml(c.phone || "")}</td>
      <td>${escapeHtml([c.city, c.state, c.country].filter(Boolean).join(", "))}</td>
    `;
    tr.querySelector(".star").addEventListener("click", (e) => {
      e.stopPropagation();
      toggleFavorite(c);
    });
    tr.addEventListener("click", () => openDrawer(c.apollo_id));
    body.appendChild(tr);
  }
}

function renderPagination(total, page, perPage) {
  const pages = Math.max(Math.ceil(total / perPage), 1);
  const wrap = el("pagination");
  wrap.innerHTML = "";
  const prev = document.createElement("button");
  prev.textContent = "Prev";
  prev.disabled = page <= 1;
  prev.onclick = () => { state.page--; loadContacts(); };
  const next = document.createElement("button");
  next.textContent = "Next";
  next.disabled = page >= pages;
  next.onclick = () => { state.page++; loadContacts(); };
  const label = document.createElement("span");
  label.textContent = `Page ${page} of ${pages} (${total.toLocaleString()} contacts)`;
  wrap.append(prev, label, next);
}

async function toggleFavorite(c) {
  const r = await fetch(`/api/contacts/${c.apollo_id}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ is_favorite: !c.is_favorite }),
  });
  if (r.ok) loadContacts();
}

async function openDrawer(id) {
  const r = await fetch(`/api/contacts/${id}`);
  const c = await r.json();
  el("drawer-content").innerHTML = `
    <h2>${escapeHtml(c.full_name || "")}</h2>
    <div class="contact-sub">${escapeHtml(c.title || "")} at ${escapeHtml(c.organization_name || "")}</div>
    <div class="field"><label>Email</label>${escapeHtml(c.email || "—")} (${escapeHtml(c.email_status || "unknown")})</div>
    <div class="field"><label>Phone</label>${escapeHtml(c.phone || "—")}</div>
    <div class="field"><label>Location</label>${escapeHtml([c.city, c.state, c.country].filter(Boolean).join(", ") || "—")}</div>
    <div class="field"><label>LinkedIn</label>${c.linkedin_url ? `<a href="${c.linkedin_url}" target="_blank" rel="noopener">${c.linkedin_url}</a>` : "—"}</div>
    <div class="field">
      <label>Tags</label>
      <div class="tags" id="tag-list">${c.tags.map((t) => `<span class="tag-chip">${escapeHtml(t)}</span>`).join("")}</div>
      <input type="text" id="tag-input" placeholder="Add a tag and press Enter" style="margin-top:6px" />
    </div>
    <div class="field">
      <label>Notes</label>
      <textarea id="notes-input" rows="4">${escapeHtml(c.notes || "")}</textarea>
    </div>
    <button class="save-btn" id="save-notes">Save</button>
  `;

  let tags = [...c.tags];
  el("tag-input").addEventListener("keydown", (e) => {
    if (e.key === "Enter" && e.target.value.trim()) {
      tags.push(e.target.value.trim());
      e.target.value = "";
      el("tag-list").innerHTML = tags.map((t) => `<span class="tag-chip">${escapeHtml(t)}</span>`).join("");
    }
  });

  el("save-notes").addEventListener("click", async () => {
    await fetch(`/api/contacts/${id}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ notes: el("notes-input").value, tags }),
    });
    closeDrawer();
    loadContacts();
  });

  el("drawer").classList.add("open");
  el("drawer-backdrop").classList.add("open");
}

function closeDrawer() {
  el("drawer").classList.remove("open");
  el("drawer-backdrop").classList.remove("open");
}

function escapeHtml(str) {
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function init() {
  el("search-input").addEventListener(
    "input",
    debounce((e) => {
      state.q = e.target.value;
      state.page = 1;
      loadContacts();
    }, 300)
  );

  for (const key of ["company", "title", "country", "email_status"]) {
    el(`filter-${key}`).addEventListener("change", (e) => {
      state.filters[key] = e.target.value;
      state.page = 1;
      loadContacts();
    });
  }
  el("filter-favorite").addEventListener("change", (e) => {
    state.filters.favorite = e.target.checked ? "1" : "";
    state.page = 1;
    loadContacts();
  });
  el("clear-filters").addEventListener("click", () => {
    state.q = "";
    state.filters = { company: "", title: "", country: "", email_status: "", favorite: "" };
    state.page = 1;
    el("search-input").value = "";
    for (const key of ["company", "title", "country", "email_status"]) el(`filter-${key}`).value = "";
    el("filter-favorite").checked = false;
    loadContacts();
  });

  document.querySelectorAll("th[data-sort]").forEach((th) => {
    th.addEventListener("click", () => {
      const key = th.dataset.sort;
      if (state.sort === key) state.order = state.order === "asc" ? "desc" : "asc";
      else { state.sort = key; state.order = "asc"; }
      loadContacts();
    });
  });

  el("drawer-close").addEventListener("click", closeDrawer);
  el("drawer-backdrop").addEventListener("click", closeDrawer);

  loadStats();
  loadFacets();
  loadContacts();
}

init();
