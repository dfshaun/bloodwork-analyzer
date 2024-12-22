import streamlit as st
# ... [previous imports stay the same]

# Only changing the relevant parts where we display images
def main():
    # ... [previous code stays the same]
    
    if uploaded_file is not None:
        file_extension = uploaded_file.name.split('.')[-1].lower()
        
        if file_extension == 'pdf':
            pdf_bytes = uploaded_file.read()
            
            with st.spinner('Processing PDF...'):
                image = process_pdf(pdf_bytes)
                
            if image is None:
                return
            
            st.image(image, caption='Uploaded Blood Work (PDF)', use_container_width=True)  # Changed here
        else:
            image = Image.open(uploaded_file)
            st.image(image, caption='Uploaded Blood Work', use_container_width=True)  # Changed here
            
        # ... [rest of the code stays the same]

# ... [rest of the file stays the same]