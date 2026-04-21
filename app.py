from flask import Flask, render_template, request, redirect
import psycopg2
import os

app = Flask(__name__)

DATABASE_URL = os.environ.get("DATABASE_URL")

def get_db_connection():
    if DATABASE_URL:
        return psycopg2.connect(DATABASE_URL)
    return None


@app.route('/')
def index():
    conn = get_db_connection()

    if conn is None:
        expenses = []
        total = 0
        return render_template('index.html', expenses=expenses, total=total)

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


@app.route('/add', methods=['POST'])
def add_expense():
    conn = get_db_connection()
    if conn is None:
        return "Database not connected."

    name = request.form['name']
    amount = float(request.form['amount'])

    cur = conn.cursor()
    cur.execute(
        'INSERT INTO expenses (name, amount) VALUES (%s, %s);',
        (name, amount)
    )

    conn.commit()
    cur.close()
    conn.close()

    return redirect('/')


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


if __name__ == '__main__':
    app.run(debug=True)