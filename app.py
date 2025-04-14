from flask import Flask, render_template, request, redirect, url_for
from dotenv import load_dotenv

import os
import cloudinary
import cloudinary.uploader
import mysql.connector
from datetime import datetime

load_dotenv()

app = Flask(__name__)

# MySQL connection settings
def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )

# Cloudinary configuration
cloudinary.config(
    cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
    api_key=os.getenv('CLOUDINARY_API_KEY'),
    api_secret=os.getenv('CLOUDINARY_API_SECRET')
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
            # Upload image to Cloudinary
            upload_result = cloudinary.uploader.upload(file)
            image_url = upload_result['secure_url']  # Get the image URL

            # Save URL to MySQL database
            conn = get_db_connection()
            c = conn.cursor()
            c.execute("INSERT INTO images (filename, upload_time) VALUES (%s, %s)",
                      (image_url, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            conn.commit()
            conn.close()
            return redirect(url_for('index'))

    # Fetch image URLs from DB
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT filename FROM images ORDER BY id DESC")
    images = c.fetchall()
    conn.close()
    return render_template('index.html', images=images)

if __name__ == '__main__':
    app.run(debug=True)
