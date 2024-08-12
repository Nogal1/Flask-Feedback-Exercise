from flask import Flask
from models import db, User

app = Flask(__name__)

# Configurations (you'll need to update with your actual database URI)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///your-database-name'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database
db.init_app(app)

# Create the tables (run this once, or use migrations)
with app.app_context():
    db.create_all()
