# CLAUDE.md - Excel Processor

## Project Overview
Excel Processor is a personal finance automation tool designed to streamline the management of credit card statements and payslips. It cleans and categorizes transaction data from Excel files, extracts salary information from PDF payslips, generates detailed expense reports, and integrates directly with the [Actual Budget](https://actualbudget.org/) application.

### Tailored Design Philosophy
**CRITICAL:** This project is intentionally **non-generic**. It is strictly tailored to the specific, consistent formats of the user's Israeli bank statements and employer payslips.
- **No Generalization:** Do not attempt to abstract the logic to support multiple banks or different payslip structures unless explicitly requested.
- **Format Stability:** The input Excel (`data.xlsx`) and PDF (`payslip.pdf`) are assumed to have a fixed structure (column names, Hebrew labels, and layout).
- **Direct Mapping:** Logic in `src/main.py`, `src/core/excel.py`, and `src/core/pdf.py` is hardcoded to match these specific formats for maximum efficiency and accuracy for the user's personal use.

### Key Technologies
- **Language:** Python 3.11+
- **Data Processing:** `pandas`, `openpyxl`
- **PDF Extraction:** `pypdf`
- **Budget Integration:** `actualpy` (Actual Budget API)
- **Dependency Management:** `uv`
- **Command Runner:** `just`

### Architecture
The project is designed as a functional data transformation pipeline, adhering to the following principles:
- **Functional Pipeline:** Data flows through a series of transformations, primarily managed by `pandas` and custom logic.
- **Pure vs. Impure Separation:**
    - **Pure Functions (`src/core/`):** Contain deterministic logic for data transformation, parsing, and calculation. These functions have no side effects and are easily testable.
    - **Impure Functions/Scripts (`src/io/` and `src/main.py`):** Handle side effects such as file I/O, PDF decryption, and API interactions with Actual Budget. `src/main.py` orchestrates the pipelines.
- **Component Breakdown:**
    - **`src/core/`**: Core pure logic for Excel cleaning (`excel.py`), PDF parsing (`pdf.py`), and category management (`categories.py`).
    - **`src/io/`**: Impure operations for different formats and services.
    - **`src/main.py`**: The single entry point that orchestrates the Excel and Payslip pipelines.

---

## Building and Running

### Prerequisites
- [uv](https://github.com/astral-sh/uv) installed.
- [just](https://github.com/casey/just) installed.
- A `.env` file with the following variables:
  - `ACTUAL_SERVER_URL`: URL of your Actual Budget server.
  - `ACTUAL_PASSWORD`: Your Actual Budget password.
  - `ACTUAL_BUDGET_ID`: The ID of the budget file.
  - `PAYSLIP_PASSWORD`: Password for encrypted payslip PDFs.

### Key Commands
Refer to the `justfile` for the primary commands used to build, run, and test the project.

### Standalone Utility Scripts
These isolated helper scripts are separate from the main pipeline and leverage PEP 723 inline metadata to run in auto-provisioned environments via `uv run <script>` (or via `just` commands):
- **Run budget schema exploration**: `just explore` (runs `scripts/list_accounts.py` and `scripts/list_categories.py`)
- **Zero out category balances**: `just zero-out` (runs `scripts/zero_out_balances.py`)

---

## Development Conventions

### Coding Style
- **Type Hinting:** Mandatory for all function signatures and complex variables.
- **Defensive Copying:** To ensure functions are "pure" and "idiot-proof," always start data transformation functions with `new_df = dataframe.copy()`. This prevents accidental side effects on the input data, regardless of whether subsequent pandas operations return a view or a copy.
- **Hebrew Support:** The codebase handles Hebrew column names and categories commonly found in Israeli bank/credit card statements.

### Data Flow
1.  **Entry Point:** `just run` initiates the process.
2.  **Discovery & Preparation:** The `init` target (run as a dependency of `just run`) searches the `~/Downloads` directory for the latest `.xlsx` statement and `payslip*.pdf`. It copies them to the project root as `data.xlsx` and `payslip.pdf`, respectively, after cleaning up old files, and runs `uv sync`.
3.  **Execution:** The `run` target starts the FastAPI server (`uv run python -m src.main`).
4.  **Excel Pipeline:** `src/main.py` reads `data.xlsx`, processes it using `src/core/excel.py`, writes `actual.csv`, prints a report, and imports to Actual Budget.
5.  **Payslip Pipeline (Optional):** If `payslip.pdf` exists, `src/main.py` decrypts it, extracts data using `src/core/pdf.py`, prints a report, and imports to Actual Budget.