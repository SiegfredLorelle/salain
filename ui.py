import streamlit as st
from classical import classify_email
from scripts.preprocess.extract_features import extract_features
import numpy as np
from paddleocr import PaddleOCR
from PIL import Image
import cv2

# Initialize session state for persistent storage
if 'email_text' not in st.session_state:
    st.session_state.email_text = ""
if 'ocr_complete' not in st.session_state:
    st.session_state.ocr_complete = False
if 'image_processed' not in st.session_state:
    st.session_state.image_processed = False

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

# Streamlit UI
st.title("Salain - Malicious Email Detector")
st.markdown("Protect yourself from malicious emails 🇵🇭")

# Input Section
input_type = st.radio("Choose input type:", ("Text", "Image"), 
                      on_change=lambda: setattr(st.session_state, 'image_processed', False))

if input_type == "Text":
    # Direct text input mode
    text_input = st.text_area("Paste email content here:", height=200)
    st.session_state.email_text = text_input
    st.session_state.ocr_complete = True
else:
    # Image input mode
    upload_tab, camera_tab = st.tabs(["Upload Image", "Camera Capture"])
    
    image_file = None
    
    with upload_tab:
        uploaded_file = st.file_uploader("Upload email screenshot:", 
                                        type=["png", "jpg", "jpeg"],
                                        on_change=lambda: setattr(st.session_state, 'image_processed', False))
        if uploaded_file:
            image_file = uploaded_file
    
    with camera_tab:
        camera_file = st.camera_input("Take a photo of the email",
                                     on_change=lambda: setattr(st.session_state, 'image_processed', False))
        if camera_file:
            image_file = camera_file
    
    # Process the image if one is provided from either source
    if image_file and not st.session_state.image_processed:
        try:
            col1, col2 = st.columns([1, 2])
            
            with col1:
                # Display image
                image = Image.open(image_file)
                st.image(image, caption="Email Image", use_container_width=True)
            
            with col2:
                # Process image and display extracted text
                with st.spinner("Extracting text from image..."):
                    extracted_text = process_image_with_ocr(image)
                    # Set the session state variable
                    st.session_state.email_text = extracted_text
                    st.session_state.ocr_complete = True
                    st.session_state.image_processed = True
                
                st.subheader("Extracted Text:")
                if extracted_text:
                    # Make the text area editable for user corrections
                    edited_text = st.text_area(
                        "Review and edit the extracted text if needed:",
                        value=extracted_text,
                        height=200,
                        key="ocr_edit_area"
                    )
                    # Update the session state with edited text
                    st.session_state.email_text = edited_text
                    st.info("You can edit the text above to correct any OCR mistakes before analysis.")
                else:
                    st.warning("No text found in the image. Try adjusting the image or using a clearer photo.")
                    # Provide an empty text area for manual entry
                    manual_text = st.text_area(
                        "Enter the email text manually:",
                        value="",
                        height=200,
                        key="manual_text_area"
                    )
                    st.session_state.email_text = manual_text
        except Exception as e:
            st.error(f"Error processing image: {str(e)}")
            st.session_state.ocr_complete = False
    elif image_file and st.session_state.image_processed:
        # Display the previously processed image and text
        col1, col2 = st.columns([1, 2])
        
        with col1:
            # Display image
            image = Image.open(image_file)
            st.image(image, caption="Email Image", use_container_width=True)
        
        with col2:
            st.subheader("Extracted Text:")
            # Make the text area editable for user corrections
            edited_text = st.text_area(
                "Review and edit the extracted text if needed:",
                value=st.session_state.email_text,
                height=200,
                key="ocr_edit_area_cached"
            )
            # Update the session state with edited text
            st.session_state.email_text = edited_text
            st.info("You can edit the text above to correct any OCR mistakes before analysis.")

# Add a separator
st.markdown("---")

# Analysis Section
col1, col2 = st.columns([1, 2])

with col1:
    # Prediction Logic
    analyze_button = st.button("Analyze Email")

with col2:
    # Display current text to be analyzed
    if st.session_state.email_text:
        st.text_area(
            "Text to be analyzed:",
            value=st.session_state.email_text,
            height=100,
            disabled=True
        )

if analyze_button:
    if st.session_state.email_text.strip():
        with st.spinner("Analyzing email content..."):
            try:
                prediction, confidence = classify_email(st.session_state.email_text)
                
                # Display results
                if prediction[0] == 1:
                    st.error(f"⚠️ Malicious Detected (Confidence: {confidence:.2%})")
                    st.write("Common red flags found:")
                    st.json(extract_features(st.session_state.email_text))
                else:
                    st.success(f"✅ Safe Email (Confidence: {1-confidence:.2%})")
            except Exception as e:
                st.error(f"Analysis Error: {str(e)}")
    else:
        st.warning("Please enter email text or upload an image")