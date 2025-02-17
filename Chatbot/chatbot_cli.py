import os
import sys
import openai
import streamlit as st
from langchain_community.llms import OpenAI
from langchain_community.vectorstores import Chroma
from langchain.indexes import VectorstoreIndexCreator
from langchain_community.chat_models import ChatOpenAI
from langchain_community.embeddings import OpenAIEmbeddings
from langchain.indexes.vectorstore import VectorStoreIndexWrapper
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain.chains import ConversationalRetrievalChain
import constants
# Openai Token
os.environ["OPENAI_API_KEY"] = constants.APIKEY
PERSIST = False
query = ""
if PERSIST and os.path.exists("persist"):
  print("Reusing index...\n")
  vectorstore = Chroma(persist_directory="persist", embedding_function=OpenAIEmbeddings())
  index = VectorStoreIndexWrapper(vectorstore=vectorstore)
else:
  loader = DirectoryLoader("data/")
  if PERSIST:
    index = VectorstoreIndexCreator(vectorstore_kwargs={"persist_directory":"persist"}).from_loaders([loader])
  else:
    index = VectorstoreIndexCreator(embedding=OpenAIEmbeddings()).from_loaders([loader])

# Making Retrival chain to retrieve context from Vectorstore
chain = ConversationalRetrievalChain.from_llm(
  llm=ChatOpenAI(model="gpt-4"),
  retriever=index.vectorstore.as_retriever(search_kwargs={"k": 5}),
)

chat_history = []
while True:
  if not query:
    query = input("Prompt: ")
  if query in ['quit', 'q', 'exit']:
    sys.exit()
  result = chain({"question": query, "chat_history": chat_history})
  print(result['answer'])

  chat_history.append((query, result['answer']))
  query = None



