from flask import Flask, render_template, request, redirect, url_for
from dotenv import load_dotenv
load_dotenv()
import os
import mysql.connector
from datetime import datetime

app = Flask(__name__)
UPLOAD_FOLDER = 'static/uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# MySQL connection settings
def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )

# Initialize DB table
def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS images (
            id INT AUTO_INCREMENT PRIMARY KEY,
            filename VARCHAR(255),
            upload_time DATETIME
        )
    ''')
    conn.commit()
    conn.close()

init_db()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files['image']
        if file:
            filename = file.filename
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            conn = get_db_connection()
            c = conn.cursor()
            c.execute("INSERT INTO images (filename, upload_time) VALUES (%s, %s)",
                      (filename, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            conn.commit()
            conn.close()
            return redirect(url_for('index'))

    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT filename FROM images ORDER BY id DESC")
    images = c.fetchall()
    conn.close()
    return render_template('index.html', images=images)

if __name__ == '__main__':
    app.run(debug=True)
