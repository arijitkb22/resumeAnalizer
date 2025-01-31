import pdfplumber
from docx import Document
from groq import Groq
import os
from typing import Dict, Optional
from dotenv import load_dotenv

class ResumeAnalyzer:
    def __init__(self):
        """Initialize the resume analyzer with Groq API from environment variables"""
        load_dotenv()  # Load environment variables
        api_key = os.getenv('GROQ_API_KEY')
        if not api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables")
        
        self.client = Groq(api_key=api_key)
        
        # Default prompts
        self.default_prompts = {
            "structure": "Does the resume follow a clear structure with sections like 'Education', 'Work Experience', 'Skills', etc.? Please suggest improvements.",
            "skills": "Are the skills listed relevant to the job role and clear? Provide suggestions for additional skills or clarifications.",
            "grammar": "Is the resume free from grammar or spelling mistakes? List any issues and suggest corrections.",
            "experience": "Does the work experience section include clear and measurable achievements? Suggest improvements for clarity."
        }

    def extract_text_from_pdf(self, pdf_file) -> str:
        """Extract text from PDF file"""
        text = ""
        with pdfplumber.open(pdf_file) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""
        return text

    def extract_text_from_docx(self, docx_file) -> str:
        """Extract text from DOCX file"""
        doc = Document(docx_file)
        return "\n".join([paragraph.text for paragraph in doc.paragraphs])

    def get_feedback_from_model(self, resume_text: str, prompt: str) -> str:
        """Get feedback using Groq's Mixtral model"""
        try:
            completion = self.client.chat.completions.create(
                model="mixtral-8x7b-32768",
                messages=[
                    {
                        "role": "user",
                        "content": f"{prompt}\n\nResume Text: {resume_text}"
                    }
                ],
                max_tokens=1000,
                temperature=0.7
            )
            return completion.choices[0].message.content
        except Exception as e:
            return f"Error getting feedback: {str(e)}"

    def extract_text(self, file) -> Optional[str]:
        """Extract text from uploaded file"""
        try:
            file_extension = os.path.splitext(file.name)[1].lower()
            
            if file_extension == '.pdf':
                return self.extract_text_from_pdf(file)
            elif file_extension in ['.docx', '.doc']:
                return self.extract_text_from_docx(file)
            else:
                return None
        except Exception as e:
            return None

    def analyze_resume(self, resume_text: str, prompts: Dict[str, str] = None) -> Dict[str, str]:
        """Analyze resume with given prompts"""
        prompts = prompts or self.default_prompts
        feedback = {}
        
        for key, prompt in prompts.items():
            feedback[key] = self.get_feedback_from_model(resume_text, prompt)
        
        return feedback

    def analyze_single_prompt(self, resume_text: str, prompt: str) -> str:
        """Analyze resume with a single custom prompt"""
        return self.get_feedback_from_model(resume_text, prompt)