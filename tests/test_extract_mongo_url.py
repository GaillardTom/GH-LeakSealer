import unittest
from main import extract_mongo_url

class TestExtractMongoURL(unittest.TestCase):

    def test_valid_mongo_url(self):
        code = "mongodb+srv://user:password@cluster.mongodb.net/test"
        self.assertEqual(extract_mongo_url(code), "mongodb+srv://user:password@cluster.mongodb.net")

    def test_invalid_mongo_url(self):
        code = "This is not a valid MongoDB URL"
        self.assertIsNone(extract_mongo_url(code))

if __name__ == '__main__':
    unittest.main()