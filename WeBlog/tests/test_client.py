import re
import unittest
from app import create_app, db
from app.models import User, Role, Post

class WeBlogClientTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        Role.insert_roles()
        self.client = self.app.test_client(use_cookies=True)

        # add a user
        user = User(email='shihj@qq.com', username='shihj', password='123', confirmed=True)
        db.session.add(user)
        db.session.commit()      

        # add a post
        post = Post(body='Test post', author=User.query.first())
        db.session.add(post)
        db.session.commit()      

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_home_page(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(b'Stranger' in response.data)

    def test_register_and_login(self):
        # register a new account
        response = self.client.post('/auth/register', data={
            'email': 'john@example.com',
            'username': 'john',
            'password': 'cat',
            'password2': 'cat'
        })
        self.assertEqual(response.status_code, 302)

        # login with the new account
        response = self.client.post('/auth/login', data={
            'email': 'john@example.com',
            'password': 'cat'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(re.search(b'Hello,\s+john!', response.data))
        self.assertTrue(
            b'You have not confirmed your account yet' in response.data)

        # send a confirmation token
        user = User.query.filter_by(email='john@example.com').first()
        token = user.generate_confirmation_token()
        response = self.client.get('/auth/confirm/{}'.format(token),
                                   follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        #data = response.get_data(as_text=True)
        #print(data)
        self.assertTrue(
            b'You have confirmed your account' in response.data)

        # log out
        response = self.client.get('/auth/logout', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(b'You have been logged out' in response.data)

    def test_edit_profile(self):
        # login
        response = self.client.post('/auth/login', data={
            'email': 'shihj@qq.com',
            'password': '123'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(re.search(b'Hello,\s+shihj!', response.data))

        response = self.client.post('/edit-profile', data={
            'name': 'shihj',
            'location': 'nanjing',
            'about_me': "I'm shihj"
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(b'Your profile has been updated.' in response.data)

        # log out
        response = self.client.get('/auth/logout', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(b'You have been logged out' in response.data)

    def test_post(self):
        # login
        response = self.client.post('/auth/login', data={
            'email': 'shihj@qq.com',
            'password': '123'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(re.search(b'Hello,\s+shihj!', response.data))

        response = self.client.post('/', data={
            'body': 'This is a test from test_client.',
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        #print(response.get_data(as_text=True))
        self.assertTrue(b'This is a test from test_client.' in response.data)

        # log out
        response = self.client.get('/auth/logout', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(b'You have been logged out' in response.data)
    
    def test_comment(self):
        # login
        response = self.client.post('/auth/login', data={
            'email': 'shihj@qq.com',
            'password': '123'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(re.search(b'Hello,\s+shihj!', response.data))

        post = Post.query.first()
        self.assertTrue(post is not None)

        response = self.client.post('/post/%d' % post.id, data={
            'body': 'This is a test comment from test_client.',
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(b'Your comment has been published.' in response.data)

        # log out
        response = self.client.get('/auth/logout', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(b'You have been logged out' in response.data)
    