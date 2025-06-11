from flask import Flask, render_template, request, session, redirect, url_for, flash
import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['DATABASE'] = 'notes.db'
app.config['STATIC_URL_PATH'] = '/static'

# Упрощенное подключение к БД
def get_db():
    db = sqlite3.connect(app.config['DATABASE'])
    db.row_factory = sqlite3.Row
    return db

# Инициализация БД
def init_db():
    with get_db() as db:
        db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE,
                password TEXT
            )
        ''')
        db.execute('''
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                title TEXT,
                content TEXT,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        ''')
        db.commit()

# Маршруты
@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        db = get_db()
        user = db.execute(
            'SELECT * FROM users WHERE username = ?', 
            (username,)
        ).fetchone()
        
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            return redirect(url_for('index'))
        
        flash('Invalid credentials', 'danger')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])
        
        try:
            db = get_db()
            db.execute(
                'INSERT INTO users (username, password) VALUES (?, ?)',
                (username, password)
            )
            db.commit()
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Username already exists', 'danger')
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# Уязвимые эндпоинты
@app.route('/notes')
def view_notes():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    db = get_db()
    # Уязвимость: показывает все заметки, а не только пользователя
    notes = db.execute('SELECT id, title FROM notes WHERE user_id = ?', (session["user_id"],)).fetchall()
    return render_template('notes.html', notes=notes)

@app.route('/note/<int:note_id>')
def view_note(note_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    db = get_db()
    # Уязвимость IDOR: нет проверки владельца
    note = db.execute(
        'SELECT title, content FROM notes WHERE id = ?',
        (note_id,)
    ).fetchone()
    
    if note:
        return render_template('note.html', note=note)
    
    flash('Note not found', 'danger')
    return redirect(url_for('view_notes'))

@app.route('/add', methods=['GET', 'POST'])
def add_note():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        
        db = get_db()
        db.execute(
            'INSERT INTO notes (user_id, title, content) VALUES (?, ?, ?)',
            (session['user_id'], title, content)
        )
        db.commit()
        flash('Note added successfully!', 'success')
        return redirect(url_for('view_notes'))
    
    return render_template('add_note.html')

if __name__ == '__main__':
    init_db()
    # Создаем админа и флаг, если их нет
    with get_db() as db:
        if not db.execute("SELECT id FROM users WHERE username='admin'").fetchone():
            db.execute(
                "INSERT INTO users (username, password) VALUES (?, ?)",
                ('admin', generate_password_hash('secureadmin123'))
            )
            db.commit()
            admin_id = db.execute(
                "SELECT id FROM users WHERE username='admin'"
            ).fetchone()['id']
            db.execute(
                "INSERT INTO notes (user_id, title, content) VALUES (?, ?, ?)",
                (admin_id, 'Secret Flag', 'vrnctf{1d0r_15_v3ry_51mpl3}')
            )
            db.commit()
    app.run(debug=True, host="0.0.0.0")