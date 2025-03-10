from flask import Flask, render_template
from flask import request, redirect, url_for
import sqlite3
import pandas as pd
from datetime import datetime, timedelta








app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')


expenses = []



# Database Initialization
def init_db():
    conn = sqlite3.connect('database/expenses.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY,
            amount REAL,
            category TEXT,
            date TEXT,
            description TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# Combined Add Expense Route
@app.route('/add-expense', methods=['GET', 'POST'])
def add_expense():
    if request.method == 'POST':
        # Manual Entry Logic
        if 'amount' in request.form:
            conn = sqlite3.connect('database/expenses.db')
            cursor = conn.cursor()

            cursor.execute('''
                INSERT INTO expenses (amount, category, date, description)
                VALUES (?, ?, ?, ?)
            ''', (
                request.form['amount'],
                request.form['category'],
                request.form['date'],
                request.form['description']
            ))

            conn.commit()
            conn.close()

        # CSV Import Logic
        if 'file' in request.files:
            file = request.files['file']
            if file.filename.endswith('.csv'):
                data = pd.read_csv(file)
                conn = sqlite3.connect('database/expenses.db')
                data.to_sql('expenses', conn, if_exists='append', index=False)
                conn.commit()
                conn.close()

        return redirect(url_for('dashboard'))

    return render_template('add_expense.html')


# Dashboard Route
@app.route('/dashboard')
def dashboard():
    conn = sqlite3.connect('database/expenses.db')
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM expenses')
    expenses = cursor.fetchall()

    conn.close()
    return render_template('dashboard.html', expenses=expenses)







# import data from csv file to the database
@app.route('/import-expenses', methods=['GET', 'POST'])
def import_expenses():
    if request.method == 'POST':
        file = request.files['file']
        data = pd.read_csv(file)
        conn = sqlite3.connect('database/expenses.db')
        data.to_sql('expenses', conn, if_exists='append', index=False)
        conn.commit()
        conn.close()
        return redirect(url_for('dashboard'))
    return render_template('import_expenses.html')






def add_recurring_expense():
    conn = sqlite3.connect('database/expenses.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS recurring_expenses (
            id INTEGER PRIMARY KEY,
            amount REAL,
            category TEXT,
            next_due_date TEXT
        )
    ''')

    conn.commit()
    conn.close()




def add_recurring_expenses():
    conn = sqlite3.connect('database/expenses.db')
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM recurring_expenses')
    recurring_expenses = cursor.fetchall()

    for expense in recurring_expenses:
        next_due_date = datetime.strptime(expense[3], '%Y-%m-%d')
        if next_due_date <= datetime.now():
            cursor.execute('''
                INSERT INTO expenses (amount, category, date, description)
                VALUES (?, ?, ?, ?)
            ''', (expense[1], expense[2], next_due_date.strftime('%Y-%m-%d'), 'Recurring Payment'))

            next_due_date += timedelta(days=30)
            cursor.execute('UPDATE recurring_expenses SET next_due_date = ? WHERE id = ?',
                           (next_due_date.strftime('%Y-%m-%d'), expense[0]))

    conn.commit()
    conn.close()






if __name__ == '__main__':
    app.run(debug=True)
