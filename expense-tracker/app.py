import streamlit as st
import sqlite3
import pandas as pd
from datetime import date

# ---------------- PAGE ----------------
st.set_page_config(
    page_title="Expense Tracker",
    page_icon="💸",
    layout="wide"
)

# ---------------- DATABASE ----------------
conn = sqlite3.connect("expenses.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    expense_date TEXT,
    category TEXT,
    amount REAL,
    note TEXT
)
""")
conn.commit()


# ---------------- FUNCTIONS ----------------
def add_expense(expense_date, category, amount, note):
    cursor.execute(
        "INSERT INTO expenses (expense_date, category, amount, note) VALUES (?, ?, ?, ?)",
        (expense_date, category, amount, note)
    )
    conn.commit()


def get_expenses():
    return pd.read_sql_query(
        "SELECT * FROM expenses ORDER BY expense_date DESC",
        conn
    )


# ---------------- SIDEBAR ----------------
st.sidebar.title("💸 Expense Tracker")
page = st.sidebar.radio(
    "Navigation",
    ["Dashboard", "Add Expense", "Expense History"]
)


# ---------------- DASHBOARD ----------------
if page == "Dashboard":
    st.title("📊 Expense Dashboard")

    df = get_expenses()

    if not df.empty:
        total = df["amount"].sum()
        count = len(df)
        avg = df["amount"].mean()

        col1, col2, col3 = st.columns(3)

        col1.metric("Total Spent", f"₹{total:.2f}")
        col2.metric("Transactions", count)
        col3.metric("Average", f"₹{avg:.2f}")

        st.subheader("Expenses by Category")

        chart_data = df.groupby("category")["amount"].sum()
        st.bar_chart(chart_data)

        st.subheader("Recent Expenses")
        st.dataframe(df, use_container_width=True)

    else:
        st.info("No expenses yet. Add your first expense.")


# ---------------- ADD EXPENSE ----------------
elif page == "Add Expense":
    st.title("➕ Add Expense")

    with st.form("expense_form"):
        expense_date = st.date_input("Date", value=date.today())

        category = st.selectbox(
            "Category",
            [
                "Food",
                "Travel",
                "Shopping",
                "Bills",
                "Health",
                "Entertainment",
                "Other"
            ]
        )

        amount = st.number_input(
            "Amount (₹)",
            min_value=0.0,
            step=10.0
        )

        note = st.text_input("Note")

        submitted = st.form_submit_button("Save Expense")

        if submitted:
            add_expense(
                str(expense_date),
                category,
                amount,
                note
            )
            st.success("Expense saved successfully ✅")


# ---------------- HISTORY ----------------
else:
    st.title("📜 Expense History")

    df = get_expenses()

    if not df.empty:
        st.dataframe(df, use_container_width=True)

        csv = df.to_csv(index=False).encode("utf-8")

        st.download_button(
            "⬇ Download CSV",
            csv,
            "expenses.csv",
            "text/csv"
        )
    else:
        st.info("No expense history available.")