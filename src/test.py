'''Unittests'''

import unittest
from routes import app

class FlaskTestCase(unittest.TestCase):

    def test_index(self):
        test = app.test_client(self)
        response = test.get('/login', content_type='html/text')
        self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()
