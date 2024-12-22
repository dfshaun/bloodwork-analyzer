import streamlit as st
import pytesseract
from PIL import Image
import pandas as pd
import io
import re
import plotly.express as px
import os
import subprocess

# Set page configuration
st.set_page_config(
    page_title="Blood Work Analyzer",
    page_icon="🔬",
    layout="wide"
)

def check_poppler_installation():
    """Check if poppler is installed and accessible."""
    try:
        # Try to find pdftoppm (part of poppler-utils)
        subprocess.run(['which', 'pdftoppm'], check=True, capture_output=True)
        return True
    except subprocess.CalledProcessError:
        return False

def process_pdf(pdf_bytes):
    """Process PDF with detailed error handling."""
    try:
        import pdf2image
        
        # Check poppler installation
        if not check_poppler_installation():
            st.error("Poppler is not installed or not in PATH")
            st.info("Installation instructions:")
            st.code("sudo apt-get install -y poppler-utils  # On Ubuntu/Debian\nbrew install poppler  # On macOS")
            return None
            
        # Print current working directory and PATH for debugging
        st.text(f"Current working directory: {os.getcwd()}")
        st.text(f"PATH: {os.environ.get('PATH')}")
        
        conversion_options = {
            'fmt': 'png',
            'dpi': 300,
            'output_folder': None,
            'thread_count': 1,
            'strict': False,
        }
        
        images = pdf2image.convert_from_bytes(
            pdf_bytes,
            **conversion_options
        )
        
        if not images:
            st.error("No images were extracted from the PDF")
            return None
            
        return images[0]  # Return first page
        
    except ImportError as e:
        st.error(f"Missing required library: {str(e)}")
        st.info("Try running: pip install pdf2image")
        return None
    except Exception as e:
        st.error(f"Error processing PDF: {str(e)}")
        st.text(f"Detailed error: {repr(e)}")
        return None

[... rest of your existing code ...]

def main():
    st.title("Blood Work Analyzer")
    
    st.markdown("""
    ### 📋 Instructions
    1. Upload your blood work results (PDF or image)
    2. The app will extract and analyze the values
    3. Review the analysis and visualization
    
    **Important**: This tool is for educational purposes only. Always consult with your healthcare provider
    for medical advice and interpretation of your blood work results.
    """)
    
    uploaded_file = st.file_uploader("Upload your blood work results", type=['png', 'jpg', 'jpeg', 'pdf'])
    
    if uploaded_file is not None:
        file_extension = uploaded_file.name.split('.')[-1].lower()
        
        if file_extension == 'pdf':
            # Read PDF bytes
            pdf_bytes = uploaded_file.read()
            
            with st.spinner('Processing PDF...'):
                image = process_pdf(pdf_bytes)
                
            if image is None:
                return
            
            st.image(image, caption='Uploaded Blood Work (PDF)', use_column_width=True)
        else:
            # Handle regular image uploads
            image = Image.open(uploaded_file)
            st.image(image, caption='Uploaded Blood Work', use_column_width=True)
        
        # Extract text using OCR
        with st.spinner('Processing image...'):
            extracted_text = extract_text_from_image(image)
        
        if extracted_text:
            [... rest of your existing code ...]

if __name__ == "__main__":
    main()