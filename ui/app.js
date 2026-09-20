// State Variables
let currentPayslipPassword = "";
let activeScorecardInfo = null;

// DOM Elements
const toastContainer = document.getElementById("toast-container");

const noFilesCard = document.getElementById("no-files-card");
const excelSection = document.getElementById("excel-section");

const metricOutflows = document.getElementById("metric-outflows");
const metricCount = document.getElementById("metric-count");


const btnSyncTransactions = document.getElementById("btn-sync-transactions");

const payslipCard = document.getElementById("payslip-card");
const payslipPasswordSection = document.getElementById(
  "payslip-password-section",
);
const payslipPasswordInput = document.getElementById("payslip-password");
const btnDecryptPayslip = document.getElementById("btn-decrypt-payslip");

const payslipMetricsSection = document.getElementById(
  "payslip-metrics-section",
);
const payslipNet = document.getElementById("payslip-net");
const payslipGross = document.getElementById("payslip-gross");
const payslipDate = document.getElementById("payslip-date");
const btnSyncPayslip = document.getElementById("btn-sync-payslip");

const scorecardMessage = document.getElementById("scorecard-message");
const scorecardContent = document.getElementById("scorecard-content");
const scorecardRows = document.getElementById("scorecard-rows");
const scorecardTotalExpenses = document.getElementById("scorecard-total-expenses");
const scorecardTooltip = document.getElementById("scorecard-tooltip");

// Initialize the dashboard
document.addEventListener("DOMContentLoaded", () => {
  loadDashboardData();
  setupEventListeners();
});

// Event Listeners Setup
function setupEventListeners() {

  // Sync Transactions Button
  btnSyncTransactions.addEventListener("click", () => {
    syncTransactions();
  });

  // Decrypt Payslip Button
  btnDecryptPayslip.addEventListener("click", () => {
    const password = payslipPasswordInput.value;
    if (!password) {
      showToast("Please enter a password", "error");
      return;
    }
    currentPayslipPassword = password;
    loadDashboardData(password);
  });

  // Sync Payslip Button
  btnSyncPayslip.addEventListener("click", () => {
    syncPayslip();
  });

  document.addEventListener("keydown", event => {
    if (event.key === "Escape") hideScorecardTooltip();
  });
  document.addEventListener("pointerdown", event => {
    if (!activeScorecardInfo?.contains(event.target) && !scorecardTooltip.contains(event.target)) {
      hideScorecardTooltip();
    }
  });
  window.addEventListener("resize", hideScorecardTooltip);
  window.addEventListener("scroll", hideScorecardTooltip, true);
}

// Toast notification helper
function showToast(message, type = "info") {
  const toast = document.createElement("div");
  toast.className = `toast toast-${type}`;

  toast.innerHTML = `
        <div class="toast-message">${message}</div>
        <button class="toast-close">&times;</button>
    `;

  toastContainer.appendChild(toast);

  // Animate in
  setTimeout(() => toast.classList.add("show"), 10);

  // Auto remove
  const autoRemoveTimer = setTimeout(() => {
    toast.classList.remove("show");
    setTimeout(() => toast.remove(), 350);
  }, 4500);

  // Close button click
  toast.querySelector(".toast-close").addEventListener("click", () => {
    clearTimeout(autoRemoveTimer);
    toast.classList.remove("show");
    setTimeout(() => toast.remove(), 350);
  });
}



// Fetch and load processed statement and payslip data
async function loadDashboardData(payslipPassword = "") {
  showScorecardMessage("Loading monthly targets...");
  try {
    let url = "/api/data";
    if (payslipPassword) {
      url += `?payslip_password=${encodeURIComponent(payslipPassword)}`;
    }

    const response = await fetch(url);
    if (!response.ok) {
      throw new Error("Failed to load dashboard data");
    }

    const data = await response.json();

    const excel = data.excel;
    const payslip = data.payslip;

    renderFinancialScorecard(excel, payslip);

    // Check if no files exist
    if ((!excel || !excel.exists) && (!payslip || !payslip.exists)) {
      noFilesCard.classList.remove("hidden");
      excelSection.classList.add("hidden");
      payslipCard.classList.add("hidden");
      return;
    }

    noFilesCard.classList.add("hidden");

    // Render Excel Section
    if (excel && excel.exists) {
      excelSection.classList.remove("hidden");
      if (excel.error) {
        showToast(excel.error, "error");
      } else if (excel.metrics) {
        // Populate metrics
        metricOutflows.textContent = formatCurrency(excel.metrics.total_spent);
        metricCount.textContent = excel.metrics.trans_count;



      }
    } else {
      excelSection.classList.add("hidden");
    }

    // Render Payslip Card
    if (payslip && payslip.exists) {
      payslipCard.classList.remove("hidden");

      if (payslip.error) {
        showToast(payslip.error, "error");
        showPayslipPasswordInput();
      } else if (payslip.data) {
        // Decrypted successfully
        payslipNet.textContent = formatCurrency(payslip.data.net_to_bank);
        payslipGross.textContent = formatCurrency(payslip.data.taxable_income);
        payslipDate.textContent = payslip.data.date;

        showPayslipMetrics();
        if (payslipPassword) {
          showToast("Payslip decrypted successfully!", "success");
        }
      } else if (payslip.requires_password) {
        // Encrypted and password not entered / correct yet
        showPayslipPasswordInput();
      }
    } else {
      payslipCard.classList.add("hidden");
    }
  } catch (error) {
    showScorecardMessage("Unable to load monthly targets. Reload the dashboard to try again.");
    showToast(error.message, "error");
  }
}

