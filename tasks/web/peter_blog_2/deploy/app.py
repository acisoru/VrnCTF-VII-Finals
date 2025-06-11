from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import os
from werkzeug.security import generate_password_hash

app = Flask(__name__)
app.secret_key = 'super_secret_key_123'  # For session management

# Database setup
DATABASE = 'vulnerable_blog.db'

def init_db():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        # Create users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE,
                password TEXT,
                is_admin BOOLEAN DEFAULT 0
            )
        ''')
        
        # Create posts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                content TEXT,
                author TEXT
            )
        ''')
        
        # Check if admin exists
        cursor.execute("SELECT * FROM users WHERE username = 'admin'")
        if not cursor.fetchone():
            # MD5 hash of 'admin123'
            cursor.execute(
                "INSERT INTO users (username, password, is_admin) VALUES (?, ?, 1)",
                ('admin', 'c0ce5f5206cfd9e8a7410adf40b8e888')
            )
        conn.commit()

@app.route('/')
def index():
    with sqlite3.connect(DATABASE) as conn:
        conn.row_factory = sqlite3.Row  # Return rows as dictionaries
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM posts")
        all_posts = cursor.fetchall()
    return render_template('index.html', posts=all_posts, user=session.get('user'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Vulnerable SQL query - direct string concatenation
        query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
        
        with sqlite3.connect(DATABASE) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Execute the vulnerable query
            cursor.execute(query)
            user = cursor.fetchone()
            
            if user:
                session['user'] = {
                    'username': user['username'],
                    'is_admin': bool(user['is_admin'])
                }
                return redirect(url_for('index'))
            else:
                flash('Invalid credentials')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()
            
            # Check if user exists (also vulnerable to SQLi)
            cursor.execute(f"SELECT * FROM users WHERE username = '{username}'")
            if not cursor.fetchone():
                # Vulnerable insert statement
                cursor.execute(
                    f"INSERT INTO users (username, password, is_admin) VALUES ('{username}', '{password}', 0)"
                )
                conn.commit()
                return redirect(url_for('login'))
            else:
                flash('User already exists')
    
    return render_template('register.html')

@app.route('/create_post', methods=['POST'])
def create_post():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    title = request.form.get('title')
    content = request.form.get('content')
    author = session['user']['username']
    
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        # Vulnerable insert statement
        cursor.execute(
            f"INSERT INTO posts (title, content, author) VALUES ('{title}', '{content}', '{author}')"
        )
        conn.commit()
    
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)