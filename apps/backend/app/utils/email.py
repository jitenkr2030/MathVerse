"""
MathVerse Backend API - Email Utilities
========================================
Email sending and notification utilities.
"""

from typing import Optional
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import loguru

from app.config import settings


logger = loguru.logger


async def send_password_reset_email(
    email: str,
    token: str,
    username: str
):
    """
    Send password reset email to user.
    
    Args:
        email: Recipient email address
        token: Password reset token
        username: User's username for personalization
    """
    if not settings.SMTP_HOST:
        logger.warning("SMTP not configured, skipping email send")
        return
    
    try:
        # Build email
        msg = MIMEMultipart("alternative")
        msg["Subject"] = "MathVerse - Password Reset Request"
        msg["From"] = f"MathVerse <{settings.EMAILS_FROM_EMAIL}>"
        msg["To"] = email
        
        # HTML content
        reset_link = f"{settings.FRONTEND_URL}/auth/reset-password?token={token}"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #3B82F6, #10B981); padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .header h1 {{ color: white; margin: 0; }}
                .content {{ padding: 30px; background: #f9fafb; }}
                .button {{ display: inline-block; padding: 12px 30px; background: #3B82F6; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
                .footer {{ padding: 20px; text-align: center; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>MathVerse 🧮</h1>
                </div>
                <div class="content">
                    <p>Hi {username},</p>
                    <p>We received a request to reset your password for your MathVerse account.</p>
                    <p>Click the button below to reset your password:</p>
                    <p><a href="{reset_link}" class="button">Reset Password</a></p>
                    <p>This link will expire in 1 hour.</p>
                    <p>If you didn't request this, please ignore this email or contact support if you have concerns.</p>
                </div>
                <div class="footer">
                    <p>MathVerse - Making Mathematics Beautiful</p>
                    <p>If you're having trouble, copy this link into your browser:<br>{reset_link}</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(html_content, "html"))
        
        # Send email
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.starttls()
            if settings.SMTP_USERNAME and settings.SMTP_PASSWORD:
                server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
            server.send_message(msg)
        
        logger.info(f"Password reset email sent to {email}")
        
    except Exception as e:
        logger.error(f"Failed to send password reset email: {e}")


async def send_welcome_email(
    email: str,
    username: str,
    role: str
):
    """
    Send welcome email to new users.
    
    Args:
        email: Recipient email address
        username: User's username
        role: User's role (student, teacher, creator)
    """
    if not settings.SMTP_HOST:
        logger.warning("SMTP not configured, skipping email send")
        return
    
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = "Welcome to MathVerse!"
        msg["From"] = f"MathVerse <{settings.EMAILS_FROM_EMAIL}>"
        msg["To"] = email
        
        role_benefits = {
            "student": "Access to interactive math animations and quizzes",
            "teacher": "Tools to create engaging math content",
            "creator": "Platform to share your math knowledge and earn revenue"
        }
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #3B82F6, #10B981); padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .header h1 {{ color: white; margin: 0; }}
                .content {{ padding: 30px; background: #f9fafb; }}
                .feature {{ padding: 15px; margin: 10px 0; background: white; border-radius: 5px; }}
                .footer {{ padding: 20px; text-align: center; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Welcome to MathVerse! 🎉</h1>
                </div>
                <div class="content">
                    <p>Hi {username},</p>
                    <p>Welcome to MathVerse! We're thrilled to have you join our community of math learners and creators.</p>
                    <div class="feature">
                        <strong>As a {role}, you can:</strong>
                        <p>{role_benefits.get(role, "Explore and learn mathematics through beautiful animations")}</p>
                    </div>
                    <p>Here are some quick links to get started:</p>
                    <ul>
                        <li>Explore our course catalog</li>
                        <li>Set up your profile</li>
                        <li>Join our community Discord</li>
                    </ul>
                </div>
                <div class="footer">
                    <p>MathVerse - Making Mathematics Beautiful</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(html_content, "html"))
        
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.starttls()
            if settings.SMTP_USERNAME and settings.SMTP_PASSWORD:
                server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
            server.send_message(msg)
        
        logger.info(f"Welcome email sent to {email}")
        
    except Exception as e:
        logger.error(f"Failed to send welcome email: {e}")


async def send_course_enrollment_email(
    email: str,
    username: str,
    course_title: str,
    course_url: str
):
    """
    Send email notification for course enrollment.
    
    Args:
        email: Recipient email address
        username: User's username
        course_title: Name of enrolled course
        course_url: Link to the course
    """
    if not settings.SMTP_HOST:
        logger.warning("SMTP not configured, skipping email send")
        return
    
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"You're enrolled in {course_title}!"
        msg["From"] = f"MathVerse <{settings.EMAILS_FROM_EMAIL}>"
        msg["To"] = email
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #3B82F6, #10B981); padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .header h1 {{ color: white; margin: 0; }}
                .content {{ padding: 30px; background: #f9fafb; }}
                .button {{ display: inline-block; padding: 12px 30px; background: #10B981; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
                .footer {{ padding: 20px; text-align: center; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🎉 Enrollment Complete!</h1>
                </div>
                <div class="content">
                    <p>Hi {username},</p>
                    <p>You're now enrolled in <strong>{course_title}</strong>!</p>
                    <p>Start your learning journey today:</p>
                    <p><a href="{course_url}" class="button">Start Learning</a></p>
                </div>
                <div class="footer">
                    <p>MathVerse - Making Mathematics Beautiful</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(html_content, "html"))
        
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.starttls()
            if settings.SMTP_USERNAME and settings.SMTP_PASSWORD:
                server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
            server.send_message(msg)
        
        logger.info(f"Enrollment confirmation email sent to {email}")
        
    except Exception as e:
        logger.error(f"Failed to send enrollment email: {e}")


async def send_creator_application_received(
    email: str,
    username: str
):
    """
    Send confirmation email for creator application.
    """
    if not settings.SMTP_HOST:
        logger.warning("SMTP not configured, skipping email send")
        return
    
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = "MathVerse Creator Application Received"
        msg["From"] = f"MathVerse <{settings.EMAILS_FROM_EMAIL}>"
        msg["To"] = email
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #F59E0B, #EF4444); padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .header h1 {{ color: white; margin: 0; }}
                .content {{ padding: 30px; background: #f9fafb; }}
                .footer {{ padding: 20px; text-align: center; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Application Received 📝</h1>
                </div>
                <div class="content">
                    <p>Hi {username},</p>
                    <p>Thank you for applying to become a MathVerse creator!</p>
                    <p>Our team will review your application and get back to you within 3-5 business days.</p>
                    <p>While you wait, feel free to explore our creator guidelines and prepare your first course!</p>
                </div>
                <div class="footer">
                    <p>MathVerse - Making Mathematics Beautiful</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(html_content, "html"))
        
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.starttls()
            if settings.SMTP_USERNAME and settings.SMTP_PASSWORD:
                server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
            server.send_message(msg)
        
        logger.info(f"Creator application confirmation sent to {email}")
        
    except Exception as e:
        logger.error(f"Failed to send creator application email: {e}")
