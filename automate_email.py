import smtplib
from email.message import EmailMessage
from test import search_toms_hardware

EMAIL_ADDRESS = "howlin1218@gmail.com"
EMAIL_PASSWORD = "lfwq enzr njdt fljh"  # Not your normal password!

matched_articles, matched_articles_keywords, matched_articles_titles, matched_articles_authors, matched_articles_publish_date = search_toms_hardware()

email_content = ""
# construct the message 
for link, content in matched_articles.items():
    title = matched_articles_titles[link]
    author = matched_articles_authors[link]
    publish_date = matched_articles_publish_date[link]
    keywords = matched_articles_keywords[link]
    article = matched_articles[link]
    
    content = f"""
Title: {title} 
Author: {author} 
Publish Date: {publish_date} 
Keywords: {keywords} 
Link: {link}
Article:
{article}
"""

    email_content += content

print(email_content)
msg = EmailMessage()
msg['Subject'] = "Daily Summary"
msg['From'] = "howlin1218@gmail.com"
msg['To'] = "howlin1218@gmail.com"
msg.set_content(email_content)

# Connect using TLS
with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
    smtp.ehlo()           # Identify ourselves to the SMTP server
    smtp.starttls()       # Start TLS encryption
    smtp.ehlo()           # Re-identify after starting TLS (optional but good practice)
    smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
    smtp.send_message(msg)