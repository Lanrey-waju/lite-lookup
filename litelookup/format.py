import asyncio

from prompt_toolkit.formatted_text import HTML
from rich import print
from rich.console import Console
from rich.live import Live
from rich.markdown import Markdown
from rich.padding import Padding


def print_formatted_response(response: str):
    """Prints a markdown-fomatted response all at one to stdout"""
    markdown_response = Padding(Markdown(response), (1, 1), style="green", expand=False)
    print(markdown_response)


def normal_bottom_toolbar():
    """Design bottom toolbar for normal 'lookup' interface"""
    return HTML(
        ' Press <i>"q", "quit", or "exit"</i> to <style bg="ansired">quit</style> <b>litelookup</b>'
    )


def chat_bottom_toolbar():
    """Desigh bottom toolbar for chat interface"""
    return HTML(
        ' Press <i>"q", "Ctrl + C", or "Ctrl + D"</i> to <style bg="ansired">quit</style> <b>litelookup</b>'
    )


async def stream_groq_response(groq_chat, messages, console) -> str:
    """Stream response with real-time Markdown formatting."""
    response_text = ""
    markdown = Markdown("", code_theme="monokai")
    padding = Padding(markdown, (1, 1), style="green", expand=False)

    with Live(
        padding, console=console, refresh_per_second=12, vertical_overflow="visible"
    ) as live:
        async for chunk in groq_chat.astream(messages):
            response_text += chunk.content
            # Update the Markdown content incrementally
            markdown = Markdown(response_text, code_theme="monokai")
            padding = Padding(markdown, (1, 1), style="green", expand=False)
            live.update(padding)
            await asyncio.sleep(0)  # Yield control to the event loop

    return response_text
