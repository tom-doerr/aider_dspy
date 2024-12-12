import pytest
from unittest.mock import MagicMock, patch
from aider.voice import Voice
from aider.io import InputOutput

def test_auto_submit_transcript():
    io = InputOutput()
    voice = Voice(save_dir=None)
    voice.io = io
    voice.auto_submit_transcript = True
    
    # Mock the transcription call
    with patch('aider.voice.litellm.transcription') as mock_transcribe:
        # Test successful transcription
        mock_transcribe.return_value.text = "Test transcript"
        result = voice.record_and_transcribe()
        assert result == "Test transcript"
        
        # Test failed transcription with retry
        mock_transcribe.side_effect = [Exception("First fail"), "Test retry"]
        result = voice.record_and_transcribe()
        assert result == "Test retry"
        assert mock_transcribe.call_count == 2

def test_max_lint_retries():
    from aider.commands import Commands
    
    io = MagicMock()
    commands = Commands(io=io, coder=None)
    commands.max_lint_retries = 2
    
    # Mock lint errors that keep occurring
    with patch('aider.commands.Commands.lint_edited') as mock_lint:
        mock_lint.return_value = "Error"
        commands.num_reflections = 0
        
        # First try
        commands.lint_outcome = None
        commands.reflected_message = None
        commands.run_one("test", preproc=False)
        assert commands.num_reflections == 1
        
        # Second try
        commands.lint_outcome = None
        commands.reflected_message = None
        commands.run_one("test", preproc=False)
        assert commands.num_reflections == 2
        
        # Third try should not happen due to max_lint_retries=2
        commands.lint_outcome = None
        commands.reflected_message = None
        commands.run_one("test", preproc=False)
        assert commands.num_reflections == 2

def test_voice_save_dir():
    import os
    import tempfile
    
    # Create a temporary directory
    with tempfile.TemporaryDirectory() as tmpdir:
        voice = Voice(save_dir=tmpdir)
        
        # Mock recording to create a test file
        with patch('aider.voice.Voice.record_and_transcribe') as mock_record:
            mock_record.return_value = "Test recording"
            voice.record_and_transcribe()
            
            # Check that files were saved
            files = os.listdir(tmpdir)
            assert len(files) > 0
            assert any(f.startswith("recording-") for f in files)
