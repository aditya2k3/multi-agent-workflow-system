import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from Backend.config.settings import CREDENTIALS_FILE, TOKEN_FILE

# Scopes: Calendar + Gmail Send
SCOPES = [
    "https://www.googleapis.com/auth/calendar.events",
    "https://www.googleapis.com/auth/gmail.send",
]


def get_authenticated_credentials():
    """
    Handles OAuth2 login flow.
    - First run: Opens browser for user to login and grant permission
    - Subsequent runs: Uses saved token.json
    - Auto-refreshes expired tokens
    """
    creds = None

    # Check if token already exists
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    # If no valid credentials, run login flow
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            # Refresh expired token
            creds.refresh(Request())
        else:
            # First-time login — opens browser
            if not os.path.exists(CREDENTIALS_FILE):
                raise FileNotFoundError(
                    f"credentials.json not found at {CREDENTIALS_FILE}. "
                    "Download it from Google Cloud Console."
                )

            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=8090)

        # Save token for next time
        with open(TOKEN_FILE, "w") as token:
            token.write(creds.to_json())

    return creds