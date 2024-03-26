import streamlit as st
from utils import display_credential_widget
import pathlib
import base64
import pandas as pd
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

# Display the sidebar
with st.sidebar:
    # Credential configs
    st.caption(body="Credential Configuration")
    display_credential_widget()

    # Model configs
    st.caption(body="Model Configuration")
    st.write("Model: Claude 3 Sonnet")  # [TODO] Model Selection

    # System prompt input area
    prompt_system = st.text_area(
        label="System Prompt",
        height=1,
        help="A system prompt is a way to provide context, instructions, and guidelines to Claude before presenting it with a question or task. Visit [official documentation](https://docs.anthropic.com/claude/docs/system-prompts) for more information.",
        )
    # Temperature config slider
    temperature = st.slider(
        label="Temperature",
        min_value=0.0,
        max_value=1.0,
        value=1.0,
        help="The amount of randomness injected into the response.",
        )
    # Max tokens config input area
    max_tokens = st.number_input(
        label="Max Output Tokens",
        min_value=1,
        max_value=4096,
        value=1024,
        help="The maximum number of tokens to generate before stopping. Visit [official document](https://docs.anthropic.com/claude/docs/models-overview) for more information.",
        )
    # Stop Sequences config input area
    stop_sequences = st.text_input(
        label="Stop Sequences",
        help="Custom text sequences that will cause the model to stop generating.",
        )
    # Image uploader
    uploaded_files = st.file_uploader(
        label="Upload file (Multiple files allowed)", 
        type=['jpg', 'jpeg', 'png',],
        accept_multiple_files=True,
        help="???",  # [TODO]
        )

    if uploaded_files is not None:
        rows = []
        row_index = 1
        for uploaded_file in uploaded_files:
            # Get MIME type of the image
            filename = uploaded_file.name
            if pathlib.Path(filename).suffix == ".jpg" or ".jpeg":
                mime_type = "image/jpeg"
            elif pathlib.Path(filename).suffix == ".png":
                mime_type = "image/png"

            # Use Base64 to encode the image
            bytes_data = uploaded_file.getvalue()
            base64_data = base64.b64encode(bytes_data).decode('utf-8')  # Base64 encoded image
            
            # Prepare DataFrame's row data
            rows.append({
                "is_widget": False,
                "name": f"Image {str(row_index)}",  # Name in Prompt, default: Image 1, Image 2, ..., etc.
                "mime_type": mime_type,  # MIME type
                "image_preview": f"data:image/generic;base64,{base64_data}",
                "image_base64": base64_data,})
            row_index += 1
    
    # Store image data rows
    df_files = pd.DataFrame(rows)
    st.session_state["df_files"] = df_files

    # Create editable DataFrame widget
    df_editor = st.data_editor(
        df_files,
        column_config={
            "_index": None,  # Hide index
            "is_widget": "Attach this Image",
            # "name": st.column_config.TextColumn('Name in Prompt', required=True),  # [FEATURE REQUEST] Editable image name notation
            "mime_type": None,  # Hide MIME type
            "image_preview": st.column_config.ImageColumn(
                "Preview Image", help="Streamlit app preview screenshots"
                ),
            "image_base64": None,  # Hide Base64 encoded image content
            },
        key="df_editor",
        )

# Prompt Interface
# Ref: https://docs.streamlit.io/knowledge-base/tutorials/build-conversational-apps#build-a-bot-that-mirrors-your-input
# Initialize chat history
st.caption(body="Prompt Interface")
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        # With media file, starts with
        # if message["content"][0]["type"] == "image": pass; elif message["content"][0]["text"] == "audio": pass;
        for content in message["content"]:
            if content["type"] == "text":
                st.markdown(content["text"])
            elif content["type"] == "image":
                st.image(f"data:image/generic;base64,{content['source']['data']}")

# React to user input
if prompt := st.chat_input("User Prompt"):
    message_user = {"role": "user", "content": []}

    with st.chat_message("user"):
        # Handle image part first (Claude models' preference)
        for key_row in st.session_state['df_editor']['edited_rows']:
            if st.session_state['df_editor']['edited_rows'][key_row]['is_widget']:  # If any image selected
                # Display the image name
                st.markdown(st.session_state['df_files']['name'][key_row])
                # Display the image
                st.image(st.session_state['df_files']['image_preview'][key_row])
                # Add contents to chat history
                message_user['content'].append({"type": "text", "text": st.session_state['df_files']['name'][key_row]})
                message_user['content'].append({"type": "image", "source": {
                    "type": "base64", 
                    "media_type": st.session_state['df_files']['mime_type'][key_row],
                    "data": st.session_state['df_files']['image_base64'][key_row],
                    }})

        # Display user message in chat message container
        st.markdown(prompt)
    message_user['content'].append({"type": "text", "text": prompt})
    # Add user message to chat history
    st.session_state.messages.append(message_user)

    df_files = pd.DataFrame(rows)
    st.session_state["df_files"] = df_files

    # Prepare Payload
    payload = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 1024,
        "temperature": temperature,
        "messages": [],
        }
    payload["messages"] += st.session_state.messages  ## Add all message history
    if stop_sequences:
         payload['stop_sequences'] = stop_sequences  ## Add Stop Sequences
    if prompt_system:
         payload['system'] = prompt_system  ## Add System Prompt

    # Invoke model
    # [TODO] Make it become a function
    bedrock_runtime = st.session_state["aws_session"].client("bedrock-runtime")
    result = None
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

        message_assistant = {"role": "assistant", "content": [{"type": "text", "text": output_text}]}
        # Add assistant response to chat history
        st.session_state.messages.append(message_assistant)
    except Exception as err:
        error_msg = f"Couldn't invoke Claude 3 Sonnet. Here's why: {err.response["Error"]["Code"]}: {err.response["Error"]["Message"]}"
        st.error(error_msg, icon="🚨",)
        print(error_msg)
        st.session_state.messages = []  # If error occurs, remove all messages from history
    
    # Debug information
    if st.query_params.get('debug') == "true":
        with st.expander("Debug Information", expanded=False):
            st.write("Request Payload")
            st.write(payload)
            st.divider()

            st.write("Response Payload")
            st.write(result)
            st.divider()

            st.write({
                "messages": st.session_state["messages"],
                })