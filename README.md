# Blood Work Analyzer

A Streamlit application that analyzes blood work results from uploaded images using OCR technology.

## Prerequisites

Before running this application, make sure you have:

1. Python 3.8 or higher installed
2. Tesseract OCR installed on your system:
   - Windows: Download and install from [GitHub](https://github.com/UB-Mannheim/tesseract/wiki)
   - Mac: Install via Homebrew: `brew install tesseract`
   - Linux: Install via apt: `sudo apt-get install tesseract-ocr`

## Setup

1. Create a virtual environment (recommended):
   ```
   python -m venv venv
   ```

2. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - Mac/Linux: `source venv/bin/activate`

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

## Running the Application

To run the application:

```
streamlit run app.py
```

The application will open in your default web browser.

## Usage

1. Upload a clear image of your blood work results
2. The application will automatically extract and analyze the values
3. Review the analysis and visualization
4. Check the insights provided for any abnormal results

## Important Note

This tool is for educational purposes only. Always consult with your healthcare provider for medical advice and interpretation of your blood work results.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
