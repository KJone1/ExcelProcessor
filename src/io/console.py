from returns.result import safe
from rich.console import Console
from rich.table import Table

from src.models.pdf import PayslipData


@safe
def print_payslip_report(data: PayslipData) -> None:
    console = Console()

    table = Table(title="Payslip Data Extraction", show_header=False, box=None)
    table.add_row("Date", f"[cyan]{data.date.strftime('%m/%Y')}[/cyan]")
    table.add_row("Taxable Income", f"[green]{data.taxable_income:,.2f}₪[/green]")
    table.add_row("Net to Bank", f"[bold blue]{data.net_to_bank:,.2f}₪[/bold blue]")

    console.print("-" * 30)
    console.print(table)
    console.print("-" * 30)


@safe
def print_transactions_report(csv_path: str) -> None:
    import pandas as pd

    df = pd.read_csv(csv_path)
    console = Console()

    table = Table(title="Processed Transactions")
    table.add_column("Date", style="cyan")
    table.add_column("Name", style="white")
    table.add_column("Category", style="magenta")
    table.add_column("Sum", justify="right", style="green")

    total_sum = 0
    for _, row in df.iterrows():
        date = row["Date"]
        amount = row["Amount"]
        total_sum += amount
        style = "green" if amount >= 0 else "red"

        table.add_row(
            date,
            str(row["Payee"]),
            str(row["Category"]),
            f"[{style}]{amount:,.2f}₪[/{style}]",
        )

    console.print(table)
    console.print("-" * 30)
    console.print(f"Total Transactions: [bold cyan]{len(df)}[/bold cyan]")
    console.print(f"Total Sum: [bold green]{total_sum:,.2f}₪[/bold green]")
    console.print("-" * 30)


@safe
def print_error(message: str) -> None:
    console = Console()
    console.print(f"[bold red]Error:[/bold red] {message}")
