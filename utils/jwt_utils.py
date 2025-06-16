import jwt
import os
import datetime
from datetime import timedelta
from typing import Optional, Dict, Any
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

# Load access token expiry time from .env
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))


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


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Generates a JWT for general access.
    The token contains arbitrary data (payload) and an expiry date.

    Args:
        data (Dict[str, Any]): The payload data to be encoded into the JWT.
        expires_delta (Optional[timedelta]): Optional: The timedelta after which the token expires.
    """

    to_encode = data.copy()
    if expires_delta:
        expire = datetime.datetime.now(datetime.timezone.utc) + expires_delta
    else:
        expire = datetime.datetime.now(datetime.timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """
    Decodes and validates a JWT (general purpose).
    Returns the payload as dict if the token is valid.
    Returns None in case the token has expired, is invalid, or does not work for any other reason.

    Args:
        token (str): The JWT string to be decoded.

    Returns:
        Optional[dict]: The decoded payload as a dictionary if the token is valid,
                        otherwise None if the token is expired, invalid, or cannot be decoded.
    """

    try:
        decoded_token = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return decoded_token

    except jwt.ExpiredSignatureError:
        print("Access token has expired.")
        return None

    except jwt.InvalidTokenError as e:
        print(f"Invalid access token: {e}")
        return None

