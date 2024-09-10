from flask import Flask, request, redirect, render_template
import sqlite3
import hashlib

app = Flask(__name__)

# Connect to SQLite Database
def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS urls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            original_url TEXT NOT NULL,
            short_url TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Generate a short URL
def generate_short_url(original_url):
    return hashlib.md5(original_url.encode()).hexdigest()[:6]  # Shorten to 6 characters

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        original_url = request.form['url']
        short_url = generate_short_url(original_url)
        
        # Save to the database
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("INSERT INTO urls (original_url, short_url) VALUES (?, ?)", (original_url, short_url))
        conn.commit()
        conn.close()

        return render_template('result.html', short_url=short_url)

    return render_template('index.html')

@app.route('/<short_url>')
def redirect_url(short_url):
    # Fetch the original URL from the database
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT original_url FROM urls WHERE short_url=?", (short_url,))
    original_url = c.fetchone()
    conn.close()

    if original_url:
        return redirect(original_url[0])
    else:
        return 'URL not found', 404

if __name__ == '__main__':
    init_db()  # Initialize the database
    app.run(debug=True)
