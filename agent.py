# app.py
import streamlit as st
import os
from typing import Dict, Optional
import pdfplumber
from docx import Document
from groq import Groq

class ResumeAnalyzer:
    def __init__(self):
        """Initialize the resume analyzer with Groq API from Streamlit secrets"""
        # Get API key from Streamlit secrets
        try:
            self.client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        except Exception:
            raise ValueError("GROQ_API_KEY not found in Streamlit secrets")
        
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

def main():
    st.set_page_config(page_title="Resume Analyzer", layout="wide")
    
    st.title("📄 Resume Analyzer")
    
    # Initialize analyzer
    try:
        analyzer = ResumeAnalyzer()
        
        # File upload
        uploaded_file = st.file_uploader("Upload your resume (PDF or DOCX)", type=['pdf', 'docx'])

        if uploaded_file:
            with st.spinner("Extracting text from resume..."):
                resume_text = analyzer.extract_text(uploaded_file)
                
            if resume_text:
                st.success("Resume text extracted successfully!")
                
                # Analysis options
                analysis_type = st.radio(
                    "Choose analysis type:",
                    ["Default Analysis", "Custom Prompt"]
                )

                if analysis_type == "Default Analysis":
                    if st.button("Analyze Resume"):
                        with st.spinner("Analyzing resume..."):
                            feedback = analyzer.analyze_resume(resume_text)
                            
                            # Display feedback in expandable sections
                            for section, comments in feedback.items():
                                with st.expander(f"{section.title()} Feedback", expanded=True):
                                    st.write(comments)
                                    
                else:  # Custom Prompt
                    custom_prompt = st.text_area(
                        "Enter your custom prompt:",
                        height=100,
                        placeholder="E.g., Analyze the resume's formatting and suggest improvements..."
                    )
                    
                    if custom_prompt and st.button("Get Custom Analysis"):
                        with st.spinner("Analyzing with custom prompt..."):
                            feedback = analyzer.analyze_single_prompt(resume_text, custom_prompt)
                            st.write(feedback)

                # Show extracted text in expandable section
                with st.expander("View Extracted Text", expanded=False):
                    st.text_area("Extracted Text", resume_text, height=300)
            else:
                st.error("Error extracting text from the file. Please make sure it's a valid PDF or DOCX file.")
                
    except ValueError as e:
        st.error(f"Configuration Error: {str(e)}")
        st.info("Please make sure GROQ_API_KEY is properly configured in Streamlit secrets.")
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()