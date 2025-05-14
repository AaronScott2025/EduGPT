
def fetchPDF(supabase,query):
    response = supabase.table("PDF_Files").select("*").ilike("fileName", query).execute()
    print("Debug: Supabase response data:", response.data)

    if not response.data:
        print(f"File '{query}' not found in the database.")
        return f"File '{query}' not found.", 404

    pdf_record = response.data[0]
    fileName = pdf_record["fileName"]
    link = pdf_record["link"]
    return link, fileName

def genHTML(query_param,course_list):
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Course List for {query_param}</title>
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
            }}

            h2 {{
                margin-bottom: 1em;
                font-size: 1.8em;
                color: #333;
            }}

            ul {{
                list-style-type: none;
                padding: 0;
            }}

            li {{
                background: white;
                margin: 10px 0;
                padding: 10px;
                border-radius: 6px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                font-size: 1.2em;
            }}

            a {{
                text-decoration: none;
                color: #007BFF;
                font-weight: bold;
            }}

            a:hover {{
                text-decoration: underline;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h2>Course List for {query_param}</h2>
            <ul>
    """

    for course in course_list:
        html_content += f'<li><a href="/coursecontent?course={course.strip()}&query_param={query_param}">{course.strip()}</a></li>'

    html_content += """
            </ul>
        </div>
    </body>
    </html>
    """
    return html_content