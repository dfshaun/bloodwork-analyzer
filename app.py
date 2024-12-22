import streamlit as st
import pytesseract
from PIL import Image
import pandas as pd
import io
import re
import plotly.express as px
import sys
import os

# Set page configuration
st.set_page_config(
    page_title="Blood Work Analyzer",
    page_icon="🔬",
    layout="wide"
)

def convert_pdf_to_image(pdf_bytes):
    """Convert PDF to image using pdf2image."""
    try:
        import pdf2image
        images = pdf2image.convert_from_bytes(pdf_bytes)
        return images[0] if images else None
    except Exception as e:
        st.error(f"PDF conversion error: {str(e)}")
        return None

def extract_text_from_image(image):
    """Extract text from uploaded image using OCR."""
    try:
        text = pytesseract.image_to_string(image)
        st.text("Raw OCR Output:")
        st.text(text)
        return text
    except Exception as e:
        st.error(f"OCR Error: {str(e)}")
        return None

def parse_blood_work(text):
    """Parse blood work text into structured data."""
    markers = {
        'WBC': r'WBC[:\s]+(\d+\.?\d*)',
        'RBC': r'RBC[:\s]+(\d+\.?\d*)',
        'Hemoglobin': r'(?:Hemoglobin|HGB)[:\s]+(\d+\.?\d*)',
        'Hematocrit': r'(?:Hematocrit|HCT)[:\s]+(\d+\.?\d*)',
        'Platelets': r'Platelets[:\s]+(\d+)',
        'MCV': r'MCV[:\s]+(\d+\.?\d*)',
        'MCH': r'MCH[:\s]+(\d+\.?\d*)',
        'MCHC': r'MCHC[:\s]+(\d+\.?\d*)',
        'RDW': r'RDW[:\s]+(\d+\.?\d*)'
    }
    
    results = {}
    for marker, pattern in markers.items():
        match = re.search(pattern, text)
        if match:
            value = match.group(1)
            if value.startswith('>'):
                value = value[1:]
            elif value.startswith('<'):
                value = value[1:]
            try:
                results[marker] = float(value)
            except ValueError:
                st.warning(f"Could not convert {marker} value '{value}' to number")
    
    return results

def analyze_results(results):
    """Analyze blood work results and provide insights."""
    reference_ranges = {
        'WBC': (3.4, 10.8, 'x10E3/uL'),
        'RBC': (4.14, 5.80, 'x10E6/uL'),
        'Hemoglobin': (13.0, 17.7, 'g/dL'),
        'Hematocrit': (37.5, 51.0, '%'),
        'Platelets': (150, 450, 'x10E3/uL'),
        'MCV': (79, 97, 'fL'),
        'MCH': (26.6, 33.0, 'pg'),
        'MCHC': (31.5, 35.7, 'g/dL'),
        'RDW': (11.6, 15.4, '%')
    }
    
    analysis = []
    for marker, value in results.items():
        if marker in reference_ranges:
            low, high, unit = reference_ranges[marker]
            status = "NORMAL"
            if value < low:
                status = "LOW"
            elif value > high:
                status = "HIGH"
            
            analysis.append({
                'Marker': marker,
                'Value': value,
                'Unit': unit,
                'Reference Range': f"{low}-{high}",
                'Status': status
            })
    
    return pd.DataFrame(analysis)

def create_visualization(df):
    """Create visualization of blood work results."""
    fig = px.bar(
        df,
        x='Marker',
        y='Value',
        color='Status',
        color_discrete_map={'NORMAL': 'green', 'LOW': 'blue', 'HIGH': 'red'},
        title='Blood Work Results Analysis'
    )
    fig.update_layout(xaxis_tickangle=-45)
    return fig

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
        try:
            file_extension = uploaded_file.name.split('.')[-1].lower()
            
            if file_extension == 'pdf':
                # Handle PDF
                pdf_bytes = uploaded_file.read()
                image = convert_pdf_to_image(pdf_bytes)
                if image is None:
                    st.error("Could not process PDF file")
                    return
            else:
                # Handle image
                image = Image.open(uploaded_file)
            
            # Display image without container width parameter
            st.image(image, caption='Uploaded Blood Work')
            
            # Process the image
            with st.spinner('Analyzing blood work...'):
                extracted_text = extract_text_from_image(image)
                
                if extracted_text:
                    results = parse_blood_work(extracted_text)
                    
                    if results:
                        analysis_df = analyze_results(results)
                        
                        st.subheader("Analysis Results")
                        st.dataframe(analysis_df)
                        
                        fig = create_visualization(analysis_df)
                        st.plotly_chart(fig)
                        
                        st.subheader("Key Insights")
                        abnormal_results = analysis_df[analysis_df['Status'] != 'NORMAL']
                        if len(abnormal_results) > 0:
                            st.warning("The following markers are outside the reference range:")
                            for _, row in abnormal_results.iterrows():
                                st.write(f"- {row['Marker']}: {row['Value']} {row['Unit']} ({row['Status']})")
                        else:
                            st.success("All tested markers are within normal ranges.")
                    else:
                        st.error("Could not identify blood work values in the image. Please ensure the image is clear and contains standard blood work results.")
                
        except Exception as e:
            st.error(f"Error processing file: {str(e)}")

if __name__ == "__main__":
    main()