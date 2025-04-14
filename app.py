from flask import Flask, render_template, request, redirect, url_for
from dotenv import load_dotenv
import os
import cloudinary
import cloudinary.uploader
import mysql.connector
from datetime import datetime

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Cloudinary configuration
cloudinary.config(
    cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
    api_key=os.getenv('CLOUDINARY_API_KEY'),
    api_secret=os.getenv('CLOUDINARY_API_SECRET')
)

# MySQL connection
def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )

# Initialize the images table (if not exists)
def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS images (
            id INT AUTO_INCREMENT PRIMARY KEY,
            filename VARCHAR(500),
            upload_time DATETIME
        )
    ''')
    conn.commit()
    conn.close()

init_db()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files.get('image')
        if file:
            try:
                # Upload to Cloudinary
                upload_result = cloudinary.uploader.upload(file)
                image_url = upload_result['secure_url']

                # Save image URL & time in DB
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO images (filename, upload_time) VALUES (%s, %s)",
                    (image_url, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                )
                conn.commit()
                conn.close()
                return redirect(url_for('index'))
            except Exception as e:
                print("Upload failed:", e)

    # Retrieve all image URLs
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT filename FROM images ORDER BY id DESC")
    images = cursor.fetchall()
    conn.close()
    
    return render_template('index.html', images=images)

if __name__ == '__main__':
    app.run(debug=True)
