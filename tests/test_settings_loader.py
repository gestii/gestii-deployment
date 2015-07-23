import os

os.environ['DEPLOYMENT_SETTINGS_MODULE'] = 'conf_testing'
os.environ['DEPLOYMENT_ENVIRONMENT']     = 'testing'

import unittest
import subprocess

class TestSettingsLoader(unittest.TestCase):

    def setUp(self):
        os.mkdir('conf_testing')
        subprocess.check_call([
            'cp',
            'tests/fixtures/settings.py',
            'conf_testing/settings.py'
        ])
        subprocess.check_call([
            'cp',
            'tests/fixtures/settings_testing.py',
            'conf_testing/settings_testing.py'
        ])
        open('conf_testing/__init__.py', 'a').close()

        from lib.settings_loader import settings

        self.settings = settings

    def tearDown(self):
        def delete(file):
            try:
                os.remove(file)
            except OSError, e:
                pass

        map(delete, [
            'conf_testing/settings_testing.py',
            'conf_testing/settings.py',
            'conf_testing/__init__.py',
            'conf_testing/settings_testing.pyc',
            'conf_testing/settings.pyc',
            'conf_testing/__init__.pyc',
        ])

        os.rmdir('conf_testing')

        del self.settings

    def test_null_setting(self):
        self.assertEqual(self.settings['LOG'], None)

    def test_master_setting(self):
        self.assertEqual(self.settings['FOO'], 'this')

    def test_overrided_setting(self):
        self.assertEqual(self.settings['VAR'], 'those')

    def test_nomaster_setting(self):
        self.assertEqual(self.settings['BAZ'], None)

    def test_null_setting_attribute(self):
        self.assertEqual(self.settings.LOG, None)

    def test_master_setting_attribute(self):
        self.assertEqual(self.settings.FOO, 'this')

    def test_overrided_setting_attribute(self):
        self.assertEqual(self.settings.VAR, 'those')

    def test_nomaster_setting_attribute(self):
        self.assertEqual(self.settings.BAZ, None)

    def test_null_setting_get(self):
        self.assertEqual(self.settings.get('LOG', 'default'), 'default')

    def test_master_setting_get(self):
        self.assertEqual(self.settings.get('FOO', 'default'), 'this')

    def test_overrided_setting_get(self):
        self.assertEqual(self.settings.get('VAR', 'default'), 'those')

    def test_nomaster_setting_get(self):
        self.assertEqual(self.settings.get('BAZ', 'default'), 'default')
