import os
import unittest
from unittest.mock import patch

import pytest

from aider.main import main


class TestBrowser(unittest.TestCase):
    @patch("aider.main.launch_gui")
    @patch("aider.main.main")
    def test_browser_flag_imports_streamlit(self, mock_main, mock_launch_gui):
        os.environ["AIDER_ANALYTICS"] = "false"

        # Mock the main function to simulate the behavior of the --browser flag
        mock_main.return_value = None

        # Run main with --browser and --yes flags
        try:
            main(["--browser", "--yes"])
        except TypeError as e:
            if "Descriptors cannot be created directly" in str(e):
                pytest.xfail("protobuf version is incompatible")
            raise

        # Check that launch_gui was called
        mock_launch_gui.assert_called_once()

        # Try to import streamlit
        try:
            import streamlit  # noqa: F401

            streamlit_imported = True
        except ImportError:
            streamlit_imported = False

        # Assert that streamlit was successfully imported
        self.assertTrue(
            streamlit_imported, "Streamlit should be importable after running with --browser flag"
        )


if __name__ == "__main__":
    unittest.main()
