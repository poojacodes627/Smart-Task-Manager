from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "secret123"

# ---------- DATABASE ----------
def init_db():
    conn = sqlite3.connect('database.db')

    conn.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )
    ''')

    conn.execute('''
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        task TEXT,
        priority TEXT,
        deadline TEXT,
        status TEXT,
        user_id INTEGER
    )
    ''')

    conn.close()

init_db()

# ---------- HOME ----------
@app.route('/', methods=['GET', 'POST'])
def home():
    if 'user_id' not in session:
        return redirect('/login')

    user_id = session['user_id']
    conn = sqlite3.connect('database.db')

    if request.method == 'POST':
        task = request.form['task']
        priority = request.form['priority']
        deadline = request.form['deadline']

        conn.execute(
            "INSERT INTO tasks (task, priority, deadline, status, user_id) VALUES (?, ?, ?, ?, ?)",
            (task, priority, deadline, "Pending", user_id)
        )
        conn.commit()

    tasks = conn.execute(
        "SELECT * FROM tasks WHERE user_id=?", (user_id,)
    ).fetchall()

    conn.close()

    return render_template('index.html', tasks=tasks)

# ---------- REGISTER ----------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('database.db')
        conn.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (username, password)
        )
        conn.commit()
        conn.close()

        return redirect('/login')

    return render_template('register.html')

# ---------- LOGIN ----------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('database.db')
        user = conn.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username, password)
        ).fetchone()
        conn.close()

        if user:
            session['user_id'] = user[0]
            session['username'] = username
            return redirect('/')
        else:
            return "Invalid login"

    return render_template('login.html')

# ---------- DELETE ----------
@app.route('/delete/<int:id>')
def delete(id):
    conn = sqlite3.connect('database.db')
    conn.execute("DELETE FROM tasks WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect('/')

# ---------- COMPLETE ----------
@app.route('/complete/<int:id>')
def complete(id):
    conn = sqlite3.connect('database.db')
    conn.execute(
        "UPDATE tasks SET status='Completed' WHERE id=?",
        (id,)
    )
    conn.commit()
    conn.close()
    return redirect('/')

# ---------- LOGOUT ----------
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

# ---------- RUN ----------
if __name__ == '__main__':
    app.run(debug=True)