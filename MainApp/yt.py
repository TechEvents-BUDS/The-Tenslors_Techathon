import os
import streamlit as st
from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi
from groq import Groq

# Set your YouTube API Key here
YOUTUBE_API_KEY = 'AIzaSyBpL1TZTg9eDO5AW9mAsLBC3trhoF00NPk'

# Initialize Groq client
client = Groq(api_key='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'
)


# Function to search for the best YouTube video link based on views and relevance
def search_best_youtube_video(topic):
    youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)

    # Search for videos matching the topic
    search_response = youtube.search().list(
        q=topic,
        part='snippet',
        type='video',
        maxResults=10  # Fetch top 10 relevant videos
    ).execute()

    # Extract video IDs and get video details
    video_ids = [item['id']['videoId'] for item in search_response['items']]
    video_response = youtube.videos().list(
        id=','.join(video_ids),
        part='snippet,statistics'
    ).execute()

    # Sort videos by views
    best_video = sorted(
        video_response['items'],
        key=lambda x: int(x['statistics'].get('viewCount', 0)),
        reverse=True
    )[0]  # Select the video with the most views

    # Extract the best video link
    video_id = best_video['id']
    video_title = best_video['snippet']['title']
    video_link = f"https://www.youtube.com/watch?v={video_id}"

    return {"id": video_id, "title": video_title, "link": video_link}

# Function to fetch transcript and summarize it using Groq
def get_video_summary(video_id):
    try:
        # Fetch transcript
        transcript = YouTubeTranscriptApi.get_transcript(video_id)

        # Combine transcript into a single string
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

        return summary
    except Exception as e:
        return f"Error fetching or summarizing transcript: {str(e)}"