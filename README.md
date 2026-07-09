# ResumeVision – AI Resume Analyzer

ResumeVision is an AI-powered web application that analyzes resumes using Google's Gemini API. It helps job seekers evaluate ATS compatibility, identify missing skills and resume sections, and receive personalized recommendations to improve their chances of getting shortlisted.

## Features

- AI-powered resume analysis using Google Gemini API
- ATS compatibility score with detailed explanation
- Resume summary generation
- Technical, tools, and soft skills extraction
- Missing and weak section detection
- Keyword gap analysis based on a target job description
- Personalized resume improvement suggestions
- AI-generated interview questions
- Secure resume processing (files are not permanently stored)

## Tech Stack

**Backend**
- Python
- Flask

**Frontend**
- HTML
- CSS
- JavaScript

**AI**
- Google Gemini API

**Libraries**
- pdfplumber
- python-docx
- python-dotenv
- google-generativeai

## Installation

```bash
git clone https://github.com/Sudhanshu20055/resumevision.git
cd resumevision

python -m venv venv
```

Activate the virtual environment.

**Windows**

```bash
venv\Scripts\activate
```

**macOS/Linux**

```bash
source venv/bin/activate
```

Install the required packages.

```bash
pip install -r requirements.txt
```

Create a `.env` file and add your Gemini API key.

```env
GEMINI_API_KEY=your_api_key
```

Run the application.

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
│── .env.example
│── templates/
│── static/
│── utils/
└── README.md
```

## Workflow

1. Upload a resume (PDF, DOCX, or TXT).
2. Optionally provide a target job description.
3. ResumeVision extracts the resume content.
4. Gemini AI analyzes the resume.
5. The application generates:
   - ATS Compatibility Score
   - Skills Analysis
   - Missing Resume Sections
   - Keyword Gap Analysis
   - Resume Improvement Suggestions
   - Personalized Interview Questions

## Future Enhancements

- Cover Letter Generator
- Resume Comparison
- LinkedIn Profile Analysis
- Resume Template Suggestions
- Downloadable PDF Report

## Author

**Sudhanshu Ranjan**

GitHub: https://github.com/Sudhanshu20055

## License

This project is intended for educational and learning purposes.