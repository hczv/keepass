# test_keepass_psw.py
import unittest
from unittest.mock import patch, MagicMock
import os
from plugins.vars.prompt_keepass_psw import VarsModule, ask_password, Display, PasswordPopup

class TestVarsModule(unittest.TestCase):

    @patch('plugins.vars.keepass_psw.PasswordPopup')
    @patch('plugins.vars.keepass_psw.tk.Tk')
    def test_ask_password(self, MockTk, MockPasswordPopup):
        # Mock the PasswordPopup dialog result
        mock_dialog = MockPasswordPopup.return_value
        mock_dialog.result = 'test_password'

        # Call the function and check the result
        result = ask_password()
        self.assertEqual(result, 'test_password')

        # Ensure Tkinter root was created and destroyed
        MockTk.assert_called_once()
        MockTk.return_value.destroy.assert_called_once()

    @patch.dict(os.environ, {'MOLECULE_SCENARIO': 'true'}, clear=True)
    def test_generate_data_molecule_scenario(self):
        vars_module = VarsModule()
        data = vars_module._generate_data()
        self.assertEqual(data, {'keepass_psw': 'MOLECULE_SCENARIO'})

    @patch('plugins.vars.keepass_psw.ask_password')
    def test_generate_data_ask_password(self, mock_ask_password):
        mock_ask_password.return_value = 'input_password'
        vars_module = VarsModule()
        data = vars_module._generate_data()
        self.assertEqual(data, {'keepass_psw': 'input_password'})

    def test_get_set_cached_data(self):
        vars_module = VarsModule()
        vars_module._set_cached_data('test_key', 'test_value')
        cached_data = vars_module._get_cached_data('test_key')
        self.assertEqual(cached_data, 'test_value')

    @patch.object(VarsModule, '_generate_data')
    @patch.object(VarsModule, '_get_cached_data')
    @patch.object(VarsModule, '_set_cached_data')
    def test_get_vars_with_cache(self, mock_set_cached_data, mock_get_cached_data, mock_generate_data):
        mock_get_cached_data.return_value = 'cached_data'
        vars_module = VarsModule()

        result = vars_module.get_vars(None, None, None)
        self.assertEqual(result, 'cached_data')
        mock_get_cached_data.assert_called_once_with('cached_var')
        mock_generate_data.assert_not_called()
        mock_set_cached_data.assert_not_called()

    @patch.object(VarsModule, '_generate_data')
    @patch.object(VarsModule, '_get_cached_data')
    @patch.object(VarsModule, '_set_cached_data')
    def test_get_vars_without_cache(self, mock_set_cached_data, mock_get_cached_data, mock_generate_data):
        mock_get_cached_data.return_value = None
        mock_generate_data.return_value = 'generated_data'
        vars_module = VarsModule()

        result = vars_module.get_vars(None, None, None)
        self.assertEqual(result, 'generated_data')
        mock_get_cached_data.assert_called_once_with('cached_var')
        mock_generate_data.assert_called_once()
        mock_set_cached_data.assert_called_once_with('cached_var', 'generated_data')


if __name__ == '__main__':
    unittest.main()
