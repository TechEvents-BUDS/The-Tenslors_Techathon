import streamlit as st
import os
from langchain_groq import ChatGroq
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains import create_retrieval_chain
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import PyPDFLoader
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from dotenv import load_dotenv
import time
import tempfile

# Load environment variables from the .env file
load_dotenv()

# Load API keys from the environment
groq_api_key = os.getenv('GROQ_API_KEY')
google_api_key = os.getenv("GOOGLE_API_KEY")

# Validate API keys
if not groq_api_key or not google_api_key:
    st.error("API keys for GROQ and Google Generative AI are missing. Please check your .env file.")

# Set Google API key in environment (required by the library)
os.environ["GOOGLE_API_KEY"] = google_api_key

# Streamlit title
st.title("Document Q&A-Document embeddings for educational queries")
#add subtitle
st.subheader("Ask questions based on the uploaded PDF documents")
# Initialize the LLM
llm = ChatGroq(
    groq_api_key=groq_api_key,
    model_name="Llama3-8b-8192"
)

# Define the prompt template for Q&A
qa_prompt = ChatPromptTemplate.from_template(
    """
    Answer the questions based on the provided context only.
    Please provide the most accurate response based on the question.
    <context>
    {context}
    <context>
    Questions: {input}
    """
)

# Define a function to handle vector embeddings with uploaded PDFs
def vector_embedding(uploaded_files):
    if "vectors" not in st.session_state:
        st.session_state.embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

        # Load documents from uploaded files
        st.session_state.docs = []
        for uploaded_file in uploaded_files:
            # Create a temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
                temp_file.write(uploaded_file.read())
                temp_file_path = temp_file.name

            # Use PyPDFLoader to load the PDF from file path
            loader = PyPDFLoader(temp_file_path)
            st.session_state.docs.extend(loader.load())  # Add documents from each PDF

        st.session_state.text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)  # Chunk creation
        st.session_state.final_documents = st.session_state.text_splitter.split_documents(st.session_state.docs)  # Splitting
        st.session_state.vectors = FAISS.from_documents(st.session_state.final_documents, st.session_state.embeddings)  # Create vector embeddings

# File uploader for PDF files
uploaded_files = st.file_uploader("Upload PDF files", type=["pdf"], accept_multiple_files=True)

# Button to create document embeddings
if st.button("Create Document Embeddings"):
    if uploaded_files:
        vector_embedding(uploaded_files)
        st.write("Vector Store DB is ready.")
    else:
        st.error("Please upload at least one PDF file.")

# Option to ask questions
option = st.selectbox("Choose an option", ["Ask Questions"])

# Process the selected option
if option == "Ask Questions":
    prompt1 = st.text_input("Enter Your Question From Documents")
    if prompt1:
        if "vectors" not in st.session_state:
            st.error("Please create document embeddings first by uploading PDFs and clicking the 'Create Document Embeddings' button.")
        else:
            document_chain = create_stuff_documents_chain(llm, qa_prompt)
            retriever = st.session_state.vectors.as_retriever()
            retrieval_chain = create_retrieval_chain(retriever, document_chain)

            start_time = time.process_time()
            response = retrieval_chain.invoke({'input': prompt1, 'context': st.session_state.final_documents})
            response_time = time.process_time() - start_time

            st.write(f"Response time: {response_time:.2f} seconds")
            st.write(response['answer'])

            # Add download button for the answer
            st.download_button(
                label="Download Answer",
                data=response['answer'],
                file_name="answer.txt",
                mime="text/plain"
            )