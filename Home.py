import os
import json
import datetime
from OpenAI_API import openai_api
import streamlit as st
import ollama
from prompt_collection import SYSTEM_PROMPT
from vector_db import get_collections
from vector_db import query_vectordb
from vector_db import query_all_collections
from utils import extract_command
from action_call import action_selection 
from action_call import send_email_call
import uuid
from utils import extract_email_info
from utils import extract_command_from_natural_response


try:
    OLLAMA_MODELS = ollama.list()["models"]
except Exception as e:
    st.warning("Please make sure Ollama is installed first. See https://ollama.ai for more details.")
    st.stop()



def st_ollama(model_name, user_question, chat_history_key , document):

    
    if chat_history_key not in st.session_state.keys():
        st.session_state[chat_history_key] = []
        st.session_state[chat_history_key].append({ "role":"system" ,"content":f"{SYSTEM_PROMPT}"})
    
    
    print_chat_history_timeline(chat_history_key )
        
    # run the model
    if user_question:
        # command = extract_command(user_input=user_question)
        command = extract_command_from_natural_response(user_input=user_question)
        print("this is the command -->" , command)
        if command:
            email_body = action_selection(command=command , pervious_context=st.session_state[chat_history_key][-1]['content'] , user_input=user_question)
            subject, to, email_body  = extract_email_info(email_text=email_body)
            
        st.session_state[chat_history_key].append({ "role": "user" , "content": f"{user_question}",})
        with st.chat_message("user", avatar="👨🏻‍💻"):
            st.write(user_question)

        # messages = [dict(content=message["content"], role=message["role"]) for message in st.session_state[chat_history_key]]

        context =""
        if document and document !="All Documents":
            context  = query_vectordb(collection_name=document , query=user_question , top_k=2)
            
        elif document =="All Documents":
            context = query_all_collections(query=user_question)
        else:
            context = """No relevant context provided regarding question by the user.Notify the user about the lack of context.Politely refuse to answer."""
        
        
        messages = [dict(content=f"{message['content']}.CONTEXT:{context}", role=message["role"]) for message in st.session_state[chat_history_key]]
        
        if not command:    
            def llm_stream(response):
                if model_name !="OpenAI":
                    response = ollama.chat(model_name, messages, stream=True)
                if model_name == "OpenAI":
                    response = openai_api(messages=messages)
                if model_name != "OpenAI":
                    for chunk in response:
                        yield chunk['message']['content']
                if model_name == "OpenAI":
                    for chunk in response:
                        yield chunk 

        # streaming response
        if not command:
            with st.chat_message("response", avatar="🤖"):
                chat_box = st.empty()
                response_message = chat_box.write_stream(llm_stream(messages))

            st.session_state[chat_history_key].append({"role": "assistant", "content": f"{response_message}" ,})
            
            return response_message
        else:
            button = st.sidebar.button("Send Email" ,type="primary" , on_click=send_email_call(email_address=to,
                                    email_content=email_body , email_subject=subject ))
         
            with st.chat_message("email" , avatar="📝"):
                chat_box = st.empty()
                response_message = chat_box.write(email_body)

            st.session_state[chat_history_key].append({"role": "assistant", "content": f"{email_body}"})
            return response_message



def print_chat_history_timeline(chat_history_key):
    for message in st.session_state[chat_history_key]:
        role = message["role"]
        if role == "user":
            with st.chat_message("user", avatar="👨🏻‍💻"): 
                question = message["content"]
                st.markdown(f"{question}", unsafe_allow_html=True)
        elif role == "assistant":
            with st.chat_message("assistant", avatar="🤖"):
                st.markdown(message["content"], unsafe_allow_html=True)


def assert_models_installed():
    if len(OLLAMA_MODELS) < 1:
        st.sidebar.warning("No models found. Please install at least one model e.g. `ollama run llama2`")
        st.stop()


def select_model():
    
    model_names = [model["name"] for model in OLLAMA_MODELS]
    

    llm_name = st.sidebar.selectbox(f"Choose Agent (available {len(model_names)+1})", [""] + model_names+ ["OpenAI"])
    

    return llm_name


def save_conversation(llm_name, conversation_key):

    OUTPUT_DIR = "llm_conversations"
    OUTPUT_DIR = os.path.join(os.getcwd(), OUTPUT_DIR)

    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"{OUTPUT_DIR}/{timestamp}_{llm_name.replace(':', '-')}"

    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    if st.session_state[conversation_key]:

        if st.sidebar.button("Save conversation"):
            with open(f"{filename}.json", "w") as f:
                json.dump(st.session_state[conversation_key], f, indent=4)
            st.success(f"Conversation saved to {filename}.json")


if __name__ == "__main__":

    st.set_page_config(layout="wide", page_title="OREL BUDDY - Demo", page_icon="🔴")
    
    with st.sidebar:
        st.image("/home/shamal/orel_buddy/351756950_814811153592060_760347522500670021_n.png", width=75)
        
    

    
    collection_list = get_collections()
    document = ""
    if collection_list:
        document = st.sidebar.selectbox(f"Choose Documents(available {len(collection_list)})", ["","All Documents"] + collection_list)

        
    

    st.title("OREL BUDDY")
    llm_name = select_model()
    
    assert_models_installed()
    
    if not llm_name: st.stop()

    conversation_key = f"model_{llm_name}"
    context_chain_key = f"model_{llm_name}_context_chain"
    prompt = st.chat_input(f"Ask a question ...")
    
    st_ollama(llm_name, prompt, conversation_key ,document)
    

    if st.session_state[conversation_key]:
        clear_conversation = st.sidebar.button("Clear chat")
        if clear_conversation:
            st.session_state[conversation_key] = []
            st.rerun()

    # save conversation to file
    save_conversation(llm_name, conversation_key)