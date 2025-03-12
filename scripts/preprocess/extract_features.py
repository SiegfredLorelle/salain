import re

def extract_features(text):
    features = {}

    # Number of links
    features["num_links"] = len(re.findall(r"http\S+", text))

    # Number of obfuscated words (e.g., "p@ypal")
    features["num_obfuscated"] = len(re.findall(r"\w+[@\$]\w+", text))

    # Urgency keywords
    urgency_words = ["urgent", "immediately", "verify", "password"]
    features["urgency_score"] = sum(text.count(word) for word in urgency_words)

    return features