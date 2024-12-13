# from aider.coders.base_coder import Coder
# from aider.coders.diff_coder import DiffCoder
# from aider.coders.whole_file_coder import WholeFileCoder
# from aider.coders.udiff_coder import UnifiedDiffCoder
# from aider.coders.editor_diff_coder import EditorDiffCoder
# from aider.coders.dspy_edit_coder import DSPyEditCoder
# from aider.coders.dspy_search_replace_coder import DSPySearchReplaceCoder
# from aider.coders.architect_coder import ArchitectCoder
from .architect_coder import ArchitectCoder
from .ask_coder import AskCoder
from .base_coder import Coder
from .editblock_coder import EditBlockCoder
from .editblock_fenced_coder import EditBlockFencedCoder
from .editor_editblock_coder import EditorEditBlockCoder
from .editor_whole_coder import EditorWholeFileCoder
from .help_coder import HelpCoder
from .udiff_coder import UnifiedDiffCoder
from .wholefile_coder import WholeFileCoder

__all__ = [
    HelpCoder,
    AskCoder,
    Coder,
    EditBlockCoder,
    EditBlockFencedCoder,
    WholeFileCoder,
    UnifiedDiffCoder,
    #    SingleWholeFileFunctionCoder,
    ArchitectCoder,
    EditorEditBlockCoder,
    EditorWholeFileCoder,
    DSPyEditCoder,
    DSPySearchReplaceCoder,
]
