# GEMINI.md - Excel Processor

## Project Overview
Excel Processor is a personal finance automation tool designed to manage credit card statements and payslips. It cleans and categorizes transaction data from Excel files, extracts salary information from PDF payslips, and integrates directly with the [Actual Budget](https://actualbudget.org/) application.

### Tailored Design Philosophy
**CRITICAL:** This project is intentionally **non-generic**. It is strictly tailored to the specific formats of the user's Israeli bank statements and employer payslips.
- **No Generalization:** Do not attempt to abstract the logic to support multiple banks or different payslip structures.
- **Format Stability:** The input Excel (`data.xlsx`) and PDF (`payslip.pdf`) are assumed to have a fixed structure (column names, Hebrew labels, and layout).
- **Direct Mapping:** Logic in `src/api.py`, `src/core/excel.py`, and `src/core/pdf.py` matches these specific formats.

### Key Technologies
- **Language:** Python 3.11+
- **Data Processing:** `pandas`, `openpyxl`, `pyyaml`
- **PDF Extraction:** `pypdf`
- **Web API & Hosting:** `fastapi`, `uvicorn`
- **Budget Integration:** `actualpy` (Actual Budget API)
- **Dependency Management:** `uv`
- **Command Runner:** `just`
- **Frontend:** Vanilla HTML, CSS, JavaScript

### Architecture
The project runs as a FastAPI backend serving a dashboard web UI.
- **Pure vs. Impure Separation:**
    - **Pure Functions (`src/core/`):** Deterministic logic for data transformation, parsing, and category matching. No side effects.
    - **Impure Functions (`src/io/` and `src/api.py`):** Handle file I/O, PDF decryption, API interactions, and routing.
- **Component Breakdown:**
    - **`src/core/`**: Core pure logic for Excel (`excel.py`), PDF (`pdf.py`), and category mapping (`categories.py`, loaded from `categories.yaml`).
    - **`src/io/`**: Operations for Actual Budget interaction (`actual.py`) and filesystem access (`filesystem.py`).
    - **`src/models/`**: Shared data structures like `PayslipData`.
    - **`src/api.py`**: FastAPI routing and endpoints orchestration.
    - **`src/main.py`**: Server entry point launching the FastAPI application.
    - **`ui/`**: Single Page Application dashboard serving the frontend.

---

## Building and Running

### Prerequisites
- [uv](https://github.com/astral-sh/uv) installed.
- [just](https://github.com/casey/just) installed.
- A `.env` file containing:
  - `ACTUAL_SERVER_URL`: Actual Budget server URL.
  - `ACTUAL_PASSWORD`: Actual Budget password.
  - `ACTUAL_BUDGET_ID`: Actual Budget file ID.
  - `PAYSLIP_PASSWORD`: Password for encrypted payslips.

### Key Commands
Refer to the `justfile` for commands to build, run, lint, and test.

### Standalone Utility Scripts
Helper scripts separate from the pipeline leveraging PEP 723 metadata to run in auto-provisioned environments:
- **Run budget schema exploration**: `just explore` (runs `list_accounts.py`, `list_categories.py`, `list_tags.py`, `list_payees.py`)
- **Zero out category balances**: `just zero-out` (runs `zero_out_balances.py`)

---

## Development Conventions

### Coding Style
- **Type Hinting:** Mandatory for all signatures and complex variables.
- **Defensive Copying:** Start data transformation functions with `new_df = dataframe.copy()` to prevent side effects on inputs.
- **Hebrew Support:** Handles Hebrew column names and categories.

### Data Flow
1. **Entry Point:** `just run` initiates the process.
2. **Discovery & Preparation:** The `init` target deletes old local artifacts, searches `~/Downloads` for exactly one `.xlsx` and at most one `payslip*.pdf`, copies them to the project root as `data.xlsx` and `payslip.pdf`, and runs `uv sync`. It fails if multiple target files exist.
3. **Execution:** The `run` target starts the FastAPI server (`src/main.py`), which automatically launches `http://localhost:8000/ui/index.html` in the user's default browser.
4. **Excel Pipeline:** Initiated via the UI `/api/sync/transactions` endpoint. Reads `data.xlsx`, processes it via `src/core/excel.py`, writes `actual.csv`, and imports to Actual Budget.
5. **Payslip Pipeline (Optional):** Initiated via the UI `/api/sync/payslip` endpoint. Decrypts `payslip.pdf` if needed, extracts data via `src/core/pdf.py`, and imports net pay to Actual Budget.