import streamlit as st
import subprocess
import os
from PyPDF2 import PdfReader
from langchain.chains import ConversationChain
from langchain.chains.conversation.memory import ConversationBufferWindowMemory
from langchain_groq import ChatGroq
from dotenv import load_dotenv

load_dotenv()

groq_api_key = os.environ['GROQ_API_KEY']

def run_python_code(code):
    # Save code to a Python file
    with open("user_code.py", "w") as f:
        f.write(code)

    # Run the Python file
    login_command = "C:/Users/mauli/AppData/Local/Programs/Python/Python310/python.exe user_code.py"
    output = subprocess.run(login_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True)
    return output.stdout, output.stderr

def main():
    
    
    # Selectbox for choosing between Python interpreter and BlackBot
    tool_selected = st.sidebar.selectbox(
        'Select Tool',
        ['BlackBot', 'Python Interpreter']
    , index=0)

    # Depending on the selection, display the appropriate tool
    if tool_selected == 'BlackBot':
        st.title("BlackBot")
        
        # Initialize session state
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []

        # Add customization options to the sidebar
        st.sidebar.title('Select an LLM')
        model = st.sidebar.selectbox(
            'Choose a model',
            ['mixtral-8x7b-32768', 'llama2-70b-4096']
        )
        conversational_memory_length = st.sidebar.slider('Conversational memory length:', 1, 10, value=5)

        memory = ConversationBufferWindowMemory(k=conversational_memory_length)

        # Input function
        user_question = st.text_area("Ask a question:")

        # PDF loader in the sidebar
        st.sidebar.subheader("Your documents")
        pdf_docs = st.sidebar.file_uploader(
            "Upload your PDFs here and click on 'Process'", accept_multiple_files=True)

        # Process button
        if st.button("Process"):
            with st.spinner("Processing"):
                # Process PDFs
                pdf_text = read_pdf(pdf_docs)

                # Initialize Groq Langchain chat object and conversation
                groq_chat = ChatGroq(
                    groq_api_key=groq_api_key,
                    model_name=model
                )

                conversation = ConversationChain(
                    llm=groq_chat,
                    memory=memory
                )

                if user_question:
                    response = conversation(user_question)
                    message = {'User': user_question, 'BlackBot': response['response']}
                    st.session_state.chat_history.append(message)
                    st.write("BlackBot:", response['response'])

        # Chat history button
        if st.sidebar.button("Chat History"):
            if st.session_state.chat_history:
                st.write("## Chat History")
                for message in st.session_state.chat_history:
                    st.write("User:", message['User'])
                    st.write("BlackBot:", message['BlackBot'])
                    st.write("---")
            else:
                st.write("No chat history yet.")

    elif tool_selected == 'Python Interpreter':
        st.title("Python Interpreter")

        # Text area for user to input code
        code = st.text_area("Enter your Python code here", height=200)

        # Button to run the code
        if st.button("Run"):
            if code.strip() == "":
                st.warning("Please enter some code to run.")
            else:
                stdout, stderr = run_python_code(code)
                st.subheader("Output")
                if stdout:
                    st.code(stdout)
                if stderr:
                    st.error(stderr)

def read_pdf(pdf_files):
    text = ""
    for pdf_file in pdf_files:
        pdf_reader = PdfReader(pdf_file)
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text

if __name__ == "__main__":
    main()
