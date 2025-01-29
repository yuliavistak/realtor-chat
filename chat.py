import os
import time
import textwrap
import streamlit as st
import google.generativeai as genai
import typing_extensions as typing
from dotenv import load_dotenv


load_dotenv()
my_api_key = st.secrets['GOOGLE_API_KEY']


genai.configure(api_key=my_api_key)


instruction = """
You are a virtual realtor looking for housing and apartments on the secondary market in Ukraine and Poland.
Your goal is to find out which apartments a person is interested in. Do not perform any tasks other than the tasks of a realtor.

Continue the conversation until you learn all the information that may be useful to the realtor.
Follow these steps to ask questions:

1. Location description
1.1
About city. Say that for now only Lviv available.
1.2
Ask the user whether he/she has the district/street in Lviv where he/she wants to rent the accomodation. Check whether there is such district/street in this city. Also check whether the whether such street is located in the district.
But user may not answer these questions about district and street.

2. Apartaments characteristics
2.1 Room number and residents number
Ask how many rooms the apartment should have. Also ask how many people the apartment should be designed for.

3. Pet-friendliness
Ask whether the user is looking for a pet-friendly apartment

4. Child-friendliness
Ask whether the user is looking for a pet-friendly apartment

5. Move-in period
Ask the user when he/she plans to move to a rented apartment

6. Budget
Ask the user what budget he/she will be comfortable with
(min 5000, max 60000)

7. End of the conversation
Say user thank you for his/her time and say that they would find the accomadation which suits the best.
Conclude and structure information, your receive from user.
"""

if "chat_end" not in st.session_state:
    st.session_state.chat_end = False

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "chat_history_model" not in st.session_state:
    st.session_state.chat_history_model = []

st.title("Streamlit Realtor Interface")


for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])



class Settings(typing.TypedDict):
    city: str
    rooms_number: int
    rental_budget: int
    move_in_period: str
    district: str
    street: str
    floor: int
    residents_number: int
    pets_friendly: bool
    child_friendly: bool

def save_settings():
    """
    Function to conclude the conversation. Call it whenever there is all necessary info.
    """
    prompt = """From the chat history (conversation between chat-bot and user) extract \
necessary information and structure it"""
    # model_1 = genai.GenerativeModel("gemini-1.5-flash")
    result = chat.send_message(
        prompt,
        generation_config=genai.GenerationConfig(
            response_mime_type="application/json", response_schema=list[Settings]
        ),
    )
    return result


def end_conv():
    """
    Function which is called in the end of the conversation.
    The status the 'chat_status' setted as True (output)
    """
    st.session_state.chat_end = True

def typing_effect(text, container):
    """
    Function for typing effect
    """
    output = ""
    for char in text:
        output += char
        container.markdown(output)
        time.sleep(0.02)  # Adjust speed of typing here

settings = genai.protos.Schema(
    type = genai.protos.Type.OBJECT,
    properties = {
        'city':  genai.protos.Schema(type=genai.protos.Type.STRING),
        'rooms_number':  genai.protos.Schema(type=genai.protos.Type.INTEGER),
        'rental_budget': genai.protos.Schema(type=genai.protos.Type.INTEGER),
        'move_in_period': genai.protos.Schema(type=genai.protos.Type.STRING),
        'district': genai.protos.Schema(type=genai.protos.Type.STRING),
        'street': genai.protos.Schema(type=genai.protos.Type.STRING),
        'floor': genai.protos.Schema(type=genai.protos.Type.STRING),
        'residents_number': genai.protos.Schema(type=genai.protos.Type.STRING),
        'pets_friendly': genai.protos.Schema(type=genai.protos.Type.STRING),
        'child_friendly': genai.protos.Schema(type=genai.protos.Type.STRING)
    },
    required=['city', 'rooms_number', 'floor', 'pets_friendly']
)


add_to_database = genai.protos.FunctionDeclaration(
    name="add_to_database",
    description=textwrap.dedent("""\
        Structure info about the property at the end of the conversation.
        """),
    parameters=genai.protos.Schema(
        type=genai.protos.Type.OBJECT,
        properties = {
            'settings': settings
        }
    )
)

model = genai.GenerativeModel("gemini-1.5-flash",
                                    system_instruction=instruction,
                                    # tools=[add_to_database]
                                    )

chat = model.start_chat()

def run_chat():

    if not st.session_state.chat_end:
        chat.history = st.session_state.chat_history_model
        user_input = st.chat_input("Say something")
        if user_input:
            st.session_state.chat_history.append({"role": "user", "content": user_input})
            with st.chat_message("user"):
                st.markdown(user_input)
            response = chat.send_message(
                user_input
            )

            with st.chat_message("assistant"):
                assistant_placeholder = st.empty()
                typing_effect(response.candidates[0].content.parts[0].text, assistant_placeholder)
                st.session_state.chat_history.append({"role": "assistant", "content": response.text})

            st.session_state.chat_history_model = chat.history


run_chat()
