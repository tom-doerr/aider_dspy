from aider.coders.base_coder import Coder
from aider.dspy_search_replace import DSPySearchReplaceModule
from aider.coders.editblock_prompts import EditBlockPrompts
from aider.coders.editblock_coder import find_similar_lines
from pathlib import Path


class DSPySearchReplaceCoder(Coder):
    edit_format = "dspy-search-replace"
    gpt_prompts = EditBlockPrompts()

    def __init__(self, main_model, io, **kwargs):
        super().__init__(main_model, io, **kwargs)
        self.dspy_search_replace = DSPySearchReplaceModule(self.gpt_prompts, main_model)
        
        # Train DSPy module on example edits
        self._train_dspy_module()
        
    def _train_dspy_module(self):
        """Train the DSPy module on example edits"""
        # Example training data would go here
        # For now just initialize without training
        pass

    def apply_edits(self, edits, dry_run=False):
        failed = []
        passed = []
        updated_edits = []

        for edit in edits:
            path, original, updated = edit
            full_path = self.abs_root_path(path)
            new_content = None

            if Path(full_path).exists():
                content = self.io.read_text(full_path)
                new_content = self.dspy_do_replace(full_path, content, original, updated, self.fence)

            updated_edits.append((path, original, updated))

            if new_content:
                if not dry_run:
                    self.io.write_text(full_path, new_content)
                passed.append(edit)
            else:
                failed.append(edit)

        if dry_run:
            return updated_edits

        if not failed:
            return

        blocks = "block" if len(failed) == 1 else "blocks"

        res = f"# {len(failed)} SEARCH/REPLACE {blocks} failed to match!\n"
        for edit in failed:
            path, original, updated = edit

            full_path = self.abs_root_path(path)
            content = self.io.read_text(full_path)

            res += f"""
## SearchReplaceNoExactMatch: This SEARCH block failed to exactly match lines in {path}
<<<<<<< SEARCH
{original}=======
{updated}>>>>>>> REPLACE

"""
            did_you_mean = find_similar_lines(original, content)
            if did_you_mean:
                res += f"""Did you mean to match some of these actual lines from {path}?

{self.fence[0]}
{did_you_mean}
{self.fence[1]}

"""

            if updated in content and updated:
                res += f"""Are you sure you need this SEARCH/REPLACE block?
The REPLACE lines are already in {path}!

"""
        res += (
            "The SEARCH section must exactly match an existing block of lines including all white"
            " space, comments, indentation, docstrings, etc\n"
        )
        if passed:
            pblocks = "block" if len(passed) == 1 else "blocks"
            res += f"""
# The other {len(passed)} SEARCH/REPLACE {pblocks} were applied successfully.
Don't re-send them.
Just reply with fixed versions of the {blocks} above that failed to match.
"""
        raise ValueError(res)

    def get_edits(self):
        content = self.partial_response_content
        files = self.get_inchat_relative_files()
        
        # Use DSPy to generate edits
        edits = self.dspy_search_replace.generate_edits(content, files)
        
        # Extract shell commands
        self.shell_commands += [edit[1] for edit in edits if edit[0] is None]
        edits = [edit for edit in edits if edit[0] is not None]
        
        return edits

    def dspy_do_replace(self, fname, content, original, updated, fence=None):
        """DSPy-specific version of do_replace that uses DSPy signatures"""
        if not original.strip():
            # append to existing file, or start a new file
            return content + updated
            
        # Use DSPy to find and replace the content
        return self.dspy_search_replace.replace_content(
            content=content,
            search=original,
            replace=updated
        )
