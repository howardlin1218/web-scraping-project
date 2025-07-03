import smtplib
#from email.message import EmailMessage
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import test
import os 
from dotenv import load_dotenv
from groq import Groq
from database import insert_to_supabase

load_dotenv()
api_key = os.getenv("GROQ_API_KEY")

client = Groq(api_key=api_key)

EMAIL_ADDRESS = "howlin1218@gmail.com"
EMAIL_PASSWORD = "lfwq enzr njdt fljh"  # Not your normal password!
SEPARATOR = ""

results_list = None
email_content = ""
partial_email_html = ""
final_content_html = []
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
    rows += f"<tr><td><strong>Keywords</strong></td><td>{', '.join(keywords) if keywords else ''}</td></tr>\n"
    link = f'<a href="{link}">{link}</a>'
    rows += f"<tr><td><strong>Article Link</strong></td><td>{link}</td></tr>\n"

    return f"""
<h2>Article Information</h2>\n
<table border="1" cellpadding="5" cellspacing="0" style="border-collapse: collapse;">
\n{rows}</table>\n"""
     
def convert_response_to_html_list_summary(bullet_list_response):
    lines = bullet_list_response.strip().splitlines()
    list_items = []
    for line in lines: 
        line = line.strip()
        if line[0] == "*":
            content = line[1:].strip()
            list_items.append(f"<li>{content}</li>")
    html = "<ul>\n" + "\n".join(list_items) + "\n</ul>\n"
    return "<h2>Article Summary</h2>\n"+html

def convert_response_to_html_list_sentiment(bullet_list_response):
    rows = ""
    lines = bullet_list_response.strip().splitlines()
    for line in lines: 
        line = line.strip()
        if line == "":
            continue
        if line[0] == "*":
            if "positive" in line[1:].lower():
                rows += "<tr><td><strong>Positive</strong></td><td>\n<ul>"
            if "neutral" in line[1:].lower():
                rows += "</ul>\n</td></tr>\n<tr><td><strong>Neutral</strong></td><td>\n<ul>"
            if "negative" in line[1:].lower():
                rows += "</ul>\n</td></tr>\n<tr><td><strong>Negative</strong></td><td>\n<ul>"
            continue
        rows += f"<li>{line[1:].strip()}</li>\n"
    rows += "</ul>\n</td></tr>\n"
    return f"""
<h2>Sentiment Analysis</h2>\n
<table border="1" cellpadding="5" cellspacing="0" style="border-collapse: collapse;">
\n{rows}</table>\n"""

