# AI Orchestration

## Background
This project demonstrates a simple AI orchestration pipeline by implementing a web-based chatbot. The chatbot interacts with a locally hosted Large Language Model (LLM) via the Ollama Python library. Key features include a Flask web interface for user interaction, session management for conversation history, and a resilient backend incorporating a retry mechanism for Ollama API calls. This example showcases how to orchestrate components for a conversational AI application.

---
## Pipeline
The pipeline for this implementation is as follows:

1.  **User Input & Interface**:
    * The user interacts with a web page rendered by Flask.
    * They type a message into an input field and submit the form.

2.  **Backend Request Handling**:
    * The Flask application receives the POST request at the `/` endpoint.
    * The user's message is extracted from the form data.

3.  **Session Management & Conversation History**:
    * The application maintains the conversation history (a list of user and assistant messages) within the Flask session.
    * The new user message is appended to this history.

4.  **Prompt Preparation**:
    * A base prompt template is read from a local file named `prompt.txt`.
    * The user's current input (`user_text` in the code) is formatted into this template.

5.  **LLM Interaction with Ollama, with retry mechanism**:
    * The backend calls the `ollama.chat()` function to send the prepared prompt and message history to a specified Ollama model (e.g., `qwen3`).
    * **Retry Mechanism**: This crucial step is wrapped in a retry loop.
        * If the `ollama.chat()` call fails (e.g., due to network issues or temporary Ollama service unavailability), the application will automatically retry the call.
        * It attempts up to `MAX_RETRIES` (configured to 3 in the code).
        * An exponential backoff strategy is used, starting with `INITIAL_RETRY_DELAY_SECONDS` (configured to 1 second) and increasing the delay between subsequent retries. This prevents overwhelming the service.

6.  **Response Processing**:
    * If the Ollama API call is successful (within the allowed retries), the LLM's response content is extracted.
    * If all retry attempts fail, a user-friendly error message is generated, indicating that the service could not be reached.

7.  **Updating Conversation & Rendering Output**:
    * The assistant's response (or the error message) is appended to the session's conversation history.
    * The entire conversation is then rendered into an HTML structure.
    * The Flask application sends the updated HTML page back to the user's browser, displaying the latest interaction.

In this implementation, the Flask web server orchestrates the flow from receiving user input, managing state through sessions, interacting with the Ollama service (including handling transient errors gracefully), and presenting the conversation back to the user.

---
# Steps to Run
*Prerequisite is having python and pip installed on your machine*  
1. Install using setup.sh  
```bash
chmod +x scripts/setup.sh && ./scripts/setup.sh
```
2. Run and monitor script with monitor.sh
```bash
chmod +x scripts/monitor.sh && ./scripts/monitor.sh
```



---

# Ollama Prompt
In Ollama the following was used to create a custom prompt before passing to an LLM:

```
You a coding assistant. Provide a detailed answer to the following question:

{user_text}

Provide additional analysis including:
1. Error Testing 
2. Performance Evaluation
```
*{{user_input}} is the variable which the user will use as the input in the frontend*

---

# Author
Keese Phillips