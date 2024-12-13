import re
import dspy
from typing import Optional, List, Tuple
from pathlib import Path

class SearchReplaceSignature(dspy.Signature):
    """Signature for code editing with search/replace blocks"""
    content: str = dspy.InputField(desc="The LLM response containing search/replace blocks")
    files: List[str] = dspy.InputField(desc="List of files that can be edited")
    edits: List[Tuple[Optional[str], str, str]] = dspy.OutputField(
        desc="List of (filename, search_text, replace_text) tuples. filename=None for shell commands"
    )

class DSPySearchReplaceModule(dspy.Module):
    """Module for generating code edits using DSPy"""
    def __init__(self, gpt_prompts=None):
        super().__init__()
        self.gpt_prompts = gpt_prompts
        self.predictor = dspy.Predict(SearchReplaceSignature)

    def generate_edits(self, content: str, files: List[str]) -> List[Tuple[Optional[str], str, str]]:
        """Generate search/replace edits from LLM response"""
        try:
            result = self.predictor(content=content, files=files)
            return result.edits
        except Exception as e:
            print(f"DSPy edit generation failed: {e}")
            return []

    def replace_content(self, content: str, search: str, replace: str) -> Optional[str]:
        """Replace search text with replace text in content"""
        if not search.strip():
            return content + replace
            
        # Find exact match
        if search in content:
            return content.replace(search, replace, 1)
            
        # Try matching ignoring whitespace
        search_lines = search.splitlines()
        content_lines = content.splitlines()
        
        for i in range(len(content_lines) - len(search_lines) + 1):
            chunk = content_lines[i:i + len(search_lines)]
            if all(s.strip() == c.strip() for s, c in zip(search_lines, chunk)):
                content_lines[i:i + len(search_lines)] = replace.splitlines()
                return '\n'.join(content_lines)
                
        return None
