import pytest
from unittest.mock import MagicMock, patch
from aider.dspy_edit import DSPyEditModule

def test_dspy_edit_module():
    module = DSPyEditModule()
    
    # Test successful edit generation
    result = module.generate_edit(
        file_name="test.py",
        file_content="def hello():\n    print('hello')\n",
        edit_request="Change the greeting to 'hi'"
    )
    assert isinstance(result, tuple)
    assert len(result) == 2
    
    # Test error handling
    with patch('dspy.Predict', side_effect=Exception("Test error")):
        result = module.generate_edit(
            file_name="test.py",
            file_content="def hello():\n    print('hello')\n",
            edit_request="Change the greeting"
        )
        assert result is None

def test_dspy_integration():
    with patch('aider.coders.base_coder.DSPyEditModule') as mock_dspy:
        from aider.coders.base_coder import Coder
        
        # Mock successful DSPy edit
        mock_instance = MagicMock()
        mock_instance.generate_edit.return_value = ("old code", "new code")
        mock_dspy.return_value = mock_instance
        
        # Create coder with DSPy mode enabled
        coder = Coder(None, None, dspy_mode=True)
        assert coder.dspy_mode == True
        assert coder.dspy_editor is not None
