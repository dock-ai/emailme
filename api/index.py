import os
import resend
from fastmcp import FastMCP
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware

# Initialize Resend
resend.api_key = os.environ.get("RESEND_API_KEY")

# Hardcoded for MVP
RECIPIENT_EMAIL = "yoann@dockai.co"

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

    try:
        resend.Emails.send({
            "from": "EmailMe <noreply@dockai.co>",
            "to": [RECIPIENT_EMAIL],
            "subject": f"[EmailMe] Message from {name}",
            "html": f"""
                <p><strong>From:</strong> {name} ({email})</p>
                <hr>
                <p>{message}</p>
            """,
            "reply_to": email
        })
        return f"Email sent! We'll reply to {email} soon."
    except Exception as e:
        return f"Failed to send email: {str(e)}"


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
