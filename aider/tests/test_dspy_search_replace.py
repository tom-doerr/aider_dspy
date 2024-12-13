import pytest
from aider.dspy_search_replace import DSPySearchReplaceModule, SearchReplaceSignature
from aider.coders.dspy_search_replace_coder import DSPySearchReplaceCoder
import dspy

class MockPredictor:
    def __init__(self, search_text, replace_text):
        self.search_text = search_text
        self.replace_text = replace_text

    def __call__(self, **kwargs):
        class MockResult:
            pass
        result = MockResult()
        result.search_text = self.search_text
        result.replace_text = self.replace_text
        return result

class MockDSPySearchReplaceModule(DSPySearchReplaceModule):
    def __init__(self, search_text, replace_text):
        super().__init__()
        self.search_replace_predictor = MockPredictor(search_text, replace_text)

@pytest.fixture
def mock_dspy_module():
    return MockDSPySearchReplaceModule("old", "new")

def test_dspy_search_replace_module(mock_dspy_module):
    file_name = "test.txt"
    file_content = "This is an old file."
    edit_request = "Replace 'old' with 'new'."
    result = mock_dspy_module.generate_search_replace(file_name, file_content, edit_request)
    assert result == ("old", "new")

def test_dspy_search_replace_module_failure():
    class FailingPredictor:
        def __call__(self, **kwargs):
            raise Exception("Predictor failed")

    class FailingDSPySearchReplaceModule(DSPySearchReplaceModule):
        def __init__(self):
            super().__init__()
            self.search_replace_predictor = FailingPredictor()

    module = FailingDSPySearchReplaceModule()
    file_name = "test.txt"
    file_content = "This is an old file."
    edit_request = "Replace 'old' with 'new'."
    result = module.generate_search_replace(file_name, file_content, edit_request)
    assert result is None

def test_dspy_search_replace_coder_apply_edit(mock_dspy_module):
    coder = DSPySearchReplaceCoder()
    fname = "test.txt"
    content = "This is an old file."
    edit = ("old", "new")
    new_content = coder.apply_edit(edit, fname, content)
    assert new_content == "This is an new file."

def test_dspy_search_replace_coder_apply_edit_no_edit(mock_dspy_module):
    coder = DSPySearchReplaceCoder()
    fname = "test.txt"
    content = "This is an old file."
    edit = (None, None)
    new_content = coder.apply_edit(edit, fname, content)
    assert new_content == "This is an old file."

def test_dspy_search_replace_coder_get_edits(mock_dspy_module):
    coder = DSPySearchReplaceCoder()
    fnames = ["test.txt"]
    content = ["This is an old file."]
    edit_request = "Replace 'old' with 'new'."
    edits = coder.get_edits(fnames, content, edit_request)
    assert edits == {"test.txt": ("old", "new")}

def test_dspy_search_replace_coder_get_edits_multiple_files(mock_dspy_module):
    coder = DSPySearchReplaceCoder()
    fnames = ["test1.txt", "test2.txt"]
    content = ["This is an old file.", "Another old file."]
    edit_request = "Replace 'old' with 'new'."
    edits = coder.get_edits(fnames, content, edit_request)
    assert edits == {"test1.txt": ("old", "new"), "test2.txt": ("old", "new")}
