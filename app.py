import streamlit as st
import pytesseract
from PIL import Image
import pandas as pd
import io
import re
import plotly.express as px

# Set page configuration
st.set_page_config(
    page_title="Blood Work Analyzer",
    page_icon="🔬",
    layout="wide"
)

def extract_text_from_image(image):
    """Extract text from uploaded image using OCR."""
    try:
        text = pytesseract.image_to_string(image)
        # Add debug output
        st.text("Raw OCR Output:")
        st.text(text)
        return text
    except Exception as e:
        st.error(f"Error processing image: {str(e)}")
        return None

def parse_blood_work(text):
    """Parse blood work text into structured data."""
    # Extended blood work markers and their patterns
    markers = {
        # Basic Blood Count
        'WBC': r'WBC[:\s]+(\d+\.?\d*)',
        'RBC': r'RBC[:\s]+(\d+\.?\d*)',
        'Hemoglobin': r'Hemoglobin[:\s]+(\d+\.?\d*)',
        'Hematocrit': r'Hematocrit[:\s]+(\d+\.?\d*)',
        'Platelets': r'Platelets[:\s]+(\d+)',
        'MCV': r'MCV[:\s]+(\d+\.?\d*)',
        'MCH': r'MCH[:\s]+(\d+\.?\d*)',
        'MCHC': r'MCHC[:\s]+(\d+\.?\d*)',
        'RDW': r'RDW[:\s]+(\d+\.?\d*)',
        
        # Thyroid Panel
        'TSH': r'TSH[:\s]+(\d+\.?\d*)',
        'T4': r'Thyroxine \(T4\)[:\s]+(\d+\.?\d*)',
        'T3': r'Triiodothyronine \(T3\)[:\s]+(\d+\.?\d*)',
        'Free T3': r'Triiodothyronine \(T3\), Free[:\s]+(\d+\.?\d*)',
        'Reverse T3': r'Reverse T3[:\s]+(\d+\.?\d*)',
        
        # Iron Studies
        'Iron': r'Iron[:\s]+(\d+)',
        'TIBC': r'Iron Bind\.Cap\.\(TIBC\)[:\s]+(\d+)',
        'UIBC': r'UIBC[:\s]+(\d+)',
        'Ferritin': r'Ferritin[:\s]+(\d+\.?\d*)',
        'Iron Saturation': r'Iron Saturation[:\s]+(\d+)',
        
        # Lipid Panel
        'Cholesterol': r'Cholesterol, Total[:\s]+(\d+)',
        'Triglycerides': r'Triglycerides[:\s]+(\d+)',
        'HDL': r'HDL Cholesterol[:\s]+(\d+)',
        'LDL': r'LDL Chol Calc[:\s]+(\d+)',
        'VLDL': r'VLDL Cholesterol[:\s]+(\d+)',
        
        # Hormones
        'Testosterone': r'Testosterone[:\s]+([><]?\d+\.?\d*)',
        'Free Testosterone': r'Free Testosterone\(Direct\)[:\s]+(\d+\.?\d*)',
        'DHEA-Sulfate': r'DHEA-Sulfate[:\s]+(\d+\.?\d*)',
        'Estradiol': r'Estradiol[:\s]+(\d+\.?\d*)',
        'FSH': r'FSH[:\s]+([><]?\d+\.?\d*)',
        'LH': r'LH[:\s]+([><]?\d+\.?\d*)',
        
        # Vitamins
        'Vitamin B12': r'Vitamin B12[:\s]+([><]?\d+)',
        'Vitamin D': r'Vitamin D, 25-Hydroxy[:\s]+(\d+\.?\d*)',
        'Vitamin B6': r'Vitamin B6[:\s]+(\d+\.?\d*)',
        
        # Minerals
        'Zinc': r'Zinc[:\s]+(\d+)',
        'Copper': r'Copper[:\s]+(\d+)',
        
        # Additional Markers
        'PSA': r'Prostate Specific Ag[:\s]+(\d+\.?\d*)',
        'SHBG': r'Sex Horm Binding Glob[:\s]+(\d+\.?\d*)',
        'IGF-1': r'Insulin-Like Growth Factor I[:\s]+(\d+)',
        'Prolactin': r'Prolactin[:\s]+(\d+\.?\d*)'
    }
    
    results = {}
    for marker, pattern in markers.items():
        match = re.search(pattern, text)
        if match:
            value = match.group(1)
            # Handle greater than/less than symbols
            if value.startswith('>'):
                value = value[1:]  # Remove '>' symbol
            elif value.startswith('<'):
                value = value[1:]  # Remove '<' symbol
            results[marker] = float(value)
    
    return results

