import dspy
from typing import Optional

class SearchReplaceSignature(dspy.Signature):
    """Signature for code editing with search/replace blocks"""
    file_name: str = dspy.InputField()
    file_content: str = dspy.InputField()
    edit_request: str = dspy.InputField()
    search_text: str = dspy.OutputField(desc="Text to search for in the file")
    replace_text: str = dspy.OutputField(desc="Text to replace the search text with")

class DSPySearchReplaceModule(dspy.Module):
    """Module for generating code edits using DSPy"""
    def __init__(self):
        super().__init__()
        self.search_replace_predictor = dspy.Predict(SearchReplaceSignature)

    def generate_search_replace(self, file_name: str, file_content: str, edit_request: str) -> Optional[tuple]:
        """Generate a search/replace edit for the given file and request"""
        try:
            result = self.search_replace_predictor(
                file_name=file_name,
                file_content=file_content,
                edit_request=edit_request
            )
            return result.search_text, result.replace_text
        except Exception as e:
            print(f"DSPy search/replace generation failed: {e}")
            return None
