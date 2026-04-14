import requests
import configparser

global QA_string
global event_string
global default_string

QA_string = '''You are a learning assistant. Your task is to answer the user's questions.
 Pay attention to making explanations detailed, professional, and easy to understand.
'''
event_string = '''You are an event recommendation assistant. 
Your task is to analyze the needs provided by the user and connect them with relevant activities.
 Activities can be sourced from the internet.
'''
default_string = '''You are a helper! Your users are university students. 
Your replies should be conversational, informative, use simple words, and be straightforward.
Output "If you have any problems, send "\help" for more information." at the start of the conversation. 
'''


# A simple client for the ChatGPT REST API
class ChatGPT:
    system_message = default_string
    def __init__(self, config, command = '/default'):
        global course_string
        global event_string
        global default_string

        # Read API configuration values from the ini file
        api_key = config['CHATGPT']['API_KEY']
        base_url = config['CHATGPT']['BASE_URL']
        model = config['CHATGPT']['MODEL']
        api_ver = config['CHATGPT']['API_VER']

        # Construct the full REST endpoint URL for chat completions
        self.url = f'{base_url}/deployments/{model}/chat/completions?api-version={api_ver}'

        # Set HTTP headers required for authentication and JSON payload
        self.headers = {
            "accept": "application/json",
            "Content-Type": "application/json",
            "api-key": api_key,
        }

        # Define the system prompt to guide the assistant’s behavior
        if command == '/default':
            self.system_message = (default_string)
        elif command == '/QA':
            self.system_message = (QA_string)
        elif command == '/event':
            self.system_message = (event_string)

    def submit(self, user_message: str):
        
        # Build the conversation history: system + user message
        messages = [
            {"role": "system", "content": self.system_message},
            {"role": "user", "content": user_message},
        ]

        # Prepare the request payload with generation parameters
        payload = {
            "messages": messages,
            "temperature": 1,     # randomness of output (higher = more creative)
            "max_tokens": 150,    # maximum length of the reply
            "top_p": 1,           # nucleus sampling parameter
            "stream": False       # disable streaming, wait for full reply
        }    

        # Send the request to the ChatGPT REST API
        response = requests.post(self.url, json=payload, headers=self.headers)

        # If successful, return the assistant’s reply text
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        else:
            # Otherwise return error details
            return "Error: " + response.text
    

if __name__ == '__main__':
    # Load configuration from ini file
    config = configparser.ConfigParser()
    config.read('config.ini')    

    # Initialize ChatGPT client
    chatGPT = ChatGPT(config)

    # Simple REPL loop: read user input, send to ChatGPT, print reply
    while True:
        print('Input your query: ', end='')
        response = chatGPT.submit(input())

        print(response)
