# GEMINI.md - Excel Processor

## Project Overview
Excel Processor is a personal finance automation tool designed to streamline the management of credit card statements and payslips. It cleans and categorizes transaction data from Excel files, extracts salary information from PDF payslips, generates detailed expense reports, and integrates directly with the [Actual Budget](https://actualbudget.org/) application.

### Tailored Design Philosophy
**CRITICAL:** This project is intentionally **non-generic**. It is strictly tailored to the specific, consistent formats of the user's Israeli bank statements and employer payslips.
- **No Generalization:** Do not attempt to abstract the logic to support multiple banks or different payslip structures unless explicitly requested.
- **Format Stability:** The input Excel (`data.xlsx`) and PDF (`payslip.pdf`) are assumed to have a fixed structure (column names, Hebrew labels, and layout).
- **Direct Mapping:** Logic in `main.py`, `generate_csv.py`, and `extract_payslip.py` is hardcoded to match these specific formats for maximum efficiency and accuracy for the user's personal use.

### Key Technologies
- **Language:** Python 3.9+
- **Data Processing:** `pandas`, `openpyxl`
- **PDF Extraction:** `pypdf`
- **Budget Integration:** `actualpy` (Actual Budget API)
- **Dependency Management:** `uv`
- **Command Runner:** `just`
- **Functional Utilities:** `returns`

### Architecture
The project is designed as a functional data transformation pipeline, adhering to the following principles:
- **Functional Pipeline:** Data flows through a series of transformations, primarily managed by `pandas` and custom logic.
- **Railway Oriented Programming (ROP):** Utilizes monads (via the `returns` library) to handle success and failure paths cleanly without excessive try-except blocks.
- **Pure vs. Impure Separation:**
    - **Pure Functions (`src/core/`):** Contain deterministic logic for data transformation, parsing, and calculation. These functions have no side effects and are easily testable.
    - **Impure Functions/Scripts (`src/io/` and Root Scripts):** Handle side effects such as file I/O, PDF decryption, and API interactions with Actual Budget.
- **Component Breakdown:**
    - **`src/core/`**: Core pure logic for Excel cleaning (`excel.py`), PDF parsing (`pdf.py`), and category management (`categories.py`).
    - **`src/io/`**: Impure operations for different formats and services.
    - **Root Scripts**: Orchestrate the pipelines (e.g., `run.sh` calling the Python scripts in sequence).


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
Refer to the `justfile` and `run.sh` for the primary commands used to build, run, and test the project.


---

## Development Conventions

### Coding Style
- **Type Hinting:** Mandatory for all function signatures and complex variables.
- **Functional Programming:** The project utilizes the `returns` library for functional patterns (e.g., `Result` containers).
- **Defensive Copying:** To ensure functions are "pure" and "idiot-proof," always start data transformation functions with `new_df = dataframe.copy()`. This prevents accidental side effects on the input data, regardless of whether subsequent pandas operations return a view or a copy.
- **Hebrew Support:** The codebase handles Hebrew column names and categories commonly found in Israeli bank/credit card statements.

### Data Flow
1.  **Entry Point:** `run.sh` initiates the entire process.
2.  **Discovery & Preparation:** `run.sh` searches the `~/Downloads` directory for the latest `.xlsx` statement and `payslip*.pdf`. It copies them to the project root as `data.xlsx` and `payslip.pdf`, respectively, after cleaning up old files.
3.  **Process:** `main.py` cleans `data.xlsx` and produces `out.xlsx`.
4.  **Map:** `generate_csv.py` transforms `out.xlsx` into `actual.csv` with mapped categories.
5.  **Import:** `import_transactions.py` pushes `actual.csv` to Actual Budget.
6.  **Payslip (Optional):** If `payslip.pdf` exists, `extract_payslip.py` parses it and uploads the net income to Actual Budget.