def analyze_results(results):
    """Analyze blood work results and provide insights."""
    # Extended reference ranges
    reference_ranges = {
        # Basic Blood Count
        'WBC': (3.4, 10.8, 'x10E3/uL'),
        'RBC': (4.14, 5.80, 'x10E6/uL'),
        'Hemoglobin': (13.0, 17.7, 'g/dL'),
        'Hematocrit': (37.5, 51.0, '%'),
        'Platelets': (150, 450, 'x10E3/uL'),
        'MCV': (79, 97, 'fL'),
        'MCH': (26.6, 33.0, 'pg'),
        'MCHC': (31.5, 35.7, 'g/dL'),
        'RDW': (11.6, 15.4, '%'),
        
        # Thyroid Panel
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
        'Iron Saturation': (15, 55, '%'),
        
        # Lipid Panel
        'Cholesterol': (100, 199, 'mg/dL'),
        'Triglycerides': (0, 149, 'mg/dL'),
        'HDL': (39, 999, 'mg/dL'),  # >39 is normal
        'LDL': (0, 99, 'mg/dL'),
        'VLDL': (5, 40, 'mg/dL'),
        
        # Hormones
        'Testosterone': (264, 916, 'ng/dL'),
        'Free Testosterone': (8.7, 25.1, 'pg/mL'),
        'DHEA-Sulfate': (138.5, 475.2, 'ug/dL'),
        'Estradiol': (7.6, 42.6, 'pg/mL'),
        'FSH': (1.5, 12.4, 'mIU/mL'),
        'LH': (1.7, 8.6, 'mIU/mL'),
        
        # Vitamins
        'Vitamin B12': (232, 1245, 'pg/mL'),
        'Vitamin D': (30.0, 100.0, 'ng/mL'),
        'Vitamin B6': (3.4, 65.2, 'ug/L'),
        
        # Minerals
        'Zinc': (44, 115, 'ug/dL'),
        'Copper': (69, 132, 'ug/dL'),
        
        # Additional Markers
        'PSA': (0.0, 4.0, 'ng/mL'),
        'SHBG': (16.5, 55.9, 'nmol/L'),
        'IGF-1': (95, 290, 'ng/mL'),
        'Prolactin': (3.9, 22.7, 'ng/mL')
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
        title='Blood Work Results Analysis',
        labels={'Value': 'Value (normalized to reference range)'},
        height=600
    )
    
    # Rotate x-axis labels for better readability
    fig.update_layout(
        xaxis_tickangle=-45,
        showlegend=True,
        margin=dict(b=100)  # Increase bottom margin for rotated labels
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
        file_extension = uploaded_file.name.split('.')[-1].lower()
        
        if file_extension == 'pdf':
            try:
                import PyPDF2
                import pdf2image
                import io
                
                # Convert PDF to images
                pdf_bytes = uploaded_file.read()
                images = pdf2image.convert_from_bytes(pdf_bytes)
                
                # Use the first page
                image = images[0]
                st.image(image, caption='Uploaded Blood Work (PDF)', use_column_width=True)
                
            except Exception as e:
                st.error(f"Error processing PDF: {str(e)}")
                st.info("Note: PDF processing requires poppler to be installed. On Mac, install with: brew install poppler")
                return
        else:
            # Handle regular image uploads
            image = Image.open(uploaded_file)
            st.image(image, caption='Uploaded Blood Work', use_column_width=True)
        
        # Extract text using OCR
        with st.spinner('Processing image...'):
            extracted_text = extract_text_from_image(image)
        
        if extracted_text:
            # Parse blood work results
            results = parse_blood_work(extracted_text)
            
            if results:
                # Analyze results
                analysis_df = analyze_results(results)
                
                # Display results in a table
                st.subheader("Analysis Results")
                st.dataframe(analysis_df)
                
                # Create and display visualization
                fig = create_visualization(analysis_df)
                st.plotly_chart(fig)
                
                # Provide insights
                st.subheader("Key Insights")
                abnormal_results = analysis_df[analysis_df['Status'] != 'NORMAL']
                if len(abnormal_results) > 0:
                    st.warning("The following markers are outside the reference range:")
                    for _, row in abnormal_results.iterrows():
                        st.write(f"- {row['Marker']}: {row['Value']} {row['Unit']} ({row['Status']})")
                else:
                    st.success("All tested markers are within normal ranges.")
                
                st.info("""
                **Remember**: Reference ranges can vary by laboratory and individual factors such as age,
                sex, and medical history. Always discuss your results with your healthcare provider.
                """)
            else:
                st.error("Could not identify blood work values in the image. Please ensure the image is clear and contains standard blood work results.")

if __name__ == "__main__":
    main()