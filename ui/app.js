// State Variables
let actualStatus = null;
let currentPayslipPassword = "";

// DOM Elements
const toastContainer = document.getElementById("toast-container");

const noFilesCard = document.getElementById("no-files-card");
const excelSection = document.getElementById("excel-section");

const metricOutflows = document.getElementById("metric-outflows");
const metricAvg = document.getElementById("metric-avg");
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
}

// Toast notification helper
function showToast(message, type = "info") {
  const toast = document.createElement("div");
  toast.className = `toast toast-${type}`;

  let emoji = "ℹ️";
  if (type === "success") emoji = "🟢";
  if (type === "error") emoji = "🔴";

  toast.innerHTML = `
        <span class="toast-icon">${emoji}</span>
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
        metricAvg.textContent = formatCurrency(excel.metrics.avg_trans);
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
    showToast(error.message, "error");
  }
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
  btnDecryptPayslip.querySelector(".spinner").classList.add("hidden");
  btnDecryptPayslip.querySelector(".btn-text").textContent =
    "Load & Extract Payslip";
  btnDecryptPayslip.disabled = false;
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
    } else if (btnElement === btnDecryptPayslip) {
      textSpan.textContent = "Decrypting...";
    }
  } else {
    btnElement.disabled = false;
    spinnerSpan.classList.add("hidden");
    if (btnElement === btnSyncTransactions) {
      textSpan.textContent = "Syncy Transactions to Actual Budget";
      textSpan.textContent = "Sync Transactions to Actual Budget";
    } else if (btnElement === btnSyncPayslip) {
      textSpan.textContent = "Sync Payslip to Actual Budget";
    } else if (btnElement === btnDecryptPayslip) {
      textSpan.textContent = "Load & Extract Payslip";
    }
  }
}

// Formatting Helpers
function formatCurrency(value) {
  const num = parseFloat(value);
  if (isNaN(num)) return "₪0.00";
  return (
    "₪" +
    num.toLocaleString("en-US", {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    })
  );
}

function formatNumber(value) {
  const num = parseFloat(value);
  if (isNaN(num)) return "0.00";
  return num.toLocaleString("en-US", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });
}
