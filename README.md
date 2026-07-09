# ResumeVision

ResumeVision is an AI-powered resume analyzer that helps job seekers evaluate and improve their resumes using Google's Gemini API. It analyzes uploaded resumes, estimates ATS compatibility, identifies missing or weak sections, extracts skills, and provides personalized suggestions to increase the chances of getting shortlisted.

## Features

- ATS compatibility score with explanation
- Resume summary
- Technical, tools, and soft skills extraction
- Missing resume section detection
- Weak section analysis with suggestions
- Keyword gap analysis using a job description
- Personalized resume improvement recommendations
- AI-generated interview questions

## Tech Stack

- Python
- Flask
- Google Gemini API
- HTML
- CSS
- JavaScript
- pdfplumber
- python-docx

## Installation

```bash
git clone https://github.com/Sudhanshu20055/resumevision.git
cd resumevision

python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
```

Create a `.env` file and add your Gemini API key.

```env
GEMINI_API_KEY=your_api_key
```

Run the application:

```bash
python app.py
```

Open your browser:

```
http://127.0.0.1:5000
```

## Project Structure

```
resumevision/
│── app.py
│── requirements.txt
│── templates/
│── static/
│── utils/
└── README.md
```

## Workflow

1. Upload your resume (PDF, DOCX, or TXT).
2. Optionally provide a job description.
3. ResumeVision extracts the resume text.
4. Gemini AI analyzes the content.
5. The application generates:
   - ATS Score
   - Skills Analysis
   - Missing Sections
   - Keyword Gaps
   - Resume Improvement Suggestions
   - Interview Questions

## Future Enhancements

- Cover Letter Generator
- LinkedIn Profile Review
- Resume Template Suggestions
- Multi-language Resume Analysis

## License

This project is created for educational and learning purposes.