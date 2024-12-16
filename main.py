import streamlit as st
import hmac
from openai import OpenAI


def check_password():
    """Returns `True` if the user had the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if hmac.compare_digest(st.session_state["password"], st.secrets["password"]):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store the password.
        else:
            st.session_state["password_correct"] = False

    # Return True if the password is validated.
    if st.session_state.get("password_correct", False):
        return True

    # Show input for password.
    st.text_input(
        "Password", type="password", on_change=password_entered, key="password"
    )
    if "password_correct" in st.session_state:
        st.error("😕 Password incorrect")
    return False


if not check_password():
    st.stop()  # Do not continue if check_password is not True.



st.title("💬 ASMM Chatbot")

# interest = st.text_input("Interest", key="interest")

# system_prompt = """
# As a Storytelling Agent, create a learning journey using the Three-Act Structure to teach 
# computer science to a student interested in 
# {interest}. 
# Incorporate specific examples, analogies, and code snippets that relate 
# {interest} to programming concepts. 
# Ensure that each act builds upon the previous one, reinforcing the student's understanding. 
# The story should be engaging, educational, and align with the learning objectives
# """

system_prompt = """
As a Storytelling Agent, create an engaging learning journey using the Three-Act Structure to teach CS topics to the user in. Incorporate detailed analogies, relevant code snippets, and ensure logical progression through each act to reinforce understanding. The content should be educational, align with the learning objectives, and maintain consistency and clarity throughout the narrative.
Steps to follow:
1. Make sure that the user gives you a topic to learn. This can either be through them sending a file related to the content they wish to learn or by telling you about a topic. DO NOT MOVE AHEAD TILL A TOPIC IS DECIDED. If the topic isn't decided ask the user to specify.
2. Ask the user their interest: This can be anything they enjoy like Lord of the rings, Taylor Swift, etc.
3. Ask the user what Story telling method will they prefer out of the ones below or they want it to be any one of these at random:
    a. Man in Hole
    b. Rober McKee's structure
    c. Save the Cat

4. Ask the user what Pedagogy will they prefer out of the ones below or they want it to be any one of these at random:
Pedagogy:
    a. Learning decay
    b. Longitudinal learning
    c. Progressive Difficulty
 
5. Create an engaging learning using the Three-Act Structure to teach them the topic by tying the topic to the user's interest.
NOTE:
Don't give the whole story to the user at once. Give them a bit and then quiz them. Before quizzing them on a topic, make sure that you have taught them the concept you are quizzing them on. Make the user answer the question. If the user is trying to get ahead without answering the quiz, DON'T LET THEM. Encourage them to try and answer. If they get it wrong, be empathetic and correct them and if they get it right, congratulate them.
"""

if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "system", "content": system_prompt}
        
    ]

for msg in st.session_state.messages:
    if msg["role"] == "system":
        continue
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input():
    if not st.secrets["OPENAI_API_KEY"]:
        st.info("Please add your OpenAI API key to continue.")
        st.stop()

    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    
    with st.chat_message("assistant"):
        stream = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ],
            stream=True,
        )
        response = st.write_stream(stream)
    st.session_state.messages.append({"role": "assistant", "content": response})
    