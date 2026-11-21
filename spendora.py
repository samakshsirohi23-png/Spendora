"""
================================================================================
                                SPENDORA
     An Expense Intelligence & Budget Management System in Python
================================================================================
Bennett University - School of Computer Science Engineering and Technology
Course: Computational Thinking and Programming (2026CSAE100)
Academic Year: 2026-27

Team Members and Module Responsibilities:
1. Samaksh Sirohi    (S26CSEU1307) - CSV File Handling, Budget Alerts & Integration
2. Shatakshi          (S26CSEU1309) - Income Management Module
3. Keshav Garg        (S26CSEU1312) - Expense Management Module
4. Divyansh Choudhary (S26CSEU1319) - Category & Budget Management Module
5. Nikhil Yadav       (S26CSEU1293) - Expense Analysis & Reports Module
================================================================================
"""

import csv
import os
from datetime import datetime

# File paths for permanent data storage
TRANSACTIONS_FILE = "spendora_transactions.csv"
BUDGET_FILE = "spendora_budget.csv"

# Predefined categories for student budgeting
DEFAULT_CATEGORIES = [
    "Food",
    "Transport",
    "Education",
    "Entertainment",
    "Shopping",
    "Bills",
    "Health",
    "Other"
]

# Default income sources
DEFAULT_INCOME_SOURCES = [
    "Pocket Money",
    "Part-time Job",
    "Freelance",
    "Scholarship",
    "Gift",
    "Other"
]

# ==============================================================================
# MODULE 5 (Part A): CSV FILE HANDLING & DATA STORAGE
# Developed by: Samaksh Sirohi (Enrollment No: S26CSEU1307)
# ==============================================================================

