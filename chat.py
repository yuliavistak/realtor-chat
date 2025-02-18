import time
import os
import streamlit as st
import google.generativeai as genai
import typing_extensions as typing
from dotenv import load_dotenv


load_dotenv()
my_api_key = os.getenv('GOOGLE_API_KEY')
# my_api_key = st.secrets['GOOGLE_API_KEY']


genai.configure(api_key=my_api_key)

instruction = """
You are LetAFlat chat-bot, a virtual realtor looking for housing and apartments in Ukraine and Poland.
Your goal is to find out which apartments a person is interested in. Do not perform any tasks other than the tasks of a realtor.
That means if the user ask the questions not related to the apartment search, do not answer these questions.

Do not say hello if you have already said hello.

In the beginning ask the questions, user must answer:

1. Location
Say that for now only Lviv available. (!!!Save this in settings!!!). So, for now, do not ask about the city, just inform the user.
Ask the user whether he/she has the district/street in Lviv where he/she wants to rent the accomodation.
**It's okay if the user has no district/street prefferences. If he/she didn't answer the question, or answered unclearly, move to the next question.

2. Budget
Ask the user what is the expected rental monthly payment (in UAH)?
(min 5000 UAH, max 60000 UAH)
**This question is required. So if the user has not answered the question, ask again until he/she does.

3. Room number 
Ask how many rooms the apartment should have (min 1, max 5).
**This question is required. So if the user has not answered the question, ask again until he/she does.

4. Additional characterostics of the apartment
Firstly, in one question ask about the following characteristics:
floor, number of residents, pet-friendliness and child-friendliness.

If the user answer about specific characteristic and you want to justify, ask the following (according th that characteristic):
4.1 Floor
Also ask about the desired floor (min 1, max 20).

4.2 Residents number
Also ask how many people the apartment should be designed for (single/student/family/other).

4.3. Pet-friendliness
Ask whether the user is looking for a pet-friendly apartment. If the user has mentioned about his/her pets before, do not ask this.

4.4. Child-friendliness
Ask whether the user is looking for a child-friendly apartment. If the user has mentioned about his/her children before, do not ask this.
 
**It's okay if the user has no such prefferences and didn't answer any questions from part 4. In such case, move to the next question.

5. Move-in period
Ask the user when he/she plans to move to a rented apartment (e.g., ASAP/one-two-weeks/one month/more than one month)
**It's okay if the user has don't know the answer. In such case, move to the next part.

6. End of the conversation
Say user thank you for his/her time and say that they would find the accomodation which suits the best.
Conclude and structure information, your receive from user.

P.S. Take into account the information you already receive, so you do not need to ask the question if it is not necessarily.


After function calling just say to user smth like"Okey, thank you for your time. We noted everything and start to search for the apartment which best suits you"


"""


class Settings(typing.TypedDict):
    city: str
    rooms: int
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
    Function to conclude the conversation.
    Call it whenever the user has aswered all questionns and there is all necessary info.
    If user did not give clear answer, save that answer, do not create anything else.
    """
    prompt = f"""From the chat history (conversation between chat-bot and user) extract \
necessary information:
{st.session_state.chat_history}


**The required attributes: city, budget, rental_budget. Other attributes are not required.

**If the attributes are not required and the user didn't provide corresponding information, do not save the null values in the output."""
    print('START OF FUNCTION CALLING')

    model_1 = genai.GenerativeModel("gemini-1.5-flash")
    result = model_1.generate_content(
        prompt,
        generation_config=genai.GenerationConfig(
            response_mime_type="application/json", response_schema=list[Settings]
        ),
    )

    print('RESULT OF FUNCTION CALLING')

    if result.candidates:
        generated_text = result.candidates[0].content.parts[0].text

    else:
        generated_text = ""


    with open("settings.txt", "w", encoding="utf-8") as text:
        text.write(generated_text)

    # return generated_text

def typing_effect(text, container):
    """
    Function for typing effect
    """
    output = ""
    for char in text:
        output += char
        container.markdown(output)
        time.sleep(0.02)  # Adjust speed of typing here


model = genai.GenerativeModel("gemini-1.5-flash",
                                    system_instruction=instruction,
                                    tools=[save_settings]
                                    )

chat = model.start_chat(enable_automatic_function_calling=True)


if "chat_end" not in st.session_state:
    st.session_state.chat_end = False

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "chat_history_model" not in st.session_state:
    st.session_state.chat_history_model = []
    greetings = "Hello! I'm LetAFlat chat-bot. I'm here to help you \
to find the accomodation which best suits you."
    st.session_state.chat_history.append({"role": "assistant",
                                                "content": greetings})
    chat.history = st.session_state.chat_history_model

st.title("LetAFlat")


for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


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
                st.session_state.chat_history.append({"role": "assistant",
                                                      "content":
                                                      response.candidates[0].content.parts[0].text})

        st.session_state.chat_history_model = chat.history



run_chat()
