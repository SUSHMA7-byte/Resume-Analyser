from flask import Flask, request, render_template, redirect, url_for
import fitz  
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import os
import tempfile

app = Flask(__name__)

def check_resume_match(resume_path, job_keywords):
    try:
        with fitz.open(resume_path) as pdf_document:
            resume_text = ""
            for page_number in range(pdf_document.page_count):
                page = pdf_document[page_number]
                resume_text += page.get_text()

        resume_tokens = word_tokenize(resume_text.lower())
        stop_words = set(stopwords.words('english'))

        filtered_tokens = []
        for word in resume_tokens:
            if word.isalnum() and word not in stop_words:
                filtered_tokens.append(word)

        matched_keywords = []
        for keyword in job_keywords:
            keyword_parts = keyword.split()
            if all(keyword_part.lower() in filtered_tokens for keyword_part in keyword_parts):
                matched_keywords.append(keyword)

        return matched_keywords

    except Exception as e:
        return f"Error processing the resume: {e}"


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        if 'resume' not in request.files:
            return "No file part"
        
        resume_file = request.files['resume']

        if resume_file.filename == '':
            return "No selected file"

        if resume_file and resume_file.filename.endswith('.pdf'):
            temp_dir = tempfile.gettempdir()
            temp_path = os.path.join(temp_dir, "temp_resume.pdf")
            resume_file.save(temp_path)

            job_keywords = request.form.get("job_keywords", "")
            job_keywords = [keyword.strip() for keyword in job_keywords.split(',')]

            matched_keywords = check_resume_match(temp_path, job_keywords)

            return render_template("index.html", matched_keywords=matched_keywords, keywords=job_keywords)
    
    return render_template("index.html", matched_keywords=None)


if __name__ == "__main__":
    app.run(debug=True)
