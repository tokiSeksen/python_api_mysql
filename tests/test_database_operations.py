from unittest.mock import MagicMock, patch
import unittest

from app.database_operations import insert_data, fetch_all


class DatabaseOperationsTestCase(unittest.TestCase):

    def setUp(self):
        self.mock_mysql = MagicMock()

    def tearDown(self):
        pass

    @patch('app.database_operations.execute_query')
    def test_insert_data(self, mock_execute_query):
        mock_cursor = MagicMock()

        mock_execute_query.return_value = mock_cursor

        query = "INSERT INTO links (username, destination_url, title) VALUES (%s, %s, %s)"
        params = ('test_user', 'https://google.com', 'Google Url')

        insert_data(self.mock_mysql, query, params)

        mock_execute_query.assert_called_once_with(self.mock_mysql, query, params)
        self.mock_mysql.connection.commit.assert_called_once()
        mock_cursor.close.assert_called_once()

    @patch('app.database_operations.execute_query')
    def test_fetch_all(self, mock_execute_query):
        mock_cursor = MagicMock()
        mock_execute_query.return_value = mock_cursor

        query = "SELECT * FROM links WHERE username = %s"
        params = ('test_user', 'https://google.com', 'Google Url')

        # Mock the fetchall result
        mock_result = [('test_user', 'https://google.com', 'Google Url')]  # Adjust this to match your expected results
        mock_cursor.fetchall.return_value = mock_result

        result = fetch_all(self.mock_mysql, query, params)

        mock_execute_query.assert_called_once_with(self.mock_mysql, query, params)
        mock_cursor.fetchall.assert_called_once()
        mock_cursor.close.assert_called_once()

        self.assertEqual(result, mock_result)


if __name__ == '__main__':
    unittest.main()
