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
        return text
    except Exception as e:
        st.error(f"Error processing image: {str(e)}")
        return None

def parse_blood_work(text):
    """Parse blood work text into structured data."""
    # Common blood work markers and their units
    markers = {
        'WBC': r'WBC[:\s]+(\d+\.?\d*)',
        'RBC': r'RBC[:\s]+(\d+\.?\d*)',
        'Hemoglobin': r'(?:Hemoglobin|HGB)[:\s]+(\d+\.?\d*)',
        'Hematocrit': r'(?:Hematocrit|HCT)[:\s]+(\d+\.?\d*)',
        'Platelets': r'Platelets[:\s]+(\d+)',
        'Glucose': r'Glucose[:\s]+(\d+)',
        'Calcium': r'Calcium[:\s]+(\d+\.?\d*)',
        'Sodium': r'Sodium[:\s]+(\d+)',
        'Potassium': r'Potassium[:\s]+(\d+\.?\d*)',
        'Chloride': r'Chloride[:\s]+(\d+)',
        'CO2': r'CO2[:\s]+(\d+)',
        'BUN': r'BUN[:\s]+(\d+)',
        'Creatinine': r'Creatinine[:\s]+(\d+\.?\d*)',
    }

    results = {}
    for marker, pattern in markers.items():
        match = re.search(pattern, text)
        if match:
            results[marker] = float(match.group(1))

    return results

def analyze_results(results):
    """Analyze blood work results and provide insights."""
    # Reference ranges (these are approximate and should be verified with lab-specific ranges)
    reference_ranges = {
        'WBC': (4.0, 11.0, 'K/µL'),
        'RBC': (4.5, 5.9, 'M/µL'),
        'Hemoglobin': (13.5, 17.5, 'g/dL'),
        'Hematocrit': (41.0, 53.0, '%'),
        'Platelets': (150, 450, 'K/µL'),
        'Glucose': (70, 99, 'mg/dL'),
        'Calcium': (8.6, 10.2, 'mg/dL'),
        'Sodium': (135, 145, 'mEq/L'),
        'Potassium': (3.5, 5.0, 'mEq/L'),
        'Chloride': (98, 106, 'mEq/L'),
        'CO2': (23, 29, 'mEq/L'),
        'BUN': (7, 20, 'mg/dL'),
        'Creatinine': (0.6, 1.2, 'mg/dL'),
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
    return fig

def main():
    st.title("Blood Work Analyzer")

    st.markdown("""
    ### 📋 Instructions
    1. Upload a clear image of your blood work results
    2. The app will extract and analyze the values
    3. Review the analysis and visualization

    **Important**: This tool is for educational purposes only. Always consult with your healthcare provider
    for medical advice and interpretation of your blood work results.
    """)

    uploaded_file = st.file_uploader("Upload your blood work image", type=['png', 'jpg', 'jpeg'])

    if uploaded_file is not None:
        # Display the uploaded image
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
