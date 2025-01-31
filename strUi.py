import streamlit as st
import os
from agent import ResumeAnalyzer
from dotenv import load_dotenv

def main():
    # Load environment variables
    load_dotenv()
    
    st.set_page_config(page_title="Resume Analyzer", layout="wide")
    
    st.title("📄 Resume Analyzer & Job Search")
    
    try:
        analyzer = ResumeAnalyzer()
        
        # Create tabs for Resume Analyzer, Job Search, and Interview Questions
        tab1, tab2 = st.tabs(["🔍 Job Search & Interview Questions", "📄 Resume Analyzer"])

        # Tab 1: Job Search & Interview Questions
        with tab1:
            st.header("🔍 Job Search")
            job_title = st.text_input("Enter Job Title", placeholder="e.g., Software Engineer", key="job_title")
            experience_level = st.selectbox("Select Experience Level", ["Entry", "Mid", "Senior"])
            location = st.text_input("Enter Location", placeholder="e.g., India", value="India", key="location")
            days_ago = st.slider("Jobs posted within (days)", min_value=1, max_value=30, value=30, key="days_ago")
            role = st.selectbox("Select Your role here", ["Frontend", "Backend", "Testing"])

            if job_title and st.button("Search Jobs", key="search_jobs"):
                with st.spinner("Searching for jobs..."):
                    job_results = analyzer.search_jobs(job_title, experience_level, role, location, days_ago)
                    st.write(job_results)

            st.header("❓ Interview Questions")
            company_name = st.text_input("Enter Company Name", placeholder="e.g., Google", key="company_name")

            if company_name and st.button("Generate Interview Questions", key="generate_faqs"):
                with st.spinner("Generating interview questions..."):
                    interview_questions = analyzer.generate_interview_questions(company_name, experience_level, role)
                    st.write(interview_questions)

        # Tab 2: Resume Analyzer
        with tab2:
            st.header("📄 Resume Analyzer")
            uploaded_file = st.file_uploader("Upload your resume (PDF or DOCX)", type=['pdf', 'docx'], key="resume_uploader")

            if uploaded_file:
                with st.spinner("Extracting text from resume..."):
                    resume_text, error_message = analyzer.extract_text(uploaded_file)
                    
                if resume_text:
                    st.success("Resume text extracted successfully!")
                    
                    with st.expander("View Extracted Text", expanded=False):
                        st.text_area("Extracted Text", resume_text, height=300, key="extracted_text")
                    
                    analysis_type = st.radio(
                        "Choose analysis type:",
                        ["Default Analysis", "Custom Prompt"],
                        key="analysis_type"
                    )

                    if analysis_type == "Default Analysis":
                        if st.button("Analyze Resume", key="analyze_resume"):
                            with st.spinner("Analyzing resume..."):
                                feedback = analyzer.analyze_resume(resume_text)
                                
                                for section, comments in feedback.items():
                                    with st.expander(f"{section.title()} Feedback", expanded=True):
                                        st.write(comments)
                                        
                    else:
                        custom_prompt = st.text_area(
                            "Enter your custom prompt:",
                            height=100,
                            placeholder="E.g., Analyze the resume's formatting and suggest improvements...",
                            key="custom_prompt"
                        )
                        
                        if custom_prompt and st.button("Get Custom Analysis", key="custom_analysis"):
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