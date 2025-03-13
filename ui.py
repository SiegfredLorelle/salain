import streamlit as st
from PIL import Image
from scripts.classical import classify_email
from scripts.preprocess.extract_features import extract_features
from scripts.ocr import (
    load_ocr_model, 
    process_file_upload, 
    process_camera_capture
)

# Initialize minimal session state for tracking
if 'extracted_text' not in st.session_state:
    st.session_state.extracted_text = ""

# Initialize OCR model at app startup
ocr_model = load_ocr_model()

# Streamlit UI
st.title("Salain - Malicious Email Detector")
st.markdown("Protect yourself from malicious emails 🇵🇭")

# Input Method Selection
input_method = st.radio(
    "Choose input method:",
    ["Text Input", "Upload Image", "Camera Capture"],
    horizontal=True,
    on_change=lambda: setattr(st.session_state, 'extracted_text', "")
)

def analyze_email_content(text):
    """Analyze email content and display results"""
    if not text.strip():
        st.warning("Please enter text to analyze")
        return
        
    with st.spinner("Analyzing email content..."):
        try:
            prediction, confidence = classify_email(text)
            
            # Display results
            if prediction[0] == 1:
                st.error(f"⚠️ Malicious Detected (Confidence: {confidence:.2%})")
                st.write("Common red flags found:")
                st.json(extract_features(text))
            else:
                st.success(f"✅ Safe Email (Confidence: {1-confidence:.2%})")
        except Exception as e:
            st.error(f"Analysis Error: {str(e)}")

# Display the appropriate input method
if input_method == "Text Input":
    # Direct text input
    text_input_value = st.text_area(
        "Paste email content here:",
        height=200,
        key="direct_text_input"
    )
    
    # Add analyze button
    if st.button("Analyze Email", key="text_analyze_button"):
        analyze_email_content(text_input_value)

elif input_method == "Upload Image":
    # Image upload
    uploaded_file = st.file_uploader(
        "Upload email screenshot:",
        type=["png", "jpg", "jpeg"],
        key="uploaded_file"
    )
    
    # Process the uploaded file
    if uploaded_file is not None:
        # Display the image
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Email Image", use_container_width=True)
        
        # Extract text if not already done
        if st.session_state.extracted_text == "":
            st.session_state.extracted_text = process_file_upload(uploaded_file)
    
    # Display text area for editing OCR results or manual entry
    if uploaded_file is not None:
        if st.session_state.extracted_text:
            text_value = st.text_area(
                "Extracted text (edit if needed):",
                value=st.session_state.extracted_text,
                height=200,
                key="upload_extracted_text"
            )
            st.info("You can edit the text above to correct any OCR mistakes before analysis.")
        else:
            st.warning("No text found in the image. Try adjusting the image or using a clearer photo.")
            text_value = st.text_area(
                "Enter the email text manually:",
                height=200,
                key="upload_manual_text"
            )
    else:
        text_value = st.text_area(
            "Enter email text manually:",
            height=200,
            key="upload_no_file_text"
        )
    
    # Add analyze button
    if st.button("Analyze Email", key="upload_analyze_button"):
        analyze_email_content(text_value)

elif input_method == "Camera Capture":
    # Camera capture
    camera_file = st.camera_input(
        "Take a photo of the email",
        key="camera_file"
    )
    
    # Process the camera file
    if camera_file is not None and st.session_state.extracted_text == "":
        st.session_state.extracted_text = process_camera_capture(camera_file)
    
    # Display text area for editing OCR results or manual entry
    if camera_file is not None:
        if st.session_state.extracted_text:
            text_value = st.text_area(
                "Extracted text (edit if needed):",
                value=st.session_state.extracted_text,
                height=200,
                key="camera_extracted_text"
            )
            st.info("You can edit the text above to correct any OCR mistakes before analysis.")
        else:
            st.warning("No text found in the image. Try adjusting the camera or using a clearer photo.")
            text_value = st.text_area(
                "Enter the email text manually:",
                height=200,
                key="camera_manual_text"
            )
    else:
        text_value = st.text_area(
            "Enter email text manually:",
            height=200,
            key="camera_no_image_text"
        )
    
    # Add analyze button
    if st.button("Analyze Email", key="camera_analyze_button"):
        analyze_email_content(text_value)