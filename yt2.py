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

# Function to generate flashcards and logical questions
def generate_flashcards_and_questions(transcript, num_flashcards=5):
    flashcards = []
    questions = []
    sentences = transcript.split('. ')
    random.shuffle(sentences)
    unique_sentences = list(set(sentences))  # Remove duplicates

    for sentence in unique_sentences[:num_flashcards]:
        question = sentence.split(" ")[0:5]  # First 5 words as the question
        flashcards.append({
            "question": " ".join(question) + "...?",
            "answer": sentence
        })

        # Generate logical question based on the content
        if "process" in sentence or "steps" in sentence:
            question_text = f"What is the {sentence.split()[1]}?"
            questions.append({
                "question": question_text,
                "answer": sentence
            })
        elif "why" in sentence or "how" in sentence:
            question_text = f"Why is {sentence.split()[2]} important?"
            questions.append({
                "question": question_text,
                "answer": sentence
            })

    return flashcards, questions

# Main Streamlit App
def main():
    st.title("AI Learning Bot with Flashcards and Assessment")
    st.write("Learn topics through YouTube videos, summaries, and interactive flashcards!")

    # Session state for persistent data
    if "summary" not in st.session_state:
        st.session_state.summary = None
    if "flashcards" not in st.session_state:
        st.session_state.flashcards = None
    if "questions" not in st.session_state:
        st.session_state.questions = None
    if "full_transcript" not in st.session_state:
        st.session_state.full_transcript = None
    if "video_link" not in st.session_state:
        st.session_state.video_link = None
    if "current_flashcard_index" not in st.session_state:
        st.session_state.current_flashcard_index = 0

    # Input for topic
    topic = st.text_input("Enter Topic:", "")

    # Fetch video on topic
    if topic and st.session_state.video_link is None:
        best_video = search_best_youtube_video(topic)
        st.session_state.video_link = best_video["link"]
        st.session_state.full_transcript, st.session_state.summary = get_video_summary(best_video["id"])

    # Display video link
    if st.session_state.video_link:
        st.write(f"**Best Video Link:** {st.session_state.video_link}")

    # Display summary
    if st.session_state.summary:
        st.write("### Video Summary")
        st.write(st.session_state.summary)

    # Generate flashcards and questions
    if st.session_state.full_transcript:
        st.session_state.flashcards, st.session_state.questions = generate_flashcards_and_questions(st.session_state.full_transcript)

    # Display flashcards
    if st.session_state.flashcards:
        st.write("### Flashcards")
        for flashcard in st.session_state.flashcards:
            st.write(f"**Q:** {flashcard['question']}")
            st.write(f"**A:** {flashcard['answer']}")

    # Display questions
    if st.session_state.questions:
        st.write("### Logical Questions")
        for question in st.session_state.questions:
            st.write(f"**Q:** {question['question']}")
            st.write(f"**A:** {question['answer']}")

if __name__ == "__main__":
    main()