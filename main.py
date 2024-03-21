import streamlit as st
from utils import display_credential_widget
import json

# Page config should be placed at the top of the app
st.set_page_config(
    page_title='Amazon Bedrock Playground',
    page_icon=":speech_balloon:",
    layout="wide",
    initial_sidebar_state="auto",
    menu_items=None,
    )

# App Inrerface
st.title(body="Amazon Bedrock Playground")
st.subheader(body="Claude 3 Sonnet")

# Display the sidebar
with st.sidebar:
    display_credential_widget()
    st.caption(body="Model Configuration")
    prompt_system = st.text_area(
        label="System Prompt",
        height=1,
        help="A system prompt is a way to provide context, instructions, and guidelines to Claude before presenting it with a question or task. Visit [official documentation](https://docs.anthropic.com/claude/docs/system-prompts) for more information.",
        )
    temperature = st.slider(
        label="Temperature",
        min_value=0.0,
        max_value=1.0,
        value=1.0,
        help="The amount of randomness injected into the response.")
    max_tokens = st.number_input(
        label="Max Output Tokens",
        min_value=1,
        max_value=4096,
        value=1024,
        help="The maximum number of tokens to generate before stopping. Visit [official document](https://docs.anthropic.com/claude/docs/models-overview) for more information.")
    stop_sequences = st.text_input(
        label="Stop Sequences",
        help="Custom text sequences that will cause the model to stop generating.",
    )

# Prompt Interface
# Ref: https://docs.streamlit.io/knowledge-base/tutorials/build-conversational-apps#build-a-bot-that-mirrors-your-input
# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):  # [TODO] With media file?
        st.markdown(message["content"][0]["text"])

# React to user input
if prompt := st.chat_input("User Prompt"):
    # Display user message in chat message container
    st.chat_message("user").markdown(prompt)
    # Add user message to chat history
    message_user = {"role": "user", "content": [{"type": "text", "text": prompt}]}
    st.session_state.messages.append(message_user)
    payload = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 1024,
        "temperature": temperature,
        }
    payload["messages"] = st.session_state.messages
    if stop_sequences:
         payload['stop_sequences'] = stop_sequences
    if prompt_system:
         payload['system'] = prompt_system
    # Invoke model
    bedrock_runtime = st.session_state["aws_session"].client("bedrock-runtime")
    try:
        response = bedrock_runtime.invoke_model(
            modelId="anthropic.claude-3-sonnet-20240229-v1:0",
            body=json.dumps(payload),
        )
        result = json.loads(response.get("body").read())
        output_list = result.get("content", [])
        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            for output in output_list:
                output_text = output["text"]
                st.markdown(output_text)
        # Add assistant response to chat history
        message_assistant = {"role": "assistant", "content": [{"type": "text", "text": output_text}]}
        st.session_state.messages.append(message_assistant)
    except Exception as err:
        print(
                "Couldn't invoke Claude 3 Sonnet. Here's why: %s: %s",
                err.response["Error"]["Code"],
                err.response["Error"]["Message"],
            )
        



    if st.query_params.get('debug') == "true":
        with st.expander("Debug Information", expanded=False):
            st.write("Request Payload")
            st.write(payload)
            st.divider()
            st.write({
                "messages": st.session_state["messages"],
            })