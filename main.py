from flask import Flask, render_template, redirect, url_for, request, flash, send_file, session
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user, login_required
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_bootstrap import Bootstrap
from forms import RegistrationForm, LoginForm
from dotenv import load_dotenv
import os
import json


load_dotenv()


app = Flask(__name__)

SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///todo.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
Bootstrap(app)

login = LoginManager(app)

@login.user_loader
def load_user(user_id):
    return User.query.get(user_id)

db = SQLAlchemy(app)

class Todo(db.Model):
    __tablename__ = "todos"
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(200))
    done = db.Column(db.Boolean)


    def __repr__(self):
        return self.text

class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))

    def __repr__(self):
        return '<Register %r>' % self.name


db.create_all()



@app.route("/")
def cover():

    return render_template("layout.html")

@app.route("/home")
def home():
    undone = Todo.query.filter_by(done=False).all()
    done = Todo.query.filter_by(done=True).all()

    return render_template("index.html", undone=undone, done=done)



@app.route('/add', methods=['POST'])
@login_required
def add():
    todo = Todo(text=request.form['todoitem'], done=False)
    db.session.add(todo)
    db.session.commit()

    return redirect(url_for('home'))


@app.route('/done/<id>')
def done(id):
    todo = Todo.query.filter_by(id=int(id)).first()
    todo.done = True
    db.session.commit()

    return redirect(url_for('home'))


@app.route("/update/<int:id>")
def update(id):
    todo = Todo.query.filter_by(id=id).first()
    todo.done = not todo.done
    db.session.commit()
    return redirect(url_for("home"))

@app.route("/delete/<int:id>")
def delete(id):
    todo = Todo.query.filter_by(id=id).first()
    db.session.delete(todo)
    db.session.commit()
    return redirect(url_for("home"))


@app.route('/register', methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():

        if User.query.filter_by(email=form.email.data).first():
            print(User.query.filter_by(email=form.email.data).first())
            #User already exists
            flash("You've already signed up with that email, log in instead!")
            return redirect(url_for('login'))

        hash_and_salted_password = generate_password_hash(
            form.password.data,
            method='pbkdf2:sha256',
            salt_length=8
        )
        new_user = User(
            email=form.email.data,
            name=form.name.data,
            password=hash_and_salted_password,
        )
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for("home"))

    return render_template("register.html", form=form, current_user=current_user)



@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        user = User.query.filter_by(email=email).first()
        # Email doesn't exist or password incorrect.
        if not user:
            flash("That email does not exist, please try again.")
            return redirect(url_for('login'))
        elif not check_password_hash(user.password, password):
            flash('Password incorrect, please try again.')
            return redirect(url_for('login'))
        else:
            login_user(user)
            return redirect(url_for('home'))
    return render_template("login.html", form=form, current_user=current_user)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('cover'))



if __name__ =="__main__":
    app.run(debug=True)