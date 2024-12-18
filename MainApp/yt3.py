import os
import random
import streamlit as st
from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi
from groq import Groq

# Set your YouTube API Key here
YOUTUBE_API_KEY = 'AIzaSyBpL1TZTg9eDO5AW9mAsLBC3trhoF00NPk'

# Initialize Groq client
client = Groq(api_key='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')

# Function to search for the best YouTube video link
def search_best_youtube_video(topic):
    youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
    search_response = youtube.search().list(
        q=topic, part='snippet', type='video', maxResults=10
    ).execute()
    video_ids = [item['id']['videoId'] for item in search_response['items']]
    video_response = youtube.videos().list(
        id=','.join(video_ids), part='snippet,statistics'
    ).execute()

    best_video = sorted(
        video_response['items'],
        key=lambda x: int(x['statistics'].get('viewCount', 0)),
        reverse=True
    )[0]
    video_id = best_video['id']
    video_title = best_video['snippet']['title']
    video_link = f"https://www.youtube.com/watch?v={video_id}"
    return {"id": video_id, "title": video_title, "link": video_link}

# Function to fetch transcript and summarize using Groq
def get_video_summary(video_id):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        full_transcript = " ".join([entry['text'] for entry in transcript])

        # Summarize the transcript using Groq
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "system",
                    "content":"You are a guide for students who need to quickly understand the content of YouTube videos. \
            You should summarize the transcript in the best way possible, focusing on key topics and ideas. \
            The output should be a list with bullet points."
                },
                {
                    "role": "user",
                    "content": full_transcript
                }
            ],
            temperature=1,
            max_tokens=1024,
            top_p=1,
            stream=True,
            stop=None,
        )

        summary = ""
        for chunk in completion:
            summary += chunk.choices[0].delta.content or ""

        return full_transcript, summary
    except Exception as e:
        return "", f"Error fetching or summarizing transcript: {str(e)}"

# Function to generate logical and context-aware flashcards
def generate_flashcards(transcript, num_flashcards=5):
    sentences = transcript.split('. ')
    random.shuffle(sentences)
    unique_sentences = list(set(sentences))  # Remove duplicates

    flashcards = []
    for sentence in unique_sentences[:num_flashcards]:
        if len(sentence.split()) > 5:  # Ensure meaningful questions
            # Check if the sentence mentions a key concept or term
            if "is" in sentence:
                question = f"What is described as {sentence.split(' ')[0]}?"
                answer = sentence
            elif "are" in sentence:
                question = f"What are the key aspects of {sentence.split(' ')[0]}?"
                answer = sentence
            else:
                question = f"Can you explain {sentence.split(' ')[0]}?"
                answer = sentence
            flashcards.append({
                "question": question,
                "answer": answer
            })

    return flashcards

# Main Streamlit App
def main():
    st.title("AI Learning Bot with Flashcards")
    st.write("Learn topics through YouTube videos, summaries, and interactive flashcards!")

    # Session state for persistent data
    if "flashcards" not in st.session_state:
        st.session_state.flashcards = None
    if "full_transcript" not in st.session_state:
        st.session_state.full_transcript = None
    if "video_link" not in st.session_state:
        st.session_state.video_link = None
    if "current_flashcard_index" not in st.session_state:
        st.session_state.current_flashcard_index = 0
    if "video_summary" not in st.session_state:
        st.session_state.video_summary = None

    # Input for topic
    topic = st.text_input("Enter Topic:", "")

    # Fetch video on topic
    if topic and st.session_state.video_link is None:
        best_video = search_best_youtube_video(topic)
        st.session_state.video_link = best_video['link']
        st.session_state.video_id = best_video['id']
        st.session_state.full_transcript, _ = get_video_summary(best_video['id'])
        st.subheader("Best Video Link:")
        st.markdown(f"[Watch Video]({st.session_state.video_link})")

    # Buttons for actions
    flashcards_button = st.button("Generate Flashcards")
    summary_button = st.button("Generate Video Summary")

    # Generate Video Summary
    if summary_button and st.session_state.full_transcript:
        # Only generate and display the summary if it hasn't been generated before
        if not st.session_state.video_summary:
            _, summary = get_video_summary(st.session_state.video_id)
            st.session_state.video_summary = summary
            st.subheader("Video Summary:")
            st.write(st.session_state.video_summary)

    # Generate Flashcards
    # Generate Flashcards
    if flashcards_button and st.session_state.full_transcript:
        # Generate flashcards and reset the current index
        st.session_state.flashcards = generate_flashcards(st.session_state.full_transcript)
        st.session_state.current_flashcard_index = 0

        st.subheader("Interactive Flashcards")
        st.markdown(
            """
            <style>
                .flashcard-container {
                    display: grid;
                    grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
                    gap: 20px;
                    margin-top: 20px;
                }
                .flip-card {
                    background-color: transparent;
                    perspective: 1000px;
                    width: 100%;
                    height: 180px;
                }
                .flip-card-inner {
                    position: relative;
                    width: 100%;
                    height: 100%;
                    text-align: center;
                    transition: transform 0.6s;
                    transform-style: preserve-3d;
                }
                .flip-card:hover .flip-card-inner {
                    transform: rotateY(180deg);
                }
                .flip-card-front, .flip-card-back {
                    position: absolute;
                    width: 100%;
                    height: 100%;
                    backface-visibility: hidden;
                    border: 2px solid #ddd;
                    border-radius: 10px;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    font-size: 14px;
                    padding: 10px;
                }
                .flip-card-front {
                    background-color: #f9f9f9;
                    color: #333;
                }
                .flip-card-back {
                    background-color: #ffeebc;
                    color: #333;
                    transform: rotateY(180deg);
                }
            </style>
            """,
            unsafe_allow_html=True
        )

        # Display all flashcards
        st.markdown('<div class="flashcard-container">', unsafe_allow_html=True)
        for flashcard in st.session_state.flashcards:
            st.markdown(f"""
                <div class="flip-card">
                    <div class="flip-card-inner">
                        <div class="flip-card-front">
                            <strong>Q:</strong> {flashcard['question']}
                        </div>
                        <div class="flip-card-back">
                            <strong>A:</strong> {flashcard['answer']}
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)


if __name__ == "__main__":
    main()