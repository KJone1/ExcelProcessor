# AGENTS.md - Excel Processor

## Purpose and usage

This is a personal tool, run manually about once a month to sync
credit card transactions and an optional payslip to Actual Budget.

**CRITICAL:** This project is intentionally **non-generic**. It is strictly tailored to the specific formats of the user's Israeli bank statements and employer payslips.

- **No Generalization:** Do not attempt to abstract the logic to support multiple banks or different payslip structures.

## Data sources

- Transactions: the Excel statement is processed into a clean CSV.
- Payslip: the PDF is processed into `PayslipData`, kept in memory.

## Dashboard

The dashboard lets you preview transactions and sync them to your Actual Budget instance.

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

Refer to the `justfile` for commands to build, run, and lint.

## Scripts

The `scripts/` folder contains tools to explore and manage Actual Budget data through its API.

## Development conventions

- Keep type hints on signatures and complex variables.
- Keep comments short and explain why when useful. Do not add class docstrings.
- Keep all configuration and constants in `settings.py`.
- Keep the pandas `.pipe()` notation for the Excel processing chain.
- Categories use INI because mixed Hebrew and English text is easier to read than in YAML or TOML.
- Do not write or run tests unless the user explicitly asks.
