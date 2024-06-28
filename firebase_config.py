import os
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, firestore

# Load environment variables from .env file
load_dotenv()

# Get the path to the service account key file from the environment variable
key_path = os.getenv('FIREBASE_KEY_PATH')

if not key_path:
    raise ValueError("FIREBASE_KEY_PATH environment variable not set.")

# Initialize the Firebase Admin SDK
cred = credentials.Certificate(key_path)
firebase_admin.initialize_app(cred)

# Initialize Firestore
db = firestore.client()
