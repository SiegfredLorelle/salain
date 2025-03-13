import streamlit as st
from classical import classify_email
from scripts.preprocess.extract_features import extract_features
import numpy as np
from paddleocr import PaddleOCR
from PIL import Image
import cv2

# Initialize minimal session state for file tracking
if 'uploaded_file_processed' not in st.session_state:
    st.session_state.uploaded_file_processed = False
if 'camera_file_processed' not in st.session_state:
    st.session_state.camera_file_processed = False
if 'extracted_text' not in st.session_state:
    st.session_state.extracted_text = ""

# Load OCR model only once
@st.cache_resource
def load_ocr_model():
    try:
        return PaddleOCR(use_angle_cls=True, lang='en', show_log=False)
    except Exception as e:
        st.error(f"Failed to load OCR model: {str(e)}")
        return None

# Initialize OCR model at app startup
ocr = load_ocr_model()

def process_image_with_ocr(image):
    """Process image using PaddleOCR and return cleaned text"""
    if ocr is None:
        st.error("OCR model is not available")
        return ""
    
    try:
        # Convert image to numpy array
        img_array = np.array(image)
        
        # Ensure image is in correct format
        if len(img_array.shape) == 2:  # Convert grayscale to RGB
            img_array = cv2.cvtColor(img_array, cv2.COLOR_GRAY2RGB)
        elif img_array.shape[2] == 4:  # Convert RGBA to RGB
            img_array = cv2.cvtColor(img_array, cv2.COLOR_RGBA2RGB)
        
        # Run OCR on the image
        result = ocr.ocr(img_array, cls=True)
        
        # Extract text from OCR result
        if result and result[0]:
            text = " ".join([line[1][0] for line in result[0]])
            return text.strip()
        else:
            return ""
    except Exception as e:
        st.error(f"OCR Error: {str(e)}")
        return ""

# Function to process uploaded file
def process_uploaded_file():
    if st.session_state.uploaded_file is not None and not st.session_state.uploaded_file_processed:
        try:
            # Process image with OCR
            image = Image.open(st.session_state.uploaded_file)
            with st.spinner("Extracting text from image..."):
                st.session_state.extracted_text = process_image_with_ocr(image)
            st.session_state.uploaded_file_processed = True
        except Exception as e:
            st.error(f"Error processing uploaded file: {str(e)}")
            st.session_state.extracted_text = ""

# Function to process camera file
def process_camera_file():
    if st.session_state.camera_file is not None and not st.session_state.camera_file_processed:
        try:
            # Process image with OCR
            image = Image.open(st.session_state.camera_file)
            with st.spinner("Extracting text from camera image..."):
                st.session_state.extracted_text = process_image_with_ocr(image)
            st.session_state.camera_file_processed = True
        except Exception as e:
            st.error(f"Error processing camera file: {str(e)}")
            st.session_state.extracted_text = ""

# Streamlit UI
st.title("Salain - Malicious Email Detector")
st.markdown("Protect yourself from malicious emails 🇵🇭")

# Input Method Selection
input_method = st.radio(
    "Choose input method:",
    ["Text Input", "Upload Image", "Camera Capture"],
    horizontal=True,
    on_change=lambda: (
        setattr(st.session_state, 'uploaded_file_processed', False),
        setattr(st.session_state, 'camera_file_processed', False),
        setattr(st.session_state, 'extracted_text', "")
    )
)

# Display the appropriate input method
if input_method == "Text Input":
    # Direct text input
    text_input_value = st.text_area(
        "Paste email content here:",
        height=200,
        key="direct_text_input"
    )
    
    # Add analyze button directly under this input
    text_analyze_button = st.button("Analyze Email", key="text_analyze_button")
    
    # Analysis logic for text input
    if text_analyze_button:
        if text_input_value.strip():
            with st.spinner("Analyzing email content..."):
                try:
                    prediction, confidence = classify_email(text_input_value)
                    
                    # Display results
                    if prediction[0] == 1:
                        st.error(f"⚠️ Malicious Detected (Confidence: {confidence:.2%})")
                        st.write("Common red flags found:")
                        st.json(extract_features(text_input_value))
                    else:
                        st.success(f"✅ Safe Email (Confidence: {1-confidence:.2%})")
                except Exception as e:
                    st.error(f"Analysis Error: {str(e)}")
        else:
            st.warning("Please enter email text before analyzing")

