import streamlit as st
import nltk
import  PyPDF2
from langchain_groq import ChatGroq
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains import create_retrieval_chain
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import os
from nltk.tokenize import sent_tokenize
from nltk.corpus import stopwords
from collections import OrderedDict

# Load environment variables

nltk.download('punkt_tab')
nltk.download('stopwords')

groq_api_key = "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"
os.environ["GOOGLE_API_KEY"] ="AIzaSyDzHd1NaXsn1xLyYFs3Pmn99QPYNkPImEY"


# Initialize the ChatGroq model
llm = ChatGroq(groq_api_key=groq_api_key, model_name="Llama3-8b-8192")

# Define the prompt template for automatic question-answer generation
qna_prompt = ChatPromptTemplate.from_template(
    """
    Generate a question based on the provided context, and provide its answer.
    <context>
    {context}
    <context>
    Question and Answer:
    """
)

# Vector embedding function
def vector_embedding():
    if "vectors" not in st.session_state:
        st.session_state.embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
        st.session_state.loader = PyPDFDirectoryLoader("./uploaded_pdfs")  # Data Ingestion
        st.session_state.docs = st.session_state.loader.load()  # Load documents
        st.session_state.text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)  # Chunk splitting
        st.session_state.final_documents = st.session_state.text_splitter.split_documents(st.session_state.docs[:20])  # First 20 docs
        st.session_state.vectors = FAISS.from_documents(st.session_state.final_documents, st.session_state.embeddings)  # Vector store

# CSS for card flip effect
card_flip_css = """
<style>
.card {
    width: 300px;
    height: 200px;
    perspective: 1000px;
    margin-bottom: 20px;
}
.card-inner {
    position: relative;
    width: 100%;
    height: 100%;
    transform-style: preserve-3d;
    transform: rotateY(0deg);
    transition: transform 0.6s;
}
.card:hover .card-inner {
    transform: rotateY(180deg);
}
.card-front, .card-back {
    position: absolute;
    width: 100%;
    height: 100%;
    backface-visibility: hidden;
}
.card-back {
    transform: rotateY(180deg);
}
.card-front {
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    font-size: 16px;
    background-color: #f8f9fa;
    color: #343a40;
    padding: 10px;
    text-align: center;
    border: 1px solid #ddd;
    border-radius: 8px;
}
.card-back {
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    font-size: 16px;
    background-color: #343a40;
    color: #f8f9fa;
    padding: 10px;
    text-align: center;
    border: 1px solid #ddd;
    border-radius: 8px;
    padding:15px;

}
</style>
"""

# HTML structure for card flip
def card_flip(question, answer):
    return f"""
    <div class="card">
        <div class="card-inner">
            <div class="card-front">
                <p>{question}</p>
            </div>
            <div class="card-back">
                <h3>Answer</h3>
                <p>{answer}</p>
            </div>
        </div>
    </div>
    """


def summarize_pdf(pdf_file):
    pdf = PyPDF2.PdfReader(pdf_file)
    summary = ""

    # Extract text from all pages of the PDF
    for page in range(len(pdf.pages)):
        page_obj = pdf.pages[page]
        text = page_obj.extract_text()
        summary += text

    return summary


# Summarize the content using NLTK to rank sentences and get top key points
def get_key_points(summary):
    stop_words = set(stopwords.words('english'))
    sentences = sent_tokenize(summary)
    rank = OrderedDict()

    for i, sent in enumerate(sentences):
        words = sent.split()
        ranked_words = [w for w in words if not w in stop_words]
        rank[i] = len(ranked_words)

    sorted_sentences = sorted(rank.items(), key=lambda x: x[1], reverse=True)
    top_sentences = [sentences[i[0]] for i in sorted_sentences[:5]]

    return " ".join(top_sentences)
# Main function
def main():
    st.markdown(card_flip_css, unsafe_allow_html=True)

    # File uploader for PDFs
    uploaded_files = st.file_uploader("Upload PDF files for flashcard generation", type="pdf",
                                      accept_multiple_files=True)
    if uploaded_files:
        st.write(f"You have uploaded {len(uploaded_files)} files.")

        # Save uploaded files locally
        os.makedirs("./uploaded_pdfs", exist_ok=True)
        for uploaded_file in uploaded_files:
            with open(f"./uploaded_pdfs/{uploaded_file.name}", "wb") as f:
                f.write(uploaded_file.read())

        if st.button("Get Key Points"):
            # Extract text from uploaded PDFs
            summary = ""
            for uploaded_file in uploaded_files:
                summary += summarize_pdf(uploaded_file)

            if summary.strip():
                st.write("Extracting key points...")

                # Summarize and extract key points
                key_points = get_key_points(summary)
                st.write("### Key Points:")
                st.write(key_points)

        # Vector store setup
        if st.button("Get Flash Cards"):
            vector_embedding()
            st.success("Vector store created. Flashcard generation ready!")

    # Flashcard generation
    if "vectors" in st.session_state:
        st.write("Generating flashcards...")
        document_chain = create_stuff_documents_chain(llm, qna_prompt)
        retriever = st.session_state.vectors.as_retriever()
        retrieval_chain = create_retrieval_chain(retriever, document_chain)

        # Generate flashcards
        # Generate flashcards
        for i, doc in enumerate(st.session_state.final_documents):
            st.write(f"### Flashcard {i + 1}")

            try:
                # Pass the correct input key
                response = retrieval_chain.invoke({'input': doc.page_content})

                # Verify response structure
                if response and "answer" in response:
                    qna_split = response['answer'].split("Question:", 1)
                    if len(qna_split) > 1:
                        qa_content = qna_split[1].split("Answer:", 1)
                        if len(qa_content) == 2:
                            question = qa_content[0].strip()
                            answer = qa_content[1].strip()
                        else:
                            question = "Question not generated correctly"
                            answer = "Answer not generated correctly"
                    else:
                        question = "No valid question found"
                        answer = "No valid answer found"
                else:
                    question = "Failed to generate question"
                    answer = "Failed to generate answer"

            except Exception as e:
                st.error(f"Error processing document {i + 1}: {e}")
                continue

            # Display flashcard
            with st.container():
                st.markdown(card_flip(question=question, answer=answer), unsafe_allow_html=True)


if __name__ == "__main__":
    main()

