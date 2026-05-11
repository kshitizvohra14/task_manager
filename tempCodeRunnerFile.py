from flask import Flask, render_template
from config import Config
from models import db
from extensions import socketio

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
socketio.init_app(app)

from routes.tasks import task_bp
from routes.auth import auth_bp
from routes.analytics import analytics_bp

app.register_blueprint(task_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(analytics_bp)

@app.route('/')
def home():
    return render_template('login.html')
@app.route('/register')
def register():
    return render_template('register.html')
@app.route('/dashboard')
def dashboard():
    return render_template('index.html')
if __name__ == '__main__':
    with app.app_context():
        db.create_all()

    socketio.run(app, debug=True)