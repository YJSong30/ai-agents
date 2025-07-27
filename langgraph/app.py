from typing import Annotated
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from dotenv import load_dotenv
from IPython.display import Image, display
import gradio as gr
from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from langchain_openai import ChatOpenAI
from pydantic import BaseModel
import random

print("Hello World")

class State(BaseModel):
  messages: Annotated[list, add_messages]
  # messages field should be processed with the 'add_messages' handler.
  # when graph runs, langgraph uses this annotation to automatically manage and update the messages list
  

graph_builder = StateGraph(State)

llm = ChatOpenAI(model="gpt-4o-mini")

def chatbot_node(old_state: State) -> State:
  response = llm.invoke(old_state.messages)
  new_state = State(messages = [response])
  return new_state
  
graph_builder.add_node("chatbot", chatbot_node)
graph_builder.add_edge(START, "chatbot")
graph_builder.add_edge("chatbot", END)

graph = graph_builder.compile()
with open("graph.png", "wb") as f:
  f.write(graph.get_graph().draw_mermaid_png())

# display(Image(graph.get_graph().draw_mermaid_png()))

def chat(user_input: str, history):
    initial_state = State(messages=[{"role": "user", "content": user_input}])
    result = graph.invoke(initial_state)
    print(result)
    return result['messages'][-1].content


gr.ChatInterface(chat, type="messages").launch()


