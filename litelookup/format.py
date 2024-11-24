from rich.padding import Padding
from rich import print
from rich.markdown import Markdown
from prompt_toolkit.formatted_text import HTML


def print_formatted_response(response: str):
    markdown_response = Padding(Markdown(response), (1, 1), style="green", expand=False)
    print(markdown_response)


def normal_bottom_toolbar():
    return HTML(
        ' Press <i>"q", "quit", or "exit"</i> to <style bg="ansired">quit</style> <b>litelookup</b>'
    )


def chat_bottom_toolbar():
    return HTML(
        ' Press <i>"q", "Ctrl + C", or "Ctrl + D"</i> to <style bg="ansired">quit</style> <b>litelookup</b>'
    )
