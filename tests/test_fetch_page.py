import unittest
from unittest.mock import patch, Mock
from main import fetch_page
import requests

class TestFetchPage(unittest.TestCase):

    @patch('main.requests.sessions.Session.get')
    def test_fetch_page_success(self, mock_get):
        # Mock a successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"items": ["item1", "item2"]}
        mock_get.return_value = mock_response

        session = requests.sessions.Session()
        result = fetch_page(session, 'a', 1)
        self.assertEqual(result.json(), {"items": ["item1", "item2"]})

    @patch('main.requests.sessions.Session.get')
    def test_fetch_page_rate_limit(self, mock_get):
        # Mock a rate limit response followed by a successful response
        mock_rate_limit_response = Mock()
        mock_rate_limit_response.status_code = 403
        mock_success_response = Mock()
        mock_success_response.status_code = 200
        mock_success_response.json.return_value = {"items": ["item1"]}
        mock_get.side_effect = [mock_rate_limit_response, mock_success_response]

        session = requests.sessions.Session()
        result = fetch_page(session, 'b', 2)
        self.assertEqual(result.json(), {"items": ["item1"]})

    @patch('main.requests.sessions.Session.get')
    def test_fetch_page_failure(self, mock_get):
        # Mock a failed response
        mock_response = Mock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response

        session = requests.sessions.Session()
        with self.assertRaises(Exception):
            fetch_page(session, 'c', 3)

if __name__ == '__main__':
    unittest.main()