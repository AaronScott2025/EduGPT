import requests
from flask import Flask, render_template, request, jsonify
from supabase import create_client, Client
import ollama
from chatBot import chatbot
from courseFunctions import courseContentFunctions, courseFunctions
from LLM import process
import os

SUPABASE_URL = "https://kkkfxnvmknncxdwadqvg.supabase.co"
SUPABASE_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtra2Z4bnZta25uY3hkd2FkcXZnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDU5NTA2NzUsImV4cCI6MjA2MTUyNjY3NX0.bBBMoEiexmjxTv_dnY693QEWsWJxkQcn8jYcwTTHe_g"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_API_KEY)
app = Flask(__name__)

@app.route('/') #Main GUI
def main_screen():
    return render_template('MainGUI.html')


@app.route('/Courses') #Display Generated Courses based on Query
def courses():
    query_param = request.args.get('query')
    prof = request.args.get('proficiency')
    if not query_param:
        return "Query parameter is missing.", 400

    query = query_param.replace(" ", "")
    print(f"Debug: Searching for fileName '{query}'.")
    try:
        link, fileName = courseFunctions.fetchPDF(supabase,query)
        try:
            pdf_response = requests.get(link)
            pdf_response.raise_for_status()

            pdf_path = os.path.join("context.pdf")
            with open(pdf_path, "wb") as file:
                file.write(pdf_response.content)
            print(f"PDF '{fileName}' downloaded and saved successfully.")

            process.loadRAG(pdf_path, query)
            course = process.LLM(query, f"Based on the sections in the context, generate names for a 10 course workflow for a {prof} student. "
                    "The courses should be in chronological order in which the student should learn them. Entry level course first, Advanced course last. "
                    "Don't use any additional text outside of the Array.")
            ollama_response = ollama.chat(model='Llama3', messages=[
                {'role': 'system', 'content': 'You are a system that takes out excessive text from a comma seperated list of course names.'},
                {'role': 'user', 'content': f'Given the following content: {course}. '
                                            f'Take out any excessive text containing irrelevant info. Dont add any additional text either. '
                                            f''
                                            f'You should return a plain comma seperated list with no additional text added. Dont say anything else other than the list'}
            ])
            course_list = ollama_response.get('message', {}).get('content', '').split(",")
            html_content = courseFunctions.genHTML(query_param,course_list)

            with open("./templates/Courses.html", "w", encoding="utf-8") as file:
                file.write(html_content)

            return html_content

        except Exception as download_error:
            print("Error during PDF download:", download_error)
            return f"Error during PDF download: {download_error}", 500

    except Exception as db_error:
        print("Error occurred while querying the database:", db_error)
        return f"Error occurred while querying the database: {db_error}", 500

@app.route('/coursecontent')
def course_content():
    course_name = request.args.get('course')
    query_param = request.args.get('query_param')
    try:
        content_sections = courseContentFunctions.generateCoursework(query_param, course_name)
        return courseContentFunctions.genHTML(course_name, content_sections)
    except Exception as error:
        print("Error generating course content:", error)
        return f"Error generating course content: {error}", 500
    
@app.route('/return', methods=['GET'])
def returntocourses():
    return render_template('Courses.html')

@app.route('/chatbot')
def chatbot_ui():
    content = request.args.get("content", "Let's chat!")
    return chatbot.loadchatbot(content)

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_message = data["message"]
    content = data["content"]

    return jsonify({"response": chatbot.chat(ollama, content, user_message)})


@app.route('/quiz', methods=['GET'])
def quiz():
    content_sections = request.args.get('contentSections')
    all_questions = []
    print (content_sections)
    x = 0
    for section in content_sections:
        if not x == 20:
            ollama_response = ollama.chat(
                model='Llama3',
                messages=[
                    {
                        'role': 'system',
                        'content': (
                            f'Given the context: {section} you will generate 2 questions about the text, '
                            f'and separate them with a "|" symbol. Only generate the 2 questions with the symbol, '
                            f'no additional text. The user must be able to figure out the answer from the text and ONLY from the text. No inferences. '
                            f'Example Output: How would you define Reinforcement Learning? | Explain the idea of delayed feedback'
                        )
                    }
                ]
            )
            print(ollama_response.get('message', {}).get('content', ''))
            questions_str = ollama_response.get('message', {}).get('content', '')
            questions = [q.strip() for q in questions_str.split('|') if q.strip()]
            all_questions.append(questions)
            x+=1
        else:
            break
    html_form = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Quiz</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 2em; }
            label { font-weight: bold; }
            div { margin-bottom: 1em; }
        </style>
    </head>
    <body>
        <h1>Quiz</h1>
        <form action="/grading" method="post">
    """

    question_index = 0
    for questions in all_questions:
        for question in questions:
            html_form += f"""
            <div>
                <label for="answer_{question_index}">{question}</label><br>
                <input type="hidden" name="questions[]" value="{question}">
                <input type="text" id="answer_{question_index}" name="answers[]" placeholder="Your answer here" required>
            </div>
            """
            question_index += 1
            print(ollama_response.get('message', {}).get('content', ''))

    html_form += """
            <input type="submit" value="Submit">
        </form>
    </body>
    </html>
    """
    return html_form


@app.route('/grading', methods=['POST'])
def grading():
    questions = request.form.getlist('questions[]')
    answers = request.form.getlist('answers[]')
    total_score = 0
    num_questions = len(questions)

    for x in range(num_questions):
        ollama_response = ollama.chat(
            model='Llama3',
            messages=[
                {
                    'role': 'system',
                    'content': (
                        f'You are a grading system that will rank a students score from 1 through 10 based on the correctness of the response. You should only respond with the number, and no additional text.\n'
                        f'Example:\n'
                        f'Question: What are some common applications of Reinforcement Learning?\n'
                        f'Students Answer: Reinforcement learning is widely used in robotics, game playing, autonomous vehicles, personalized recommendations, and financial trading to optimize decision-making through trial-and-error interactions.\n'
                        f'Output: 10\n'
                        f'Example2:\n'
                        f'Question: What are some common applications of Reinforcement Learning?\n'
                        f'Students Answer: Apples and bananas\n'
                        f'Output: 1\n'
                        f'This is the one you should grade:\n'
                        f'Question: {questions[x]}\n'
                        f'Students Answer: {answers[x]}'
                    )
                }
            ]
        )
        score = int(ollama_response.get('message', {}).get('content', '0').strip())
        total_score += score

    final_grade = (total_score / 400) * 100 if num_questions > 0 else 0
    if final_grade < 60:
        msg = "Try to keep studying this topic, you have scored a VERY low score, and dont demonstrate full understanding."
    elif final_grade < 70:
        msg = "Youll need to review a bit more of this topic, but good job"
    elif final_grade < 90:
        msg = "Great Work! You've shown a very solid understanding of this topic!"
    else:
        msg = "Amazing! You've mastered this topic!"

    Grade = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Grading Result</title>
    </head>
    <body>
        <h1>Your Final Grade: {final_grade:.2f}%</h1>
        <h2>{msg}</h2>
        <form action="/return" method="get">
            <button type="submit">Return</button>
        </form>
    </body>
    </html>
    """

    return Grade

if __name__ == '__main__':
    app.run(debug=True)

