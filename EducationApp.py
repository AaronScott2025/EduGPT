import requests
from flask import Flask, render_template, request, jsonify
from supabase import create_client, Client
import ollama
from chatBot import chatbot
from courseFunctions import courseContentFunctions, courseFunctions
from LLM import process
import os

from quiz import quizFunctions

SUPABASE_URL = "https://kkkfxnvmknncxdwadqvg.supabase.co"
SUPABASE_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtra2Z4bnZta25uY3hkd2FkcXZnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDU5NTA2NzUsImV4cCI6MjA2MTUyNjY3NX0.bBBMoEiexmjxTv_dnY693QEWsWJxkQcn8jYcwTTHe_g"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_API_KEY)
app = Flask(__name__)

@app.route('/') #Main GUI
def main_screen():
    return render_template('MainGUI.html')


@app.route('/Courses') #Display Generated Courses based on Query
def courses():
    query_param = request.args.get('query') #Topic
    prof = request.args.get('proficiency') #Proficiency

    query = query_param.replace(" ", "") #For Processing
    try:
        link, fileName = courseFunctions.fetchPDF(supabase,query) #Get PDF from Supabase
        try:
            pdf_response = requests.get(link)
            pdf_response.raise_for_status()

            pdf_path = os.path.join("context.pdf") #Save as context.pdf in local
            with open(pdf_path, "wb") as file:
                file.write(pdf_response.content)

            process.loadRAG(pdf_path, query) #Creates embeddings if they dont exist already.
            course = process.LLM(query, f"Based on the sections in the context, generate names for a 10 course workflow for a {prof} student. " #Generates workflow
                    "The courses should be in chronological order in which the student should learn them. Entry level course first, Advanced course last. "
                    "Don't use any additional text outside of the Array.")
            ollama_response = ollama.chat(model='Llama3', messages=[ #Cleanup-model. Cleans the data from the csv by removing additional text.
                {'role': 'system', 'content': 'You are a system that takes out excessive text from a comma seperated list of course names.'},
                {'role': 'user', 'content': f'Given the following content: {course}. '
                                            f'Take out any excessive text containing irrelevant info. Dont add any additional text either. '
                                            f''
                                            f'You should return a plain comma seperated list with no additional text added. Dont say anything else other than the list'}
            ])
            course_list = ollama_response.get('message', {}).get('content', '').split(",") #Turn into CSV
            html_content = courseFunctions.genHTML(query_param,course_list) #Generate the HTML

            with open("./templates/Courses.html", "w", encoding="utf-8") as file: #Save HTML
                file.write(html_content)

            return html_content #Return HTML

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
        content_sections = courseContentFunctions.generateCoursework(query_param, course_name) #Generates Coursework through RAG
        return courseContentFunctions.genHTML(course_name, content_sections) # Creates the HTML for the content
    except Exception as error:
        print("Error generating course content:", error)
        return f"Error generating course content: {error}", 500
    
@app.route('/return', methods=['GET'])
def returntocourses():
    return render_template('Courses.html') #Saved Courses Page

@app.route('/chatbot')
def chatbot_ui():
    content = request.args.get("content")
    return chatbot.loadchatbot(content) #Load Chatbot UI

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_message = data["message"] # Question
    content = data["content"] # Content for Reference

    return jsonify({"response": chatbot.chat(ollama, content, user_message)}) #Return Response


@app.route('/quiz', methods=['GET'])
def quiz():
    content_sections = request.args.get('contentSections') # All the content sections
    all_questions = [] #Allocate Questions variable
    x = 0 # Failsafe (Stops at 20 questions)
    for section in content_sections: #All Sections
        if not x == 10: #Failsafe
            questions = quizFunctions.llamagen(section) #Generate questions
            all_questions.append(questions) #Append to all-question list
            x+=1
        else:
            break #Failsafe
    quizpage = quizFunctions.makeHTML(all_questions) #Generate HTML
    return quizpage #Returns HTML


@app.route('/grading', methods=['POST'])
def grading():
    questions = request.form.getlist('questions[]') #All Questions
    answers = request.form.getlist('answers[]') #All Answers
    total_score = 0 # Set Total Score
    for x in range(len(questions)): # All Questions
        total_score = quizFunctions.grade(questions[x],answers[x],total_score) # Total score + Graded Section
    return quizFunctions.finalGrade(total_score) #Math + HTMLGeneration

if __name__ == '__main__':
    app.run(debug=True)

