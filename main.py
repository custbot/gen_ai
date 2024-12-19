import asyncio
from react_agent.graph import graph
from langchain_core.messages import AIMessage, HumanMessage
from langchain.agents import initialize_agent, AgentType
from langchain.memory import ConversationBufferMemory


# Initialize memory
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)



async def main():
    print("Welcome to the DCS Agent Support, how can I help you today. Type 'exit' to quit.")

    while True:
        # Prompt the user for input
        user_input = input("You: ")
        if user_input.lower() == "exit":
            print("Goodbye!")
            break

        # Prepare the message in the format expected by the graph
        test_query = {"messages": [HumanMessage(content=user_input)]}

        # Invoke the graph to get the agent's response
        response = await graph.ainvoke(test_query)

        # Extract and print the final answer
        final_answer = next(
            (message.content for message in reversed(response["messages"]) 
             if isinstance(message, AIMessage) and message.content),
            "No final answer found."

        )
        print("Bot:", final_answer)

# Run the async main function
if __name__ == "__main__":
    asyncio.run(main())
