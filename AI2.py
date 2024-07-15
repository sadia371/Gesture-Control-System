import os
import speech_recognition as sr
import pyttsx3
import pywhatkit
import openai

# Initialize the speech recognition and text-to-speech engines
recognizer = sr.Recognizer()
engine = pyttsx3.init()

# Set your OpenAI API key
openai.api_key = 'sk-proj-LKq0UTOAfXSV1J7nrsFPT3BlbkFJzIlpXvPrKy4MIMDtK6qP'

def speak(text):
    """Convert text to speech."""
    engine.say(text)
    engine.runAndWait()

def listen():
    """Listen for a voice command and return it as text."""
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
        try:
            command = recognizer.recognize_google(audio)
            print(f"You said: {command}")
            return command.lower()
        except sr.UnknownValueError:
            print("Sorry, I did not understand that.")
            return None
        except sr.RequestError:
            print("Sorry, my speech service is down.")
            return None

def open_application(app_name):
    """Open an application based on the provided name."""
    try:
        if os.name == 'nt':  # Windows
            os.system(f'start {app_name}')
        elif os.name == 'posix':  # macOS/Linux
            os.system(f'open -a "{app_name}"')
        speak(f"Opening {app_name}")
    except Exception as e:
        speak(f"Could not open {app_name}. {str(e)}")

def open_folder(folder_path):
    """Open a folder based on the provided path."""
    try:
        if os.path.isdir(folder_path):
            os.startfile(folder_path) if os.name == 'nt' else os.system(f'open "{folder_path}"')
            speak(f"Opening folder {folder_path}")
        else:
            speak("Folder not found.")
    except Exception as e:
        speak(f"Could not open folder. {str(e)}")

def search_google(query):
    """Perform a Google search."""
    try:
        speak(f"Searching for {query} on Google")
        pywhatkit.search(query)
    except Exception as e:
        speak(f"Could not perform the search. {str(e)}")

def search_chatgpt(query):
    """Search and show results from ChatGPT."""
    try:
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=query,
            max_tokens=100
        )
        answer = response.choices[0].text.strip()
        print(f"ChatGPT response: {answer}")
        speak(answer)
    except Exception as e:
        speak(f"Could not retrieve information from ChatGPT. {str(e)}")

def main():
    keyword = "hello"
    print(f"Say '{keyword}' to start...")
    while True:
        command = listen()
        if command and keyword in command:
            speak("How can I help you?")
            while True:
                command = listen()
                if command:
                    if "open" in command:
                        item = command.replace("open", "").strip()
                        if os.path.exists(item) and os.path.isdir(item):
                            open_folder(item)
                        else:
                            open_application(item)
                    elif "search" in command or "google" in command:
                        query = command.replace("search", "").replace("google", "").strip()
                        search_google(query)
                    elif "ask" in command or "chatgpt" in command:
                        query = command.replace("ask", "").replace("chatgpt", "").strip()
                        search_chatgpt(query)
                    elif "exit" in command or "quit" in command:
                        speak("Goodbye!")
                        return
                    else:
                        speak("Sorry, I can only open applications, folders, search Google, or ask ChatGPT.")
                else:
                    print("No command detected, listening for keyword...")
                    break

if __name__ == "__main__":
    main()
