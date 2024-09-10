from flask import Flask, request, redirect, render_template, url_for, send_from_directory
import sqlite3
import hashlib
import os

app = Flask(__name__)

# Initialize the SQLite Database
def init_db():
    with sqlite3.connect('database.db') as conn:
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS urls (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                original_url TEXT NOT NULL,
                short_url TEXT NOT NULL
            )
        ''')
        conn.commit()

# Generate a short URL
def generate_short_url(original_url):
    return hashlib.md5(original_url.encode()).hexdigest()[:6]  # Shorten to 6 characters

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        original_url = request.form['url']
        short_url = generate_short_url(original_url)
        
        # Save to the database
        with sqlite3.connect('database.db') as conn:
            c = conn.cursor()
            c.execute("INSERT INTO urls (original_url, short_url) VALUES (?, ?)", (original_url, short_url))
            conn.commit()

        return render_template('result.html', short_url=short_url)

    return render_template('index.html')

@app.route('/<short_url>')
def redirect_url(short_url):
    # Fetch the original URL from the database
    with sqlite3.connect('database.db') as conn:
        c = conn.cursor()
        c.execute("SELECT original_url FROM urls WHERE short_url=?", (short_url,))
        original_url = c.fetchone()

    if original_url:
        return redirect(original_url[0])
    else:
        return render_template('404.html'), 404  # Render a custom 404 page if URL not found

# Handle favicon requests to avoid the 500 error
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico')

if __name__ == '__main__':
    init_db()  # Initialize the database
    app.run(debug=True)
