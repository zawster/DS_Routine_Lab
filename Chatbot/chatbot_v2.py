import os
import sys
import openai
import streamlit as st
from langchain_community.llms import OpenAI
from langchain_community.vectorstores import Chroma
from langchain.indexes import VectorstoreIndexCreator
from langchain_community.chat_models import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain
from langchain_community.embeddings import OpenAIEmbeddings
from langchain.indexes.vectorstore import VectorStoreIndexWrapper
from langchain_community.document_loaders import DirectoryLoader, TextLoader

import constants

# Setting my Openai API KEY
os.environ["OPENAI_API_KEY"] = constants.APIKEY

def save_uploaded_files(uploaded_files, temp_dir="temp_data"):
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)
    for uploaded_file in uploaded_files:
        file_path = os.path.join(temp_dir, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
    return temp_dir

st.title("Chatbot with Dynamic Data Upload")

# Sidebar for persistence or can be hardcoded as well.
PERSIST = st.sidebar.checkbox("Persist Index", value=False)

# File uploader for data files.
uploaded_files = st.file_uploader("Upload data files", type=["pdf", "txt", "docx"], accept_multiple_files=True)

# Initialize session state variables if they don't exist.
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "chain" not in st.session_state:
    st.session_state.chain = None
if "index" not in st.session_state:
    st.session_state.index = None


if uploaded_files and st.session_state.chain is None:
    # Save the files to a temp directory.
    data_dir = save_uploaded_files(uploaded_files)
    
    # generating embeddings
    with st.spinner('Initializing index and generating embeddings...'):
        loader = DirectoryLoader(data_dir)
        if PERSIST and os.path.exists("persist"): # Use existing embeddings
            st.info("Reusing index from persist directory...")
            vectorstore = Chroma(persist_directory="persist", embedding_function=OpenAIEmbeddings())
            st.session_state.index = VectorStoreIndexWrapper(vectorstore=vectorstore)
        else: # Generate new embeddings
            if PERSIST:
                st.session_state.index = VectorstoreIndexCreator(
                    vectorstore_kwargs={"persist_directory": "persist"}
                ).from_loaders([loader])
            else:
                st.session_state.index = VectorstoreIndexCreator(
                    embedding=OpenAIEmbeddings()
                ).from_loaders([loader])
    
        st.session_state.chain = ConversationalRetrievalChain.from_llm(
            llm=ChatOpenAI(model="gpt-4"),
            retriever=st.session_state.index.vectorstore.as_retriever(search_kwargs={"k": 5}),
        )
    st.success("Index and retrieval chain initialized!")
else:
    st.info("Index and Embeddings already exists.")

# Retrieving Answers
question = st.text_input("Enter your question:")

if st.button("Submit"):
    if not st.session_state.chain:
        st.error("The chatbot is not ready yet. Please upload files first.")
    elif question.strip() == "":
        st.error("Please enter a valid question.")
    else:
        with st.spinner("Generating answer..."):
            result = st.session_state.chain({"question": question, "chat_history": st.session_state.chat_history})
            answer = result.get("answer", "No answer returned.")
        st.write("**Answer:**")
        st.write(answer)
        st.session_state.chat_history.append((question, answer))