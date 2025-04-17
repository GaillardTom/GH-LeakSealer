import unittest
from unittest.mock import patch
from main import setup_session

class TestSetupSession(unittest.TestCase):

    @patch('main.os.getenv')
    def test_setup_session_valid_env(self, mock_getenv):
        # Mock environment variables
        mock_getenv.side_effect = lambda key: 'valid_token' if key == 'GH_API_TOKEN' else 'mongodb+srv://valid-url'

        session = setup_session()
        self.assertIsNotNone(session)

    @patch('main.os.getenv')
    def test_setup_session_missing_gh_token(self, mock_getenv):
        # Mock missing GH_API_TOKEN
        mock_getenv.side_effect = lambda key: None if key == 'GH_API_TOKEN' else 'mongodb+srv://valid-url'

        with self.assertRaises(ValueError) as context:
            setup_session()
        self.assertEqual(str(context.exception), "GH_API_TOKEN is required.")

    @patch('main.os.getenv')
    def test_setup_session_missing_mongo_uri(self, mock_getenv):
        # Mock missing mongo_uri
        mock_getenv.side_effect = lambda key: 'valid_token' if key == 'GH_API_TOKEN' else None

        with self.assertRaises(ValueError) as context:
            setup_session()
        self.assertEqual(str(context.exception), "mongo_uri is required.")

if __name__ == '__main__':
    unittest.main()