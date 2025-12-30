from flask import Flask, render_template, request, redirect, url_for, flash
from pymongo import MongoClient

app = Flask(__name__)


app.secret_key = 'your-super-secret-key-here' 


client = MongoClient('mongodb://localhost:27017/')
db = client['portfolio']

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


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.run(debug=True, port=3000)