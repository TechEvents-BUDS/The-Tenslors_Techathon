# main.py
import streamlit as st
from streamlit_option_menu import option_menu
from PIL import Image
import random
from yt import search_best_youtube_video, get_video_summary
from flashcardmod import main as load_flashcard_page  # Import the flashcard module
from codeassitant import get_code_assistant_response, system_prompt  # Import the code assistant module

# Temporary dictionary for user data (For demonstration only. Use a proper database for production.)
users_db = {"admin@example.com": {"name": "Admin", "password": "admin123"}}

# Global session state to track user login
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "current_user" not in st.session_state:
    st.session_state["current_user"] = None

def add_custom_css():
    st.markdown(
        """
        <style>
        .main {
            background-color: #f0f2f6;
        }
        .stButton>button {
            background-color: #4CAF50;
            color: white;
            border-radius: 12px;
        }
        .stTextInput>div>div>input {
            border: 2px solid #4CAF50;
            border-radius: 12px;
        }
        .stRadio>div>div>label {
            font-weight: bold;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

def load_signup_page():
    """User signup and login page."""
    st.title("FlashLearn App: Welcome!")
    st.write("Your personalized learning companion")
    choice = st.radio("Choose an option:", ["Login", "Sign Up"], index=0)

    if choice == "Sign Up":
        st.header("Create a New Account")
        name = st.text_input("Enter your Name:")
        email = st.text_input("Enter your Email:")
        password = st.text_input("Create a Password:", type="password")
        confirm_password = st.text_input("Confirm Password:", type="password")

        if st.button("Sign Up"):
            if password != confirm_password:
                st.error("Passwords do not match!")
            elif email in users_db:
                st.error("Email is already registered!")
            else:
                users_db[email] = {"name": name, "password": password}
                st.success("Account created successfully! Please log in.")

    elif choice == "Login":
        st.header("Log In")
        email = st.text_input("Email:")
        password = st.text_input("Password:", type="password")

        if st.button("Log In"):
            user_data = users_db.get(email)
            if user_data and user_data["password"] == password:
                st.success(f"Welcome back, {user_data['name']}!")
                st.session_state["logged_in"] = True
                st.session_state["current_user"] = email
            else:
                st.error("Invalid email or password!")

def load_learning_companion_page():
    st.title("Your Personalized Learning Companion")

    # Section 1: Setting Preferences
    st.header("Set Your Preferences")
    domain = st.selectbox("Select Learning Domain:",
                          ["Data Science", "Web Development", "Machine Learning", "Cybersecurity"])
    duration = st.slider("Daily Learning Time (minutes):", 10, 120, 30)
    skill_level = st.radio("Skill Level:", ["Beginner", "Intermediate", "Advanced"])

    st.write("### User Prompts")
    user_goal = st.text_area("Describe your learning goal:", "e.g., Become proficient in NumPy and pandas.")

    st.write("#### Settings Summary")
    st.write(f"**Domain:** {domain}")
    st.write(f"**Daily Time:** {duration} minutes")
    st.write(f"**Skill Level:** {skill_level}")
    st.write(f"**Goal:** {user_goal}")

    # Section 2: Note-Taking with Summarization
    st.header("Notes and Summarization")
    user_notes = st.text_area("Write your learning notes here:")

    if st.button("Summarize Notes"):
        if user_notes.strip():
            # Simulate summarization output for now
            summary = f"Summary: The notes focus on {domain}. Key areas to enhance: {user_goal}."
            st.success(summary)

            # Simulate extracting points from notes
            points = ["Key point 1", "Key point 2", "Key point 3"]
            st.write("### Extracted Key Points")
            for idx, point in enumerate(points, 1):
                st.write(f"{idx}. {point}")
        else:
            st.warning("Please input notes to summarize.")

    # Section 3: Quizzes for Practice
    st.header("Quizzes for Practice")
    st.write("### Generate Custom Quizzes")

    if domain == "Data Science":
        question_pool = [
            ("What is a DataFrame in pandas?", "A two-dimensional data structure."),
            ("Define NumPy.", "A library for numerical computations."),
        ]
    elif domain == "Web Development":
        question_pool = [
            ("What does HTML stand for?", "HyperText Markup Language."),
            ("What is the purpose of CSS?", "Styling web pages."),
        ]
    elif domain == "Machine Learning":
        question_pool = [
            ("What is supervised learning?", "Learning using labeled data."),
            ("What does 'overfitting' mean?", "Model performs well on training data but poorly on new data."),
        ]
    else:
        question_pool = [
            ("What is a firewall?", "A security measure to block unauthorized access."),
            ("Define phishing.", "Fraudulent attempt to steal sensitive information."),
        ]

    num_quizzes = st.number_input("How many quiz questions would you like?", min_value=1, max_value=5, value=3, step=1)

    if st.button("Generate Quiz"):
        st.write("### Quiz Questions")
        random.shuffle(question_pool)
        for idx, (question, answer) in enumerate(question_pool[:num_quizzes], 1):
            with st.expander(f"Question {idx}: {question}"):
                st.write(f"**Answer:** {answer}")

    st.write("Happy Learning! 🚀")

def load_feedback_page():
    st.title("Feedback Center")
    st.header("Submit Feedback for Peer Review")
    user_feedback = st.text_area("Enter your feedback:", "Provide constructive feedback here...")
    if st.button("Submit Feedback"):
        st.success("Feedback submitted successfully!")

    st.header("Received Feedback")
    st.write("1. Great work on the recent quiz!")
    st.write("2. Consider improving your consistency in learning.")

def load_journal_page():
    st.title("Personal Journal")
    st.header("Daily Reflections")
    journal_entry = st.text_area("Write your reflection for today:", "What did you learn today?")
    if st.button("Save Journal Entry"):
        st.success("Journal entry saved successfully!")

    st.header("Previous Entries")
    st.write("- Entry 1: 'Learned about logistic regression.'")
    st.write("- Entry 2: 'Refined my understanding of gradient descent.'")

def load_home_page():
    st.title("Flash App: Your Adaptive Learning Companion")
    st.header("User Profile")
    # Fetch and display the current user's info
    current_user = st.session_state["current_user"]
    user_data = users_db.get(current_user, {})
    st.write(f"**Name:** {user_data.get('name', 'Unknown')}")
    st.write("**Current Level:** Intermediate")
    st.write("**Focus Area:** Data Science")

    st.header("Recommendations")
    st.write("1. Video: 'Advanced Python Techniques'")
    st.write("2. Article: 'Getting Started with Machine Learning'")
    st.write("3. Quiz: 'Python Basics Review'")

    st.header("Past Learning History")
    st.write("- Completed: 'Intro to Python' course")
    st.write("- Quiz: Scored 85% on 'Data Structures'")
    st.write("- Journal: 'Reflections on Debugging Techniques'")

    # Add an image
    image = Image.open('path_to_image.jpg')
    st.image(image, caption='Learning is fun with Flash App!', use_column_width=True)

def load_video_preparation_page():
    st.title("QuickVid Insights")
    st.write("Enter a topic to find the best YouTube video and get its summary.")
    topic = st.text_input("Enter a topic you want to learn:", "")

    if topic:
        with st.spinner('Searching for the best video...'):
            result = search_best_youtube_video(topic)
            st.subheader("Best Video Link:")
            st.write(result['link'])

        if st.button("Get Video Summary"):
            with st.spinner('Fetching and summarizing the video transcript...'):
                video_summary = get_video_summary(result['id'])
                st.subheader("Video Summary:")
                st.write(video_summary)

# Add custom CSS
add_custom_css()

# Navigation bar updates
with st.sidebar:
    if st.session_state["logged_in"]:
        selected = option_menu(
            menu_title="Flash App Navigation",
            options=["Home", "Video Preparation", "Learning Companion", "Feedback", "Personal Journal", "Flashcards", "Code Assistant", "Logout"],
            icons=["house", "video", "book", "chat", "pencil", "cards", "code", "box-arrow-right"],
            menu_icon="grid-3x3-gap",
            default_index=0
        )
        if selected == "Logout":
            st.session_state["logged_in"] = False
            st.rerun()
    else:
        selected = option_menu(
            menu_title="Flash App Navigation",
            options=["Login/Signup"],  # Only show Login/Signup for logged-out users
            icons=["box-arrow-in-right"],
            menu_icon="grid-3x3-gap",
            default_index=0
        )


# Load Pages
if selected == "Login/Signup":
    load_signup_page()
elif selected == "Home" and st.session_state["logged_in"]:
    load_home_page()
elif selected == "Video Preparation" and st.session_state["logged_in"]:
    load_video_preparation_page()
elif selected == "Learning Companion" and st.session_state["logged_in"]:
    load_learning_companion_page()
elif selected == "Feedback" and st.session_state["logged_in"]:
    load_feedback_page()
elif selected == "Personal Journal" and st.session_state["logged_in"]:
    load_journal_page()
elif selected == "Flashcards" and st.session_state["logged_in"]:
    load_flashcard_page()
elif selected == "Code Assistant" and st.session_state["logged_in"]:
    st.title('Code Assistant with Groq API')
    code_input = st.text_area('Enter your code', height=300)
    if st.button('Get Assistance'):
        if code_input:
            response = get_code_assistant_response(code_input)
            st.subheader('Code Assistant Response')
            st.text_area('Response', value=response, height=300)
        else:
            st.warning('Please enter some code.')
    if st.button('Start New Conversation'):
        st.session_state.messages = [{"role": "system", "content": system_prompt}]
        st.success('Conversation has been reset. Feel free to ask anything again!')
else:
    st.warning("Please log in to access this page.")