// Derive targets from the same local data used by the other two panels.
function calculateFinancialScorecard(transactions, income) {
  const net = Math.round(income.net_to_bank * 100);
  let housing = 300000;
  const funCategories = new Set(["Eating out", "Social & Fun", "Vacation & Travel"]);
  const utilityCategories = new Set(["Electricity", "ארנונה", "Water", "Utilities"]);
  const utilityPayees = /electricity bill|arnona|bezeq|strauss water|חברת החשמל|חשמל לישראל|ארנונה|בזק|שטראוס מים/i;
  let essentials = 0;
  let fun = 0;

  // Work in agorot so sums and status comparisons agree at currency precision.
  for (const transaction of transactions) {
    const amount = Math.round(transaction.Amount * 100);
    const payee = (transaction.Payee || "").toLowerCase();
    const isPaybox = payee.includes("paybox");
    const magnitude = Math.abs(amount);
    const isRent = isPaybox && magnitude >= 290000 && magnitude <= 310000;
    const isPayboxUtility = isPaybox && magnitude >= 80000 && magnitude <= 90000;
    if (isRent) {
      // The fixed rent already covers payments; rent refunds still reduce housing.
      if (amount < 0) housing += amount;
    } else if (isPayboxUtility || utilityCategories.has(transaction.Category) || utilityPayees.test(payee)) {
      housing += amount;
    } else if (funCategories.has(transaction.Category)) {
      fun += amount;
    } else {
      essentials += amount;
    }
  }

  const living = housing + essentials;
  const totalExpenses = living + fun;
  const remaining = net - totalExpenses;

  return {
    totalExpenses: totalExpenses / 100,
    rows: [
      {
        name: "Living Expenses", rule: "No more than 40% of net",
        description: "Rent + utilities + essentials",
        target: Math.round(net * 0.40), actual: living, base: net, minimum: false,
      },
      {
        name: "Guilt-Free Fun", rule: "No more than 20% of net",
        description: "Fun includes Eating out/Wolt, Social & Fun, and Vacation & Travel",
        target: Math.round(net * 0.20), actual: fun, base: net, minimum: false,
      },
      {
        name: "Monthly Investing", rule: "No less than 40% of net",
        description: "What's left from net pay after expenses goes to investing.",
        target: Math.round(net * 0.40), actual: remaining, base: net, minimum: true,
      },
    ],
  };
}

function showScorecardMessage(message) {
  hideScorecardTooltip();
  scorecardContent.classList.add("hidden");
  scorecardRows.replaceChildren();
  scorecardTotalExpenses.textContent = "";
  scorecardMessage.textContent = message;
  scorecardMessage.classList.remove("hidden");
}

function renderFinancialScorecard(excel, payslip) {
  if (!excel?.exists || !payslip?.exists) {
    showScorecardMessage("Add both data.xlsx and payslip.pdf to the project root to see monthly targets.");
    return;
  }
  if (excel.error || payslip.error) {
    showScorecardMessage("Monthly targets are unavailable until both files load successfully.");
    return;
  }
  if (!payslip.data && payslip.requires_password) {
    showScorecardMessage("Unlock the payslip to calculate monthly targets.");
    return;
  }
  if (!Array.isArray(excel.transactions) || !payslip.data) {
    showScorecardMessage("Monthly targets need categorized transactions and payslip income.");
    return;
  }

  const net = payslip.data.net_to_bank;
  if (!Number.isFinite(net) || net <= 0 ||
      excel.transactions.some(transaction => !Number.isFinite(transaction.Amount))) {
    showScorecardMessage("Monthly targets require valid expense amounts and positive net pay.");
    return;
  }

  const scorecard = calculateFinancialScorecard(excel.transactions, payslip.data);
  hideScorecardTooltip();
  scorecardRows.replaceChildren();
  for (const row of scorecard.rows) {
    const tr = document.createElement("tr");
    const recommendation = document.createElement("th");
    recommendation.scope = "row";
    recommendation.textContent = row.name;
    const info = document.createElement("button");
    info.type = "button";
    info.className = "scorecard-info";
    info.textContent = "i";
    info.setAttribute("aria-label", `About ${row.name}`);
    info.addEventListener("mouseenter", () => showScorecardTooltip(info, row.description));
    info.addEventListener("focus", () => showScorecardTooltip(info, row.description));
    info.addEventListener("click", () => showScorecardTooltip(info, row.description));
    info.addEventListener("mouseleave", () => {
      if (activeScorecardInfo === info && document.activeElement !== info) hideScorecardTooltip();
    });
    info.addEventListener("blur", hideScorecardTooltip);
    recommendation.appendChild(info);
    const rule = document.createElement("span");
    rule.className = "scorecard-detail";
    rule.textContent = row.rule;
    recommendation.appendChild(rule);

    const target = document.createElement("td");
    const actual = document.createElement("td");
    const status = document.createElement("td");
    const badge = document.createElement("span");
    const onTarget = row.minimum ? row.actual >= row.target : row.actual <= row.target;
    const prefix = row.minimum ? "No less than " : "No more than ";
    target.textContent = prefix + formatCurrency(row.target / 100);
    actual.textContent = formatCurrency(row.actual / 100);

    const detail = document.createElement("span");
    detail.className = "scorecard-detail";
    detail.textContent = `(${(row.actual / row.base * 100).toFixed(1)}%)`;
    actual.appendChild(detail);

    badge.className = `status-badge ${onTarget ? "status-on-target" : "status-off-target"}`;
    badge.textContent = onTarget ? "ON TARGET" : "OFF TARGET";
    status.appendChild(badge);
    tr.append(recommendation, target, actual, status);
    scorecardRows.appendChild(tr);
  }
  scorecardTotalExpenses.textContent = formatCurrency(scorecard.totalExpenses);
  scorecardMessage.classList.add("hidden");
  scorecardContent.classList.remove("hidden");
}

