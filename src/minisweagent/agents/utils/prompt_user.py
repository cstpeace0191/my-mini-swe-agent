from prompt_toolkit.formatted_text.html import HTML
from prompt_toolkit.history import FileHistory
from prompt_toolkit.output import DummyOutput
from prompt_toolkit.shortcuts import PromptSession

from minisweagent import global_config_dir

_history = FileHistory(global_config_dir / "interactive_history.txt")

try:
    prompt_session = PromptSession(history=_history)
    _multiline_prompt_session = PromptSession(history=_history, multiline=True)
except Exception:
    prompt_session = PromptSession(history=_history, output=DummyOutput())
    _multiline_prompt_session = PromptSession(history=_history, multiline=True, output=DummyOutput())


def _multiline_prompt() -> str:
    return _multiline_prompt_session.prompt(
        "",
        bottom_toolbar=HTML(
            "Submit message: <b fg='yellow' bg='black'>Esc, then Enter</b> | "
            "Navigate history: <b fg='yellow' bg='black'>Arrow Up/Down</b> | "
            "Search history: <b fg='yellow' bg='black'>Ctrl+R</b>"
        ),
    )
