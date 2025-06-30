import json
from langchain.schema.messages import HumanMessage, AIMessage
from datetime import datetime

def save_chat_history_json(chat_history, file_path):
    with open(file_path, "w") as f:
        json_data = [message.dict() for message in chat_history]
        json.dump(json_data, f)

def load_chat_history_json(file_path):
    with open(file_path, "r") as f:
        json_data = json.load(f)
        messages = [HumanMessage(**message) if message["type"] == "human" else AIMessage(**message) for message in json_data]
        return messages

def get_timestamp():
    return datetime.now().strftime("%Y_%m_%d_%H_%M_%S")

















'''import json
from langchain.schema.messages import HumanMessage, AIMessage
from datetime import datetime
import os
import streamlit as st
import yaml

# Load configuration
with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

# Ensure chat history path exists
os.makedirs(config["chat_history_path"], exist_ok=True)

def save_chat_history_json(chat_history, file_path):
    """
    Saves the chat history into a JSON file.
    
    Args:
        chat_history (list): List of chat messages (HumanMessage, AIMessage).
        file_path (str): Path where the chat history will be saved.
    """
    try:
        with open(file_path, "w") as f:
            # Convert messages to dictionaries and save them as a JSON file
            json_data = [message.dict() for message in chat_history]
            json.dump(json_data, f, ensure_ascii=False, indent=4)
            print(f"Chat history saved to {file_path}")
    except Exception as e:
        print(f"Error saving chat history: {e}")

def load_chat_history_json(file_path):
    """
    Loads the chat history from a JSON file.
    
    Args:
        file_path (str): Path of the chat history file to load.
    
    Returns:
        list: List of messages (HumanMessage, AIMessage).
    """
    try:
        with open(file_path, "r") as f:
            json_data = json.load(f)
            messages = []
            for message in json_data:
                if message.get("type") == "human":
                    messages.append(HumanMessage(**message))
                else:
                    messages.append(AIMessage(**message))
            return messages
    except FileNotFoundError:
        print(f"File {file_path} not found. Starting a new session.")
        return []
    except Exception as e:
        print(f"Error loading chat history: {e}")
        return []

def get_timestamp():
    """
    Returns the current timestamp formatted as YYYY_MM_DD_HH_MM_SS.
    
    Returns:
        str: Current timestamp.
    """
    return datetime.now().strftime("%Y_%m_%d_%H_%M_%S")

def initialize_session():
    """
    Initializes the session state for chat history and session key.
    """
    if "history" not in st.session_state:
        st.session_state.history = []
    if "session_key" not in st.session_state:
        st.session_state.session_key = "new_session"

def save_chat_history():
    """
    Save the chat history to a file with a valid name.
    """
    try:
        if st.session_state.history:
            # Generate the file name based on the session key or timestamp
            if st.session_state.session_key == "new_session":
                # Assign a new unique session key for new sessions
                st.session_state.session_key = get_timestamp()

            # Construct the full file path
            file_name = st.session_state.session_key
            file_path = os.path.join(config["chat_history_path"], f"{file_name}.json")

            # Save chat history to file
            save_chat_history_json(st.session_state.history, file_path)
        else:
            print("No chat history to save.")
    except Exception as e:
        print(f"Error saving chat history: {e}")

def load_chat_history():
    """
    Loads the chat history for the current session.
    """
    try:
        if st.session_state.session_key and st.session_state.session_key != "new_session":
            file_path = os.path.join(config["chat_history_path"], f"{st.session_state.session_key}.json")
            st.session_state.history = load_chat_history_json(file_path)
        else:
            st.session_state.history = []
    except Exception as e:
        print(f"Error loading chat history: {e}")

# Initialize session state
initialize_session()
'''