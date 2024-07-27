import unittest
from unittest.mock import patch
from ansible.plugins.loader import vars_loader

# Mock Display to avoid actual logging
class MockDisplay:
    def debug(self, msg):
        pass

    def v(self, msg):
        pass

# Patching the Display to use the mock
display = MockDisplay()

class TestKeepassPswVarsPlugin(unittest.TestCase):
    def setUp(self):
        self.plugin = vars_loader.get('keepass_psw')

    @patch('hczv.keepass.ask_password', return_value='mocked_password')
    def test_get_vars_first_call(self, mock_ask_password):
        # First call should ask for password
        vars_data = self.plugin.get_vars(None, None, None)
        self.assertEqual(vars_data['keepass_psw'], 'mocked_password')
        mock_ask_password.assert_called_once()

    @patch('hczv.keepass.ask_password', return_value='mocked_password')
    def test_get_vars_cached_call(self, mock_ask_password):
        # First call to set the cache
        self.plugin.get_vars(None, None, None)
        # Reset the mock to check if it's called again
        mock_ask_password.reset_mock()
        # Second call should use cache
        vars_data = self.plugin.get_vars(None, None, None)
        self.assertEqual(vars_data['keepass_psw'], 'mocked_password')
        mock_ask_password.assert_not_called()

    @patch.dict('os.environ', {'MOLECULE_SCENARIO': 'true'})
    def test_get_vars_molecule_scenario(self):
        # If MOLECULE_SCENARIO is set, it should return 'MOLECULE_SCENARIO'
        vars_data = self.plugin.get_vars(None, None, None)
        self.assertEqual(vars_data['keepass_psw'], 'MOLECULE_SCENARIO')

if __name__ == '__main__':
    unittest.main()
