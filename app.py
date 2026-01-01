from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
from pymongo import MongoClient
import os

app = Flask(__name__)


app.secret_key = os.getenv('SECRET_KEY', 'your-super-secret-key-here')


MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
client = MongoClient(MONGODB_URI)
db = client['portfolio_db']  

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/projects')
def projects():
    projects_list = list(db.projects.find())
    return render_template('projects.html', projects=projects_list)

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
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
    app.run()