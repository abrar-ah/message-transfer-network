import unittest
import pep8
from ddt import ddt, data
import os

PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
FILES = []
for root, dirs, files in os.walk(PATH):
    for file in files:
        if file.endswith(".py"):
            FILES.append(os.path.join(root, file))


@ddt
class TestCodeFormat(unittest.TestCase):
    @data(*FILES)
    def test_pep8(self, file_path):
        """
        Tests all the python files for conforming to PEP-8 standards
        """

        # please ignore checks that PEP8 does not enforce
        pep8style = pep8.StyleGuide(quiet=False, ignore=(
            "E24", "E121", "E123", "E126", "E226",  "E501", "E704"))

        result = pep8style.check_files([file_path])
        self.assertEqual(0, result.total_errors,
                         f"Found code style errors: {file_path}")
