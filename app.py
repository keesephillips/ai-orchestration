from ollama import chat, ChatResponse
import os, json, html, time
from flask import Flask, request, session, redirect, url_for, make_response

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "8200E54A64AF2F8FFB509F99AFE8CF4C")  

HTML_SKELETON = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>AIPI561 Chatbot</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 2rem; }}
    .msg {{ margin: .8em 0; }}
    .user {{ color: blue; font-weight: bold; }}
    .assistant {{ color: green; font-weight: bold; }}
  </style>
</head>
<body>
  <h1>Chatbot via Ollama</h1>
  <form method="POST">
    <input type="text" name="message" placeholder="Type your message…" required autofocus>
    <button type="submit">Send</button>
  </form>
  {conversation}
</body>
</html>
"""

def render_conversation(turns):
    rows = []
    for t in turns:
        role_cls = "user" if t["role"] == "user" else "assistant"
        label = "You" if t["role"] == "user" else "Chatbot"
        rows.append(
            f'<div class="msg"><span class="{role_cls}">{label}:</span> {html.escape(t["text"])}</div>'
        )
    return "\n".join(rows)

@app.route("/", methods=["GET", "POST"])
def index():
    try:
        with open('prompt.txt','r') as f:
            prompt_template = f.read()
    except FileNotFoundError:
        app.logger.error("prompt.txt not found!")
        prompt_template = "User query: {user_text}" 

    if "conversation" not in session:
        session["conversation"] = []

    if request.method == "POST":
        user_text = request.form.get("message", "").strip()
        if user_text:
            session["conversation"].append({"role": "user", "text": user_text})
            session.modified = True 

            assistant_text = None
            last_exception = None

            for attempt in range(MAX_RETRIES):
                try:
                    app.logger.info(f"Attempt {attempt + 1}/{MAX_RETRIES} to call Ollama model.")
                    formatted_prompt = prompt_template.format(user_text=user_text)
                    
                    response: ChatResponse = chat(model='qwen3', messages=[
                        {
                            'role': 'user',
                            'content': formatted_prompt,
                        },
                    ])
                    assistant_text = response.message.content
                    app.logger.info("Ollama call successful.")
                    break  
                
                except Exception as exc:
                    last_exception = exc
                    app.logger.warning(f"Attempt {attempt + 1}/{MAX_RETRIES} failed. Error: {exc}")
                    if attempt < MAX_RETRIES - 1:
                        delay = min(INITIAL_RETRY_DELAY_SECONDS * (2 ** attempt), 30) 
                        app.logger.info(f"Retrying in {delay} seconds...")
                        time.sleep(delay)
                    else:
                        app.logger.error(f"All {MAX_RETRIES} attempts to connect to Ollama failed.")
                        assistant_text = (
                            f"Error: Could not connect to the Ollama model after {MAX_RETRIES} attempts. "
                            f"Please try again later. (Details: {type(last_exception).__name__})"
                        )

            session["conversation"].append({"role": "assistant", "text": assistant_text})
            session.modified = True 

        page = HTML_SKELETON.format(conversation=render_conversation(session["conversation"]))
        return make_response(page, 200, {"Content-Type": "text/html"})

    page = HTML_SKELETON.format(conversation=render_conversation(session["conversation"]))
    return make_response(page, 200, {"Content-Type": "text/html"})

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))  
    app.run(host="0.0.0.0", port=port)
