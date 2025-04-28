# Import necessary libraries
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import PhotoImage
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import datetime

# Database setup for persistent data storage
conn = sqlite3.connect("expenses.db")
cursor = conn.cursor()

# table for storing expense data remember to look up more on this self note
cursor.execute("""
    CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY,         -- Unique ID for each expense
        category TEXT,                  --Expense category (e.g., Food, Rent)
        amount REAL,                    -- Amount of the expense
        description TEXT,               -- Optional description of the expense
        timestamp TEXT                  -- Date and time of the expense entry
    )
""")
conn.commit()

# Global Budget Limit
BUDGET_LIMIT = 500.00  

# Function to navigate between windows
def switch_window(current_window, new_window_func):
    current_window.withdraw()  # Hide the current window
    new_window_func()          # Open the new window

# Main Dashboard Window
def main_dashboard():
    """
    Main dashboard window where users can see total expenses, navigate to other
    sections like analytics and add expense, and view budget alerts.
    """
    dashboard = tk.Toplevel()
    dashboard.title("Everyday Expenses Dashboard")
    dashboard.geometry("600x400")

    # Add an image/logo to the dashboard self note remember to get real photo during final testing
    logo_image = PhotoImage(file="logo.png")  # doesnt exist yet in my project directory
    tk.Label(dashboard, image=logo_image).pack()
    dashboard.image = logo_image  # Keep a reference to avoid garbage collection

    # Display total expenses
    cursor.execute("SELECT SUM(amount) FROM expenses")
    total_expenses = cursor.fetchone()[0] or 0
    tk.Label(dashboard, text=f"Total Expenses: ${total_expenses:.2f}", font=("Arial", 14)).pack(pady=10)

    # Navigation buttons
    tk.Button(dashboard, text="Add Expense", command=lambda: switch_window(dashboard, expense_entry_form)).pack(pady=5)
    tk.Button(dashboard, text="View Analytics", command=lambda: switch_window(dashboard, analytics_window)).pack(pady=5)
    tk.Button(dashboard, text="Exit", command=dashboard.destroy).pack(pady=20)

# Expense Entry Form Window
def expense_entry_form():
    """
    Window for adding a new expense to the tracker. Includes input fields,
    input validation, and saving the expense to the SQLite database.
    """
    entry_form = tk.Toplevel()
    entry_form.title("Add Expense")
    entry_form.geometry("400x300")

    # Labels and input fields
    tk.Label(entry_form, text="Category:").grid(row=0, column=0, padx=10, pady=5)
    category_var = ttk.Combobox(entry_form, values=["Food", "Rent", "Utilities", "Entertainment", "Misc"], state="readonly")
    category_var.grid(row=0, column=1)

    tk.Label(entry_form, text="Amount ($):").grid(row=1, column=0, padx=10, pady=5)
    amount_entry = tk.Entry(entry_form)
    amount_entry.grid(row=1, column=1)

    tk.Label(entry_form, text="Description:").grid(row=2, column=0, padx=10, pady=5)
    description_entry = tk.Entry(entry_form)
    description_entry.grid(row=2, column=1)

    # Submit expense function
    def add_expense():
        category = category_var.get()
        amount = amount_entry.get()
        description = description_entry.get()

        # Validate input
        try:
            amount = float(amount)
            if amount <= 0:
                raise ValueError("Amount must be positive.")
        except ValueError:
            messagebox.showerror("Input Error", "Please enter a valid positive number.")
            return

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("INSERT INTO expenses (category, amount, description, timestamp) VALUES (?, ?, ?, ?)",
                       (category, amount, description, timestamp))
        conn.commit()

        # Check budget threshold
        cursor.execute("SELECT SUM(amount) FROM expenses")
        total = cursor.fetchone()[0] or 0
        if total > BUDGET_LIMIT:
            messagebox.showwarning("Budget Alert", f"Total expenses (${total:.2f}) exceed the budget limit (${BUDGET_LIMIT:.2f})!")

        messagebox.showinfo("Success", "Expense added successfully!")
        entry_form.destroy()
        main_dashboard()

    tk.Button(entry_form, text="Submit Expense", command=add_expense).grid(row=3, column=1, pady=10)

    # Back navigation
    tk.Button(entry_form, text="Back", command=lambda: switch_window(entry_form, main_dashboard)).grid(row=4, column=1)

# Analytics Window
def analytics_window():
    """
    Window for viewing analytics, including a bar graph of expenses per category
    and the ability to export expense data to a CSV file.
    """
    analytics = tk.Toplevel()
    analytics.title("Spending Analytics")
    analytics.geometry("600x400")

    # Show graph of spending trends
    def plot_expenses():
        cursor.execute("SELECT category, SUM(amount) FROM expenses GROUP BY category")
        data = cursor.fetchall()

        if not data:
            messagebox.showwarning("No Data", "No expense data available for analytics.")
            return

        categories, amounts = zip(*data)
        plt.figure(figsize=(6, 4))
        plt.bar(categories, amounts, color="skyblue", edgecolor="black")
        plt.xlabel("Categories")
        plt.ylabel("Total Spent ($)")
        plt.title("Spending Trends")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()

    # Export to CSV function
    def export_to_csv():
        cursor.execute("SELECT category, amount, description, timestamp FROM expenses")
        data = cursor.fetchall()

        if not data:
            messagebox.showwarning("No Data", "No expenses to export.")
            return

        df = pd.DataFrame(data, columns=["Category", "Amount ($)", "Description", "Timestamp"])
        df.to_csv("expenses.csv", index=False)
        messagebox.showinfo("Export Successful", "Expenses saved to 'expenses.csv'.")

    # Buttons for analytics
    tk.Button(analytics, text="Show Spending Graph", command=plot_expenses).pack(pady=10)
    tk.Button(analytics, text="Export to CSV", command=export_to_csv).pack(pady=10)
    tk.Button(analytics, text="Back", command=lambda: switch_window(analytics, main_dashboard)).pack(pady=10)

# Root (welcome) window
root = tk.Tk()
root.title("Everyday Expenses Tracker")
root.geometry("400x300")

# Welcome screen image
welcome_image = PhotoImage(file="welcome.png")  # remember to put welcome.png in my project directory
tk.Label(root, image=welcome_image).pack()
root.image = welcome_image

# Welcome screen navigation
tk.Button(root, text="Go to Dashboard", command=lambda: switch_window(root, main_dashboard)).pack(pady=10)
tk.Button(root, text="Exit", command=root.quit).pack(pady=10)

root.mainloop()