"""Blogly application."""

from flask import Flask, request, redirect, render_template, session, flash
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User, Post, Tag

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///blogly'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SECRET_KEY']= 'passwordnot'

toolbar = DebugToolbarExtension(app)

connect_db(app)

db.create_all()

@app.route('/')
def root():
    """Show recent list of posts in order of most recent to least"""

    posts = Post.query.order_by(Post.created_at.desc()).limit(10).all()
    return render_template("posts/home.html", posts=posts)
   

@app.errorhandler(404)
def page_not_found(e):
    """Show 404 NOT FOUND page."""

    return render_template('404.html'), 404



@app.route('/users')
def user_list():
    """ Display full list of users""" 
    users = User.query.order_by(User.last_name, User.first_name).all()
    return render_template('users/index.html', users=users)

@app.route('/users/new', methods=["GET"])
def new_user_form():
    """ Show form to create a new user"""

    return render_template('users/new.html')

@app.route('/users/new', methods=["POST"])
def create_new_user():
    """ Create a new user throught the user creator form"""

    first_name = request.form['first_name']
    last_name = request.form['last_name']
    image_url = request.form['image_url']

    image_url = image_url if image_url else None

    new_user = User(first_name=first_name, last_name=last_name, image_url=image_url)

    db.session.add(new_user)
    db.session.commit()

    return redirect('/users')

@app.route('/users/<int:user_id>')
def show_user(user_id):
    """ SHow info about specific user"""

    user = User.query.get_or_404(user_id)
    
    return render_template('users/detail.html', user=user)

@app.route('/users/<int:user_id>/edit', methods=["GET"])
def edit_user(user_id):
    """ Show a user edit form to edit user information"""

    user = User.query.get_or_404(user_id)
    return render_template('users/edit.html', user=user)

@app.route('/users/<int:user_id>/edit', methods=["POST"])
def update_user(user_id):
    """ Handle editing form and update user info"""

    user = User.query.get_or_404(user_id)

    user.first_name = request.form['first_name']
    user.last_name = request.form['last_name']
    user.image_url = request.form['image_url']


    db.session.add(user)
    db.session.commit()

    return redirect("/users")

@app.route('/users/<int:user_id>/delete', methods=["POST"])
def delete_user(user_id):
    """ Handle a submission to delete a specific user"""

    user = User.query.get_or_404(user_id)

    db.session.delete(user)
    db.session.commit()

    return redirect("/users")


@app.route('/users/<int:user_id>/posts/new')
def new_post_form(user_id):
    """Show a form to create a new post"""
    user = User.query.get_or_404(user_id) 
    tags = Tag.query.all()

    return render_template('posts/new.html', user=user, tags=tags)

@app.route('/users/<int:user_id>/posts/new', methods=["POST"])
def new_post(user_id):
    """Create a new post from submitted form data"""
    user = User.query.get_or_404(user_id)

    tag_ids = [int(num) for num in request.form.getlist("tags")]
    tags = Tag.query.filter(Tag.id.in_(tag_ids)).all()

    new_post = Post(title=request.form['title'], content=request.form['content'], user=user, tags=tags)

    db.session.add(new_post)
    db.session.commit()

    return redirect(f"/users/{user_id}")

@app.route('/posts/<int:post_id>')
def show_post(post_id):
    """Show info page for a user's post"""

    post = Post.query.get_or_404(post_id)
    return render_template('posts/blog.html', post=post)

@app.route('/posts/<int:post_id>/edit')
def edit_post(post_id):
    """Show a form to edit an user's post"""

    post = Post.query.get_or_404(post_id)
    tags = Tag.query.all()
    return render_template('posts/edit.html', post=post, tags=tags)

@app.route('/posts/<int:post_id>/edit', methods=["POST"])
def update_post(post_id):
    """Update edits made to post"""
    post = Post.query.get_or_404(post_id)
    post.title = request.form['title']
    post.content = request.form['content']
    tag_ids = [int(num) for num in request.form.getlist("tags")]
    post.tags = Tag.query.filter(Tag.id.in_(tag_ids)).all()

    db.session.add(post)
    db.session.commit()
    return redirect(f"/users/{post.user_id}")

@app.route('/posts/<int:post_id>/delete', methods=["POST"])
def delete_post(post_id):
    """Method to handle the deletion of a post"""

    post = Post.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    return redirect(f"/users/{post.user_id}")



@app.route('/tags')
def show_tags():
    """Display page with tags"""

    tags = Tag.query.all()
    return render_template('tags/index.html', tags=tags)


@app.route('/tags/new')
def new_tag_form():
    """Display form for a new tag"""

    posts = Post.query.all()
    return render_template('tags/new.html', posts=posts)


@app.route("/tags/new", methods=["POST"])
def new_tag():
    """Handle submission for a new tag"""

    post_ids = [int(num) for num in request.form.getlist("posts")]
    posts = Post.query.filter(Post.id.in_(post_ids)).all()
    new_tag = Tag(name=request.form['name'], posts=posts)

    db.session.add(new_tag)
    db.session.commit()

    return redirect("/tags")


@app.route('/tags/<int:tag_id>')
def show_tag(tag_id):
    """Direct to a specific tag's page"""

    tag = Tag.query.get_or_404(tag_id)
    return render_template('tags/tags.html', tag=tag)


@app.route('/tags/<int:tag_id>/edit')
def edit_a_tag_form(tag_id):
    """Display the form used to edit a specific tag"""

    tag = Tag.query.get_or_404(tag_id)
    posts = Post.query.all()
    return render_template('tags/edit.html', tag=tag, posts=posts)


@app.route('/tags/<int:tag_id>/edit', methods=["POST"])
def edit_tag(tag_id):
    """handle request to update tag"""

    tag = Tag.query.get_or_404(tag_id)
    tag.name = request.form['name']
    post_ids = [int(num) for num in request.form.getlist("posts")]
    tag.posts = Post.query.filter(Post.id.in_(post_ids)).all()

    db.session.add(tag)
    db.session.commit()

    return redirect("/tags")


@app.route('/tags/<int:tag_id>/delete', methods=["POST"])
def delete_tag(tag_id):
    """Delete a tag"""

    tag = Tag.query.get_or_404(tag_id)
    db.session.delete(tag)
    db.session.commit()

    return redirect("/tags")