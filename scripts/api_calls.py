import os
from openai import OpenAI
from spacy.lang.am.examples import sentences

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY", "<The_key>"))

def get_gpt4o_response(prompt: str) -> str:
    """
    sends a prompt to the GPT model and retrieves the response.
    Args:
        prompt (str): The input prompt to send to GPT-4o.
    Returns:
        str: The response from GPT 4o.
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0,
            max_tokens=1000,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"An error occurred: {str(e)}"

if __name__ == "__main__":
    user_prompt = input("Enter your prompt: ")
    print("Fetching response from GPT-4o...")
    response = get_gpt4o_response(user_prompt)
    print("\nGPT-4o Response:")
    sentences = response.split(".")
    formatted = "\n".join(sentence.strip() + "." for sentence in sentences if sentence.strip())
    print(formatted)