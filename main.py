from test import synthetic_labeld_emails
from classical import classify_email
import random

random_email = random.choice(list(synthetic_labeld_emails.keys()))

result = classify_email(random_email)


# Print result
print(f"\nEmail: {random_email}")
print(f"\nClassified as: {result}")
print(f"\nIs Actually: {synthetic_labeld_emails[random_email]}\n")