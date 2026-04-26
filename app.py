from flask import Flask, render_template, request, redirect
import psycopg2
import os

app = Flask(__name__)

# Get database URL from environment variable
DATABASE_URL = os.environ.get("DATABASE_URL")


# Connect to database
def get_db_connection():
    try:
        if DATABASE_URL:
            return psycopg2.connect(DATABASE_URL)
    except:
        return None
    return None


# Auto-create table
def init_db():
    conn = get_db_connection()
    if conn:
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS expenses (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                amount DECIMAL NOT NULL
            );
        """)
        conn.commit()
        cur.close()
        conn.close()
init_db()


# Home page
@app.route('/')
def index():
    conn = get_db_connection()

    if conn is None:
        return "Database connection failed."

    cur = conn.cursor()

    cur.execute('SELECT * FROM expenses ORDER BY id DESC;')
    expenses = cur.fetchall()

    cur.execute('SELECT SUM(amount) FROM expenses;')
    total = cur.fetchone()[0]

    if total is None:
        total = 0

    cur.close()
    conn.close()

    return render_template('index.html', expenses=expenses, total=total)


# Add expense
@app.route('/add', methods=['POST'])
def add_expense():
    name = request.form['name']
    amount = request.form['amount']

    conn = get_db_connection()
    if conn is None:
        return "Database not connected."

    cur = conn.cursor()
    cur.execute(
        'INSERT INTO expenses (name, amount) VALUES (%s, %s);',
        (name, amount)
    )

    conn.commit()
    cur.close()
    conn.close()

    return redirect('/')


# Delete expense
@app.route('/delete/<int:id>')
def delete_expense(id):
    conn = get_db_connection()

    if conn is None:
        return "Database not connected."

    cur = conn.cursor()
    cur.execute('DELETE FROM expenses WHERE id = %s;', (id,))

    conn.commit()
    cur.close()
    conn.close()

    return redirect('/')


# Run app
if __name__ == '__main__':
    init_db()   
    app.run(debug=True)