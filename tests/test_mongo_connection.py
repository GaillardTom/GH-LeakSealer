import unittest
from unittest.mock import patch
from main import test_mongo_connection
import os

class TestMongoConnection(unittest.TestCase):

    @patch('pymongo.MongoClient')
    def test_valid_mongo_connection(self, mock_mongo_client):
        # Mock the list_database_names method to return a sample list
        mock_client_instance = mock_mongo_client.return_value
        mock_client_instance.list_database_names.return_value = ['db1', 'db2']

        # Test with a valid MongoDB URI from GitHub Actions secrets
        mongo_uri = os.getenv('MONGO_URI')
        print("Mongo URI:", mongo_uri)  # Debugging line to check the Mongo URI
        if not mongo_uri:
            self.fail("MONGO_URI environment variable is not set.")
        result = test_mongo_connection(mongo_uri)
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