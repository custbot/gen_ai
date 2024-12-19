import chainlit as cl
from react_agent.graph import graph
from langchain_core.messages import AIMessage, HumanMessage
from langchain.memory import ConversationBufferWindowMemory

# Initialize memory
memory = ConversationBufferWindowMemory(k=10, memory_key="chat_history", return_messages=True)

# State variable to track which tool to use
action_context = {"active_action": None}

# Welcome message with action buttons
@cl.on_chat_start
async def start():
    """
    Send a welcome message with action buttons for common options.
    """
    actions = [
        cl.Action(name="search_contracts", value="search_contracts", description="Search for a specific contract."),
        cl.Action(name="summarize_contract", value="summarize_contract", description="Summarize a contract."),
        cl.Action(name="invoice_lookup", value="invoice_lookup", description="Get invoice details."),
    ]

    await cl.Message(
        content="Welcome to DCS Agent Support! How can I assist you today?",
        actions=actions,
    ).send()

# Handle specific actions triggered by buttons
@cl.action_callback("search_contracts")
async def search_contracts(action: cl.Action):
    action_context["active_action"] = "search_contracts"
    await cl.Message(content="Please enter the contract query you'd like to search.").send()

@cl.action_callback("summarize_contract")
async def summarize_contract(action: cl.Action):
    action_context["active_action"] = "summarize_contract"
    await cl.Message(content="Please provide the contract ID or details you'd like summarized.").send()

@cl.action_callback("invoice_lookup")
async def invoice_lookup(action: cl.Action):
    action_context["active_action"] = "invoice_lookup"
    await cl.Message(content="Please provide the customer name for invoice details.").send()




@cl.on_message
async def handle_message(message: cl.Message):
    """
    Handle user input and pass it through the graph for consistent processing.
    """
    # Extract the user input
    user_input = message.content

    # Store user input in memory
    memory.chat_memory.add_message(HumanMessage(content=user_input))

    # Modify test_query based on the active action context
    if action_context["active_action"] == "search_contracts":
        # Add a special instruction for contract search
        memory.chat_memory.add_message(HumanMessage(content="Use the contract lookup tool."))
    elif action_context["active_action"] == "invoice_lookup":
        # Add a special instruction for invoice search
        memory.chat_memory.add_message(HumanMessage(content="Use the invoice lookup tool."))
    elif action_context["active_action"] == "summarize_contract":
        # Add a special instruction for summarization
        memory.chat_memory.add_message(HumanMessage(content="Summarize the following contract."))

    # Prepare the query for the graph
    test_query = {"messages": memory.chat_memory.messages}

    # Pass the query through the graph
    graph_response = await graph.ainvoke(test_query)

    # Extract the final answer
    response = next(
        (msg.content for msg in reversed(graph_response["messages"]) if isinstance(msg, AIMessage) and msg.content),
        "No final answer found."
    )

    # Store agent's response in memory
    memory.chat_memory.add_message(AIMessage(content=response))

    # Send the response back to the user
    await cl.Message(content=response).send()

    # Reset the action context after handling the query
    action_context["active_action"] = None
