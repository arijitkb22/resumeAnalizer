import streamlit as st
import os
from agent import ResumeAnalyzer
from dotenv import load_dotenv

def main():
    # Load environment variables
    load_dotenv()
    
    st.set_page_config(page_title="Resume Analyzer", layout="wide")
    
    st.title("📄 Resume Analyzer")
    
    # Initialize analyzer (will use API key from .env)
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
        st.info("Please make sure GROQ_API_KEY is set in your .env file.")
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()