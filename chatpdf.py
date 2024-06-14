# -*- coding: utf-8 -*-
"""
Created on Mon Apr  1 20:15:15 2024

@author: chuhuivoon
"""

#%%
# Pre-requisite 

# pip install streamlit
# pip3 install streamlit-extras
# pip install htbuilder
# pip install python-dotenv

# To run the app use: streamlit run xxx.py
# To run the app while setting the base to dark use: streamlit run xxx.py --theme.base='dark' 

#%%
# Imports 

from htbuilder import HtmlElement, div, ul, li, br, hr, a, p, img, styles, classes, fonts
from htbuilder.units import percent, px
from htbuilder.funcs import rgba, rgb
from dotenv import load_dotenv
from typing import Optional


import logging
import sys
import time
import requests
import streamlit as st
import os
import tempfile

st.set_page_config(
    page_title=None,
    page_icon="favicon.ico",
    layout="wide",
    initial_sidebar_state="expanded"
)


log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
logging.basicConfig(format=log_format, stream=sys.stdout, level=logging.INFO)


BASE_API_URL = "http://127.0.0.1:7860/api/v1/process"
FLOW_ID = "91927e67-c4da-42a5-aa5a-1fb276e4be9f"

TWEAKS = {
  "ChatOpenAI-3GQoa": {},
  "CombineDocsChain-7vywi": {},
  "Chroma-xeR4E": {},
  "OpenAIEmbeddings-ggyc2": {},
  "Document-V63pg": {},
  "RetrievalQA-xV3cM": {},
  "PyPDFLoader-0ShX7": {}
}


load_dotenv()

def run_flow(inputs: dict, flow_id: str, tweaks: Optional[dict] = None) -> dict:
    api_url = f"{BASE_API_URL}/{flow_id}"
    payload = {"inputs": inputs}
    if tweaks:
        payload["tweaks"] = tweaks
    response = requests.post(api_url, json=payload)
    return response.json()

def generate_response(query, pdf_file_path):
    logging.info(f"input: {query}, pdf_file_path={pdf_file_path}")
    inputs = {"query": query, "pdf_file": pdf_file_path}

    response = run_flow(inputs, flow_id=FLOW_ID, tweaks=TWEAKS)
    
    try:
        result = response.get("result", {})
        if "result" in result:
            result_text = result["result"]
            logging.info(f"answer: {result_text}")
            return result_text
        else:
            logging.error(f"Unexpected response format: {response}")
            return "Sorry, there was a problem finding an answer for you."
    except Exception as exc:
        logging.error(f"error: {exc}")
        return "Sorry, there was a problem finding an answer for you."
    

with st.sidebar:
    st.title('🤗💬 MSF ChatBot')
    st.markdown('''
    ## Upload a PDF file.
    ''')

    # Upload a PDF file
    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

    pdf_file_path = None

    if uploaded_file:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            temp_file.write(uploaded_file.read())
            pdf_file_path = temp_file.name
        st.info("PDF file uploaded successfully!")
        TWEAKS["PyPDFLoader-0ShX7"]["pdf_file"] = pdf_file_path  ## add the parameters that are to be manipulated
    else:
        st.warning("Please upload a PDF file.")

# main chatbox
def main(): 
    
    st.header("Welcome to MSF Chatbot! 🤖")
    st.markdown(''' :rainbow[Chat Application powered by Langflow] 🚀''')
    st.markdown(" ##### You may ask me information on GenAI training programs 📚📖📝 ")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"], avatar=message["avatar"]):
            st.write(message["content"])

    if query := st.chat_input("You may start with what are the programs offered in MSF?"):
        st.session_state.messages.append(
            {
                "role": "user",
                "content": query,
                "avatar": "💬",  # Emoji representation for user
            }
        )
        with st.chat_message(
            "user",
            avatar="💬",  # Emoji representation for user
        ):
            st.write(query)

        with st.chat_message(
            "assistant",
            avatar="🤖",  # Emoji representation for assistant
        ):
            message_placeholder = st.empty()
            with st.spinner(text="Thinking..."):
                assistant_response = generate_response(query, pdf_file_path)
                message_placeholder.write(assistant_response)

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": assistant_response,
                "avatar": "🤖",  # Emoji representation for assistant
            }
        )

if __name__ == "__main__":
    main()  # main function execution
