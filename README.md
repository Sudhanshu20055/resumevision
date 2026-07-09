# ResumeLens

I built this because I kept hearing the same problem from friends applying
for jobs — they'd send out resumes and just... never hear back, with zero
idea why. No feedback, no idea if their resume was even getting past the
ATS filters companies use before a human even looks at it.

So this is a small web app where you upload your resume and it uses
Google's Gemini API to tell you:

- an ATS compatibility score (with reasoning, not just a random number)
- what skills it picked up from your resume (technical / tools / soft skills)
- which standard sections you're missing (Summary, Projects, etc.)
- which sections exist but are weak, and how to fix them
- keyword gaps if you paste in a job description you're targeting
- a list of concrete things to improve
- interview questions it thinks you'd likely get asked, based on your resume

## Stack

- Python + Flask on the backend
- Google Gemini API for the actual analysis
- pdfplumber for PDFs, python-docx for Word docs
- plain HTML/CSS/JS on the frontend, no React or build tools, kept it simple

## Running it locally

You'll need Python 3.10+.

\`\`\`bash
git clone <your-repo-url>
cd resumelens
python -m venv venv
venv\Scripts\activate      # on Mac/Linux: source venv/bin/activate
pip install -r requirements.txt
\`\`\`

Grab a free API key from [Google AI Studio](https://aistudio.google.com/apikey),
then:

\`\`\`bash
copy .env.example .env     # Mac/Linux: cp .env.example .env
\`\`\`

Open `.env` and drop your key in:

\`\`\`
GEMINI_API_KEY=your_key_here
\`\`\`

Then just run it:

\`\`\`bash
python app.py
\`\`\`

and open `http://127.0.0.1:5000`.

## How it's structured

\`\`\`
resumelens/
├── app.py                  → Flask routes
├── requirements.txt
├── .env.example
├── utils/
│   ├── resume_parser.py    → pulls text out of the uploaded file
│   └── gemini_analyzer.py  → builds the prompt + talks to Gemini
├── templates/
│   └── index.html
└── static/
    ├── style.css
    └── script.js
\`\`\`

## What happens under the hood

1. You drop in a resume (PDF/DOCX/TXT), optionally paste a job description
2. The backend extracts the raw text from whatever file you gave it
3. That text gets sent to Gemini along with a prompt that forces it to
   respond in a specific JSON structure (score, skills, gaps, etc.)
4. The frontend takes that JSON and renders it — the score dial, skill
   tags, section checklist, weak-section callouts, and the interview
   question tabs at the bottom

## Things worth knowing

- Model defaults to `gemini-2.0-flash`, changeable via `GEMINI_MODEL` in
  `.env` if you hit quota issues or want to try a different one
- 8MB upload limit
- Files get deleted right after text extraction, nothing gets stored
- Scanned/image-based PDFs won't work well since there's no OCR — it needs
  actual selectable text in the PDF
- This is a dev-server setup, not meant for production as-is

## If something breaks

- `GEMINI_API_KEY is not set` → check your `.env` file actually has the key in it, not the placeholder
- `429 quota exceeded` → your Google Cloud project probably needs billing linked, even though you won't get charged within free-tier limits
- Upload fails silently → check file type (pdf/docx/txt only) and size (<8MB)