from aider.coders.base_coder import Coder
from aider.dspy_search_replace import DSPySearchReplaceModule

class DSPySearchReplaceCoder(Coder):
    edit_format = "dspy-search-replace"

    def __init__(self, main_model, io, **kwargs):
        super().__init__(main_model, io, **kwargs)
        self.dspy_search_replace = DSPySearchReplaceModule()
        self.gpt_prompts = self.main_model.gpt_prompts  # Ensure gpt_prompts is accessible

    def apply_edit(self, edit, fname, content):
        search_text, replace_text = edit
        if search_text is None or replace_text is None:
            return content

        return content.replace(search_text, replace_text)

    def get_edits(self, fnames, content, edit_request):
        edits = {}
        for fname, file_content in zip(fnames, content):
            edit = self.dspy_search_replace.generate_search_replace(
                file_name=fname,
                file_content=file_content,
                edit_request=edit_request,
            )
            if edit:
                edits[fname] = edit
        return edits
