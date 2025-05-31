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
    with open('prompt.txt','r') as f:
        prompt = f.read()
        
    if "conversation" not in session:
        session["conversation"] = []

    if request.method == "POST":
        user_text = request.form.get("message", "").strip()
        if user_text:
            session["conversation"].append({"role": "user", "text": user_text})

            try:
                response: ChatResponse = chat(model='qwen3', messages=[
                {
                    'role': 'user',
                    'content': prompt.format(user_text=user_text),
                },
                ])
                assistant_text = response.message.content
            except Exception as exc:
                assistant_text = f"Error: {exc}"

            session["conversation"].append({"role": "assistant", "text": assistant_text})

        page = HTML_SKELETON.format(conversation=render_conversation(session["conversation"]))
        return make_response(page, 200, {"Content-Type": "text/html"})

    page = HTML_SKELETON.format(conversation=render_conversation(session["conversation"]))
    return make_response(page, 200, {"Content-Type": "text/html"})

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))  
    app.run(host="0.0.0.0", port=port)
