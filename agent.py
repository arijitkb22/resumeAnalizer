import streamlit as st
import os
from typing import Dict, Optional
import pdfplumber
from docx import Document
from groq import Groq
import traceback
import io

class ResumeAnalyzer:
    def __init__(self):
        """Initialize the resume analyzer with Groq API from Streamlit secrets"""
        try:
            self.client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        except Exception:
            raise ValueError("GROQ_API_KEY not found in Streamlit secrets")
        
        self.default_prompts = {
    "structure": (
        "You are a seasoned HR professional with 15+ years of experience in hiring, "
        "who has analyzed millions of resumes across various industries. Your goal is to help candidates "
        "improve their resumes by providing expert feedback on structure. \n\n"
        "Analyze the given resume and evaluate whether it follows a logical and professional structure. "
        "Does it include key sections such as 'Contact Information', 'Summary', 'Education', 'Work Experience', "
        "'Skills', and 'Certifications' (if applicable)? Are the sections well-organized and easy to navigate? "
        "Provide constructive suggestions to enhance clarity, readability, and flow."
    ),

    "skills": (
        "You are an experienced talent acquisition specialist who has matched thousands of professionals to their ideal roles. "
        "Your task is to assess the skills listed in the resume and ensure they align with industry expectations. \n\n"
        "Check if the listed skills are relevant to the candidate's field. Are they clearly stated and well-categorized "
        "(e.g., technical skills, soft skills, tools, languages)? \n"
        "Suggest any missing key skills that would strengthen the resume and make the candidate more competitive. "
        "Also, recommend better phrasing or structuring if necessary."
    ),

    "grammar": (
        "You are an expert resume editor and linguistic specialist with a deep understanding of professional communication. "
        "Your job is to thoroughly check the resume for grammatical errors, spelling mistakes, and awkward phrasing. \n\n"
        "Identify any grammatical issues, punctuation errors, or inconsistent verb tenses. "
        "Highlight areas where clarity can be improved and suggest alternative wording to make the resume more polished and professional."
    ),

    "experience": (
        "You are a recruitment consultant who has reviewed thousands of resumes to find the best candidates for top companies. "
        "Your task is to analyze the 'Work Experience' section of the resume and ensure it effectively showcases achievements. \n\n"
        "Does the candidate describe their experience with action-oriented bullet points? "
        "Are there quantifiable achievements (e.g., 'Increased sales by 30%', 'Led a team of 10') that demonstrate impact? \n"
        "Suggest improvements to make this section stronger, emphasizing measurable results, leadership, and industry-specific keywords."
    )
}

    def extract_text_from_pdf(self, pdf_file) -> tuple[str, str]:
        """
        Extract text from PDF file with enhanced error handling
        Returns: (text, error_message)
        """
        try:
            # Convert StreamlitUploadedFile to bytes
            pdf_bytes = pdf_file.read()
            pdf_file.seek(0)  # Reset file pointer
            
            # Try to open PDF from bytes
            with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
                text = ""
                for page_num, page in enumerate(pdf.pages, 1):
                    try:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text
                        else:
                            return "", f"Page {page_num} appears to be empty or unreadable"
                    except Exception as e:
                        return "", f"Error extracting text from page {page_num}: {str(e)}"
                
                if not text.strip():
                    return "", "No text could be extracted from the PDF. The file might be scanned or image-based."
                return text, ""
                
        except Exception as e:
            error_detail = traceback.format_exc()
            return "", f"PDF processing error: {str(e)}\n\nTechnical details:\n{error_detail}"

    def extract_text_from_docx(self, docx_file) -> tuple[str, str]:
        """
        Extract text from DOCX file with enhanced error handling
        Returns: (text, error_message)
        """
        try:
            docx_bytes = docx_file.read()
            docx_file.seek(0)
            
            doc = Document(io.BytesIO(docx_bytes))
            text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
            
            if not text.strip():
                return "", "No text could be extracted from the DOCX file. The file might be empty or corrupted."
            return text, ""
            
        except Exception as e:
            error_detail = traceback.format_exc()
            return "", f"DOCX processing error: {str(e)}\n\nTechnical details:\n{error_detail}"

    def extract_text(self, file) -> tuple[Optional[str], Optional[str]]:
        """Extract text from uploaded file with enhanced error handling"""
        try:
            if not file:
                return None, "No file uploaded"
                
            file_extension = os.path.splitext(file.name)[1].lower()
            
            if file_extension == '.pdf':
                return self.extract_text_from_pdf(file)
            elif file_extension in ['.docx', '.doc']:
                return self.extract_text_from_docx(file)
            else:
                return None, f"Unsupported file type: {file_extension}. Please upload a PDF or DOCX file."
                
        except Exception as e:
            error_detail = traceback.format_exc()
            return None, f"File processing error: {str(e)}\n\nTechnical details:\n{error_detail}"

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
    
    try:
        analyzer = ResumeAnalyzer()
        
        uploaded_file = st.file_uploader("Upload your resume (PDF or DOCX)", type=['pdf', 'docx'])

        if uploaded_file:
            with st.spinner("Extracting text from resume..."):
                resume_text, error_message = analyzer.extract_text(uploaded_file)
                
            if resume_text:
                st.success("Resume text extracted successfully!")
                
                # Show extracted text in expandable section
                with st.expander("View Extracted Text", expanded=False):
                    st.text_area("Extracted Text", resume_text, height=300)
                
                # Analysis options
                analysis_type = st.radio(
                    "Choose analysis type:",
                    ["Default Analysis", "Custom Prompt"]
                )

                if analysis_type == "Default Analysis":
                    if st.button("Analyze Resume"):
                        with st.spinner("Analyzing resume..."):
                            feedback = analyzer.analyze_resume(resume_text)
                            
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

            else:
                st.error(error_message)
                st.info("Troubleshooting tips:")
                st.markdown("""
                - Make sure the PDF is not password protected
                - Check if the PDF contains actual text (not just scanned images)
                - Try converting scanned PDFs using OCR software first
                - Verify the file is not corrupted by opening it in another PDF reader
                """)
                
    except ValueError as e:
        st.error(f"Configuration Error: {str(e)}")
        st.info("Please make sure GROQ_API_KEY is properly configured in Streamlit secrets.")
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        st.info("Please try again or contact support if the issue persists.")

if __name__ == "__main__":
    main()