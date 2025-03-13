from paddleocr import PaddleOCR
import numpy as np
import cv2
from PIL import Image
import streamlit as st

# Load OCR model only once
@st.cache_resource
def load_ocr_model():
    """Initialize and cache the PaddleOCR model"""
    try:
        return PaddleOCR(use_angle_cls=True, lang='en', show_log=False)
    except Exception as e:
        st.error(f"Failed to load OCR model: {str(e)}")
        return None

def normalize_image(image):
    """Normalize image to ensure it's in correct format for OCR"""
    img_array = np.array(image)
    
    # Convert grayscale to RGB if needed
    if len(img_array.shape) == 2:
        img_array = cv2.cvtColor(img_array, cv2.COLOR_GRAY2RGB)
    # Convert RGBA to RGB if needed
    elif img_array.shape[2] == 4:
        img_array = cv2.cvtColor(img_array, cv2.COLOR_RGBA2RGB)
    
    return img_array

def process_image_with_ocr(image, ocr_model=None):
    """
    Process image using PaddleOCR and return extracted text
    
    Args:
        image: PIL Image object
        ocr_model: Optional pre-loaded OCR model
    
    Returns:
        str: Extracted text from the image
    """
    # Load model if not provided
    if ocr_model is None:
        ocr_model = load_ocr_model()
        
    if ocr_model is None:
        st.error("OCR model is not available")
        return ""
    
    try:
        # Normalize the image
        img_array = normalize_image(image)
        
        # Run OCR on the image
        result = ocr_model.ocr(img_array, cls=True)
        
        # Extract text from OCR result
        if result and result[0]:
            text = " ".join([line[1][0] for line in result[0]])
            return text.strip()
        else:
            return ""
    except Exception as e:
        st.error(f"OCR Error: {str(e)}")
        return ""

def process_file_upload(uploaded_file):
    """Process an uploaded file and extract text"""
    if uploaded_file is None:
        return ""
    
    try:
        image = Image.open(uploaded_file)
        with st.spinner("Extracting text from image..."):
            return process_image_with_ocr(image)
    except Exception as e:
        st.error(f"Error processing uploaded file: {str(e)}")
        return ""

def process_camera_capture(camera_file):
    """Process a camera capture file and extract text"""
    if camera_file is None:
        return ""
    
    try:
        image = Image.open(camera_file)
        with st.spinner("Extracting text from camera image..."):
            return process_image_with_ocr(image)
    except Exception as e:
        st.error(f"Error processing camera file: {str(e)}")
        return ""