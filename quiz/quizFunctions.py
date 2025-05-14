import ollama


def llamagen(section):
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
    return questions

def makeHTML(all_questions):
    quizpage = """
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
            quizpage += f"""
            <div>
                <label for="answer_{question_index}">{question}</label><br>
                <input type="hidden" name="questions[]" value="{question}">
                <input type="text" id="answer_{question_index}" name="answers[]" placeholder="Your answer here" required>
            </div>
            """
            question_index += 1

    quizpage += """
            <input type="submit" value="Submit">
        </form>
    </body>
    </html>
    """
    return quizpage


def grade(question,answer,total_score):
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
                    f'Question: {question}\n'
                    f'Students Answer: {answer}'
                )
            }
        ]
    )
    score = int(ollama_response.get('message', {}).get('content', '0').strip())
    total_score += score
    return total_score

def finalGrade(total_score):
    final_grade = (total_score / 200) * 100
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
