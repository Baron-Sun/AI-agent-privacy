import streamlit as st
import re

from langchain.agents import create_tool_calling_agent
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from src.build_agent.custom_tool import request_url,run_java_program,html_to_text
from src.build_agent.custom_tool import summarize_tool,identify_tool,categorize_tool
from langchain import hub
agent_prompt = hub.pull("hwchase17/openai-functions-agent")

llm = ChatOpenAI(model="gpt-4o-2024-08-06",
                 temperature=0,
                 api_key="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")


def extract_url(text):
    url_pattern = r'(https?://[^\s]+)'
    match = re.search(url_pattern, text)
    if match:
        return match.group(0)
    else:
        return False

class agent_:
    def __init__(self,url):
        self.url = url
        request_url(extract_url(self.url))
        run_java_program()
        agent_prompt.messages[0].prompt.template = f"""
        You are an assistant specialized in helping users analyze website’s privacy policy.
        Here is the privacy policy provided: {html_to_text()} \n
        You have the following tool-calling abilities:
        1. Use the `categorize_tool` to help the user categorize policies within a URL. The specific categories are explained further below.
        2. Use the `identify_tool` to help the user identify Opt-out Options (which means that website privacy policies sometimes provide users the option to opt-out of certain collections and uses of their personal data).
        3. Use the `summarize_tool` to help the user summarize the number of each policy category and the number of policies containing Opt-out Options within a URL.

        There is an annotation scheme consisting of ten data practice categories with its explanation:
        ...

        As an assistant, you need to fulfill the following requirements:
        a. When the user provides you with a URL, you need to summarize the content within the URL for the user.
        b. Guide the user to understand the policy content and use the appropriate tools to answer the user's questions.
        c. Only when it is necessary to summarize, categorize policies, or identify Opt-out Options, tools should be called. At all other times, please answer the user's questions based on your preset content."""

        tools = [summarize_tool, identify_tool, categorize_tool]
        agent = create_tool_calling_agent(llm, tools, agent_prompt)
        self.agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
        message_history = ChatMessageHistory()
        self.agent_with_chat_history = RunnableWithMessageHistory(
            self.agent_executor,
            lambda session_id: message_history,
            input_messages_key="input",
            history_messages_key="chat_history",
        )

    def invoke(self,query):
        response = self.agent_with_chat_history.invoke(
            {"input": query},
            # This is needed because in most real world scenarios, a session id is needed
            # It isn't really used here because we are using a simple in memory ChatMessageHistory
            config={"configurable": {"session_id": "<foo>"}},
        )
        return response['output']


def main():
    st.title("Privacy Policy Analysis Agent")

    # Initialize session state for agent, messages, and initialization status if not already done
    if 'agent' not in st.session_state:
        st.session_state.agent = None
        st.session_state.messages = []
        st.session_state.initialized = False

    # Input for URL
    url = st.text_input("Hello, I’m your usable privacy policy assistant. I’m here to help you quickly understand the content of this privacy policy, please enter the URL of the Privacy Policy:")

    if url:
        if not st.session_state.initialized:
            st.session_state.agent = agent_(url)
            st.session_state.initialized = True
            # Perform initial invoke to summarize content
            initial_summary = st.session_state.agent.invoke(f"Please summarize this url:{url}")
            st.session_state.messages.append({"role": "assistant", "content": initial_summary})

    # Show conversation history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    # Chat input for user query
    prompt = st.chat_input("Ask a question about the privacy policy:")

    if prompt:
        # Display the user's message immediately
        st.session_state.messages.append({"role": "user", "content": prompt})
        # Show a spinner while processing the request
        with st.spinner("Processing your request..."):
            # Call the agent and get the response
            response = st.session_state.agent.invoke(prompt)
            # Update the session state with the agent's response
            st.session_state.messages.append({"role": "assistant", "content": response})

        # Re-render the chat messages
        st.experimental_rerun()  # Refresh to show the new messages


if __name__ == "__main__":
    main()