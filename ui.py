import streamlit as st
from classical import classify_email
from scripts.preprocess.extract_features import extract_features

# Streamlit UI
st.title("Salain - Email Threat Detector")
st.markdown("Protect yourself from malicious emails 🇵🇭")

# Input Section
input_type = st.radio("Choose input type:", ("Text", "Image"))

email_text = ""
if input_type == "Text":
    email_text = st.text_area("Paste email content here:", height=200)
else:
    uploaded_file = st.file_uploader("Upload email screenshot:", 
                                   type=["png", "jpg", "jpeg"])
    if uploaded_file:
            email_text = "TODO: Add OCR"
            st.subheader("Extracted Text:")
            st.write(email_text)

# Prediction Logic
if st.button("Analyze Email"):
    if email_text.strip():
        prediction, confidence = classify_email(email_text)
        
        # Display results
        if prediction[0] == 1:
            st.error(f"⚠️ Malicious Detected (Confidence: {confidence:.2%})")
            st.write("Common red flags found:")
            st.json(extract_features(email_text))
        else:
            st.success(f"✅ Safe Email (Confidence: {1-confidence:.2%})")
    else:
        st.warning("Please enter email text or upload an image")