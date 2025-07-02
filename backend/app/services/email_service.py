# backend/app/services/email_service.py
"""
Email service for user registration notifications
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
        # Email configuration - update these in your settings
        self.smtp_server = getattr(settings, 'SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = getattr(settings, 'SMTP_PORT', 587)
        self.smtp_username = getattr(settings, 'SMTP_USERNAME', '')
        self.smtp_password = getattr(settings, 'SMTP_PASSWORD', '')
        self.from_email = getattr(settings, 'FROM_EMAIL', 'noreply@docaposte.fr')

    async def send_registration_notification(self, admin_email: str, user_email: str, username: str, user_id: int):
        """Send email notification to admin about new user registration"""
        try:
            subject = "New User Registration Pending Approval - Talk4Finance"

            # Create approval and rejection URLs
            base_url = getattr(settings, 'BASE_URL', 'http://localhost:3000')
            approve_url = f"{base_url}/talk4finance/admin/approve-user/{user_id}?action=approve"
            reject_url = f"{base_url}/talk4finance/admin/approve-user/{user_id}?action=reject"

            html_body = f"""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h2 style="color: #00ACB5;">New User Registration - Talk4Finance</h2>

                    <p>A new user has registered for Talk4Finance and is awaiting your approval.</p>

                    <div style="background-color: #f8f9fa; padding: 15px; border-left: 4px solid #00ACB5; margin: 20px 0;">
                        <h3 style="margin-top: 0;">User Details:</h3>
                        <p><strong>Email:</strong> {user_email}</p>
                        <p><strong>Username:</strong> {username}</p>
                        <p><strong>Registration Date:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                    </div>

                    <p>Please review this registration and take appropriate action:</p>

                    <div style="text-align: center; margin: 30px 0;">
                        <a href="{approve_url}" 
                           style="background-color: #28a745; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; margin-right: 10px; display: inline-block;">
                            ✓ Approve User
                        </a>
                        <a href="{reject_url}" 
                           style="background-color: #dc3545; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block;">
                            ✗ Reject User
                        </a>
                    </div>

                    <p style="font-size: 12px; color: #666; margin-top: 30px;">
                        This is an automated message from Talk4Finance. If you believe you received this email in error, please contact the system administrator.
                    </p>
                </div>
            </body>
            </html>
            """

            await self._send_email(admin_email, subject, html_body)
            logger.info(f"Registration notification sent to admin: {admin_email}")

        except Exception as e:
            logger.error(f"Failed to send registration notification: {str(e)}")
            raise

    async def send_approval_notification(self, user_email: str, username: str, approved: bool, rejection_reason: Optional[str] = None):
        """Send email notification to user about registration approval/rejection"""
        try:
            if approved:
                subject = "Your Talk4Finance Account Has Been Approved!"
                html_body = f"""
                <html>
                <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                        <h2 style="color: #00ACB5;">Welcome to Talk4Finance!</h2>

                        <p>Hi {username},</p>

                        <p>Great news! Your registration for Talk4Finance has been approved by our administrator.</p>

                        <div style="background-color: #d4edda; border: 1px solid #c3e6cb; color: #155724; padding: 15px; border-radius: 5px; margin: 20px 0;">
                            <strong>✓ Account Approved</strong><br>
                            You can now log in and start using Talk4Finance to analyze Docaposte's financial data.
                        </div>

                        <p>You can access the platform at: <a href="{getattr(settings, 'BASE_URL', 'http://localhost:3000')}/talk4finance/login">Talk4Finance Login</a></p>

                        <p>If you have any questions or need assistance, please don't hesitate to contact our support team.</p>

                        <p>Best regards,<br>The Talk4Finance Team</p>
                    </div>
                </body>
                </html>
                """
            else:
                subject = "Your Talk4Finance Registration Status"
                html_body = f"""
                <html>
                <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                        <h2 style="color: #dc3545;">Talk4Finance Registration Update</h2>

                        <p>Hi {username},</p>

                        <p>Thank you for your interest in Talk4Finance. Unfortunately, your registration has not been approved at this time.</p>

                        <div style="background-color: #f8d7da; border: 1px solid #f5c6cb; color: #721c24; padding: 15px; border-radius: 5px; margin: 20px 0;">
                            <strong>✗ Registration Not Approved</strong><br>
                            {f"Reason: {rejection_reason}" if rejection_reason else "Please contact the administrator for more information."}
                        </div>

                        <p>If you believe this is an error or have questions about this decision, please contact our administrator.</p>

                        <p>Best regards,<br>The Talk4Finance Team</p>
                    </div>
                </body>
                </html>
                """

            await self._send_email(user_email, subject, html_body)
            logger.info(f"Approval notification sent to user: {user_email} (approved: {approved})")

        except Exception as e:
            logger.error(f"Failed to send approval notification: {str(e)}")
            raise

    async def _send_email(self, to_email: str, subject: str, html_body: str):
        """Send email using SMTP"""
        if not self.smtp_username or not self.smtp_password:
            logger.warning("SMTP credentials not configured, skipping email send")
            return

        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.from_email
            msg['To'] = to_email

            html_part = MIMEText(html_body, 'html')
            msg.attach(html_part)

            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.smtp_username, self.smtp_password)
            server.send_message(msg)
            server.quit()

        except Exception as e:
            logger.error(f"SMTP error: {str(e)}")
            raise

# Create global instance
email_service = EmailService()

# Import datetime for email templates
from datetime import datetime