from unittest import TestCase
from app import app
from models import db, User, DEFAULT_IMAGE, Post

app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///blogly_test"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config["DEBUG_TB_HOSTS"] = ["dont-show-debug-toolbar"]

db.drop_all()
db.create_all()


class UsersTestCase(TestCase):

    def setUp(self):
        """setup sample data"""

        # clear data from previous sessions
        
        # user creation test
        user = User(first_name="John", last_name="Doe")
        db.session.add(user)
        db.session.commit()
            

        post = Post(title="First Blog!", content="YoYo", user_id=user.id)
        db.session.add(post)
        db.session.commit()

        id_str = str(user.id)
        
        self.user = user
        self.id_str = id_str
        self.post = post
        

    def tearDown(self):
        """ teardown session from any bad commits or adds"""

        db.session.rollback()

        User.query.delete()
        Post.query.delete()

    def test_users_list(self):
        """ check home page renders and list is displayed upon user redirect on loading into server"""

        with app.test_client() as client:
            resp = client.get("/users")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn(self.id_str, html)
    
    def test_add_users_redirect(self):
        """ check if add user redirects after using user form"""

        with app.test_client() as client:
            data = {"first_name": "John", "last_name": "Doe", "image_url":""}
            resp = client.post("/users/new", data=data)

            self.assertEqual(resp.status_code, 302)

    def test_add_user(self):
        """ checks if new user has been added"""

        with app.test_client() as client:
            resp = client.post("/users/new", data=data, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('John Doe', html)


    def test_delete_user(self):
        """checks if user will get deleted"""

        with app.test_client() as client:
            resp = client.post(f"/users/{self.user.id}/delete", follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertNotIn(self.user.first_name, html)
            self.assertNotIn(self.user.last_name, html)

    def test_user_detail_page(self):
        """checks if user details page is shown and checks for user details displayed"""

        with app.test_client() as client:
            resp = client.get(f"/users/{self.user.id}")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn(self.user.image_url, html)
            self.assertIn(f"<h1>{ self.user.first_name } { self.user.last_name }</h1>", html)
    

    def test_home_html(self):
        """checks if home page is properly displayed"""

        with app.test_client() as client:
            resp = client.get("/")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("<h1>Blogly Recent Posts</h1>", html)

    def test_blog_post_page(self):
        """checks if correct blog post page is properly displayed"""

        with app.test_client() as client:
            resp = client.get(f"/posts/{self.post.id}")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn(self.post.user.first_name, html)
            self.assertIn(self.post.user.last_name, html)

    def test_blog_post(self):
        """test for submission handling of a new blog entry and the posting onto user page"""

        with app.test_client() as client:
            data = {"title": "First Blog!", "content": "YoYo", "user_id":f"{self.user.id}"}
            resp = client.post("/users/<int:user_id>/posts/new", data=data, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn(f"<small>{ self.post.created_at }</small>", html)