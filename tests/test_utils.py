# tests/test_utils.py
import unittest
import os
import shutil
from app.core.utils import sanitize_filename, cleanup_temp_files
from config import TEMP_DIR

class TestUtils(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory for testing
        self.test_dir = "tests/test_temp"
        os.makedirs(self.test_dir, exist_ok=True)

    def tearDown(self):
        # Clean up the temporary directory after testing
        shutil.rmtree(self.test_dir)

    def test_sanitize_filename(self):
        invalid_filename = "My/Invalid\\Filename*?:<>|.txt"
        sanitized_filename = sanitize_filename(invalid_filename)
        self.assertEqual(sanitized_filename, "MyInvalidFilename.txt")

        empty_filename = ""
        sanitized_filename = sanitize_filename(empty_filename)
        self.assertEqual(sanitized_filename, "untitled")

        whitespace_filename = "   "
        sanitized_filename = sanitize_filename(whitespace_filename)
        self.assertEqual(sanitized_filename, "untitled")

    def test_cleanup_temp_files(self):
        # Create some temporary files within the test directory
        with open(os.path.join(self.test_dir, "temp_file1.txt"), "w") as f:
            f.write("Test file 1")
        with open(os.path.join(self.test_dir, "temp_file2.txt"), "w") as f:
            f.write("Test file 2")

        # Call the cleanup function
        cleanup_temp_files(self.test_dir)

        # Check if the temporary directory has been removed
        self.assertFalse(os.path.exists(os.path.join(self.test_dir, TEMP_DIR)))

if __name__ == '__main__':
    unittest.main()