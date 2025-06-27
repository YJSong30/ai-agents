'''
- create an AI Agent that will use tool calling to send a push notification to your phone whenever the user wants to connect
- create another agent that is an evaluator for the original llm

'''

from dotenv import load_dotenv
from openai import OpenAI
import json
import os
import requests
from pypdf import PdfReader
import gradio as gr
from models.evaluation import Evaluation

load_dotenv(override=True)

openai = OpenAI()
gemini = OpenAI(api_key=os.getenv('GOOGLE_API_KEY'), base_url='https://generativelanguage.googleapis.com/v1beta/openai/')

MODEL_NAME = {
"OPEN_AI": "gpt-4o-mini",
"GEMINI": "gemini-2.5-flash"
}


def push(text):
    requests.post(
        "https://api.pushover.net/1/messages.json",
        data={
            "token": os.getenv("PUSHOVER_TOKEN"),
            "user": os.getenv("PUSHOVER_USER"),
            "message": text,
        }
    )

# Tool 1: Record user data
def record_user_data(email, name):
    push(f"Someone named, {name}, with email, {email}, wants to get in touch with you")
    return {"recorded: ok"}

# Tool JSON
record_user_data_json = {
    "name": "record_user_data",
    "description": "Use this tool to record that a user is interested in being in touch and provided a name and an email address",
    "parameters": {
        "type": "object",
        "properties": {
            "email": {
                "type": "string",
                "description": "The email address of this user"
            },
            "name": {
                "type": "string",
                "description": "The user's name"
            }
        },
        "required": ["email", "name"]
    }
}

tools = [{"type": "function", "function": record_user_data_json}]

def handle_tool_call(tool_call):
    tool_name = tool_call.function.name
    arguments = json.loads(tool_call.function.arguments) # converts '{"email": "user@example.com", "name": "John"}' -> # {'email': 'user@example.com', 'name': 'John'}
    print(f"Tool call: {tool_name} with arguments: {arguments}")

    if tool_name == "record_user_data":
        return record_user_data(arguments.get("email"), arguments.get("name"))

# Evaluate llm response to make sure it's professional enough
def evaluate_llm_response(first_llm_response):
    system_prompt = f"You are an evaluation assistant. Evaluate the response and make sure it sounds professional. Make sure to include a score from 0 to 10. A professional response would be above a 7.0"
    test_messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Evaluate this response {first_llm_response}"}
    ]

    evaluator_response = gemini.beta.chat.completions.parse(model=MODEL_NAME["GEMINI"], messages=test_messages, response_format=Evaluation)
    evaluation = evaluator_response.choices[0].message.parsed

    return evaluation


# Create llm response
def create_llm_response(messages, attempts=0) -> str:
    if attempts >= 3:
        return "Max attempts reached. Evaluator tool determined AI response could not formulate an answer"

    # 1. Get AI response
    response = openai.chat.completions.create(model=MODEL_NAME["OPEN_AI"], messages=messages, tools=tools)
    response_content = response.choices[0].message.content

    if response_content:
        print("RESPONSE: " + response_content)
    else:
        print("RESPONSE: [No text content - tool call only]")
    
    # 2. Handle tool call
    if response.choices[0].message.tool_calls:
        # print("AI wants to use tools:", response.choices[0].message.tool_calls)
        tool_call = response.choices[0].message.tool_calls[0]
        # print("tool call: ", tool_call)
        handle_tool_call(tool_call)
        return "Thank you for your information, it has been recorded. I'll be in touch soon!"


    if response_content:
        # 4. Evaluate the response
        evaluation = evaluate_llm_response(response_content)
        print(f"DEBUG: Evaluation score: {evaluation.score}. Evaluation feedback: {evaluation.feedback}")

        # 5. If evaluate score is too low, rerun create_llm_response
        if evaluation.score < 4.0:
            return create_llm_response(messages, attempts + 1)  # Pass attempts

    return response_content

reader = PdfReader("me/resume.pdf")
resume = ""
for page in reader.pages:
    text = page.extract_text()
    if text:
        resume += text

with open("me/summary.txt", "r", encoding="utf-8") as f:
    summary = f.read()

name = "Young Song"

system_prompt = f"You are acting as {name}. You are answering questions on {name}'s website, \
particularly questions related to {name}'s career, background, skills and experience. \
Your responsibility is to represent {name} for interactions on the website as faithfully as possible. \
You are given a summary of {name}'s background which you can use to answer questions. \
Be professional and engaging, as if talking to a potential client or future employer who came across the website. \
If you don't know the answer to any question, try to answer it to the best of your abilities but also recommend them to reach out directly for more specific information. \
If the user is engaging in discussion, try to steer them towards getting in touch via email; ask for their name and email and record it using your record_user_details tool. "

system_prompt += f"\n\n## Summary:\n{summary}\n\n"
system_prompt += f"With this context, please chat with the user, always staying in character as {name}."


def chat(message, history):
    if "patent" in message:
        system = system_prompt + "\n\nEverything in your reply needs to be in pig latin - \
            it is mandatory that you respond only and entirely in pig latin"
    else:
        system = system_prompt

    messages = [
        {"role": "system", "content": system}
    ] + history + [{"role": "user", "content": message}]

    response = create_llm_response(messages)
    return response

if __name__ == "__main__":
    # test_messages = [
    #     {"role": "system", "content": "You are an assistant. When someone asks for your email, give them your email and use the record_user_data tool to log the interaction"},
    #     {"role": "user", "content": "what's your email address?"}
    #     ]
    # result = create_llm_response(test_messages)
    # print("Response content:", result)

    # # Add the AI's response to the conversation
    # test_messages.append({"role": "assistant", "content": result})
    
    # # User provides their name
    # test_messages.append({"role": "user", "content": "My name is John"})
    
    # # Get AI's response (should use the tool now)
    # result2 = create_llm_response(test_messages)
    # print("Second response:", result2)
    gr.ChatInterface(chat, type="messages").launch()

