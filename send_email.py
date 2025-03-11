import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
import dotenv
import os
from datetime import datetime

def send_inactivity_notice(user_data):
    """
    Send inactivity notice email to controller
    user_data should be a dictionary containing:
    - first_name
    - last_name
    - cid
    - email
    - hours
    - positions (list)
    """
    # Email credentials
    dotenv.load_dotenv()
    sender_email = os.getenv("EMAIL_ADDRESS")
    sender_password = os.getenv("EMAIL_PASSWORD")

    # Create message
    msg = MIMEMultipart('related')
    msg['Subject'] = 'VATUSA ZJX: Removal Notice - Controller Inactivity'
    msg['From'] = sender_email
    msg['To'] = user_data['email']

    # Read and attach the logo image
    with open('./logo.png', 'rb') as f:
        logo_data = f.read()
    logo = MIMEImage(logo_data)
    logo.add_header('Content-ID', '<logo>')
    msg.attach(logo)

    positions_list = "<br>".join(user_data['positions']) if user_data['positions'] else "No positions worked"
    
    html = f"""
    <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333333;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    background-color: #003087;
                    color: white;
                    padding: 20px;
                    text-align: center;
                }}
                .content {{
                    padding: 20px;
                    background-color: #ffffff;
                }}
                .footer {{
                    text-align: center;
                    padding: 20px;
                    font-size: 12px;
                    color: #666666;
                    border-top: 1px solid #dddddd;
                    margin-top: 20px;
                }}
                .legal-text {{
                    font-size: 11px;
                    color: #888888;
                    line-height: 1.4;
                    margin-top: 15px;
                }}
                .stats-box {{
                    background-color: #f5f5f5;
                    padding: 15px;
                    margin: 20px 0;
                    border-radius: 5px;
                }}
                .footer-logo {{
                    width: 150px;
                    height: auto;
                    margin: 20px auto;
                    display: block;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Jacksonville ARTCC</h1>
                </div>
                <div class="content">
                    <p>Dear {user_data['first_name']} {user_data['last_name']},</p>
                    
                    <p>This email is to inform you that you have been removed from the Jacksonville ARTCC (ZJX) roster due to inactivity, in accordance with VATUSA policies.</p>
                    
                    <div class="stats-box">
                        <h3>Activity Summary - Past 90 Days</h3>
                        <p><strong>Controller Information:</strong><br>
                        Name: {user_data['first_name']} {user_data['last_name']}<br>
                        CID: {user_data['cid']}<br>
                        Total Hours: {user_data['hours']:.2f}</p>
                        
                        <p><strong>Positions Worked:</strong><br>
                        {positions_list}</p>
                    </div>
                    
                    <p>To maintain active status, controllers must complete at least 3 hours of controlling time within a 90-day period. If you wish to return to ZJX in the future, you will need to reapply through VATUSA.</p>
                    
                    <p>We thank you for your service to the Jacksonville ARTCC and wish you the best in your future endeavors.</p>
                    
                    <p>Best regards,<br>
                    Jacksonville ARTCC Staff</p>
                </div>
                <div class="footer">
                    <img src="cid:logo" alt="Jacksonville ARTCC Logo" class="footer-logo">
                    <p>© {datetime.now().year} Virtual Jacksonville ARTCC. All rights reserved.</p>
                    <p>Virtual Jacksonville ARTCC</p>
                    <div class="legal-text">
                        <p>This email is intended for {user_data['first_name']} {user_data['last_name']} ({user_data['cid']}) ONLY.<br>
                        If you believe that you received this email in error, contact the ZJX staff immediately.<br>
                        This email is not related to any real life aviation bodies or the F.A.A.</p>
                        
                        <p>Do not reply to this email unless it asks you to do so; this inbox might be unmonitored.</p>
                    </div>
                </div>
            </div>
        </body>
    </html>
    """

    # Create the HTML part
    html_part = MIMEText(html, 'html')
    msg.attach(html_part)

    # Send email
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(sender_email, sender_password)
            smtp.send_message(msg)
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False
