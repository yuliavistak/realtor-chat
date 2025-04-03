import time
# import streamlit as st
import google.generativeai as genai
# import typing_extensions as typing
from dotenv import load_dotenv


load_dotenv()
my_api_key = st.secrets['GOOGLE_API_KEY']


genai.configure(api_key=my_api_key)


settings = {
            "city": '',
            "rooms": 0,
            "rental_budget": 0,
            "move_in_period": '',
            "district": '',
            "street": '',
            "floor": 0,
            "residents_number": 0,
            "pets_friendly": False,
            "child_friendly": False
        }
# Чи є додаткові побажання стосовно бажаного поверху, скільки мешканців планує проживати, чи плануєте проживати з тваринами чи дітьми?

questions = {
            ("city", "district", "street"): ['I would like to warn you that we are currently working only in Lviv, you can see available apartments from owners in other cities [link to our Ukrainian channel]', 'Do you want to live in a specific district?', 'Do you want to live in a specific street? If yes, in which?'],
            ("rental_budget"): ['What is the expected rental monthly payment (in UAH)?'],
            ("rooms"): ['How many rooms would you like?'],
            ("floor", "residents_number", "pets_friendly", "child_friendly"): ['Do you have other additional prefferences about floor?', 'How many people are planning to live there?', 'Do you plan to live with pets?', 'Do you plan to live with children?'],
            ("move_in_period"): ['When do you plan to move to a rented apartment?']
        }


greetings_instruction = """You are LetAFlat AI-assistant,
a virtual realtor looking for housing and apartments in Ukraine and Poland.
Your goal is to find out which apartments a person is interested in (for renting only).
Do not perform any tasks other than the tasks of a realtor.
At the beggining greet with user, but don't ask about location,
since the chatbot is available only for flats in Lviv."""

greetings_model = genai.GenerativeModel("gemini-1.5-flash",
                                    system_instruction=greetings_instruction
                                    )
gr_chat = greetings_model.start_chat(enable_automatic_function_calling=True)

ask_instruction = """You are helpful assistant which help to rewrite and reask the questions.
You will receive chathistory (user & chat). Help chatbot to reask the question or too respond the user. 
If the chatbot asked just 1 question, rewrite it. Do not perform any other tasks"""

ask_model = genai.GenerativeModel("gemini-1.5-flash",
                                    system_instruction=ask_instruction
                                    )

ask_chat = ask_model.start_chat(enable_automatic_function_calling=True)


check_instruction = """You are a helpful assistant which checks whether the user provides full information about specific characteristics.
You will a characteristic, main questions set, and chat history (chatbot&user). You should determine whether the user's answers completely provide info for the characteritic.
Provide only yes/no. (yes - if answers are complete; no - otherwise)"""


check_model = genai.GenerativeModel("gemini-1.5-flash",
                                    system_instruction=check_instruction
                                    )

check_chat = check_model.start_chat(enable_automatic_function_calling=True)


save_instruction = """You are helpful assistant which extracts main from chat history.
You receive the attribute (flat characteristic) and extract the
 value of the characteristic the user wants."""


save_model = genai.GenerativeModel("gemini-1.5-flash",
                                    system_instruction=save_instruction
                                    )

save_chat = save_model.start_chat(enable_automatic_function_calling=True)


summary_instruction = """You are helpful assistant which creates summary of the received dict (point by point).
You should provide it to user, reask if everything is correct and ask to write what to change if something is not correct."""


summary_model = genai.GenerativeModel("gemini-1.5-flash",
                                    system_instruction=summary_instruction
                                    )

summary_chat = summary_model.start_chat(enable_automatic_function_calling=True)

approve_instruction = """You are helpful assistant whether the user approved the correcteness of the summary.
You will receive a part of chathistory (chatbot and user). You should say 'yes' if the user approved the correctness, and 'no' otherwise"""
approve_model = genai.GenerativeModel("gemini-1.5-flash",
                                    system_instruction=approve_instruction
                                    )

approve_chat = approve_model.start_chat(enable_automatic_function_calling=True)

def ask(question: list):
    """
    Helps chatbot formulate questions
    """
    response = ask_chat.send_message(
            f'{question}'
        )
    response_text = response.candidates[0].content.parts[0].text
    return response_text