elif input_method == "Upload Image":
    # Image upload with callback
    uploaded_file = st.file_uploader(
        "Upload email screenshot:",
        type=["png", "jpg", "jpeg"],
        key="uploaded_file",
        on_change=lambda: setattr(st.session_state, 'uploaded_file_processed', False)
    )
    
    # Process the uploaded file if needed
    if uploaded_file is not None:
        process_uploaded_file()
        
        # Display the image
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Email Image", use_container_width=True)
    
    # Display text area for editing OCR results or manual entry
    if uploaded_file is not None:
        if st.session_state.extracted_text:
            upload_text_value = st.text_area(
                "Extracted text (edit if needed):",
                value=st.session_state.extracted_text,
                height=200,
                key="upload_extracted_text"
            )
            st.info("You can edit the text above to correct any OCR mistakes before analysis.")
        else:
            st.warning("No text found in the image. Try adjusting the image or using a clearer photo.")
            upload_text_value = st.text_area(
                "Enter the email text manually:",
                height=200,
                key="upload_manual_text"
            )
    else:
        upload_text_value = st.text_area(
            "Enter email text manually:",
            height=200,
            key="upload_no_file_text"
        )
    
    # Add analyze button for upload
    upload_analyze_button = st.button("Analyze Email", key="upload_analyze_button")
    
    # Analysis logic for uploaded image
    if upload_analyze_button:
        if upload_text_value.strip():
            with st.spinner("Analyzing email content..."):
                try:
                    prediction, confidence = classify_email(upload_text_value)
                    
                    # Display results
                    if prediction[0] == 1:
                        st.error(f"⚠️ Malicious Detected (Confidence: {confidence:.2%})")
                        st.write("Common red flags found:")
                        st.json(extract_features(upload_text_value))
                    else:
                        st.success(f"✅ Safe Email (Confidence: {1-confidence:.2%})")
                except Exception as e:
                    st.error(f"Analysis Error: {str(e)}")
        else:
            st.warning("Please enter text to analyze")

elif input_method == "Camera Capture":
    # Camera capture with callback
    camera_file = st.camera_input(
        "Take a photo of the email",
        key="camera_file",
        on_change=lambda: setattr(st.session_state, 'camera_file_processed', False)
    )
    
    # Process the camera file if needed
    if camera_file is not None:
        process_camera_file()
    
    # Display text area for editing OCR results or manual entry
    if camera_file is not None:
        if st.session_state.extracted_text:
            camera_text_value = st.text_area(
                "Extracted text (edit if needed):",
                value=st.session_state.extracted_text,
                height=200,
                key="camera_extracted_text"
            )
            st.info("You can edit the text above to correct any OCR mistakes before analysis.")
        else:
            st.warning("No text found in the image. Try adjusting the camera or using a clearer photo.")
            camera_text_value = st.text_area(
                "Enter the email text manually:",
                height=200,
                key="camera_manual_text"
            )
    else:
        camera_text_value = st.text_area(
            "Enter email text manually:",
            height=200,
            key="camera_no_image_text"
        )
    
    # Add analyze button for camera
    camera_analyze_button = st.button("Analyze Email", key="camera_analyze_button")
    
    # Analysis logic for camera image
    if camera_analyze_button:
        if camera_text_value.strip():
            with st.spinner("Analyzing email content..."):
                try:
                    prediction, confidence = classify_email(camera_text_value)
                    
                    # Display results
                    if prediction[0] == 1:
                        st.error(f"⚠️ Malicious Detected (Confidence: {confidence:.2%})")
                        st.write("Common red flags found:")
                        st.json(extract_features(camera_text_value))
                    else:
                        st.success(f"✅ Safe Email (Confidence: {1-confidence:.2%})")
                except Exception as e:
                    st.error(f"Analysis Error: {str(e)}")
        else:
            st.warning("Please enter text to analyze")