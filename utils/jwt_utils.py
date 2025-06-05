import jwt
import os
import datetime
from datetime import timedelta
from typing import Optional
from uuid import UUID

from dotenv import load_dotenv

# Load environmental variables
load_dotenv()

# Read the secret key from .env
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
# Signature algorithm (HMAC with SHA-256)
JWT_ALGORITHM = "HS256"

# Check that the
if not JWT_SECRET_KEY:
    raise ValueError("JWT_SECRET_KEY environment variable not set. Please add it to your .env file.")


def create_magic_link_token(employee_id: UUID, email: str, expires_delta: Optional[timedelta] = None) -> str:
    """
    Generates a JWT for the Magic Link.
    The token contains employee_id, email and an expiry date.

    Args:
        employee_id (UUID): The UUID of the employee to be authenticated.
        email (str): The email address of the employee to be authenticated.
        expires_delta (Optional[timedelta]): Optional: The timespan (30 min) after which the token expires.

    Returns:
        encoded_jwt (str): The encoded JWT-String.
    """

    # expire date calculation
    if expires_delta:
        expire = datetime.datetime.now(datetime.timezone.utc) + expires_delta
    else:
        # expire time set to 30 minutes
        expire = datetime.datetime.now(datetime.timezone.utc) + timedelta(minutes=30)

    # creation of the payload of the token
    # 'exp' is a standard JWT claim for the expiry date
    # 'employee_id' und 'email' are own claims to identify an employee
    to_encode = {"exp": expire, "employee_id": str(employee_id),
                 "email": email}

    # encoding the token (signature)
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt


def decode_magic_link_token(token: str) -> Optional[dict]:
    """
    Decodes and validates the Magic Link JWT.
    Returns the payload as dict, if tokes is valid.
    Returns None in case the token has expired, is invalid or does not work for any other reason.

    Args:
        token (str): The JWT string to be decoded.

    Returns:
        decoded_token (Optional[dict]): The decoded payload as dict or None.
    """

    try:
        # Decoding of JWT (validation of signature and expiry date)
        decoded_token = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return decoded_token

    except jwt.ExpiredSignatureError:
        # Error when token has expired
        print("Magic link token has expired.")
        return None

    except jwt.InvalidTokenError as e:
        # Error when token is invalid
        print(f"Invalid magic link token: {e}")
        return None

