import unittest
from unittest.mock import patch
from main import test_mongo_connection
import dotenv
import os

dotenv.load_dotenv()
class TestMongoConnection(unittest.TestCase):

    @patch('pymongo.MongoClient')
    def test_valid_mongo_connection(self, mock_mongo_client):
        # Mock the list_database_names method to return a sample list
        mock_client_instance = mock_mongo_client.return_value
        mock_client_instance.list_database_names.return_value = ['db1', 'db2']

        # Test with a valid MongoDB URI
        result = test_mongo_connection(os.getenv('MONGO_URI'))
        if result:
            print("MongoDB connection successful:", result)
            self.assertEqual(result, ['db1', 'db2'])
        else:
            self.fail("MongoDB connection failed")

    @patch('pymongo.MongoClient')
    def test_invalid_mongo_connection(self, mock_mongo_client):
        # Mock the MongoClient to raise an exception
        mock_mongo_client.side_effect = Exception("Connection failed")

        # Test with an invalid MongoDB URI
        result = test_mongo_connection('mongodb+srv://invalid-url')
        self.assertIsNone(result)

    def test_empty_mongo_url(self):
        # Test with an empty MongoDB URI
        result = test_mongo_connection('')
        self.assertIsNone(result)

if __name__ == '__main__':
    unittest.main()