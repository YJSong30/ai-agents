## career-conversations chatbot

chatbot that will hold context through system prompt and have messages as well. will use evaluator to make sure response is professional and will add tools to save user's name and email and send push notification

### python, pip, virtualenv

### packages

    requests - making http requests
    python-dotenv - load .env file
    gradio - ui interface
    pypdf - read pdf file
    openai - connect to llm
    openai-agents -

## to install

before installing, activate virtualenv

mac: virtualenv venv
windows: python -m venv venv

activate:
source venv/bin/activate
source venv/Scripts/activate

deactivate: deactivate

pip install -r ./requirements.txt

## to run

python main.py
