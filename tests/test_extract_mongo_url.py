import unittest
from main import extract_mongo_url

class TestExtractMongoURL(unittest.TestCase):

    def test_valid_mongo_url(self):
        code = "mongodb+srv://user:password@cluster.mongodb.net/test"
        result = extract_mongo_url(code)
        self.assertEqual(result, "mongodb+srv://user:password@cluster.mongodb.net")

    def test_malformed_mongo_url(self):
        code = "mongodb+srv:/malformed-url"
        result = extract_mongo_url(code)
        self.assertIsNone(result)

    def test_special_characters_in_url(self):
        code = "mongodb+srv://user:pass@host!"
        result = extract_mongo_url(code)
        self.assertEqual(result, "mongodb+srv://user:pass@host!")

    def test_embedded_mongo_url(self):
        code = "Some text mongodb+srv://embedded-url more text"
        result = extract_mongo_url(code)
        self.assertEqual(result, "mongodb+srv://embedded-url")
    def test_weird_mongo_url(self):
            code = "Some texWaldshadlkasldkjasdkasdasda!@#)$*@!#@!&*(sdastasdasda# mongodb+srv://tom:gaillard@randomhosht.mongo.net/embedded-url more@ tasdasdasdadssadasdext"
            result = extract_mongo_url(code)
            self.assertEqual(result, "mongodb+srv://tom:gaillard@randomhosht.mongo.net")
    def test_no_mongo_url(self):
        code = "No MongoDB URL here"
        result = extract_mongo_url(code)
        self.assertIsNone(result)

if __name__ == '__main__':
    unittest.main()