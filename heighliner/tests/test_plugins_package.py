import subprocess
import unittest

import mock

from heighliner.plugins import package


class TestPackage(unittest.TestCase):

    @mock.patch('heighliner.plugins.package.subprocess')
    def test_do_script(self, subprocess):
        package.do(meta={'name': 'foo', 'version': '1.0', 'type': None},
                   data={'script': "./foo_script.sh"})
        subprocess.check_call.assert_called_with("./foo_script.sh", shell=True)

    def test_do_script_error(self):
        with self.assertRaises(subprocess.CalledProcessError):
            package.do(meta={'name': 'foo', 'version': '1.0', 'type': None},
                       data={'script': "/bin/false"})
