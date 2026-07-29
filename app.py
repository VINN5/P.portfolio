from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your-super-secret-key-here')

# MongoDB Connection
MONGODB_URI = os.getenv('MONGODB_URI')

db = None
try:
    if MONGODB_URI:
        client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
        client.admin.command('ping')   # Test the connection
        db = client['portfolio_db']
        print("✅ MongoDB connected successfully")
    else:
        print("❌ MONGODB_URI environment variable is missing")
except Exception as e:
    print(f"❌ MongoDB connection failed: {e}")
    db = None


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/projects')
def projects():
    if db is None:
        return "Database connection failed. Please check the MONGODB_URI environment variable.", 500
    projects_list = list(db.projects.find())
    return render_template('projects.html', projects=projects_list)


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        if db is None:
            flash('Database is currently unavailable. Please try again later.', 'danger')
            return redirect(url_for('contact'))
        contact_data = {
            'name': request.form['name'],
            'email': request.form['email'],
            'message': request.form['message']
        }
        db.contacts.insert_one(contact_data)
        flash('Thank you! Your message has been sent successfully.', 'success')
        return redirect(url_for('contact'))
    return render_template('contact.html')


@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory('static', filename)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run(debug=True)