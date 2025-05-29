from flask import Flask, render_template, request, redirect, url_for, flash, session
import pyodbc
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Change this to a random secret key

# SQL Server connection configuration
server = 'RRHHT2'  # Change if your server is different
database = 'facial'  # Change to your database name
username = 'pepe'  # Change to your SQL Server username
password = '123'  # Change to your SQL Server password
driver= '{ODBC Driver 17 for SQL Server}'

conn_str = f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}'

def get_db_connection():
    conn = pyodbc.connect(conn_str)
    return conn

@app.route('/')
def home():
    if 'user_id' in session:
        return render_template('home.html')
    return redirect(url_for('login'))

@app.route('/scores', methods=['GET', 'POST'])
def scores():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    categories = ['Medicina Veterinaria', 'Psicología']
    scores = {}
    user_id = session['user_id']
    if request.method == 'POST':
        conn = get_db_connection()
        cursor = conn.cursor()
        for category in categories:
            score = request.form.get(category)
            scores[category] = score
            # Check if score exists for user and category
            cursor.execute("SELECT id FROM scores WHERE user_id = ? AND category = ?", (user_id, category))
            existing = cursor.fetchone()
            if existing:
                cursor.execute("UPDATE scores SET score = ? WHERE id = ?", (score, existing.id))
            else:
                cursor.execute("INSERT INTO scores (user_id, category, score) VALUES (?, ?, ?)", (user_id, category, score))
        conn.commit()
        conn.close()
        flash('Puntuaciones guardadas correctamente.', 'success')
    else:
        # Load existing scores
        conn = get_db_connection()
        cursor = conn.cursor()
        for category in categories:
            cursor.execute("SELECT score FROM scores WHERE user_id = ? AND category = ?", (user_id, category))
            row = cursor.fetchone()
            if row:
                scores[category] = row.score
        conn.close()
    return render_template('scores.html', categories=categories, scores=scores)

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    conn = get_db_connection()
    cursor = conn.cursor()
    # Query average scores by category
    cursor.execute("""
        SELECT category, AVG(CAST(score AS FLOAT)) as avg_score
        FROM scores
        GROUP BY category
    """)
    results = cursor.fetchall()
    conn.close()
    categories = [row.category for row in results]
    avg_scores = [row.avg_score for row in results]
    return render_template('dashboard.html', categories=categories, avg_scores=avg_scores)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password_input = request.form['password']
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, email, password FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()
        conn.close()
        if user and check_password_hash(user.password, password_input):
            session['user_id'] = user.id
            session['user_name'] = user.name
            return redirect(url_for('home'))
        else:
            flash('Correo o contraseña incorrectos', 'error')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password_input = request.form['password']
        hashed_password = generate_password_hash(password_input)
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
        existing_user = cursor.fetchone()
        if existing_user:
            flash('El correo ya está registrado', 'error')
            conn.close()
            return render_template('register.html')
        cursor.execute("INSERT INTO users (name, email, password) VALUES (?, ?, ?)", (name, email, hashed_password))
        conn.commit()
        conn.close()
        flash('Cuenta creada exitosamente. Por favor, inicia sesión.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        # For simplicity, just flash a message. Implement email sending if needed.
        flash('Si el correo existe, se enviaron instrucciones para restablecer la contraseña.', 'info')
        return redirect(url_for('login'))
    return render_template('forgot_password.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
