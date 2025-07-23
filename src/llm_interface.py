import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def ask_gptOnce(prompt: str, model="gpt-3.5-turbo", temperature=0.7) -> tuple[str, int]: #gpt-4o
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=temperature,
        )
        answer = response.choices[0].message.content.strip()
        tokens_used = response.usage.total_tokens
        return answer, tokens_used
    except Exception as e:
        return f"Error: {str(e)}", 0
    
    load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def ask_gpt(messages: list[dict], model="gpt-3.5-turbo", temperature=0.7) -> tuple[str, int]:
    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
        )
        answer = response.choices[0].message.content.strip()
        tokens_used = response.usage.total_tokens
        return answer, tokens_used
    except Exception as e:
        return f"Error: {str(e)}", 0
