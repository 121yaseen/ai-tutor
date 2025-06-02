import os
from google.cloud import firestore
from google.auth.credentials import AnonymousCredentials


def get_firestore_client():
    # If FIRESTORE_EMULATOR_HOST is set, use the emulator for local development
    if os.environ.get("FIRESTORE_EMULATOR_HOST"):
        # Emulator does not require credentials
        return firestore.Client(project=os.environ.get("GCLOUD_PROJECT", "demo-project"), credentials=AnonymousCredentials())
    # Otherwise, use default credentials (GCP)
    return firestore.Client() 