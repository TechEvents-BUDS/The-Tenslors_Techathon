import streamlit as st
from groq import Groq

# Initialize Groq client
client = Groq(
    api_key="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"
)

# Define system prompt
system_prompt = """
You are a professional code assistant skilled in explaining, improving, and debugging code. Your tasks are:
1. Summarize what the provided code does in a clear and simple way.
2. Detect and give fixes for any bugs or errors in the code.
Always ensure that your suggestions are clear, concise, and actionable. Avoid ambiguity and explain the rationale behind any modifications or bug fixes.
"""

# Function to get completion from Groq
def get_code_assistant_response(code_input):
    completion = client.chat.completions.create(
        model="llama-3.2-11b-vision-preview",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": code_input}
        ],
        temperature=1,
        max_tokens=1024,
        top_p=1,
        stream=False,
        stop=None,
    )
    # Correctly access the message content
    return completion.choices[0].message.content  # Corrected line

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

