"""Example of using an existing API token with the BigFix REST API via Python requests.
Ref: https://developer.bigfix.com/rest-api/api/token.html
Ref: https://help.hcl-software.com/bigfix/11.0/platform/Platform/Config/c_token_authentication.html
11.0.6 or higher: On the root server, first execute 'besadmin /createtokenkey' or 'BESAdmin.sh -createtokenkey' to enable token usage.
"""

import os
import requests

# If we have the python-dotenv package, load environment variables from a .env file for convenience; otherwise, rely on environment variables being set by other means (e.g. export in shell, setx in Windows, CI/CD secrets, etc.)
try:
    from dotenv import load_dotenv
    load_dotenv() # loads environment variables from a .env file if present
except ImportError:
    print("python-dotenv not found, skipping .env loading. Set environment variables manually or install python-dotenv for .env support.")

server = os.getenv("BES_SERVER")
token = os.getenv("BES_TOKEN")
REQUESTS_CA_BUNDLE = os.getenv("REQUESTS_CA_BUNDLE")  # Set this env var if using a self-signed cert.
verify = REQUESTS_CA_BUNDLE if REQUESTS_CA_BUNDLE else False

required_env_vars = {
    "BES_SERVER": server,
    "BES_TOKEN": token,
}
missing_env_vars = [name for name, value in required_env_vars.items() if not value]
if missing_env_vars:
    print(f"Missing required environment variables: {', '.join(missing_env_vars)}")
    exit(1)

# Authorization header for token-based authentication
headers = {"Authorization": f"Bearer {token}"}

print("Attempting login with token to verify connectivity and credentials...")
try:
    response = requests.get(f"{server}/api/login", headers=headers, verify=verify)
    response.raise_for_status()
    print("Login successful.")
    print("Token is valid and can be used for authentication.")

except requests.exceptions.RequestException as e:
    print(f"Error during login: {e}")
    exit(1)

try:
    # Example retrieving current session info:
    response = requests.get(f"{server}/api/session", headers=headers, verify=verify)
    response.raise_for_status()
    print(f"Current session info: {response.text}")

except requests.exceptions.RequestException as e:
    print(f"Error retrieving session info: {e}")
    exit(1)
