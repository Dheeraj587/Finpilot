import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL","gemini-3.1-flash-lite")
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE",'0'))

def get_llm():
    """The single place where the LLM is created. Every node will call this."""
    if not GEMINI_API_KEY or GEMINI_API_KEY == "paste_your_key_here":
        raise RuntimeError("GOOGLE_API_KEY is missing. Add your key to the .env file.")

    from langchain_google_genai import ChatGoogleGenerativeAI

    return ChatGoogleGenerativeAI(
        model=GEMINI_MODEL,
        temperature=LLM_TEMPERATURE,
    )