def load_transactions(filename=TRANSACTIONS_FILE):
    """
    Reads existing transactions from a CSV file.
    Returns a list of transaction dictionaries.
    If the file does not exist, creates it with a header row.
    """
    transactions = []
    if not os.path.exists(filename):
        # Create a new CSV file with header if it doesn't exist
        try:
            with open(filename, mode="w", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow(["Date", "Type", "Category", "Amount", "Description"])
        except Exception as e:
            print(f"[Error] Could not initialize transactions file: {e}")
        return transactions

    try:
        with open(filename, mode="r", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                try:
                    transactions.append({
                        "date": row["Date"].strip(),
                        "type": row["Type"].strip().capitalize(),
                        "category": row["Category"].strip().capitalize(),
                        "amount": float(row["Amount"]),
                        "description": row["Description"].strip()
                    })
                except (ValueError, KeyError):
                    # Skip corrupted or malformed rows
                    continue
    except Exception as e:
        print(f"[Error] Failed to read transactions: {e}")

    return transactions

def save_all_transactions(transactions, filename=TRANSACTIONS_FILE):
    """
    Overwrites the CSV file with the complete list of transactions.
    """
    try:
        with open(filename, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["Date", "Type", "Category", "Amount", "Description"])
            for t in transactions:
                writer.writerow([t["date"], t["type"], t["category"], f"{t['amount']:.2f}", t["description"]])
        return True
    except Exception as e:
        print(f"[Error] Failed to save transactions: {e}")
        return False

def append_transaction_to_csv(transaction, filename=TRANSACTIONS_FILE):
    """
    Appends a single transaction to the CSV file to avoid rewriting everything.
    """
    file_exists = os.path.exists(filename)
    try:
        with open(filename, mode="a", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            if not file_exists:
                writer.writerow(["Date", "Type", "Category", "Amount", "Description"])
            writer.writerow([
                transaction["date"],
                transaction["type"],
                transaction["category"],
                f"{transaction['amount']:.2f}",
                transaction["description"]
            ])
        return True
    except Exception as e:
        print(f"[Error] Failed to append transaction: {e}")
        return False

def load_budget(filename=BUDGET_FILE):
    """
    Loads monthly budget settings from budget.csv.
    Returns a dictionary: {"monthly_budget": float, "categories": {cat: float}}
    """
    budget_data = {
        "monthly_budget": 0.0,
        "categories": {}
    }
    if not os.path.exists(filename):
        return budget_data

    try:
        with open(filename, mode="r", newline="", encoding="utf-8") as file:
            reader = csv.reader(file)
            for row in reader:
                if len(row) >= 2:
                    key = row[0].strip()
                    try:
                        val = float(row[1].strip())
                        if key.lower() == "monthly_budget":
                            budget_data["monthly_budget"] = val
                        else:
                            budget_data["categories"][key.capitalize()] = val
                    except ValueError:
                        continue
    except Exception as e:
        print(f"[Error] Failed to load budget: {e}")

    return budget_data

def save_budget(budget_data, filename=BUDGET_FILE):
    """
    Saves monthly budget and category limits to budget.csv.
    """
    try:
        with open(filename, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["monthly_budget", f"{budget_data['monthly_budget']:.2f}"])
            for cat, limit in budget_data["categories"].items():
                writer.writerow([cat, f"{limit:.2f}"])
        return True
    except Exception as e:
        print(f"[Error] Failed to save budget: {e}")
        return False

# Helper function for date input
def get_validated_date(prompt="Enter date (YYYY-MM-DD) or press Enter for today: "):
    """
    Validates user date input. Defaults to current date if blank.
    """
    while True:
        user_input = input(prompt).strip()
        if user_input == "":
            return datetime.now().strftime("%Y-%m-%d")
        try:
            parsed = datetime.strptime(user_input, "%Y-%m-%d")
            return parsed.strftime("%Y-%m-%d")
        except ValueError:
            print("  [!] Invalid date format. Please enter in YYYY-MM-DD format (e.g. 2026-10-15).")

# Helper function for positive float input
def get_positive_float(prompt):
    """
    Prompts the user until a positive float is entered.
    """
    while True:
        val_str = input(prompt).strip()
        try:
            val = float(val_str)
            if val <= 0:
                print("  [!] Amount must be greater than zero. Please try again.")
            else:
                return val
        except ValueError:
            print("  [!] Invalid numeric value. Please enter a valid number (e.g. 250 or 1500.50).")

# ==============================================================================
# MODULE 1: INCOME MANAGEMENT
# Developed by: Shatakshi (Enrollment No: S26CSEU1309)
# ==============================================================================

def add_income(transactions):
    """
    Records a new income entry from the user.
    Appends to memory list and persists to CSV file.
    """
    print("\n" + "=" * 50)
    print("           ADD NEW INCOME RECORD")
    print("=" * 50)

    # 1. Date
    date = get_validated_date("Enter date of income (YYYY-MM-DD) [Enter for Today]: ")

    # 2. Income Source
    print("\nSelect Income Source:")
    for idx, source in enumerate(DEFAULT_INCOME_SOURCES, 1):
        print(f"  {idx}. {source}")
    print(f"  {len(DEFAULT_INCOME_SOURCES) + 1}. Custom Source")

    source_choice = input(f"Enter choice (1-{len(DEFAULT_INCOME_SOURCES) + 1}): ").strip()
    try:
        source_idx = int(source_choice)
        if 1 <= source_idx <= len(DEFAULT_INCOME_SOURCES):
            category = DEFAULT_INCOME_SOURCES[source_idx - 1]
        elif source_idx == len(DEFAULT_INCOME_SOURCES) + 1:
            category = input("Enter custom income source name: ").strip().capitalize()
            if not category:
                category = "Other"
        else:
            category = "Other"
    except ValueError:
        category = "Other"

    # 3. Amount
    amount = get_positive_float("Enter income amount (Rs.): ")

    # 4. Description
    desc = input("Enter description or remarks (optional): ").strip()
    if not desc:
        desc = "No remarks"

    # Create transaction dictionary
    transaction = {
        "date": date,
        "type": "Income",
        "category": category,
        "amount": amount,
        "description": desc
    }

    # Add to list and save to CSV
    transactions.append(transaction)
    append_transaction_to_csv(transaction)

    print("\n[SUCCESS] Income of Rs. {:.2f} from '{}' recorded successfully!".format(amount, category))

def view_income_records(transactions):
    """
    Displays all income transactions in a formatted tabular view.
    """
    print("\n" + "=" * 70)
    print("                     INCOME RECORDS")
    print("=" * 70)

    income_list = [t for t in transactions if t["type"] == "Income"]

    if not income_list:
        print("  No income records found. Add an income record from the main menu!")
        print("=" * 70)
        return

    print(f"{'S.No':<6}{'Date':<14}{'Source':<18}{'Amount (Rs.)':<15}{'Description'}")
    print("-" * 70)

    total_income = 0.0
    for idx, item in enumerate(income_list, 1):
        print(f"{idx:<6}{item['date']:<14}{item['category']:<18}{item['amount']:<15.2f}{item['description']}")
        total_income += item["amount"]

    print("-" * 70)
    print(f"TOTAL INCOME RECORDED: Rs. {total_income:.2f}")
    print("=" * 70)

# ==============================================================================
# MODULE 2: EXPENSE MANAGEMENT
# Developed by: Keshav Garg (Enrollment No: S26CSEU1312)
# ==============================================================================

def add_expense(transactions, categories, budget_data):
    """
    Records a new daily expense with category, date, amount, and description.
    Also triggers an immediate budget check alert.
    """
    print("\n" + "=" * 50)
    print("           RECORD DAILY EXPENSE")
    print("=" * 50)

    # 1. Date
    date = get_validated_date("Enter date of expense (YYYY-MM-DD) [Enter for Today]: ")

    # 2. Category selection
    print("\nSelect Expense Category:")
    for idx, cat in enumerate(categories, 1):
        print(f"  {idx}. {cat}")
    print(f"  {len(categories) + 1}. Add New Category")

    cat_choice = input(f"Enter choice (1-{len(categories) + 1}): ").strip()
    try:
        cat_idx = int(cat_choice)
        if 1 <= cat_idx <= len(categories):
            category = categories[cat_idx - 1]
        elif cat_idx == len(categories) + 1:
            new_cat = input("Enter new category name: ").strip().capitalize()
            if new_cat and new_cat not in categories:
                categories.append(new_cat)
                category = new_cat
            elif new_cat in categories:
                category = new_cat
            else:
                category = "Other"
        else:
            category = "Other"
    except ValueError:
        category = "Other"

    # 3. Amount
    amount = get_positive_float("Enter expense amount (Rs.): ")

    # 4. Description
    desc = input("Enter brief description (e.g. Canteen lunch, Metro recharge): ").strip()
    if not desc:
        desc = "General expense"

    # Create transaction dictionary
    transaction = {
        "date": date,
        "type": "Expense",
        "category": category,
        "amount": amount,
        "description": desc
    }

    transactions.append(transaction)
    append_transaction_to_csv(transaction)

    print(f"\n[SUCCESS] Expense of Rs. {amount:.2f} for '{category}' added successfully!")

    # Instant alert check
    if budget_data["monthly_budget"] > 0:
        current_spent = sum(t["amount"] for t in transactions if t["type"] == "Expense")
        monthly_limit = budget_data["monthly_budget"]
        pct = (current_spent / monthly_limit) * 100

        print("\n" + "-" * 50)
        print(">> INSTANT BUDGET MONITOR <<")
        print(f"   Total Spent: Rs. {current_spent:.2f} / Rs. {monthly_limit:.2f} ({pct:.1f}%)")
        if current_spent > monthly_limit:
            exceeded_by = current_spent - monthly_limit
            print(f"   [!] ALERT: You have EXCEEDED your monthly budget by Rs. {exceeded_by:.2f}!")
        elif pct >= 85:
            remaining = monthly_limit - current_spent
            print(f"   [!] WARNING: You have utilized {pct:.1f}% of your budget! Only Rs. {remaining:.2f} left.")
        else:
            remaining = monthly_limit - current_spent
            print(f"   [i] On track! Remaining budget: Rs. {remaining:.2f}")
        print("-" * 50)

def view_all_expenses(transactions):
    """
    Displays all recorded expenses in an organized table.
    """
    print("\n" + "=" * 70)
    print("                     EXPENSE RECORDS")
    print("=" * 70)

    expense_list = [t for t in transactions if t["type"] == "Expense"]

    if not expense_list:
        print("  No expenses recorded yet. Good job or start adding expenses!")
        print("=" * 70)
        return

    print(f"{'S.No':<6}{'Date':<14}{'Category':<18}{'Amount (Rs.)':<15}{'Description'}")
    print("-" * 70)

    total_expense = 0.0
    for idx, item in enumerate(expense_list, 1):
        print(f"{idx:<6}{item['date']:<14}{item['category']:<18}{item['amount']:<15.2f}{item['description']}")
        total_expense += item["amount"]

    print("-" * 70)
    print(f"TOTAL EXPENSES: Rs. {total_expense:.2f}")
    print("=" * 70)

def filter_expenses_by_category(transactions, categories):
    """
    Filters and displays expenses belonging to a specific category.
    """
    print("\n" + "=" * 50)
    print("        FILTER EXPENSES BY CATEGORY")
    print("=" * 50)

    print("Available Categories:")
    for idx, cat in enumerate(categories, 1):
        print(f"  {idx}. {cat}")

    choice = input(f"Select category to filter (1-{len(categories)}): ").strip()
    try:
        idx = int(choice)
        if 1 <= idx <= len(categories):
            selected_cat = categories[idx - 1]
        else:
            print("[!] Invalid category choice.")
            return
    except ValueError:
        print("[!] Invalid input.")
        return

    filtered = [t for t in transactions if t["type"] == "Expense" and t["category"].lower() == selected_cat.lower()]

    print("\n" + "=" * 70)
    print(f"       EXPENSE RECORDS FOR CATEGORY: {selected_cat.upper()}")
    print("=" * 70)

    if not filtered:
        print(f"  No expense records found for category '{selected_cat}'.")
        print("=" * 70)
        return

    print(f"{'S.No':<6}{'Date':<14}{'Amount (Rs.)':<15}{'Description'}")
    print("-" * 70)
    cat_total = 0.0
    for idx, item in enumerate(filtered, 1):
        print(f"{idx:<6}{item['date']:<14}{item['amount']:<15.2f}{item['description']}")
        cat_total += item["amount"]

    print("-" * 70)
    print(f"TOTAL FOR {selected_cat.upper()}: Rs. {cat_total:.2f}")
    print("=" * 70)

# ==============================================================================
# MODULE 3: CATEGORY & BUDGET MANAGEMENT
# Developed by: Divyansh Choudhary (Enrollment No: S26CSEU1319)
# ==============================================================================

def set_monthly_budget(budget_data):
    """
    Sets or updates the overall monthly budget limit and optional category caps.
    """
    print("\n" + "=" * 50)
    print("            SET MONTHLY BUDGET")
    print("=" * 50)
    print(f"Current Monthly Budget: Rs. {budget_data['monthly_budget']:.2f}")

    new_budget = get_positive_float("Enter new monthly budget limit (Rs.): ")
    budget_data["monthly_budget"] = new_budget

    # Ask if user wants to set category-wise budgets
    set_cat = input("\nDo you want to set individual category limits? (y/n): ").strip().lower()
    if set_cat == 'y':
        print("\nEnter category budget caps (enter 0 to skip or remove limit):")
        for cat in DEFAULT_CATEGORIES:
            curr_limit = budget_data["categories"].get(cat, 0.0)
            prompt = f"  Budget for {cat} (Current: Rs. {curr_limit:.2f}) [Enter for no change]: "
            val_str = input(prompt).strip()
            if val_str:
                try:
                    val = float(val_str)
                    if val > 0:
                        budget_data["categories"][cat] = val
                    elif val == 0 and cat in budget_data["categories"]:
                        del budget_data["categories"][cat]
                except ValueError:
                    print(f"    Invalid input for {cat}, keeping existing limit.")

    save_budget(budget_data)
    print(f"\n[SUCCESS] Monthly budget of Rs. {new_budget:.2f} saved successfully!")

def view_budget_status(budget_data, transactions):
    """
    Displays the current budget status, spending progress, and remaining allowance.
    """
    print("\n" + "=" * 60)
    print("                 BUDGET STATUS OVERVIEW")
    print("=" * 60)

    monthly_limit = budget_data.get("monthly_budget", 0.0)
    total_spent = sum(t["amount"] for t in transactions if t["type"] == "Expense")

    if monthly_limit == 0:
        print("  No monthly budget set yet! Please set a budget using Option 4.")
        print(f"  Total Expenses Incurred So Far: Rs. {total_spent:.2f}")
        print("=" * 60)
        return

    remaining = monthly_limit - total_spent
    percentage = (total_spent / monthly_limit) * 100

    print(f"  Monthly Budget Limit : Rs. {monthly_limit:>10.2f}")
    print(f"  Total Amount Spent   : Rs. {total_spent:>10.2f}")
    print(f"  Remaining Balance    : Rs. {remaining:>10.2f}")
    print(f"  Budget Utilization   : {percentage:>9.1f}%")

    # Simple text progress bar
    bar_length = 30
    filled_length = int(min(percentage, 100) / 100 * bar_length)
    bar = "#" * filled_length + "-" * (bar_length - filled_length)
    print(f"\n  Progress: [{bar}] {min(percentage, 999):.1f}%")

    # Category limits breakdown if configured
    if budget_data["categories"]:
        print("\n  Category-wise Budget Caps:")
        print(f"  {'Category':<16}{'Budget':<12}{'Spent':<12}{'Status'}")
        print("  " + "-" * 50)
        for cat, limit in budget_data["categories"].items():
            cat_spent = sum(t["amount"] for t in transactions if t["type"] == "Expense" and t["category"].lower() == cat.lower())
            status = "EXCEEDED" if cat_spent > limit else f"OK ({cat_spent/limit*100:.0f}%)"
            print(f"  {cat:<16}Rs.{limit:<9.2f}Rs.{cat_spent:<9.2f}{status}")

    print("=" * 60)

def manage_categories(categories):
    """
    Allows adding new custom expense categories.
    """
    print("\n" + "=" * 50)
    print("            MANAGE CATEGORIES")
    print("=" * 50)
    print("Current Categories:")
    for idx, cat in enumerate(categories, 1):
        print(f"  {idx}. {cat}")

    new_cat = input("\nEnter new category name (or press Enter to cancel): ").strip().capitalize()
    if new_cat:
        if new_cat in categories:
            print(f"  [i] Category '{new_cat}' already exists!")
        else:
            categories.append(new_cat)
            print(f"  [SUCCESS] Category '{new_cat}' added successfully!")
    else:
        print("  No category added.")

# ==============================================================================
# MODULE 4: EXPENSE ANALYSIS & REPORT GENERATION
# Developed by: Nikhil Yadav (Enrollment No: S26CSEU1293)
# ==============================================================================

def calculate_category_totals(transactions):
    """
    Computes total spending per category.
    Returns a dictionary: {category: total_amount}
    """
    totals = {}
    for t in transactions:
        if t["type"] == "Expense":
            cat = t["category"]
            totals[cat] = totals.get(cat, 0.0) + t["amount"]
    return totals

def display_ascii_chart(category_totals, total_expense):
    """
    Computational Feature:
    Visualizes expense breakdown using a horizontal ASCII bar chart.
    """
    print("\n  Category Spending Visual Chart:")
    print("  " + "-" * 55)
    max_bar_width = 25

    # Sort categories in descending order of spending
    sorted_cats = sorted(category_totals.items(), key=lambda x: x[1], reverse=True)

    for cat, amt in sorted_cats:
        pct = (amt / total_expense) * 100 if total_expense > 0 else 0
        bar_len = int((amt / total_expense) * max_bar_width) if total_expense > 0 else 0
        bar = "#" * bar_len
        print(f"  {cat:<14} | {bar:<{max_bar_width}} | {pct:>5.1f}% (Rs. {amt:.2f})")
    print("  " + "-" * 55)

def generate_expense_analysis(transactions, budget_data):
    """
    Computes high-level financial metrics:
    - Total Income, Total Expenses, Net Savings
    - Highest & Lowest spending categories
    - Average daily spending
    - Visual ASCII chart
    """
    print("\n" + "=" * 65)
    print("            SPENDORA EXPENSE INTELLIGENCE & ANALYSIS")
    print("=" * 65)

    total_income = sum(t["amount"] for t in transactions if t["type"] == "Income")
    total_expense = sum(t["amount"] for t in transactions if t["type"] == "Expense")
    net_savings = total_income - total_expense

    savings_rate = (net_savings / total_income * 100) if total_income > 0 else 0.0

    print(f"  Total Income Recorded   : Rs. {total_income:>10.2f}")
    print(f"  Total Expenses Incurred : Rs. {total_expense:>10.2f}")
    print(f"  Net Savings / Balance   : Rs. {net_savings:>10.2f}")
    if total_income > 0:
        print(f"  Savings Rate            : {savings_rate:>9.1f}%")

    if total_expense == 0:
        print("\n  [i] No expenses recorded yet for detailed analysis.")
        print("=" * 65)
        return

    # Category analysis
    cat_totals = calculate_category_totals(transactions)

    # Highest & Lowest category
    highest_cat = max(cat_totals.items(), key=lambda x: x[1])
    lowest_cat = min(cat_totals.items(), key=lambda x: x[1])

    print("\n  Key Insights:")
    print(f"  - Highest Spending Category : {highest_cat[0]} (Rs. {highest_cat[1]:.2f}, {highest_cat[1]/total_expense*100:.1f}%)")
    print(f"  - Lowest Spending Category  : {lowest_cat[0]} (Rs. {lowest_cat[1]:.2f}, {lowest_cat[1]/total_expense*100:.1f}%)")

    # Unique dates calculation for daily average
    expense_dates = set(t["date"] for t in transactions if t["type"] == "Expense")
    num_days = max(len(expense_dates), 1)
    daily_avg = total_expense / num_days
    print(f"  - Active Spending Days      : {num_days}")
    print(f"  - Average Daily Spend       : Rs. {daily_avg:.2f} / day")

    # ASCII Chart
    display_ascii_chart(cat_totals, total_expense)

    # Rule-Based Smart Suggestions (Computational Thinking)
    print("\n  Spendora Smart Financial Advice:")
    if savings_rate < 15 and total_income > 0:
        print("  * [Alert] Your savings rate is below 15%! Try to curtail non-essential spending.")
    elif savings_rate >= 30:
        print("  * [Great Job!] Healthy savings rate above 30%. Consider putting savings in an FD or emergency fund.")

    if highest_cat[0] == "Food" and (highest_cat[1] / total_expense) > 0.40:
        print("  * [Tip] Over 40% of your expenses go towards Food. Consider eating at the college mess more often.")
    elif highest_cat[0] == "Entertainment" and (highest_cat[1] / total_expense) > 0.25:
        print("  * [Tip] Entertainment spending is relatively high (>25%). Review weekend outings.")

    print("=" * 65)

def generate_monthly_report(transactions, budget_data):
    """
    Generates a formal monthly expense report that can be viewed or exported.
    """
    print("\n" + "=" * 65)
    print("               SPENDORA MONTHLY SUMMARY REPORT")
    print("=" * 65)

    month_input = input("Enter month to filter (YYYY-MM) or press Enter for All Time: ").strip()

    if month_input:
        selected_transactions = [t for t in transactions if t["date"].startswith(month_input)]
        header_title = f"MONTHLY REPORT FOR {month_input}"
    else:
        selected_transactions = transactions
        header_title = "COMPREHENSIVE ALL-TIME FINANCIAL REPORT"

    if not selected_transactions:
        print(f"  No records found for '{month_input}'.")
        print("=" * 65)
        return

    income_total = sum(t["amount"] for t in selected_transactions if t["type"] == "Income")
    expense_total = sum(t["amount"] for t in selected_transactions if t["type"] == "Expense")
    net_balance = income_total - expense_total

    print(f"\n  Report Scope: {header_title}")
    print("  " + "-" * 60)
    print(f"  {'Metric':<30}{'Value (Rs.)'}")
    print("  " + "-" * 60)
    print(f"  {'Total Income':<30}Rs. {income_total:>10.2f}")
    print(f"  {'Total Expenditure':<30}Rs. {expense_total:>10.2f}")
    print(f"  {'Net Savings / Balance':<30}Rs. {net_balance:>10.2f}")

    if budget_data["monthly_budget"] > 0:
        budget_limit = budget_data["monthly_budget"]
        utilization = (expense_total / budget_limit) * 100
        print(f"  {'Predefined Budget':<30}Rs. {budget_limit:>10.2f}")
        print(f"  {'Budget Utilization':<30}{utilization:>9.1f}%")
        compliance = "Within Budget" if expense_total <= budget_limit else "OVER BUDGET"
        print(f"  {'Budget Compliance Status':<30}{compliance}")

    print("  " + "-" * 60)
    print("\n  Category-wise Breakdown:")
    print(f"  {'Category':<20}{'Amount (Rs.)':<15}{'Share (%)'}")
    print("  " + "-" * 45)

    cat_totals = calculate_category_totals(selected_transactions)
    for cat, amt in sorted(cat_totals.items(), key=lambda x: x[1], reverse=True):
        share = (amt / expense_total * 100) if expense_total > 0 else 0
        print(f"  {cat:<20}Rs. {amt:<11.2f}{share:>6.1f}%")

    print("=" * 65)

# ==============================================================================
# MODULE 5 (Part B): BUDGET ALERTS, TESTING & INTEGRATION
# Developed by: Samaksh Sirohi (Enrollment No: S26CSEU1307)
# ==============================================================================

def check_budget_alerts(transactions, budget_data):
    """
    Evaluates current spending vs budget and displays actionable notifications.
    Thresholds:
      - 0% - 79%: Healthy spending
      - 80% - 99%: Caution / Warning zone
      - 100%+: Exceeded budget / Critical alert
    """
    print("\n" + "=" * 60)
    print("               BUDGET NOTIFICATIONS & ALERTS")
    print("=" * 60)

    monthly_limit = budget_data.get("monthly_budget", 0.0)
    if monthly_limit <= 0:
        print("  [Notice] No monthly budget set! Please configure your budget")
        print("  in Option 4 to enable proactive spending alerts.")
        print("=" * 60)
        return

    total_spent = sum(t["amount"] for t in transactions if t["type"] == "Expense")
    pct = (total_spent / monthly_limit) * 100

    print(f"  Budget Limit : Rs. {monthly_limit:.2f}")
    print(f"  Total Spent  : Rs. {total_spent:.2f} ({pct:.1f}%)\n")

    if total_spent > monthly_limit:
        excess = total_spent - monthly_limit
        print("  [CRITICAL ALERT] 🚨")
        print(f"  You have EXCEEDED your monthly budget by Rs. {excess:.2f}!")
        print("  Immediate Action: Stop discretionary spending and review transactions.")
    elif pct >= 80:
        remaining = monthly_limit - total_spent
        print("  [WARNING ALERT] ⚠️")
        print(f"  You have reached {pct:.1f}% of your monthly budget!")
        print(f"  Only Rs. {remaining:.2f} is remaining for the rest of the period.")
        print("  Suggestion: Slow down on entertainment and dining out.")
    else:
        remaining = monthly_limit - total_spent
        print("  [HEALTHY STATUS] [OK]")
        print(f"  You are well within your budget limit ({pct:.1f}% consumed).")
        print(f"  Remaining safe spending allowance: Rs. {remaining:.2f}")

    # Check individual category alerts
    if budget_data["categories"]:
        print("\n  Category-Level Alerts:")
        for cat, limit in budget_data["categories"].items():
            cat_spent = sum(t["amount"] for t in transactions if t["type"] == "Expense" and t["category"].lower() == cat.lower())
            if cat_spent > limit:
                print(f"  - [!] '{cat}' has exceeded its cap by Rs. {cat_spent - limit:.2f} (Spent: Rs.{cat_spent:.2f} / Cap: Rs.{limit:.2f})")
            elif (cat_spent / limit) >= 0.85:
                print(f"  - [!] '{cat}' is near its limit ({cat_spent/limit*100:.1f}% used).")

    print("=" * 60)

def view_all_transactions(transactions):
    """
    Displays unified chronological list of all Income and Expense transactions.
    """
    print("\n" + "=" * 80)
    print("                     ALL TRANSACTIONS (UNIFIED VIEW)")
    print("=" * 80)

    if not transactions:
        print("  No transactions found in records!")
        print("=" * 80)
        return

    print(f"{'S.No':<5}{'Date':<13}{'Type':<10}{'Category':<16}{'Amount (Rs.)':<15}{'Description'}")
    print("-" * 80)

    for idx, t in enumerate(transactions, 1):
        sign = "+" if t["type"] == "Income" else "-"
        amt_str = f"{sign}Rs. {t['amount']:.2f}"
        print(f"{idx:<5}{t['date']:<13}{t['type']:<10}{t['category']:<16}{amt_str:<15}{t['description']}")

    print("-" * 80)
    tot_inc = sum(t["amount"] for t in transactions if t["type"] == "Income")
    tot_exp = sum(t["amount"] for t in transactions if t["type"] == "Expense")
    print(f"  Total Income: Rs. {tot_inc:.2f} | Total Expenses: Rs. {tot_exp:.2f} | Net Balance: Rs. {tot_inc - tot_exp:.2f}")
    print("=" * 80)

def display_welcome_banner():
    """
    Displays Spendora CLI banner and student project info.
    """
    print("""
========================================================================
       __                           _                  
      / _| _ _   __ _ _   _| | _  _ _ _ _ 
      \\_ \\| '_ \\ / _ \\ '_ \\ /  |/ _ \\| '_/ _ |
       _) | |) |  _/ | | | (| | () | | | (_| |
      |_/| ./ \\_|| ||\\,|\\_/||  \\,|
            |_|                                     
            Track  *  Plan  *  Grow
      Expense Intelligence for Bennett University Students
========================================================================
Course  : Computational Thinking and Programming (2026CSAE100)
Batch   : 37 / S-19
Members : Samaksh, Shatakshi, Keshav, Divyansh, Nikhil
========================================================================
""")

def main():
    """
    Main function: Orchestrates program startup, data loading,
    menu loop, and clean exit.
    """
    display_welcome_banner()

    # Load persistent data
    print("[1/2] Loading transactions from CSV...")
    transactions = load_transactions(TRANSACTIONS_FILE)
    print(f"      Loaded {len(transactions)} transaction(s).")

    print("[2/2] Loading budget configuration from CSV...")
    budget_data = load_budget(BUDGET_FILE)
    if budget_data["monthly_budget"] > 0:
        print(f"      Active Monthly Budget: Rs. {budget_data['monthly_budget']:.2f}")
    else:
        print("      No monthly budget configured yet.")

    categories = list(DEFAULT_CATEGORIES)

    # Main Interactive Loop
    while True:
        print("\n" + "=" * 45)
        print("               SPENDORA MAIN MENU")
        print("=" * 45)
        print("  1. Add Income Record")
        print("  2. Add Expense Record")
        print("  3. View All Expenses")
        print("  4. View All Income Records")
        print("  5. View All Transactions (Unified)")
        print("  6. Filter Expenses by Category")
        print("  7. Set / Update Monthly Budget")
        print("  8. View Budget Status")
        print("  9. Check Budget Alerts & Warnings")
        print(" 10. Financial Analysis & Insights (Chart)")
        print(" 11. Generate Monthly Summary Report")
        print(" 12. Manage Expense Categories")
        print(" 13. Save & Exit")
        print("=" * 45)

        choice = input("Enter your choice (1-13): ").strip()

        if choice == "1":
            add_income(transactions)

        elif choice == "2":
            add_expense(transactions, categories, budget_data)

        elif choice == "3":
            view_all_expenses(transactions)

        elif choice == "4":
            view_income_records(transactions)

        elif choice == "5":
            view_all_transactions(transactions)

        elif choice == "6":
            filter_expenses_by_category(transactions, categories)

        elif choice == "7":
            set_monthly_budget(budget_data)

        elif choice == "8":
            view_budget_status(budget_data, transactions)

        elif choice == "9":
            check_budget_alerts(transactions, budget_data)

        elif choice == "10":
            generate_expense_analysis(transactions, budget_data)

        elif choice == "11":
            generate_monthly_report(transactions, budget_data)

        elif choice == "12":
            manage_categories(categories)

        elif choice == "13":
            print("\nSaving latest data to CSV files...")
            save_all_transactions(transactions, TRANSACTIONS_FILE)
            save_budget(budget_data, BUDGET_FILE)
            print("\n[!] Thank you for using Spendora! Track, Plan, and Grow.")
            print("Exiting program. Goodbye!\n")
            break

        else:
            print("\n[!] Invalid choice! Please select an option between 1 and 13.")

if __name__ == "__main__":
    main()