import unittest
from unittest.mock import patch, MagicMock
from hatchery import get_elixir_details  # Replace `your_module` with the actual module name


#this unit test does not access the database, it makes up fake data to test the function
class TestHatcheryFunctions(unittest.TestCase):

    @patch('hatchery.db')  # Mock the Firestore database
    def test_get_elixir_details(self, mock_db):
        # Setup mock
        mock_collection = MagicMock()
        mock_document = MagicMock()
        mock_document.exists = True
        mock_document.to_dict.return_value = {
            'secondary_trait3': 'Showy',
            'position': 1,
            'title': 'Coral Playful Dragon Egg Elixir',
            'image_file': 'pb7.png',
            'rgb': '(250, 129, 84)',
            'secondary_trait1': 'Unique',
            'secondary_trait2': 'Drive',
            'primary_trait': 'Playful'
        }
        mock_collection.where.return_value.get.return_value = [mock_document]
        mock_db.collection.return_value = mock_collection

        # Call the function
        result = get_elixir_details(1)

        # Assert the result
        expected_result = {
            'secondary_trait3': 'Showy',
            'position': 1,
            'title': 'Coral Playful Dragon Egg Elixir',
            'image_file': 'pb7.png',
            'rgb': '(250, 129, 84)',
            'secondary_trait1': 'Unique',
            'secondary_trait2': 'Drive',
            'primary_trait': 'Playful'
        }
        self.assertEqual(result, expected_result)

if __name__ == '__main__':
    unittest.main()