def check_answer_completeness(subject: str, question: list, history: list) -> bool:
    """
    Function for checking whether the user provides enough information for a specific attribute.
    """

    prompt =f"""The discussed subjects are: {subject}.
 The question is {question}. Chat history: {history}"""
    response = check_chat.send_message(
            prompt
        )
    response_text = response.candidates[0].content.parts[0].text
    # print(response_text)
    return response_text in ('yes', 'Yes', 'yes\n')

def save_ans(key: str, history: list):
    """
    Saves info in settings
    """
    response = save_chat.send_message(
            f'Characteristic: {key}. Chat history: {history}'
        )
    response_text = response.candidates[0].content.parts[0].text
    # print(response_text)
    settings[key] = response_text
    print('\nSAVED--------------\n')
    # print(settings)

def parse_first(history: list|dict):
    """
    Parse info from answer: whether there are mentioned characteristics and their values
    """
    for keys, question in questions.items():
        for key in keys:
            time.sleep(2)
            if isinstance(keys, str):
                key = keys
                # print(key)
                completeness = check_answer_completeness(key, question, history)
                if completeness:
                    save_ans(key, history)
                break
            # print(key)
            completeness = check_answer_completeness(key, question, history)
            if completeness:
                save_ans(key, history)

def create_summary(settings: dict):
    """
    Formulates summary of the conversation
    """
    response = summary_chat.send_message(
            f'Please, reask if everything is correct: {settings}'
        )
    response_text = response.candidates[0].content.parts[0].text
    return response_text

def approve(history: str):
    """
    Check whether the user approved the final summary
    """
    prompt = f"""Check whether the user approved {history}"""
    response = approve_chat.send_message(
            prompt
        )
    response_text = response.candidates[0].content.parts[0].text
    # print(response_text)
    return response_text in ('yes', 'Yes', 'yes\n')


def typing_effect(text, container):
    """
    Function for typing effect
    """
    output = ""
    for char in text:
        output += char
        container.markdown(output)
        # time.sleep(0.02)  # Adjust speed of typing here
    return

def main() -> dict:
    """
    Main user's flow function
    """

    user_ans = '.'

    response = gr_chat.send_message(user_ans)
    response_text = response.candidates[0].content.parts[0].text
    print(response_text)

    user_ans = input('User: ')

    general_history = []
    general_history.append(
            {
                'chatbot': response_text
            }
    )

    general_history.append(
            {
                'user': user_ans
            }
    )

    parse_first(general_history)

    required = ["rental_budget", "rooms"]

    for keys, question in questions.items():
        step_subjects = []
        step_questions = []


        for i, key in enumerate(keys):

            if isinstance(keys, str):
                key = keys
                if not settings[key]:
                    step_subjects.append(key)
                    step_questions.append(question[i])
                break
            if not settings[key]:
                step_subjects.append(key)
                step_questions.append(question[i])

        if step_subjects:
            history = [
                {
                    'chatbot': " ".join(step_questions)
                }
            ]

            quest = ask(history)
            print(quest)

            user_ans = input('User: ')

            history.append(
                {
                    'user':user_ans
                }
            )

            for characteristic in step_subjects:
                time.sleep(2)
                if characteristic in required:
                    completeness = False
                    while not completeness:
                        completeness = check_answer_completeness(characteristic,
                                                                step_questions,
                                                                history)
                        if completeness:
                            save_ans(characteristic, history)
                            break

                        response_text = ask(history)
                        print(response_text)
                        user_ans = input('User: ')

                        history.append(
                            {
                                'user':user_ans
                            }
                        )
                else:
                    completeness = check_answer_completeness(characteristic,
                                                            step_questions,
                                                            history)
                    if completeness:
                        save_ans(characteristic, history)


    response_text = create_summary(settings)
    print(response_text)

    user_ans = input('User: ')

    approve_history = [
        {'chatbot': response_text},
        {'user': user_ans}
    ]

    approved = approve(approve_history)
    while not approved:
        parse_first(approve_history[1])
        response_text = create_summary(settings)
        print(response_text)

        user_ans = input('User: ')
        approve_history = [
            {'chatbot': response_text},
            {'user': user_ans}
        ]
        approved = approve(approve_history)

    print('Thank you for your time!')


main()
