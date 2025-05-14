import json


def chat(ollama,content,user_message):
    reply = ollama.chat(
        model='Llama3',
        messages=[
            {
                'role': 'system',
                'content': f'You are answering a users questions reguarding the following section: {content}'
                           f''
                           f'You should guide them to an understanding in their question. Base your response off the user query, and use the content as a reference. '
            },
            {
                'role': 'user',
                'content': f'{user_message}'
            }
        ]
    )
    return reply.get('message', {}).get('content', '')

def loadchatbot(content):
    chatbot_html = f""" 
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Chatbot UI</title>
        <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap" rel="stylesheet">
        <style>
            body {{
                margin: 0;
                padding: 0;
                background: linear-gradient(135deg, #a8edea, #fed6e3);
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                font-family: 'Roboto', sans-serif;
            }}
            .container {{
                background: #fff;
                padding: 2em 3em;
                border-radius: 12px;
                box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
                text-align: center;
                width: 400px;
            }}
            h2 {{
                margin-bottom: 1em;
                font-size: 1.8em;
                color: #333;
            }}
            .chat-box {{
                height: 300px;
                overflow-y: auto;
                border: 1px solid #ccc;
                border-radius: 6px;
                padding: 10px;
                background: white;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}
            .chat-input {{
                display: flex;
                margin-top: 10px;
            }}
            input {{
                flex: 1;
                padding: 10px;
                border: none;
                outline: none;
                border-radius: 6px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                font-size: 1.2em;
            }}
            button {{
                padding: 10px;
                border: none;
                background-color: #007BFF;
                color: white;
                cursor: pointer;
                border-radius: 6px;
                margin-left: 5px;
                font-size: 1.2em;
            }}
            button:hover {{
                background-color: #0056b3;
            }}
            .back-button {{
                margin-top: 10px;
                padding: 10px;
                border: none;
                background-color: #ff4d4d;
                color: white;
                cursor: pointer;
                border-radius: 6px;
                font-size: 1.2em;
            }}
            .back-button:hover {{
                background-color: #cc0000;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h2>Teaching Assistant</h2>
            <p>{content}</p>
            <div class="chat-box" id="chatBox">
            </div>
            <div class="chat-input">
                <input type="text" id="userInput" placeholder="Type a message...">
                <button onclick="sendMessage()">Send</button>
            </div>
            <button class="back-button" onclick="goBack()">Back</button>
        </div>

    <script>
        function sendMessage() {{
            var inputField = document.getElementById("userInput");
            var chatBox = document.getElementById("chatBox");
            var userMessage = inputField.value.trim();

            if (userMessage !== "") {{
                // Display user's message in chat box
                var userDiv = document.createElement("div");
                userDiv.textContent = "You: " + userMessage;
                userDiv.style.padding = "10px";
                userDiv.style.margin = "5px";
                userDiv.style.backgroundColor = "#007bff";
                userDiv.style.color = "white";
                userDiv.style.borderRadius = "5px";
                chatBox.appendChild(userDiv);

                // Send message to backend /chat route
                fetch('/chat', {{
                    method: 'POST',
                    headers: {{
                        'Content-Type': 'application/json'
                    }},
                   body: JSON.stringify({{ message: userMessage, content: {json.dumps(content)} }})

                }})
                .then(response => {{
                    if (!response.ok) {{
                        throw new Error(`HTTP error! Status: ${{response.status}}`);
                    }}
                    return response.json();  // Ensure JSON is returned
                }})
                .then(data => {{
                    var botDiv = document.createElement("div");
                    botDiv.textContent = "Bot: " + data.response;
                    botDiv.style.padding = "10px";
                    botDiv.style.margin = "5px";
                    botDiv.style.backgroundColor = "#f4f4f4";
                    botDiv.style.color = "black";
                    botDiv.style.borderRadius = "5px";
                    chatBox.appendChild(botDiv);
                }})
                .catch(error => {{
                    console.error('Error:', error);
                    var errorDiv = document.createElement("div");
                    errorDiv.textContent = "Error: Unable to get response.";
                    errorDiv.style.padding = "10px";
                    errorDiv.style.margin = "5px";
                    errorDiv.style.backgroundColor = "red";
                    errorDiv.style.color = "white";
                    errorDiv.style.borderRadius = "5px";
                    chatBox.appendChild(errorDiv);
                }});
                inputField.value = ""; // Clear input field
            }}
        }}
    </script>
    <script>
            function goBack() {{
    window.history.back();
    }}
        </script>
    </body>
    </html>
    """
    return chatbot_html