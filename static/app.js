const buttons = document.querySelectorAll("nav button");
const tabs = document.querySelectorAll(".tab");

function showTab(name) {
  buttons.forEach((b) => b.classList.toggle("active", b.dataset.tab === name));
  tabs.forEach((t) => t.classList.toggle("active", t.id === name));
}

buttons.forEach((btn) => {
  btn.addEventListener("click", () => showTab(btn.dataset.tab));
});

async function loadStores() {
  const response = await fetch("/stores");
  const stores = await response.json();

  const select = document.getElementById("store-select");
  stores.forEach((store) => {
    const opt = document.createElement("option");
    opt.value = store;
    opt.textContent = store;
    select.appendChild(opt);
  });
  select.addEventListener("change", () => {
    loadMetrics(select.value);
    loadUsers(select.value, usersPrefix.value);
  });
  loadMetrics(select.value);
}

let currentMetrics = null;

async function loadMetrics(store) {
  const response = await fetch(`/stores/${store}/metrics`);
  const metrics = await response.json();
  currentMetrics = metrics;
  renderOverview(metrics);
  renderRevenue(metrics);
  renderPeople(metrics);
}

function renderOverview(data) {
  document.getElementById("unique-users").textContent = data.unique_users;
  document.getElementById("author-sets").textContent = data.author_sets;
  document.getElementById("top-authors").textContent =
    data.top_authors.join(", ");
}

let revenueChart = null;
function renderRevenue(data, start = null, end = null) {
  let labels = Object.keys(data.daily_revenue);
  if (start) labels = labels.filter((d) => d >= start);
  if (end) labels = labels.filter((d) => d <= end);
  const values = labels.map((d) => data.daily_revenue[d]);

  if (revenueChart) revenueChart.destroy();
  revenueChart = new Chart(document.getElementById("revenue-chart"), {
    type: "line",
    data: {
      labels: labels,
      datasets: [
        {
          label: "Revenue, $",
          data: values,
          pointRadius: 0,
          borderWidth: 1.5,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
    },
  });
  const topFive = document.getElementById("top-days");
  topFive.innerHTML = "";
  data.top_days.forEach((day) => {
    const li = document.createElement("li");
    li.textContent = `${day}: $${data.daily_revenue[day]}`;
    topFive.appendChild(li);
  });
}

function renderPeople(data) {
  const container = document.getElementById("best-buyer");
  const details = data.best_buyer_details;

  const rows = details.profiles
    .map(
      (p) => `
    <tr>
      <td>${p.id}</td>
      <td>${p.name}</td>
      <td>${p.email}</td>
      <td>${p.phone}</td>
      <td>${p.address ?? "-"}</td>
      <td>${p.spent}</td>
    </tr>`,
    )
    .join("");

  container.innerHTML = `
    <h3>Total spent: $${details.total_spent}</h3>
    <p>User IDs: ${details.user_ids.join(", ")}</p>
    <table>
      <tr><th>ID</th><th>Name</th><th>Email</th><th>Phone</th><th>Address</th><th>Spent</th></tr>
      ${rows}
    </table>`;
}

const chatBox = document.getElementById("chat-messages");

function addMessage(role, text) {
  const div = document.createElement("div");
  div.className = `msg ${role}`;
  div.textContent = text;
  chatBox.appendChild(div);
  chatBox.scrollTop = chatBox.scrollHeight;
  return div;
}

const chathistory = [];
const chatForm = document.getElementById("chat-form");
const chatInput = document.getElementById("chat-input");

chatForm.addEventListener("submit", async (e) => {
  e.preventDefault();

  const text = chatInput.value.trim();
  if (!text) return;

  addMessage("user", text);
  chathistory.push({ role: "user", content: text });
  chatInput.value = "";

  const placeholder = addMessage("assistant", "...");

  try {
    const resp = await fetch("/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ messages: chathistory }),
    });
    const data = await resp.json();
    placeholder.textContent = data.answer;
    chathistory.push({ role: "assistant", content: data.answer });
    (data.actions ?? []).forEach(runAction);
  } catch (err) {
    placeholder.textContent = "Error: try again";
  }
});

function renderUsers(data) {
  const numberOfUsers = document.getElementById("users-count");
  numberOfUsers.textContent = `Found ${data.count}`;
  const usersTable = document.getElementById("users-table");
  const rows = data.users
    .map(
      (u) =>
        `<tr>
      <td>${u.id}</td>
      <td>${u.name}</td>
      <td>${u.email}</td>
      <td>${u.phone}</td>
      <td>${u.address ?? "-"}</td>
    </tr>`,
    )
    .join("");
  usersTable.innerHTML = `
    <table>
    <tr><th>ID</th><th>Name</th><th>Email</th><th>Phone</th><th>Address</th></tr>
    ${rows}
  </table>`;
}

async function loadUsers(store, prefix) {
  const resp = await fetch(
    `/stores/${store}/users?email_prefix=${encodeURIComponent(prefix)}`,
  );
  const data = await resp.json();
  renderUsers(data);
}

const usersForm = document.getElementById("users-form");
const usersPrefix = document.getElementById("users-prefix");
const storeSelect = document.getElementById("store-select");

usersForm.addEventListener("submit", (e) => {
  e.preventDefault();
  loadUsers(storeSelect.value, usersPrefix.value);
});

async function runAction(action) {
  if (action.type === "show_users") {
    storeSelect.value = action.store;
    loadMetrics(action.store);
    usersPrefix.value = action.email_prefix;
    showTab("users");
    loadUsers(action.store, action.email_prefix);
  } else if (action.type === "show_revenue") {
    storeSelect.value = action.store;
    await loadMetrics(action.store);
    renderRevenue(currentMetrics, action.start_date, action.end_date);
    showTab("revenue");
  } else {
    console.warn("Unknown action", action);
  }
}

loadStores();
