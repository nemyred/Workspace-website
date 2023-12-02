from datetime import date
from flask import Flask, abort, render_template, redirect, url_for, flash
from flask_bootstrap import Bootstrap5
from flask_ckeditor import CKEditor
from flask_gravatar import Gravatar
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import relationship
from forms import RegisterForm, LoginForm, CommentForm, CreateCafeForm
import os
# prints random digits
# import uuid
# m = uuid.uuid4().hex

'''
Red underlines? Install the required packages first: 
Open the Terminal in PyCharm (bottom left). 

On Windows type:
python -m pip install -r requirements.txt

On MacOS type:
pip3 install -r requirements.txt

This will install the packages from requirements.txt for this project.
'''
# current_year = datetime.datetime.now().year

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('FLASK_KEY')
ckeditor = CKEditor(app)
Bootstrap5(app)

#Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DB_URI", 'sqlite:///cafes.db')
db = SQLAlchemy()
db.init_app(app)


#Cafe TABLE Configuration
class Cafe(db.Model):
    __tablename__ = "cafes"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    # Create Foreign Key, "users.id" the users refers to the tablename of User.
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    # Child Relationship to the User
    # Create reference to the User object. The "posts" refers to the posts property in the User class.
    author = relationship("User", back_populates="posts")
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    open_time = db.Column(db.String(250), nullable=False)
    close_time = db.Column(db.String(250), nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)
    date = db.Column(db.String(250), nullable=False)
    # Parent relationship to the comments
    comments = relationship("Comment", back_populates="parent_post")


# Create a User table for all your registered users
class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(100))
    # Parent relationship to the Cafe
    # The "author" refers to the author property in the Cafe class.
    posts = relationship("Cafe", back_populates="author")
    # Parent relationship: "comment_author" refers to the comment_author property in the Comment class.
    comments = relationship("Comment", back_populates="comment_author")

# Create a table for the comments on the blog posts
class Comment(db.Model):
    __tablename__ = "comments"
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    # Child relationship:"users.id" The users refers to the tablename of the User class.
    # "comments" refers to the comments property in the User class.
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    comment_author = relationship("User", back_populates="comments")
    # Child Relationship to the Cafe
    cafe_id = db.Column(db.Integer, db.ForeignKey("cafes.id"))
    parent_post = relationship("Cafe", back_populates="comments")


with app.app_context():
    db.create_all()

# Configure Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)


# For adding profile images to the comment section
gravatar = Gravatar(app,
                    size=100,
                    rating='g',
                    default='retro',
                    force_default=False,
                    force_lower=False,
                    use_ssl=False,
                    base_url=None)


@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User, user_id)



# Create an admin-only decorator
def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # If id is not 1 then return abort with 403 error
        if current_user.id != 1:
            flash("Opps! You do not have admin privilege")
            return abort(403)
        # Otherwise continue with the route function
        return f(*args, **kwargs)

    return decorated_function


# Create an login required decorator
def login_required(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        # Check if the user is logged in
        if not current_user.is_authenticated:
            flash("You have to login to perform such operation")
            return redirect(url_for('login'))
        return func(*args, **kwargs)
    return decorated_function

@app.route("/register", methods=['POST', 'GET'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():

        # Check if user email is already present in the database.
        result = db.session.execute(db.select(User).where(User.email == form.email.data))
        user = result.scalar()
        if user:
            # User already exists
            flash("You've already signed up with that email, log in instead!")
            return redirect(url_for('login'))

        hash_and_salted_password = generate_password_hash(
            form.password.data,
            method='pbkdf2:sha256',
            salt_length=10
        )
        new_user = User(
            email=form.email.data,
            name=form.name.data,
            password=hash_and_salted_password
        )
        db.session.add(new_user)
        db.session.commit()
        # This line will authenticate the user with Flask-Login
        login_user(new_user)
        return redirect(url_for("home"))
    return render_template("register.html", form=form, current_user=current_user)


@app.route("/")
def home():
    return render_template("index.html")



@app.route('/cafes')
def cafes():
    result = db.session.execute(db.select(Cafe).order_by(Cafe.id))
    all_cafes = result.scalars().all()
    return render_template('cafe.html', cafes=all_cafes)


@app.route('/<cafe_id>', methods=['GET', 'POST'])
def choice_cafes(cafe_id):
    result = db.get_or_404(Cafe, cafe_id)
    # Add the CommentForm to the route
    comment_form = CommentForm()
    # Only allow logged-in users to comment on posts
    if comment_form.validate_on_submit():
        if not current_user.is_authenticated:
            flash("You need to login or register to comment.")
            return redirect(url_for("login"))

        new_comment = Comment(
            text=comment_form.comment_text.data,
            comment_author=current_user,
            parent_post=result
        )
        db.session.add(new_comment)
        db.session.commit()
        return render_template('single_cafe.html')
    return render_template('single_cafe.html', cafe=result, current_user=current_user, form=comment_form)


# Use a decorator so only an admin user can create new posts
@app.route("/new", methods=["GET", "POST"])
@login_required
def add():
    form = CreateCafeForm()
    if form.validate_on_submit():
        new_cafe = Cafe(
            name=form.name.data,
            map_url=form.map_url.data,
            img_url=form.img_url.data,
            location=form.location.data,
            seats=form.seats.data,
            open_time=form.open.data,
            close_time=form.close.data,
            has_toilet=form.toilet.data,
            has_wifi=form.wifi.data,
            has_sockets=form.sockets.data,
            can_take_calls=form.calls.data,
            coffee_price=form.coffee_price.data,
            author=current_user,
            date=date.today().strftime("%B %d, %Y")
        )
        db.session.add(new_cafe)
        db.session.commit()
        return redirect(url_for("cafes"))
    return render_template("add.html", form=form, current_user=current_user)


@app.route("/login",  methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        password = form.password.data
        result = db.session.execute(db.select(User).where(User.email == form.email.data))
        # Note, email in db is unique so will only have one result.
        user = result.scalar()
        # Email doesn't exist
        if not user:
            flash("That email does not exist, please try again.")
            return redirect(url_for('login'))
        # Password incorrect
        elif not check_password_hash(user.password, password):
            flash('Password incorrect, please try again.')
            return redirect(url_for('login'))
        else:
            login_user(user)
            return redirect(url_for('cafes'))

    return render_template("login.html", form=form, current_user=current_user)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))





# # Use a decorator so only an admin user can edit a post
# @app.route("/edit/<int:post_id>", methods=["GET", "POST"])
# @admin_only
# def edit_post(post_id):
#     cafe = db.get_or_404(Cafe, post_id)
#     edit_form = CreateCafeForm(
#         title=cafe.title,
#         subtitle=cafe.subtitle,
#         img_url=cafe.img_url,
#         author=cafe.author,
#         body=cafe.body
#     )
#     if edit_form.validate_on_submit():
#         post.title = edit_form.title.data
#         post.subtitle = edit_form.subtitle.data
#         post.img_url = edit_form.img_url.data
#         post.author = current_user
#         post.body = edit_form.body.data
#         db.session.commit()
#         return redirect(url_for("show_post", post_id=post.id))
#     return render_template("make-post.html", form=edit_form, is_edit=True, current_user=current_user)


# Use a decorator so only an admin user can delete a post
@app.route("/delete/<int:cafe_id>")
@admin_only
def delete_post(cafe_id):
    cafe_to_delete = db.get_or_404(Cafe, cafe_id)
    db.session.delete(cafe_to_delete)
    db.session.commit()
    return redirect(url_for('choice_cafes'))

if __name__ == '__main__':
    app.run(debug=True, port=5002)