def construct_message(email_content=email_content, final_content_html=final_content_html, results_list=results_list):
    # construct the message 
    '''if results_list is None: 
        return ""
    for website_url, website_articles in results_list.items():
        for article_url, metadata in website_articles.items(): 
            current_article_html = ""
            llm_response_summary = ""
            llm_response_sentiment = ""
            partial_email_html = ""
            completion_summary = client.chat.completions.create(
                model="meta-llama/llama-4-scout-17b-16e-instruct",
                messages=[
                {
                    "role": "user",
                    "content": f"Summarize the following review/article, focusing on brand mentions, performance mentions, price, how it compares to other brands (if applicable) and other general information in about 7 bullet points (use * to represent bullet points). If something specified wasn't mentioned, don't mention that it wasn't mentioned in your response. I just want the summary and analysis without any greeting or response prompt like 'Here are 5 bullet points summarizing the article:'. Perform the tasks described on the following article: \n{metadata[0]}" 
                }
                ],
                temperature=0.1,
                max_completion_tokens=1024,
                top_p=0.9,
                stream=True,
                stop=None
            )
            
            for chunk in completion_summary:
                llm_response_summary += chunk.choices[0].delta.content or ""
                email_content += chunk.choices[0].delta.content or ""

            completion_analysis = client.chat.completions.create(
                model="meta-llama/llama-4-scout-17b-16e-instruct",
                messages=[
                {
                    "role": "user",
                    "content": f"I want a sentiment analysis of the following review/article, focusing on positive, neutral, and negative sentiments. Use bullet points (*) to represent the three categories of Positive/Neutral/Negative, and within those categories, use dash (-) to represent the content of that category. Basically, the structure of your response should just be 3 bullet points (*) for each of Positive/Neutral/Negative, and a list inside each category represented by dashes (-) that show the actual sentiments. I just want the analysis without any greeting or response prompt like 'Here is the sentiment analysis'. Perform the tasks described on the following article: \n{metadata[0]}" 
                }
                ],
                temperature=0.1,
                max_completion_tokens=1024,
                top_p=0.9,
                stream=True,
                stop=None
            )

            for chunk in completion_analysis:
                llm_response_sentiment += chunk.choices[0].delta.content or ""

            # current article html - for database
            current_article_html += convert_metadata_to_html(website_url, metadata[2], metadata[3], metadata[4], metadata[1], article_url)
            current_article_html += convert_response_to_html_list_summary(llm_response_summary)
            current_article_html += convert_response_to_html_list_sentiment(llm_response_sentiment)
            current_article_html += "<hr style=\"border: 1px solid #ccc; margin: 30px 0;\">"
            
            # for database
            final_content_html.append({"website": website_urls[website_url], "title": metadata[2], "author": metadata[3], "published": metadata[4], "keywords": (", ".join(metadata[1]) if metadata[1] else ""), "url": article_url, "content": current_article_html})

            # full article list html - for email
            partial_email_html += current_article_html
            
    return "<html>\n<body>\n" + partial_email_html + "\n</body>\n</html>"'''
    '''return r"""
<table border="1" cellpadding="5" cellspacing="0" style="border-collapse: collapse;">
<tr><td><strong>Title</strong></td><td>MSI unveils EdgeXpert MS-C931 desktop AI supercomputer powered by Nvidia DGX Spark</td></tr>
<tr><td><strong>Author</strong></td><td>Stephen Warwick</td></tr>
<tr><td><strong>Publish Date</strong></td><td>19 May 25</td></tr>
<tr><td><strong>Keywords</strong></td><td>msi</td></tr>
<tr><td><strong>Article Link</strong></td><td><a href="https://www.tomshardware.com/desktops/msi-unveils-edgexpert-ms-c931-desktop-ai-supercomputer-powered-by-nvidia-dgx-spark">https://www.tomshardware.com/desktops/msi-unveils-edgexpert-ms-c931-desktop-ai-supercomputer-powered-by-nvidia-dgx-spark</a></td></tr>
</table>
<ul>
<li>The MSI EdgeXpert MS-C931 desktop AI supercomputer is powered by Nvidia's DGX Spark platform and features the Nvidia GB10 Grace Blackwell Superchip, capable of 1,000 AI TOPS FP4 performance.</li>
<li>The system offers 128GB of unified LPDDR5x memory, ConnectX7 networking, and supports large language models, making it suitable for AI developers and researchers in fields like education, finance, and healthcare.</li>
<li>The MSI EdgeXpert MS-C931 is available to pre-order, but pricing is not disclosed, and interested buyers need to contact MSI directly.</li>
<li>The device is compact, weighing 1.2kg and measuring 151mm x 151mm x 52 mm, with connectivity features including 4x USB 3.2 Type C ports, a 10GbE RJ-45 connector, Wi-Fi 7, and Bluetooth 5.3.</li>
<li>Storage configurations include 1 or 4TB of NVMe M.2 storage, and the system runs on Nvidia's DGX OS, capable of running up to 200-billion-parameter large language models, or up to 405-billion-parameter models when using two devices connected via Nvidia Connect X.</li>
</ul>
"""'''

email_content_html = construct_message()
'''
with open("summaries.html", "w", encoding="utf-8") as file:
        file.write(email_content_html)
file.close()'''

def save_to_database(final_content_html=final_content_html):
    insert_to_supabase(final_content_html)

'''
msg = MIMEMultipart("alternative")
msg['Subject'] = "Daily Summary"
msg['From'] = "howlin1218@gmail.com"
msg['To'] = "howardlin@msi.com"
msg.attach(MIMEText(email_content_html, "html"))

# Connect using TLS
with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
    smtp.ehlo()           # Identify ourselves to the SMTP server
    smtp.starttls()       # Start TLS encryption
    smtp.ehlo()           # Re-identify after starting TLS (optional but good practice)
    smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
    smtp.send_message(msg)

print("email successfully sent!")
'''