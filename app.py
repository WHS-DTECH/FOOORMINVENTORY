from flask import Flask, render_template
import psycopg2
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('welcome.html')

# Example DB connection (replace with your own logic)
def get_db_connection():
    conn = psycopg2.connect(os.getenv('DATABASE_URL'))
    return conn

if __name__ == '__main__':
    app.run(debug=True)
