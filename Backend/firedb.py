import firebase_admin
from firebase_admin import credentials, firestore

cred = credentials.Certificate("firebase.json")

firebase_admin.initialize_app(cred)

# Initialize Firestore Database (if needed)
db = firestore.client()
