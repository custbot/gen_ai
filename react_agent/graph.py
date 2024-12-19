
"""Define a custom Reasoning and Action agent.

Works with a chat model with tool-calling support.
"""

from datetime import datetime, timezone
from typing import Dict, List, Literal, cast

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableConfig
from langgraph.graph import START, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_openai import ChatOpenAI 
from dotenv import load_dotenv
import os

# Load environment variables (e.g., API keys)
load_dotenv()

# Import other modules
from react_agent.configuration import Configuration
from react_agent.state import InputState, State
from react_agent.tools import TOOLS
from react_agent.utils import load_chat_model

# Initialize the language model
model = ChatOpenAI(model_name="gpt-3.5-turbo", openai_api_key=os.getenv("OPENAI_API_KEY"))

# Function to call the model
async def call_model(state: State, config: RunnableConfig) -> Dict[str, List[AIMessage]]:
    """Call the LLM powering our "agent"."""
    configuration = Configuration.from_runnable_config(config)

    # Define the prompt template
    prompt = ChatPromptTemplate.from_messages(
        [("system", configuration.system_prompt), ("placeholder", "{messages}")]
    )

    # Bind tools to the model
    model = load_chat_model(configuration.model).bind_tools(TOOLS)

    # Prepare the input for the model
    message_value = await prompt.ainvoke(
        {
            "messages": state.messages,
            "system_time": datetime.now(tz=timezone.utc).isoformat(),
        },
        config,
    )

    # Get the model's response
    response = cast(AIMessage, await model.ainvoke(message_value, config))

    # Handle the case when the model wants to call a tool at the last step
    if state.is_last_step and response.tool_calls:
        return {
            "messages": [
                AIMessage(
                    id=response.id,
                    content="Sorry, I could not find an answer to your question in the specified number of steps.",
                )
            ]
        }

    # Return the model's response
    return {"messages": [response]}


# Define a new graph
workflow = StateGraph(State, input=InputState, config_schema=Configuration)

# Define the two nodes we will cycle between
workflow.add_node(call_model)
workflow.add_node("tools", ToolNode(TOOLS))

# Set the entry point as call_model
workflow.add_edge("__start__", "call_model")

# Define routing logic
def route_model_output(state: State) -> Literal["__end__", "tools"]:
    """Route the next step based on the model's output."""
    last_message = state.messages[-1]
    if not isinstance(last_message, AIMessage):
        raise ValueError(
            f"Expected AIMessage in output edges, but got {type(last_message).__name__}"
        )
    return "__end__" if not last_message.tool_calls else "tools"

# Add conditional edges for routing
workflow.add_conditional_edges("call_model", route_model_output)
workflow.add_edge("tools", "call_model")

# Compile the graph
graph = workflow.compile(interrupt_before=[], interrupt_after=[])
graph.name = "ReAct Agent"  # Optional: Customize the name in LangSmith

graph.verbose = True
