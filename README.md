# Realtor Chatbot

### How to run it 

1. Install the requirements

   ```
   $ pip install -r requirements.txt
   ```
2. Set environmental variable
  - Create the file `.env`
  - Create the variable `GOOGLE_API_KEY` and paste the your key value.

You also may create `.toml` file and paste the key (for streamlit app, but for no it is not actual)

3. Run the app

   ```
   python renter.py
   ```

### Architecture
**1. Greeting Step**\
   In this step, the chatbot greets with the user and receive the general info what the user is looking for. The chatbot checking whether the user mentions some important info, which describes some characteristics.

**2. Asking Step**\
   In this step the chatbot iteratively asks about characteristics that are not yet available. If the user doesn't answer completely on the specific question about required characteristic, the chatbot reasks the user until he/she provides enough information.

**3. Creating and Approving Summary Step**\
   The chatbot provides the summary and asks user whether all gathered info is correct. Also if the user wants to change something, the chatbot extracts the info (in the same way as in the first step) and saves the updated summary.
