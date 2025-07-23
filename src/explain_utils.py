def build_prompt(question: str, tone: str = "simple") -> str:
    tones = {
        "simple": "Explain this in plain English for someone new to machine learning:",
        "technical": "Explain this using technical language suitable for a ML engineer:",
        "analogy": "Explain this using a real-world analogy:",
    }
    prefix = tones.get(tone, tones["simple"])
    return f"{prefix}\n\nQuestion: {question}\n\nAnswer:"

def build_system_prompt(tone: str = "simple",  length: str = "normal") -> str:
    tones = {
        "simple": "You explain ML concepts in plain English for someone new to machine learning.",
        "technical": "You are a technical assistant for ML engineers who explains concepts in a precise and detailed way.",
        "analogy": "You explain ML concepts using real-world analogies that are easy to relate to.",
    }
    
    if length == "short":
        length_instruction = " Keep the answer concise, under 100 words or 4 bullet points maximum."
    else:
        length_instruction = " Provide a full, thorough explanation with examples where relevant."

    return tones.get(tone, tones["simple"]) + length_instruction
