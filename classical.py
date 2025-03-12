from scripts.preprocess.clean_email import clean_email
from scripts.preprocess.extract_features import extract_features
import joblib
import numpy as np
from scipy.sparse import hstack

def classify_email(email_text):
    """
    Classifies an email as 'safe' or 'malicious'.

    Args:
        email_text (str): The raw email text to classify

    Returns:
        str: Classification result ('safe' or 'malicious')
    """
    # Load model and vectorizer
    model = joblib.load("models/malicious_email_classifier.pkl")
    tfidf_vectorizer = joblib.load("models/tfidf_vectorizer.pkl")

    # Extract manual features before cleaning
    email_manual_features = extract_features(email_text)
    email_manual_features_array = np.array([[
        email_manual_features['num_links'],
        email_manual_features['num_obfuscated'],
        email_manual_features['urgency_score']
    ]])

    # Clean email for TF-IDF
    email_text_clean = clean_email(email_text)
    email_tfidf = tfidf_vectorizer.transform([email_text_clean])

    # Combine features
    email_features_combined = hstack([email_tfidf, email_manual_features_array])

    # Predict and convert to text label
    prediction = model.predict(email_features_combined)
    result = "malicious" if prediction[0] == 1 else "safe"

    return result