from test import synthetic_labeld_emails
from scripts.classical import classify_email
import random

random_email = random.choice(list(synthetic_labeld_emails.keys()))

random_email = "Hello participants, The webinar 'Professional Development in Tech Industries' will begin tomorrow at 1pm EST. Link to join was sent in a previous email."

# prediction, confidence = classify_email(random_email)
prediction, confidence = classify_email(random_email)

result = "malicious" 
if prediction[0] != 1:
    confidence = 1-confidence

# Print result
print(f"\nEmail: {random_email}")
print(f"\nClassified as: {result} ({confidence:.2%} Confidence)")
print(f"\nIs actually: {synthetic_labeld_emails[random_email]}\n")