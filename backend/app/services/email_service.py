# backend/app/services/email_service.py
"""
Enhanced Email service for user registration and approval notifications
"""
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from app.core.config import settings

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        self.smtp_server = settings.SMTP_SERVER
        self.smtp_port = settings.SMTP_PORT
        self.smtp_username = settings.SMTP_USERNAME
        self.smtp_password = settings.SMTP_PASSWORD
        self.from_email = settings.FROM_EMAIL

    def _send_email(self, to_email: str, subject: str, html_body: str, text_body: str = None):
        """Send email using SMTP"""
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = self.from_email
            msg['To'] = to_email
            msg['Subject'] = subject

            # Add text part if provided
            if text_body:
                text_part = MIMEText(text_body, 'plain')
                msg.attach(text_part)

            # Add HTML part
            html_part = MIMEText(html_body, 'html')
            msg.attach(html_part)

            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                if self.smtp_username and self.smtp_password:
                    server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)

            logger.info(f"Email sent successfully to {to_email}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return False

    async def send_registration_notification(self, admin_email: str, user_email: str, username: str, user_id: int):
        """Send email notification to admin about new user registration"""

        subject = "🔔 New User Registration - Talk4Finance"

        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #00ACB5, #00929A); padding: 30px; border-radius: 12px 12px 0 0; text-align: center; }}
                .header h1 {{ color: white; margin: 0; font-size: 24px; }}
                .header p {{ color: rgba(255,255,255,0.9); margin: 5px 0 0 0; }}
                .content {{ background: white; padding: 30px; border: 1px solid #e1e5e9; }}
                .user-details {{ background: #f8f9fa; padding: 20px; border-left: 4px solid #00ACB5; margin: 20px 0; border-radius: 8px; }}
                .actions {{ margin: 30px 0; text-align: center; }}
                .btn {{ display: inline-block; padding: 12px 24px; margin: 0 10px; text-decoration: none; border-radius: 8px; font-weight: 600; }}
                .btn-approve {{ background: #10B981; color: white; }}
                .btn-reject {{ background: #EF4444; color: white; }}
                .footer {{ background: #f8f9fa; padding: 20px; border-radius: 0 0 12px 12px; text-align: center; color: #6b7280; font-size: 14px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🛡️ Admin Notification</h1>
                    <p>New user registration pending approval</p>
                </div>

                <div class="content">
                    <h2>New User Registration</h2>
                    <p>A new user has registered for Talk4Finance and is awaiting your approval.</p>

                    <div class="user-details">
                        <h3>📋 User Details:</h3>
                        <p><strong>👤 Username:</strong> {username}</p>
                        <p><strong>📧 Email:</strong> {user_email}</p>
                        <p><strong>🆔 User ID:</strong> {user_id}</p>
                        <p><strong>🕒 Registration Time:</strong> Just now</p>
                    </div>

                    <div class="actions">
                        <a href="{settings.BASE_URL}/talk4finance/admin" class="btn btn-approve">
                            ✅ Review in Admin Dashboard
                        </a>
                    </div>

                    <p><strong>⚡ Quick Actions:</strong></p>
                    <p>You can approve or reject this user directly from the admin dashboard. The user will receive an automatic notification of your decision.</p>
                </div>

                <div class="footer">
                    <p>🔒 This is an automated message from Talk4Finance Admin System</p>
                    <p>Docaposte - Financial Intelligence Platform</p>
                </div>
            </div>
        </body>
        </html>
        """

        text_body = f"""
        New User Registration - Talk4Finance

        A new user has registered and is awaiting approval:

        Username: {username}
        Email: {user_email}
        User ID: {user_id}

        Please log in to the admin dashboard to review and approve/reject this registration.
        Dashboard: {settings.BASE_URL}/talk4finance/admin

        This is an automated message from Talk4Finance.
        """

        self._send_email(admin_email, subject, html_body, text_body)

    async def send_approval_notification(self, user_email: str, username: str, approved: bool, rejection_reason: str = None):
        """Send approval/rejection notification to user"""

        if approved:
            subject = "🎉 Welcome to Talk4Finance - Account Approved!"

            html_body = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: linear-gradient(135deg, #10B981, #059669); padding: 30px; border-radius: 12px 12px 0 0; text-align: center; }}
                    .header h1 {{ color: white; margin: 0; font-size: 24px; }}
                    .content {{ background: white; padding: 30px; border: 1px solid #e1e5e9; }}
                    .success-box {{ background: #f0fdf4; padding: 20px; border-left: 4px solid #10B981; margin: 20px 0; border-radius: 8px; }}
                    .btn {{ display: inline-block; padding: 12px 24px; background: #00ACB5; color: white; text-decoration: none; border-radius: 8px; font-weight: 600; margin: 20px 0; }}
                    .footer {{ background: #f8f9fa; padding: 20px; border-radius: 0 0 12px 12px; text-align: center; color: #6b7280; font-size: 14px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🎉 Account Approved!</h1>
                    </div>

                    <div class="content">
                        <h2>Welcome to Talk4Finance, {username}!</h2>

                        <div class="success-box">
                            <p><strong>✅ Great news!</strong> Your Talk4Finance account has been approved and activated.</p>
                        </div>

                        <p>You can now access all features of our AI-powered financial intelligence platform:</p>

                        <ul>
                            <li>🤖 Interactive AI financial assistant</li>
                            <li>📊 Advanced data analytics and insights</li>
                            <li>📈 Performance metrics and reporting</li>
                            <li>💼 Docaposte financial data access</li>
                        </ul>

                        <div style="text-align: center;">
                            <a href="{settings.BASE_URL}/talk4finance/login" class="btn">
                                🚀 Login to Talk4Finance
                            </a>
                        </div>

                        <p><strong>Getting Started:</strong></p>
                        <p>Once logged in, you can start asking questions about financial data, request analysis, or explore our suggested prompts to get familiar with the platform.</p>
                    </div>

                    <div class="footer">
                        <p>Welcome to the future of financial intelligence!</p>
                        <p>Docaposte - Talk4Finance Team</p>
                    </div>
                </div>
            </body>
            </html>
            """

            text_body = f"""
            Account Approved - Talk4Finance

            Hello {username},

            Great news! Your Talk4Finance account has been approved and activated.

            You can now log in and start using our AI-powered financial intelligence platform.

            Login at: {settings.BASE_URL}/talk4finance/login

            Welcome to Talk4Finance!
            Docaposte Team
            """

        else:
            subject = "❌ Talk4Finance Registration Update"

            reason_text = f"Reason: {rejection_reason}" if rejection_reason else "No specific reason provided."

            html_body = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: linear-gradient(135deg, #EF4444, #DC2626); padding: 30px; border-radius: 12px 12px 0 0; text-align: center; }}
                    .header h1 {{ color: white; margin: 0; font-size: 24px; }}
                    .content {{ background: white; padding: 30px; border: 1px solid #e1e5e9; }}
                    .info-box {{ background: #fef2f2; padding: 20px; border-left: 4px solid #EF4444; margin: 20px 0; border-radius: 8px; }}
                    .footer {{ background: #f8f9fa; padding: 20px; border-radius: 0 0 12px 12px; text-align: center; color: #6b7280; font-size: 14px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>Registration Update</h1>
                    </div>

                    <div class="content">
                        <h2>Hello {username},</h2>

                        <div class="info-box">
                            <p><strong>Registration Status:</strong> Unfortunately, your Talk4Finance registration was not approved at this time.</p>
                            <p><strong>{reason_text}</strong></p>
                        </div>

                        <p>If you believe this is an error or would like to discuss your application, please contact our administrator:</p>
                        <p><strong>📧 Contact:</strong> {settings.ADMIN_EMAIL}</p>

                        <p>Thank you for your interest in Talk4Finance.</p>
                    </div>

                    <div class="footer">
                        <p>Docaposte - Talk4Finance Team</p>
                    </div>
                </div>
            </body>
            </html>
            """

            text_body = f"""
            Registration Update - Talk4Finance

            Hello {username},

            Unfortunately, your Talk4Finance registration was not approved at this time.
            {reason_text}

            If you have questions, please contact: {settings.ADMIN_EMAIL}

            Thank you for your interest in Talk4Finance.
            Docaposte Team
            """

        self._send_email(user_email, subject, html_body, text_body)

# Create global instance
email_service = EmailService()