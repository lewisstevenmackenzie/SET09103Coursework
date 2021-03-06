from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin

app = Flask(__name__)
app.config['SECRET_KEY'] = '8656d430a91e21e849364b1dadde70eb'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config["GPX_UPLOADS"] = "/home/40445231/SET09103Coursework/fit4all/static/gps_files"
app.config["IMAGE_UPLOADS"] = "/home/40445231/SET09103Coursework/fit4all/static/profile_images"
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'


from fit4all import routes