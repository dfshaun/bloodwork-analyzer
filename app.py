import streamlit as st
import pytesseract
from PIL import Image
import pandas as pd
import io
import re
import plotly.express as px

st.set_page_config(page_title="Blood Work Analyzer", page_icon="🔬", layout="wide")

def extract_text_from_image(image):
    """Extract text from uploaded image using OCR."""
    try:
        text = pytesseract.image_to_string(image)
        with st.expander("Show Raw OCR Output"):
            st.text(text)
        return text
    except Exception as e:
        st.error(f"OCR Error: {str(e)}")
        return None

def convert_pdf_to_image(pdf_bytes):
    """Convert PDF to image using pdf2image."""
    try:
        import pdf2image
        images = pdf2image.convert_from_bytes(pdf_bytes)
        return images[0] if images else None
    except Exception as e:
        st.error("Could not process PDF. Please ensure poppler is installed.")
        return None

def parse_blood_work(text):
    """Parse blood work text into structured data."""
    # Updated patterns for LabCorp format
    markers = {
        # CBC
        'WBC': r'WBC[^0-9B]+(\d+\.?\d*)',
        'RBC': r'RBC[^0-9B]+(\d+\.?\d*)',
        'Hemoglobin': r'Hemoglobin[^0-9]+(\d+\.?\d*)',
        'Hematocrit': r'Hematocrit[^0-9]+(\d+\.?\d*)',
        'Platelets': r'Platelets[^0-9]+(\d+)',
        'MCV': r'MCV[^0-9]+(\d+\.?\d*)',
        'MCH': r'MCH[^0-9]+(\d+\.?\d*)',
        'MCHC': r'MCHC[^0-9]+(\d+\.?\d*)',
        'RDW': r'RDW[^0-9]+(\d+\.?\d*)',
        
        # Thyroid Panel
        'TSH': r'TSH[^0-9]*?(\d+\.?\d*)',
        'T4': r'Thyroxine\s+\(T4\)[^0-9]*(\d+\.?\d*)',
        'T3': r'Triiodothyronine\s+\(T3\)[^0-9]*\s+(\d+)',
        'Free T3': r'Triiodothyronine\s+\(T3\),\s+Free[^0-9]*(\d+\.?\d*)',
        'Reverse T3': r'Reverse\s+T3[^0-9]*(\d+\.?\d*)',
        
        # Iron Studies
        'Iron': r'Iron:?\s*(\d+)',
        'TIBC': r'(?:Iron\s+Bind\.Cap\.|TIBC)[^0-9]*(\d+)',
        'UIBC': r'UIBC[^0-9]*(\d+)',
        'Ferritin': r'Ferritin[^0-9]*(\d+)',
        'Iron Saturation': r'Iron\s+Saturation[^0-9]*(\d+)',
        
        # Hormones
        'Testosterone': r'Testosterone[^0-9]*(\d+)',
        'Free Testosterone': r'Free\s+Testosterone[^0-9]*(\d+\.?\d*)',
        'Estradiol': r'Estradiol[^0-9]*(\d+\.?\d*)',
        'DHEA-Sulfate': r'DHEA-Sulfate[^0-9]*(\d+\.?\d*)',
        
        # Chemistry
        'Glucose': r'Glucose[^0-9]*(\d+)',
        'BUN': r'BUN[^0-9]*(\d+)',
        'Creatinine': r'Creatinine[^0-9]*(\d+\.?\d*)'
    }
    
    results = {}
    for marker, pattern in markers.items():
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            value = match.group(1)
            # Handle < and > symbols
            value = value.replace('<', '').replace('>', '')
            try:
                results[marker] = float(value)
            except ValueError:
                continue
    
    return results

def analyze_results(results):
    """Analyze blood work results and provide insights."""
    reference_ranges = {
        # CBC
        'WBC': (3.4, 10.8, 'x10E3/uL'),
        'RBC': (4.14, 5.80, 'x10E6/uL'),
        'Hemoglobin': (13.0, 17.7, 'g/dL'),
        'Hematocrit': (37.5, 51.0, '%'),
        'Platelets': (150, 450, 'x10E3/uL'),
        'MCV': (79, 97, 'fL'),
        'MCH': (26.6, 33.0, 'pg'),
        'MCHC': (31.5, 35.7, 'g/dL'),
        'RDW': (11.6, 15.4, '%'),
        
        # Thyroid
        'TSH': (0.450, 4.500, 'uIU/mL'),
        'T4': (4.5, 12.0, 'ug/dL'),
        'T3': (71, 180, 'ng/dL'),
        'Free T3': (2.0, 4.4, 'pg/mL'),
        'Reverse T3': (9.2, 24.1, 'ng/dL'),
        
        # Iron Studies
        'Iron': (38, 169, 'ug/dL'),
        'TIBC': (250, 450, 'ug/dL'),
        'UIBC': (111, 343, 'ug/dL'),
        'Ferritin': (30, 400, 'ng/mL'),
        'Iron Saturation': (20, 55, '%'),
        
        # Hormones
        'Testosterone': (264, 916, 'ng/dL'),
        'Free Testosterone': (8.7, 25.1, 'pg/mL'),
        'Estradiol': (7.6, 42.6, 'pg/mL'),
        'DHEA-Sulfate': (138.5, 475.2, 'ug/dL'),
        
        # Chemistry
        'Glucose': (70, 99, 'mg/dL'),
        'BUN': (7, 20, 'mg/dL'),
        'Creatinine': (0.6, 1.2, 'mg/dL')
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
    fig.update_layout(
        xaxis_tickangle=-45,
        height=600,
        margin=dict(b=100)
    )
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
                pdf_bytes = uploaded_file.read()
                image = convert_pdf_to_image(pdf_bytes)
                if image is None:
                    return
            else:
                image = Image.open(uploaded_file)
            
            st.image(image, caption='Uploaded Blood Work')
            
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
                        st.warning("Could not identify standard blood work values. Try uploading a clearer image.")
                
        except Exception as e:
            st.error("Error processing file. Please try again with a different file.")
            with st.expander("See detailed error"):
                st.text(str(e))

if __name__ == "__main__":
    main()