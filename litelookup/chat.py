import asyncio
import logging

from langchain.chains.conversation.memory import ConversationBufferWindowMemory
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory

from litelookup.config.config import load_api_key, load_model
from .config.directory import history_file
from .format import chat_bottom_toolbar, print_formatted_response
from .log.logging_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)

GROQ_MODEL = load_model()
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
    groq_chat = ChatGroq(groq_api_key=GROQ_API_KEY, model_name=GROQ_MODEL)
    memory = ConversationBufferWindowMemory(
        k=5, memory_key="chat_history", return_messages=True
    )
    session_timeout = 3600  # 1 hour in seconds

    while True:
        try:
            user_question = await asyncio.wait_for(
                session.prompt_async(">> ", bottom_toolbar=chat_bottom_toolbar),
                timeout=session_timeout,
            )
            if user_question and user_question.lower() == "q":
                break

            if not user_question:
                continue

            messages = [SystemMessage(content=SYSTEM_PROMPT)]

            # Get chat history from memory
            chat_history = memory.load_memory_variables({}).get("chat_history", [])
            if chat_history:
                messages.extend(chat_history)

            # Add current message
            messages.append(HumanMessage(content=user_question))

            response = await groq_chat.agenerate([messages])
            response_text = response.generations[0][0].text

            # Store the interaction in memory
            memory.save_context({"input": user_question}, {"output": response_text})

            print_formatted_response(response_text)
        except (KeyboardInterrupt, EOFError):
            break
        except asyncio.TimeoutError:
            logger.info("Session timed out due to inactivity")
            break
        except Exception as e:
            logger.error(f"Error: {str(e)}")
            print("An error occurred. Please try again.")

    return False
