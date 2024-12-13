import re
import dspy
from typing import Optional, List, Tuple
from pathlib import Path

class FindEditSignature(dspy.Signature):
    """Signature for finding matching content in a file"""
    content: str = dspy.InputField(desc="The file content to search in")
    search: str = dspy.InputField(desc="The text to search for")
    replace: str = dspy.InputField(desc="The text to replace with") 
    result: Optional[str] = dspy.OutputField(desc="The modified content with replacement made, or None if no match")

class ParseEditSignature(dspy.Signature):
    """Signature for parsing edit blocks from LLM response"""
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
        self.parse_predictor = dspy.Predict(ParseEditSignature)
        self.find_predictor = dspy.Predict(FindEditSignature)

    def generate_edits(self, content: str, files: List[str]) -> List[Tuple[Optional[str], str, str]]:
        """Generate search/replace edits from LLM response using DSPy"""
        try:
            result = self.parse_predictor(content=content, files=files)
            return result.edits
        except Exception as e:
            print(f"DSPy edit parsing failed: {e}")
            return []

    def replace_content(self, content: str, search: str, replace: str) -> Optional[str]:
        """Use DSPy to find and replace content"""
        try:
            result = self.find_predictor(
                content=content,
                search=search,
                replace=replace
            )
            return result.result
        except Exception as e:
            print(f"DSPy content replacement failed: {e}")
            return None

    def _parse_blocks(self, content: str, files: List[str]) -> List[Tuple[Optional[str], str, str]]:
        """Internal helper for block parsing - used to train DSPy"""
            HEAD = r"^<{5,9} SEARCH\s*$"
            DIVIDER = r"^={5,9}\s*$"
            UPDATED = r"^>{5,9} REPLACE\s*$"
            FENCE = r"^```"
            
            edits = []
            lines = content.splitlines()
            i = 0
            current_file = None
            
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
                
                # Look for filename
                if line and not line.startswith(("```", "<", "=", ">")):
                    if line in files or any(Path(f).name == line for f in files):
                        current_file = line
                    i += 1
                    continue
                
                # Look for search/replace blocks
                if re.match(HEAD, line):
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
                        edits.append((
                            current_file,
                            "\n".join(search_lines),
                            "\n".join(replace_lines)
                        ))
                i += 1
                
            return edits
            
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
