# expense_tracker.py

import csv
import os
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt
from rich import box
import matplotlib.pyplot as plt

console = Console()
file_path = "expenses.csv"

def sort_expense_file():
    if not os.path.exists(file_path):
        return

    from datetime import datetime
    with open(file_path, mode='r') as file:
        lines = list(csv.reader(file))
        header = lines[0]
        data = lines[1:]

    data.sort(key=lambda x: datetime.strptime(x[0], "%Y-%m-%d"))

    with open(file_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(header)
        writer.writerows(data)



# Create CSV file if not exists
if not os.path.exists(file_path):
    with open(file_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Date", "Category", "Amount"])

def add_expense():
    console.print("\n[bold cyan]Add New Expense[/bold cyan]")
    date = Prompt.ask("Enter date (YYYY-MM-DD)")
    category = Prompt.ask("Enter category (e.g. Food, Transport)")
    amount = Prompt.ask("Enter amount (₹)")
    
    try:
        amount = float(amount)
        datetime.strptime(date, '%Y-%m-%d')  # Validate date
    except ValueError:
        console.print("[bold red]Invalid date or amount![/bold red]")
        return

    with open(file_path, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([date, category, amount])
    
    console.print("[green]Expense added successfully![/green]")
    sort_expense_file()

    
def show_report():
    console.print("\n[bold yellow]Monthly Expense Report[/bold yellow]")

    monthly_data = {}

    with open(file_path, mode='r') as file:
        reader = list(csv.DictReader(file))

        # Convert string to datetime object and sort
        from datetime import datetime
        reader.sort(key=lambda x: datetime.strptime(x["Date"], "%Y-%m-%d"))

        for row in reader:
            month = row["Date"][:7]
            cat = row["Category"]
            amt = float(row["Amount"])
            monthly_data.setdefault(month, {})
            monthly_data[month][cat] = monthly_data[month].get(cat, 0) + amt

    for month in sorted(monthly_data):  # Month wise sorted display
        table = Table(title=f"Report for {month}", box=box.ROUNDED)
        table.add_column("Category", style="cyan")
        table.add_column("Total (₹)", style="green")
        for cat, amt in monthly_data[month].items():
            table.add_row(cat, f"₹{amt:.2f}")
        console.print(table)


def show_detailed_report():
    console.print("\n[bold green]Detailed Expense Report (Date-wise)[/bold green]")

    if not os.path.exists(file_path):
        console.print("[red]No data found![/red]")
        return

    with open(file_path, mode='r') as file:
        reader = list(csv.DictReader(file))
        from datetime import datetime
        reader.sort(key=lambda x: datetime.strptime(x["Date"], "%Y-%m-%d"))

    table = Table(title="All Expenses (Sorted by Date)", box=box.SIMPLE)
    table.add_column("Date", style="yellow")
    table.add_column("Category", style="cyan")
    table.add_column("Amount (₹)", justify="right", style="green")

    for row in reader:
        table.add_row(row["Date"], row["Category"], f"₹{float(row['Amount']):.2f}")

    console.print(table)


def plot_chart():
    console.print("\n[bold magenta]Bar Chart of All Categories (Total)[/bold magenta]")

    category_totals = {}
    with open(file_path, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            category = row["Category"].strip()
            try:
                amount = float(row["Amount"])
                if amount > 0:
                    category_totals[category] = category_totals.get(category, 0) + amount
            except:
                continue

    # Filter out zero-total categories
    category_totals = {k: v for k, v in category_totals.items() if v > 0}

    # ✅ If no data to show, generate empty chart
    if not category_totals:
        plt.figure(figsize=(8, 5))
        plt.title("No Expense Data to Display")
        plt.axis('off')  # Hide axes
        plt.savefig("expense_chart.png")
        plt.close()
        console.print("[yellow]No data found. Empty chart saved.[/yellow]")
        return

    # ✅ Otherwise, plot normal chart
    categories = list(category_totals.keys())
    amounts = list(category_totals.values())

    plt.figure(figsize=(10, 6))
    plt.bar(categories, amounts, color='mediumpurple')
    plt.xlabel("Category")
    plt.ylabel("Total Spent (₹)")
    plt.title("Expense Distribution by Category")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig("expense_chart.png")
    plt.close()

    console.print("[bold green]Chart saved as 'expense_chart.png'. Open it to view.[/bold green]")

def delete_expense():
    console.print("\n[bold red]Delete an Expense[/bold red]")

    if not os.path.exists(file_path):
        console.print("[red]No data file found![/red]")
        return

    with open(file_path, mode='r') as file:
        reader = list(csv.reader(file))
        header = reader[0]
        data = reader[1:]

    if not data:
        console.print("[yellow]No expenses to delete![/yellow]")
        return

    from datetime import datetime
    try:
        data.sort(key=lambda x: datetime.strptime(x[0], "%Y-%m-%d"))
    except:
        console.print("[red]Data format issue![/red]")
        return

    table = Table(title="Your Expenses", box=box.SIMPLE)
    table.add_column("No.", style="bold")
    table.add_column("Date", style="yellow")
    table.add_column("Category", style="cyan")
    table.add_column("Amount", justify="right", style="green")

    for idx, row in enumerate(data, start=1):
        table.add_row(str(idx), row[0], row[1], f"₹{row[2]}")

    console.print(table)

    choice = Prompt.ask("Enter the number of the row to delete (or '0' to cancel)")

    try:
        choice = int(choice)
        if choice == 0:
            console.print("[yellow]Cancelled.[/yellow]")
            return
        if 1 <= choice <= len(data):
            removed = data.pop(choice - 1)
            with open(file_path, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(header)
                writer.writerows(data)
            console.print(f"[green]Deleted:[/green] {removed[0]}, {removed[1]}, ₹{removed[2]}")
        else:
            console.print("[red]Invalid choice![/red]")
    except:
        console.print("[red]Invalid input![/red]")

    sort_expense_file()   # ✅ Automatically re-sort the file
    plot_chart()          # ✅ Automatically update chart image



def menu():
    sort_expense_file()
    while True:
        console.print("1. Add Expense")
        console.print("2. Show Monthly Report")
        console.print("3. Show Bar Chart")
        console.print("4. Show Full Detailed Report")
        console.print("5. Delete an Expense")  # ✅ NEW
        console.print("6. Exit")


        choice = Prompt.ask("Enter your choice")
        if choice == "1":
            add_expense()
        elif choice == "2":
            show_report()
        elif choice == "3":
            plot_chart()
        elif choice == "4":
            show_detailed_report()     
        elif choice == "5":
            delete_expense()  # ✅ NEW delete feature
        elif choice == "6":
            console.print("[bold blue]Goodbye![/bold blue]")
            break

        else:
            console.print("[red]Invalid choice. Try again.[/red]")

if __name__ == "__main__":
    menu()

