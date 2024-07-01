import unittest
from hatchery import Ddragon  # Replace 'hatchery' with the actual module name

class TestDdragonMethods(unittest.TestCase):

    def test_add_elixir_info(self):
        # Create a Ddragon instance
        ddragon = Ddragon(genotype="genotype1", parent1="parent1", parent2="parent2", phenotype="phenotype")

        # Elixir data
        rgb = '(250, 129, 84)'
        title = "Coral Playful Dragon Egg Elixir"
        primary = "Playful"
        secondaries = ["Unique", "Drive", "Showy"]

        # Call the add_elixir_info method
        ddragon.add_elixir_info(rgb, title, primary, secondaries)

        # Assert the attributes are set correctly
        self.assertEqual(ddragon.elixir_rgb, '(250, 129, 84)')
        self.assertEqual(ddragon.elixir_title, title)
        self.assertEqual(ddragon.elixir_primary, primary)
        self.assertEqual(ddragon.elixir_secondaries, secondaries)

if __name__ == '__main__':
    unittest.main()
