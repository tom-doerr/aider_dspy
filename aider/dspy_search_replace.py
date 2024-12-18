import re
import dspy
from typing import Optional, List, Tuple
from pathlib import Path

class FindEditSignature(dspy.Signature):
    """Find and replace content in a file"""
    content = dspy.InputField(desc="The file content to search in")
    search = dspy.InputField(desc="The text to search for")
    replace = dspy.InputField(desc="The text to replace with")
    reasoning = dspy.OutputField(desc="Step by step reasoning about how to match and replace")
    result = dspy.OutputField(desc="The modified content with replacement made, or None if no match")

class ParseEditSignature(dspy.Signature):
    """Parse edit blocks from LLM response"""
    content = dspy.InputField(desc="The LLM response containing search/replace blocks")
    files = dspy.InputField(desc="List of files that can be edited")
    reasoning = dspy.OutputField(desc="Step by step reasoning about how to parse the blocks")
    edits = dspy.OutputField(desc="List of (filename, search_text, replace_text) tuples. filename=None for shell commands")

class DSPySearchReplaceModule(dspy.Module):
    """Module for generating code edits using DSPy"""
    def __init__(self, gpt_prompts=None):
        super().__init__()
        self.gpt_prompts = gpt_prompts
        self.parse_predictor = dspy.ChainOfThought(ParseEditSignature)
        self.find_predictor = dspy.ChainOfThought(FindEditSignature)

    def generate_edits(self, content: str, files: List[str]) -> List[Tuple[Optional[str], str, str]]:
        """Generate search/replace edits from LLM response"""
        return self._parse_blocks(content, files)

    def replace_content(self, content: str, search: str, replace: str) -> Optional[str]:
        """Replace search text with replace text in content using exact matching"""
        if not search.strip():
            return content + replace
            
        # Try exact match first
        if search in content:
            return content.replace(search, replace, 1)
            
        # If no exact match, return None
        return None

    def _parse_blocks(self, content: str, files: List[str]) -> List[Tuple[Optional[str], str, str]]:
        """Internal helper for block parsing - used to train DSPy"""
        try:
            HEAD = r"^<{5,9} SEARCH\s*$"
            DIVIDER = r"^={5,9}\s*$"
            UPDATED = r"^>{5,9} REPLACE\s*$"
            FENCE = r"^```"
            
            edits = []
            lines = content.splitlines()
            i = 0
            current_file = None
            in_code_block = False
            
            while i < len(lines):
                line = lines[i].strip()
                
                # Check for shell commands in code blocks
                if line.startswith("```") and any(line.startswith(f"```{sh}") for sh in ["bash", "sh", "shell"]):
                    shell_content = []
                    i += 1
                    while i < len(lines) and not lines[i].strip().startswith("```"):
                        shell_content.append(lines[i])
                        i += 1
                    edits.append((None, "\n".join(shell_content), ""))
                    i += 1
                    continue
                
                # Handle code fence markers
                if line.startswith("```"):
                    in_code_block = not in_code_block
                    i += 1
                    continue
                
                # Look for filename outside code blocks
                if not in_code_block and line and not line.startswith(("```", "<", "=", ">")):
                    if line in files or any(Path(f).name == line for f in files):
                        current_file = line
                    i += 1
                    continue
                
                # Look for search/replace blocks inside code blocks
                if in_code_block and re.match(HEAD, line):
                    search_lines = []
                    i += 1
                    while i < len(lines) and not re.match(DIVIDER, lines[i].strip()):
                        search_lines.append(lines[i])
                        i += 1
                    
                    replace_lines = []
                    i += 1
                    while i < len(lines) and not re.match(UPDATED, lines[i].strip()):
                        replace_lines.append(lines[i])
                        i += 1
                        
                    if current_file:
                        # Remove any trailing whitespace but ensure one newline at end
                        search_content = "\n".join(search_lines).rstrip() + "\n"
                        replace_content = "\n".join(replace_lines).rstrip() + "\n"
                        edits.append((
                            current_file,
                            search_content,
                            replace_content
                        ))
                i += 1
            
            return edits
            
        except Exception as e:
            print(f"DSPy edit generation failed: {e}")
            return []

