import os
import re
from html import escape
import resend
from fastmcp import FastMCP
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware

# Initialize Resend
resend.api_key = os.environ.get("RESEND_API_KEY")

# Recipient email (configurable via env)
RECIPIENT_EMAIL = os.environ.get("RECIPIENT_EMAIL", "yoann@dockai.co")

# Email validation regex
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')

# Create MCP server
mcp = FastMCP("EmailMe")

@mcp.tool
def send_email(
    name: str,
    email: str,
    message: str
) -> str:
    """
    Send an email. Use this to contact, ask questions, or request information.

    Args:
        name: Your name
        email: Your email address for reply
        message: Your message

    Returns:
        Confirmation message
    """
    if not resend.api_key:
        return "Email service is not configured. Please try again later."

    # Validate email format
    if not EMAIL_REGEX.match(email):
        return "Invalid email format. Please provide a valid email address."

    # Sanitize inputs to prevent XSS
    safe_name = escape(name)
    safe_email = escape(email)
    safe_message = escape(message).replace('\n', '<br>')

    try:
        resend.Emails.send({
            "from": "EmailMe <noreply@dockai.co>",
            "to": [RECIPIENT_EMAIL],
            "subject": f"[EmailMe] Message from {safe_name}",
            "html": f"""
                <p><strong>From:</strong> {safe_name} ({safe_email})</p>
                <hr>
                <p>{safe_message}</p>
            """,
            "reply_to": email
        })
        return f"Email sent! We'll reply to {email} soon."
    except Exception:
        return "Failed to send email. Please try again later."


# Create ASGI app with CORS
middleware = [
    Middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )
]

app = mcp.http_app(middleware=middleware)
