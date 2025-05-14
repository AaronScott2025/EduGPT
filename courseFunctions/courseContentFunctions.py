import json

from LLM import process
import ollama

def generateCoursework(query_param,course_name):
    content = process.LLM(query_param, f"Generate a detailed and informative coursework on {course_name}."
                                       "You need to generate headers for everything that may be relevant to the prompted course. Return only"
                                       " a comma separated list of course names, and no other words. These captions should be informative only, not"
                                       " hands on"
                                       " Example:"
                                       " Input: 'Course: Introduction to punctuation'"
                                       " Output:"
                                       " Introduction, Periods, Commas, Semicolons, Colons, Question Marks, Exclamation Points, Quotation Marks, Apostrophes, Parentheses, Dashes, Hyphens, Ellipses, Punctuation Practice "
                                       f" Provide structured lessons and key concepts based on {query_param}."
                                       f" Mantain the context of the one lesson, dont dive into other chapters")

    ollama_response = ollama.chat(
        model='Llama3',
        messages=[
            {
                'role': 'system',
                'content': 'You are a system that takes out excessive text from a comma seperated list of course names.'
            },
            {
                'role': 'user',
                'content': f'Given the following content: {content}. '
                           f'Take out any excessive text containing irrelevant info. Dont add any additional text either. '
                           f'You should return a plain comma seperated list with no additional text added. Dont say anything else other than the list'
            }
        ]
    )
    ollama_response_array = ollama_response.get('message', {}).get('content', '').split(",")
    arrayforcontentconstruct = ""
    for header in ollama_response_array:
        headerCourse = header
        contentforheader = process.LLM(
            query_param,
            f"You need to generate course content for {query_param}. The header you are generating for is the subheader: {header} and the content should be 3 to 6 paragraphs long. The content is for a student"
            " without generating new headers, and should vary in size depending on the requirements of the topic. Dont give any additional text, just the content."
        )
        cleanedcontent = ollama.chat(
            model='Llama3',
            messages=[
                {
                    'role': 'system',
                    'content': f'You are a system that fixes course work for a {query_param} course content on {header}'
                },
                {
                    'role': 'user',
                    'content': f'Given the following content: {contentforheader}. '
                               f'Take out any irrelevant text. Dont add any additional text either. '
                               f'If the content is completely irrelevant, create 4 paragraphs about {header} that is accurate and relevant without any additional text.'
                }
            ]
        )
        x = cleanedcontent.get('message', {}).get('content', '')
        x = x.split(":", 1)[1].strip()
        headerCourse = f"{headerCourse} | {x}"
        arrayforcontentconstruct = f" @ {arrayforcontentconstruct} @ {headerCourse}"

    content_sections = [section.strip() for section in arrayforcontentconstruct.split(" @ ") if section.strip()]
    return content_sections

def genHTML(course_name, content_sections):

    json_sections = json.dumps(content_sections)

    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{course_name} - Course Content</title>
        <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap" rel="stylesheet">
        <style>
            body {{
                font-family: 'Roboto', sans-serif;
                margin: 0;
                padding: 20px;
                background: linear-gradient(135deg, #a8edea, #fed6e3);
            }}
            .container {{
                background: #fff;
                padding: 2em;
                border-radius: 12px;
                box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
                width: 80%;
                max-width: 800px;
                margin: auto;
            }}
            h2 {{
                text-align: center;
                color: #333;
            }}
            a {{
                text-decoration: none;
                color: inherit;
                cursor: pointer;
            }}
            .section {{
                margin-top: 20px;
                padding-bottom: 10px;
                border-bottom: 2px solid #007BFF;
            }}
            .section h3 {{
                color: #007BFF;
                font-size: 1.5em;
                margin-bottom: 5px;
            }}
            .section p {{
                font-size: 1.1em;
                color: #555;
            }}
            .quiz-button-container {{
                text-align: center;
                margin-top: 30px;
            }}
            button {{
                background-color: #007BFF;
                border: none;
                color: white;
                padding: 10px 20px;
                font-size: 1.1em;
                border-radius: 4px;
                cursor: pointer;
            }}
            button:hover {{
                background-color: #0056b3;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h2>{course_name} - Course Content</h2>
            <h4>Click on a section if you need any additional clarification on the content.</h4>
    """

    for section in content_sections:
        if "|" in section:
            header, content = section.split(" | ", 1)
            safe_content = content.strip().replace("'", "\\'").replace('"', '\\"')
            html_content += f"""
            <div class="section">
                <h3>{header.strip()}</h3>
                <p>
                    <a href="#" onclick="redirectToChatbot(`{safe_content}`)">{content.strip()}</a>
                </p>
            </div>
            """

    # Append the quiz button and include the serialized content_sections as a JS variable.
    html_content += f"""
            <div class="quiz-button-container">
                <button type="button" onclick="startQuiz()">Start Quiz</button>
            </div>
        </div>
        <script>
            var contentSections = {json_sections};

            function redirectToChatbot(content) {{
                window.location.href = `/chatbot?content=${{encodeURIComponent(content)}}`;
            }}

            function startQuiz() {{
                window.location.href = '/quiz?contentSections=' + encodeURIComponent(JSON.stringify(contentSections));
            }}
        </script>
    </body>
    </html>
    """

    return html_content