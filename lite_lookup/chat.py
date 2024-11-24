import asyncio
import time
import logging

from langchain.chains import LLMChain
from langchain_core.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
)
from langchain_core.messages import SystemMessage
from langchain.chains.conversation.memory import ConversationBufferWindowMemory
from langchain_groq import ChatGroq
from prompt_toolkit import PromptSession
from prompt_toolkit.patch_stdout import patch_stdout
from prompt_toolkit.history import FileHistory

from config.config import load_api_key
from .format import print_formatted_response, chat_bottom_toolbar
from log.logging_config import setup_logging

from config.directory import history_file


setup_logging()
logger = logging.getLogger(__name__)

GROQ_API_KEY = load_api_key()

SYSTEM_PROMPT = """
You are a friendly, helpful, and knowledgeable conversational assistant. Your goal is to provide clear, concise, and accessible information while maintaining a conversational tone. Follow these guidelines:

1. Offer direct answers to questions without unnecessary preamble.
2. Use simple language and explain complex terms when they're unavoidable.
3. Structure your responses with short paragraphs or bullet points for readability.
4. Provide examples or analogies to illustrate complex concepts when appropriate.
5. Be concise, but offer to elaborate if the topic might benefit from more detail.
6. When discussing technical topics, include brief code snippets or step-by-step instructions if relevant.
7. Always maintain a friendly and patient demeanor, especially when clarifying or rephrasing information.
8. If you're unsure about something, be honest about your limitations and suggest where the user might find more accurate information.
9. Encourage follow-up questions to ensure the user fully understands the topic.

Remember, your aim is to make information as accessible as possible while engaging in a natural, helpful conversation."""


async def start_conversation_session():
    session = PromptSession(history=FileHistory(str(history_file)))

    model = "llama3-8b-8192"

    groq_chat = ChatGroq(groq_api_key=GROQ_API_KEY, model_name=model)

    system_prompt = SYSTEM_PROMPT
    conversational_memory_length = 5

    memory = ConversationBufferWindowMemory(
        k=conversational_memory_length, memory_key="chat_history", return_messages=True
    )
    session_interactive = True
    session_timeout = 3600  # 1 hour in seconds

    while session_interactive:

        try:
            with patch_stdout():
                user_question = await asyncio.wait_for(
                    session.prompt_async(">> ", bottom_toolbar=chat_bottom_toolbar),
                    timeout=session_timeout,
                )
        except (KeyboardInterrupt, EOFError):
            break
        except asyncio.TimeoutError:
            logger.info("Session timed out due to inactivity")
            break

        if user_question and user_question == "q":
            break
        else:
            prompt = ChatPromptTemplate.from_messages(
                [
                    SystemMessage(content=system_prompt),
                    MessagesPlaceholder(variable_name="chat_history"),
                    HumanMessagePromptTemplate.from_template("{human_input}"),
                ]
            )

            conversation = LLMChain(
                llm=groq_chat,
                prompt=prompt,
                verbose=False,
                memory=memory,
            )

            response = conversation.predict(human_input=user_question)
            print_formatted_response(response)
