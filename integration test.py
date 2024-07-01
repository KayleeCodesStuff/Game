import unittest
from hatchery import get_elixir_details  # Replace 'hatchery' with the actual module name

class TestIntegrationHatcheryFunctions(unittest.TestCase):

    def test_get_elixir_details_integration(self):
        # Call the function with a position known to exist in Firestore
        position = 1
        result = get_elixir_details(position)

        # Define the expected result
        expected_result = {
            'image_file': 'pb7.png',
            'position': 1,
            'primary_trait': 'Playful',
            'rgb': '(250, 129, 84)',
            'secondary_trait1': 'Unique',
            'secondary_trait2': 'Drive',
            'secondary_trait3': 'Showy',
            'title': 'Coral Playful Dragon Egg Elixir'
        }

        # Assert the result
        self.assertEqual(result, expected_result)

if __name__ == '__main__':
    unittest.main()
