from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
from pymongo import MongoClient
from pymongo.errors import PyMongoError
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your-super-secret-key-here')

# MongoDB Connection
# MongoClient connects lazily, so creating it here costs nothing. The first
# real query (on /projects or /contact) opens the connection. The home page
# never touches the database, so it no longer waits on Atlas at cold start.
MONGODB_URI = os.getenv('MONGODB_URI')
_client = None


def get_db():
    """Return the database handle, or None if MONGODB_URI is not configured."""
    global _client
    if not MONGODB_URI:
        print("❌ MONGODB_URI environment variable is missing")
        return None
    if _client is None:
        _client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
    return _client['portfolio_db']


# Local development only: on Vercel, files in public/ are served by the CDN
# before a request ever reaches Flask. Locally, serve them from the same folder
# so /images/... and /css/... resolve the same way.
if not os.getenv('VERCEL'):
    @app.route('/<path:filename>')
    def local_public(filename):
        return send_from_directory(os.path.join(app.root_path, 'public'), filename)


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/projects')
def projects():
    db = get_db()
    if db is None:
        return "Database connection failed. Please check the MONGODB_URI environment variable.", 500
    try:
        projects_list = list(db.projects.find())
    except PyMongoError as e:
        print(f"❌ MongoDB query failed: {e}")
        return "Database connection failed. Please check the MONGODB_URI environment variable.", 500
    return render_template('projects.html', projects=projects_list)


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        db = get_db()
        if db is None:
            flash('Database is currently unavailable. Please try again later.', 'danger')
            return redirect(url_for('contact'))
        contact_data = {
            'name': request.form['name'],
            'email': request.form['email'],
            'message': request.form['message']
        }
        try:
            db.contacts.insert_one(contact_data)
        except PyMongoError as e:
            print(f"❌ MongoDB insert failed: {e}")
            flash('Database is currently unavailable. Please try again later.', 'danger')
            return redirect(url_for('contact'))
        flash('Thank you! Your message has been sent successfully.', 'success')
        return redirect(url_for('contact'))
    return render_template('contact.html')


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run(debug=True)