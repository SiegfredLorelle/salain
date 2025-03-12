import re
from bs4 import BeautifulSoup

def clean_email(text):
    # Remove HTML/CSS
    text = BeautifulSoup(text, "html.parser").get_text()

    # Remove URLs
    text = re.sub(r"http\S+|www\S+|https\S+", "", text)

    # Remove email addresses
    text = re.sub(r"\S+@\S+", "", text)

    # Remove special characters (keep letters, numbers, and basic punctuation)
    text = re.sub(r"[^a-zA-Z0-9.!?]+", " ", text)

    # Lowercase
    text = text.lower()

    return text