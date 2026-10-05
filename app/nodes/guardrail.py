import re
from app.state import financestate

MAX_MESSAGE_LENGTH =500

BULK_DESTRUCTIVE_PATTERNS =[
    r"\bdelete\s+(all|everything)\b",
    r"\bremove\s+(all|everything)\b",
    r"\bwipe\b",
    r"\bdrop\s+table\b",
    r"\btruncate\b",
    r"\berase\s+(all|everything)\b",
]

INJECTION_PATTERNS =[
    r"ignore\s+(all\s+)?(previous|prior|above)\s+instructions",
    r"disregard\s+(all\s+)?(previous|prior|above)",
    r"you\s+are\s+now\s+",
    r"reveal\s+(your\s+)?(system\s+)?prompt",
]

def _matches_any(text:str,patterns:list[str])->bool:
    return any(re.search(p,text,flags=re.IGNORECASE) for p in patterns)


def guardrail_node(state:financestate)->dict:
    message =state.user_message.strip()

    if not message:
        return{'is_safe':False,'block_reason':"Message is empty"}

    if len(message)>MAX_MESSAGE_LENGTH:
        return{
            "is_safe":False,
            'block_reason':f"Message is too long(max{MAX_MESSAGE_LENGTH} characters.)",
        }

    if _matches_any(message,BULK_DESTRUCTIVE_PATTERNS):
        return{
            'is_safe':False,
            'block_reason':"Bulk delete requests are not allowed. "
                            "Please delete specific entries one at a time.",
        
        }

    if _matches_any(message,INJECTION_PATTERNS):
        return{
            'is_safe':False,
            'block_reason':'this message looks like an attempt to override system instruction',
        }
    return {'is_safe':True,'block_reason':None}
