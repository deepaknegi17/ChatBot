import streamlit as st
from llm_chains import load_normal_chain, load_pdf_chat_chain
from langchain.memory import StreamlitChatMessageHistory
from streamlit_mic_recorder import mic_recorder
from utils import save_chat_history_json, get_timestamp, load_chat_history_json
from image_handler import handle_image
from audio_handler import transcribe_audio
from pdf_handler import add_documents_to_db
from html_templates import get_bot_template, get_user_template, css
import yaml
import os
from pathlib import Path  # For consistent path handling

# Load configuration
with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

# Ensure chat history path exists
os.makedirs(config["chat_history_path"], exist_ok=True)

# Load the appropriate chain based on session state
def load_chain(chat_history):
    if st.session_state.pdf_chat:
        print("Loading PDF chat chain")
        return load_pdf_chat_chain(chat_history)
    return load_normal_chain(chat_history)

# Utility functions
def clear_input_field():
    if st.session_state.user_question == "":
        st.session_state.user_question = st.session_state.user_input
        st.session_state.user_input = ""

def set_send_input():
    st.session_state.send_input = True
    clear_input_field()

def toggle_pdf_chat():
    st.session_state.pdf_chat = True

def save_chat_history():
    if st.session_state.history:
        file_name = (
            st.session_state.new_session_key
            if st.session_state.session_key == "new_session"
            else st.session_state.session_key
        )
        
        # Debugging print
        print(f"Saving chat history to session: {file_name}")
        
        # Ensure config["chat_history_path"] is valid
        chat_history_path = config.get("chat_history_path", "./chat_sessions")
        print(f"chat_history_path: {chat_history_path}")
        
        # Construct file path
        file_path = os.path.join(chat_history_path, f"{file_name}.json")
        
        # Debugging print
        print(f"Full file path: {file_path}")
        
        save_chat_history_json(st.session_state.history, file_path)


def load_chat_session(file_path):
    if Path(file_path).exists():
        return load_chat_history_json(file_path)
    elif "new_session" not in file_path:  # Suppress warning for "new_session"
        st.info(f"No previous chat history found for '{file_path}'. Starting a new session.")
    return []

# Main function
def main():
    st.title("Multimodal Local Chat App")
    st.write(css, unsafe_allow_html=True)

    # Sidebar configuration
    st.sidebar.title("Chat Sessions")
    chat_sessions = ["new_session"] + os.listdir(config["chat_history_path"])

    # Initialize session state variables
    if "send_input" not in st.session_state:
        st.session_state.session_key = "new_session"
        st.session_state.send_input = False
        st.session_state.user_question = ""
        st.session_state.new_session_key = None
        st.session_state.session_index_tracker = "new_session"
    if st.session_state.session_key == "new_session" and st.session_state.new_session_key:
        st.session_state.session_index_tracker = st.session_state.new_session_key
        st.session_state.new_session_key = None

    index = chat_sessions.index(st.session_state.session_index_tracker)
    st.sidebar.selectbox(
        "Select a chat session", chat_sessions, key="session_key", index=index
    )
    st.sidebar.toggle("PDF Chat", key="pdf_chat", value=False)

    # Load chat history
    if st.session_state.session_key == "new_session":
        st.session_state.history = []
    else:
        session_file = os.path.join(config["chat_history_path"], st.session_state.session_key)
        st.session_state.history = load_chat_session(session_file)

    # Initialize chat history object
    chat_history = StreamlitChatMessageHistory(key="history")

    # Input section
    user_input = st.text_input(
        "Type your message here", key="user_input", on_change=set_send_input
    )
    voice_recording_column, send_button_column = st.columns(2)
    chat_container = st.container()
    with voice_recording_column:
        voice_recording = mic_recorder(
            start_prompt="Start recording", stop_prompt="Stop recording", just_once=True
        )
    with send_button_column:
        send_button = st.button("Send", key="send_button", on_click=clear_input_field)

    # File uploaders
    uploaded_audio = st.sidebar.file_uploader("Upload an audio file", type=["wav", "mp3", "ogg"])
    uploaded_image = st.sidebar.file_uploader("Upload an image file", type=["jpg", "jpeg", "png"])
    uploaded_pdf = st.sidebar.file_uploader("Upload a PDF file",accept_multiple_files=True,key="pdf_upload", type=["pdf"],on_change=toggle_pdf_chat,)

    # Process uploaded PDFs
    if uploaded_pdf:
        with st.spinner("Processing PDF..."):
            add_documents_to_db(uploaded_pdf)

    # Handle uploaded audio
    if uploaded_audio:
        transcribed_audio = transcribe_audio(uploaded_audio.getvalue())
        print(transcribed_audio)
        llm_chain = load_chain(chat_history)
        llm_chain.run("Summarize this text: " + transcribed_audio)

    # Handle voice recordings
    if voice_recording:
        transcribed_audio = transcribe_audio(voice_recording["bytes"])
        print(transcribed_audio)
        llm_chain = load_chain(chat_history)
        llm_chain.run(transcribed_audio)

    # Handle user input
    if send_button or st.session_state.send_input:
        if uploaded_image:
            with st.spinner("Processing image..."):
                user_message = "Describe this image in detail please."
                if st.session_state.user_question:
                    user_message = st.session_state.user_question
                    st.session_state.user_question = ""
                llm_answer = handle_image(uploaded_image.getvalue(), user_message)
                chat_history.add_user_message(user_message)
                chat_history.add_ai_message(llm_answer)

        if st.session_state.user_question:
            llm_chain = load_chain(chat_history)
            llm_response = llm_chain.run(st.session_state.user_question)
            st.session_state.user_question = ""

        st.session_state.send_input = False

    # Display chat history
    if chat_history.messages:
        with chat_container:
            st.write("Chat History:")
            for message in reversed(chat_history.messages):
                if message.type == "human":
                    st.write(get_user_template(message.content), unsafe_allow_html=True)
                else:
                    st.write(get_bot_template(message.content), unsafe_allow_html=True)

    # Save chat history
    save_chat_history()

if __name__ == "__main__":
    main()

