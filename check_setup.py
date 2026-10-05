from app.config import get_llm,GEMINI_MODEL

print(f"testing model:{GEMINI_MODEL}")
try:
    llm = get_llm()
    reply =llm.invoke("reply with exactly one word:ready")
    print('LLM replied:',reply.content)
    print('setup ok')
except Exception as e:
    print('setup failed',type(e).__name__)
    print(e)
    