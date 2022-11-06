from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_login import login_user, LoginManager, UserMixin, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os 


base_dir = os.path.dirname(os.path.realpath(__file__))


app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"]= 'sqlite:///' + os.path.join(base_dir, 'my_login.db')
app.config['SQLALCHEMY_TRACK_MODIFICTIONS'] = False
app.config['SECRET_KEY'] = '421037f406989c4e4d59b162097448624b207c38'


db = SQLAlchemy(app)
login_manager = LoginManager(app)


#create Model
class User(db.Model, UserMixin):
    id = db.Column(db.Integer(), primary_key=True) #it is added automatically
    full_name = db.Column(db.String(255), nullable=False) #this means this must be filled, it can't be blank
    username = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True)
    password_hash =db.Column(db.Text(), nullable=False)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    blogpost = db.relationship('Blogpost', backref='user')


    def __repr__(self):
        return f"User <{self.full_name}>"

class Blogpost(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    author = db.Column(db.String(255), nullable=False, unique=True)
    title = db.Column(db.String(255), nullable=False, unique=True)
    content = db.Column(db.Text(), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


    def __repr__(self):
        return f"Blogpost <{self.author}>"


class Contact(db.Model):
    id = db.Column(db.Integer() ,primary_key=True)
    email = db.Column(db.String(255), nullable=False, unique=True)
    name = db.Column(db.String(255), nullable=False)
    message = db.Column(db.Text(), nullable=False)


    def __repr__(self):
        return f"Contact <{self.name}>"


@login_manager.user_loader
def user_loader(id):
    return User.query.get(id)

@app.route('/')
def index():
    user = User.query.filter_by()
    return render_template('index.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/contact')
@login_required
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')

        user_contact = Contact(name=name, email=email, message=message)
        db.session.add(user_contact)

        return redirect(url_for('index'))
    
    return render_template('contact.html')


@app.route('/login', methods=['GET','POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')

    user = User.query.filter_by(username=username).first()

    if user and check_password_hash(user.password_hash, password):
        login_user(user)
        return redirect(url_for('index'))

    return render_template('login.html')





@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/addpost', methods=['GET', 'POST'])
@login_required
def addpost():
    if request.method == 'POST':
        title = request.form.get('title')
        author = request.form.get('author')
        content = request.form.get('content')

    post = Blogpost(title=title, author=author, content=content,)


@app.route('/signup' , methods=['GET', 'POST'])
def register():
    
    if request.method == 'POST':
        full_name = request.form.get('full_name')
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm = request.form.get('confirm')

        
        user = User.query.filter_by(username=username).first()
        if user:
            return redirect(url_for('register'))
 
        email_exists = User.query.filter_by(email=email).first()
        if email_exists:
            return redirect(url_for('register'))

        
        password_hash = generate_password_hash(password)
        
        new_user = User(full_name=full_name, username=username,  email=email, password_hash=password_hash)
        db.session.add(new_user)
        db.session.commit()


        return redirect(url_for('login'))

    return render_template('signup.html')


if __name__ == "__main__":
    app.run(debug=True)