function hideScorecardTooltip() {
  scorecardTooltip.hidePopover();
  activeScorecardInfo?.removeAttribute("aria-describedby");
  activeScorecardInfo = null;
}

function showScorecardTooltip(info, description) {
  hideScorecardTooltip();
  activeScorecardInfo = info;
  info.setAttribute("aria-describedby", "scorecard-tooltip");
  scorecardTooltip.textContent = description;
  scorecardTooltip.showPopover();
  const anchor = info.getBoundingClientRect();
  const tooltip = scorecardTooltip.getBoundingClientRect();
  const left = Math.max(12, Math.min(anchor.left, window.innerWidth - tooltip.width - 12));
  const top = anchor.bottom + tooltip.height + 8 <= window.innerHeight
    ? anchor.bottom + 8 : Math.max(12, anchor.top - tooltip.height - 8);
  scorecardTooltip.style.left = `${left}px`;
  scorecardTooltip.style.top = `${top}px`;
}

// Sync Excel Transactions to Actual Budget
async function syncTransactions() {
  toggleLoading(btnSyncTransactions, true);

  try {
    const response = await fetch("/api/sync/transactions", {
      method: "POST",
    });

    const result = await response.json();

    if (!response.ok) {
      throw new Error(result.detail || "Failed to sync transactions");
    }

    showToast(result.message, "success");
  } catch (error) {
    showToast(error.message, "error");
  } finally {
    toggleLoading(btnSyncTransactions, false);
  }
}

// Sync Payslip to Actual Budget
async function syncPayslip() {
  toggleLoading(btnSyncPayslip, true);

  try {
    const response = await fetch("/api/sync/payslip", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        password: currentPayslipPassword,
      }),
    });

    const result = await response.json();

    if (!response.ok) {
      throw new Error(result.detail || "Failed to sync payslip");
    }

    showToast(result.message, "success");
  } catch (error) {
    showToast(error.message, "error");
  } finally {
    toggleLoading(btnSyncPayslip, false);
  }
}

// UI helper states
function showPayslipPasswordInput() {
  payslipPasswordSection.classList.remove("hidden");
  payslipMetricsSection.classList.add("hidden");
}

function showPayslipMetrics() {
  payslipPasswordSection.classList.add("hidden");
  payslipMetricsSection.classList.remove("hidden");
}

function toggleLoading(btnElement, isLoading) {
  const textSpan = btnElement.querySelector(".btn-text");
  const spinnerSpan = btnElement.querySelector(".spinner");

  if (isLoading) {
    btnElement.disabled = true;
    spinnerSpan.classList.remove("hidden");
    if (btnElement === btnSyncTransactions) {
      textSpan.textContent = "Syncing transactions...";
    } else if (btnElement === btnSyncPayslip) {
      textSpan.textContent = "Syncing payslip...";
    }
  } else {
    btnElement.disabled = false;
    spinnerSpan.classList.add("hidden");
    if (btnElement === btnSyncTransactions) {
      textSpan.textContent = "Sync Transactions to Actual Budget";
    } else if (btnElement === btnSyncPayslip) {
      textSpan.textContent = "Sync Payslip to Actual Budget";
    }
  }
}

// Formatting Helpers
function formatCurrency(value) {
  const num = parseFloat(value);
  if (isNaN(num)) return "₪0.00";
  const formatted = Math.abs(num).toLocaleString("en-US", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });
  return num < 0 ? `-₪${formatted}` : `₪${formatted}`;
}
