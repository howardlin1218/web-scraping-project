import smtplib
from email.message import EmailMessage
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import test
import os 
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
api_key = os.getenv("GROQ_API_KEY")

client = Groq(api_key=api_key)

EMAIL_ADDRESS = "howlin1218@gmail.com"
EMAIL_PASSWORD = "lfwq enzr njdt fljh"  # Not your normal password!
SEPARATOR = ""

results_list = test.search_all_sites()
email_content = ""
llm_response_html = []
meta_data_html = []
website_urls = {"https://www.tomshardware.com/search": "Tom's Hardware",
                "https://www.pcmag.com/search/results": "PC Mag",
                "https://thepcenthusiast.com/": "The PC Enthusiast",
                "https://hothardware.com/search": "Hot Hardware",
                "https://pcper.com/": "PC Perspective",
                "https://gamerant.com/search": "GameRant",
                "https://www.windowscentral.com/search": "Windows Central",
                "https://www.techradar.com/search": "Tech Radar"
                }

def convert_metadata_to_html(website_url, title, author, publish_date, keywords, link):
    rows = ""
    rows += f"<tr><td><strong>Website</strong></td><td>{website_urls[website_url]}</td></tr>\n"
    rows += f"<tr><td><strong>Article Title</strong></td><td>{title}</td></tr>\n"
    rows += f"<tr><td><strong>Author</strong></td><td>{author}</td></tr>\n"
    rows += f"<tr><td><strong>Publish Date</strong></td><td>{publish_date}</td></tr>\n"
    if len(keywords) > 1: 
        keywords = ", ".join(keywords)
    else: 
        keywords = "".join(keywords)
    rows += f"<tr><td><strong>Keywords</strong></td><td>{keywords}</td></tr>\n"
    link = f'<a href="{link}">{link}</a>'
    rows += f"<tr><td><strong>Article Link</strong></td><td>{link}</td></tr>\n"

    return f"""
<h2>Article Information</h2>
<table border="1" cellpadding="5" cellspacing="0" style="border-collapse: collapse;">
{rows}</table>"""
     
def convert_response_to_html_list(bullet_list_response):
    lines = bullet_list_response.strip().splitlines()
    list_items = []
    for line in lines: 
         line = line.strip()
         if line[0] == "*":
              content = line[1:].strip()
              list_items.append(f"<li>{content}</li>")
    html = "<ul>\n" + "\n".join(list_items) + "\n</ul>"
    return "<h2>Article Summary</h2>\n"+html

# construct the message 
for website_url, website_articles in results_list.items():
    email_content += f"{SEPARATOR}\nSearching on: {website_urls[website_url]}\n{SEPARATOR}\n"
    for article_url, metadata in website_articles.items(): 
        llm_response = ""
        content = f"""
Title: {metadata[2]} 
Author: {metadata[3]} 
Publish Date: {metadata[4]} 
Keywords: {metadata[1]} 
Link: {article_url}

"""     
        email_content += content
        completion = client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=[
            {
                "role": "user",
                "content": f"Summarize the following review/article, focusing on brand mentions, performance mentions, price, how it compares to other brands (if applicable) and other general information in about 7 bullet points (use * to represent bullet points). If something specified wasn't mentioned, don't mention that it wasn't mentioned in your response. I just want the summary without any greeting or response prompt like 'Here are 5 bullet points summarizing the article:'. Summarize: \n{metadata[0]}"
            }
            ],
            temperature=0.1,
            max_completion_tokens=1024,
            top_p=0.9,
            stream=True,
            stop=None
        )
        for chunk in completion:
            llm_response += chunk.choices[0].delta.content or ""
            email_content += chunk.choices[0].delta.content or ""
        email_content += f"\n{SEPARATOR}"

        llm_response = convert_response_to_html_list(llm_response)
        llm_response_html.append(llm_response)
        meta_data_html.append(convert_metadata_to_html(website_url, metadata[2], metadata[3], metadata[4], metadata[1], article_url))

with open("summaries.md", "w", encoding="utf-8") as file:
        file.write(email_content)
file.close()


email_content_html = "<html>\n<body>\n"
for index in range(len(meta_data_html)): 
    email_content_html += meta_data_html[index]
    email_content_html += "\n"
    email_content_html += llm_response_html[index]
    email_content_html += "<hr style=\"border: 1px solid #ccc; margin: 30px 0;\">"
email_content_html += "\n</body></html>"
#print(email_content_html)

msg = MIMEMultipart("alternative")
msg['Subject'] = "Daily Summary"
msg['From'] = "howlin1218@gmail.com"
msg['To'] = "howlin1218@gmail.com"
msg.attach(MIMEText(email_content_html, "html"))

# Connect using TLS
with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
    smtp.ehlo()           # Identify ourselves to the SMTP server
    smtp.starttls()       # Start TLS encryption
    smtp.ehlo()           # Re-identify after starting TLS (optional but good practice)
    smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
    smtp.send_message(msg)

print("email successfully sent!")