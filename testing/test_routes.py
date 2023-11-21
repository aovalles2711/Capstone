os.environ["DATABASE_URL"] = "postgresql:///app"

app.config["WTF_CSRF_ENABLED"] = False


class AppTestCase(unittest.TestCase):
    def setUp(self):
        app.config["TESTING"] = True
        self.client = app.test_client()
        with app.app_context():
            db.drop_all()
            db.create_all()

    def tearDown(self):
        db.session.rollback()
        app.config["TESTING"] = False

    def login_user(self):
        with self.client as c:
            with c.session_transaction() as session:
                session[CURR_USER_KEY] = 1  # Replace with user ID
        return c

    def test_signup(self):
        response = self.client.post(
            "/signup",
            data=dict(username="testuser", email="test@test.com", password="password"),
            follow_redirects=True,
        )

        self.assertEqual(response.status_code, 200)

    def test_login(self):
        # Create test user
        user = User.signup("testuser", "test@test.com", "password", None)
        db.session.add(user)
        db.session.commit()

        response = self.client.post(
            "/login",
            data=dict(username="testuser", password="password"),
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Hello, testuser!", response.data)
    
    def test_logout(self)
        user = User.signup('testuser', 'test@test.com', 'password', None)
        db.session.add(user)
        db.session.commit()

        # Log user in
        with self.client as c:
            c.post('/login', data=dict(
                username='testuser',
                password='password'
            ) follow_redirects=True)

            response = c.get('/logout', follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'You have been logged out successfully', response.data)
    
    def test_all(self):
        response = self.client.post('/all', data=dict(
        ), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
    
    def test_homepage(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Hi there!', response.data)
        self.assertIn(b'New to Workout Platform?', response.data)
        self.assertIn(b'Sign up', response.data)
    
    def test_edit_profile(self):
        with self.login_user():
            response = self.client.get('/edit_profile', follow_redirects=True)
            self.assertEqual(response.status_code, 200)
    
    def test_uploaded_file(self):
        response = self.client.get('/uploads/test.jpg')
        self.assertEqual(response.status_code, 200)

    def set_up_valid_user_session(self, user_id):
        with self.client.session_transaction() as session:
            session[CURR_USER_KEY] = user_id
    
    def test_accept_friend_request(self):
        response = self.client.post('/accept_friend_request/2')
        self.assertEqual(response.status_code, 200)

    def test_remove_friend(self):
        self.login_user()
        response = self.client.post('/remove_friend/3')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/friends_group', response.location)
