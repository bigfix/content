"""Example of getting an API token from the BigFix REST API using Python and the requests library.
Ref: https://developer.bigfix.com/rest-api/api/token.html
Ref: https://help.hcl-software.com/bigfix/11.0/platform/Platform/Config/c_token_authentication.html
11.0.6 or higher: On the root server, first execute 'besadmin /createtokenkey' or 'BESAdmin.sh -createtokenkey' to enable token usage.
"""

import os
from datetime import datetime, timezone
import requests

# If we have the python-dotenv package, load environment variables from a .env file for convenience; otherwise, rely on environment variables being set by other means (e.g. export in shell, setx in Windows, CI/CD secrets, etc.)
try:
    from dotenv import load_dotenv
    load_dotenv() # loads environment variables from a .env file if present
except ImportError:
    print("python-dotenv not found, skipping .env loading. Set environment variables manually or install python-dotenv for .env support.")


def str_to_bool(value: str = "false") -> bool:
    """Parse a boolean-like string into a boolean value."""
    return str(value).strip().lower() in {"1", "true", "yes", "y", "on"}


server = os.getenv("BES_SERVER")
username = os.getenv("BES_USERNAME")
password = os.getenv("BES_PASSWORD")
token_name = os.getenv("BES_TOKEN_NAME")
token_duration = os.getenv("BES_TOKEN_DURATION", "30")
REPLACE_TOKEN = str_to_bool(os.getenv("REPLACE_TOKEN", "false"))  # Delete and recreate token if it already exists
REQUESTS_CA_BUNDLE = os.getenv("REQUESTS_CA_BUNDLE")  # Set this env var if using a self-signed cert.
verify = REQUESTS_CA_BUNDLE if REQUESTS_CA_BUNDLE else False

required_env_vars = {
    "BES_SERVER": server,
    "BES_USERNAME": username,
    "BES_PASSWORD": password,
    "BES_TOKEN_NAME": token_name,
}
missing_env_vars = [name for name, value in required_env_vars.items() if not value]
if missing_env_vars:
    print(f"Missing required environment variables: {', '.join(missing_env_vars)}")
    exit(1)


print("Attempting login with username,password to verify connectivity and credentials...")
try:
    response = requests.get(f"{server}/api/login", auth=(username, password), verify=verify)
    response.raise_for_status()
    print("Login successful.")

except requests.exceptions.RequestException as e:
    print(f"Error during login: {e}")
    exit(1)


print("Checking for existing token with the same name...")
try:
    response = requests.get(
        f"{server}/api/token/name/{token_name}",
        auth=(username, password),
        verify=verify,
    )
    # If we get a 200 response, it means a token with the same name already exists. If we get a 404 response, it means no token with the same name exists and we can proceed to create a new one. For any other response code, we should treat it as an error.
    response.raise_for_status()

    if not REPLACE_TOKEN:
        # If we get here, it means a token with the same name already exists, so we should exit to avoid creating multiple tokens with the same name
        print(f"Error: A token with the name '{token_name}' already exists. Please choose a different name or delete the existing token before creating a new one.")
        exit(1)
    else:
        print(f"A token with the name '{token_name}' already exists. Deleting existing token and proceeding to create a new one...")
        token_id = response.json().get("Id")
        response = requests.delete(
            f"{server}/api/token/{token_id}",
            auth=(username, password),
            verify=verify,
        )
        response.raise_for_status()

except requests.exceptions.HTTPError as e:
    if response.status_code == 404:
        print("No existing token with the same name, proceeding to create a new token...")
    else:        
        print(f"Error checking for existing token: {e}")
        exit(1)

print("Requesting new token...")    
try:
    response = requests.post(
        f"{server}/api/token",
        auth=(username, password),
        params={"name": token_name, "duration": token_duration},  # duration is in days; set to 0 for never expire
        verify=verify,
    )
    response.raise_for_status()

    print(f"Token created successfully. Save this value: {response.text}")
    if bool(response.json().get("Expiration")):
        expiration_ns = response.json().get("Expiration")
        expiration_seconds = expiration_ns / 1_000_000_000  # Convert from nanoseconds to seconds.
        print(f"Token expiration time: {datetime.fromtimestamp(expiration_seconds, tz=timezone.utc).isoformat()}")
    else:
        print("New token has no expiration time (never expires).")

except requests.exceptions.RequestException as e:
    print(f"Error creating token: {e}")

print("Be sure to save the token value now, as it cannot be retrieved again from the API. If you lose the token value, you will need to delete the token and create a new one.")
