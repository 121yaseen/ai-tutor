import os
from google.cloud import firestore
from google.auth.credentials import AnonymousCredentials
from typing import Dict, Any
import json
from datetime import datetime

os.environ["FIRESTORE_EMULATOR_HOST"] = "127.0.0.1:8080"
def get_firestore_client():
    # If FIRESTORE_EMULATOR_HOST is set, use the emulator for local development
    if os.environ.get("FIRESTORE_EMULATOR_HOST"):
        # Emulator does not require credentials
        return firestore.Client(project=os.environ.get("GCLOUD_PROJECT", "demo-project"), credentials=AnonymousCredentials())
    # Otherwise, use default credentials (GCP)
    return firestore.Client()

def display_firestore_data():
    """
    Display all data from Firestore collections in a readable format.
    """
    try:
        db = get_firestore_client()
        collections = db.collections()
        
        print("\n=== Firestore Data Viewer ===\n")
        
        for collection in collections:
            print(f"\nCollection: {collection.id}")
            print("-" * 50)
            
            docs = collection.stream()
            for doc in docs:
                print(f"\nDocument ID: {doc.id}")
                data = doc.to_dict()
                
                # Format the data for better readability
                formatted_data = {}
                for key, value in data.items():
                    if isinstance(value, datetime):
                        formatted_data[key] = value.isoformat()
                    else:
                        formatted_data[key] = value
                
                print(json.dumps(formatted_data, indent=2))
                print("-" * 30)
                
        print("\n=== End of Firestore Data ===\n")
        
    except Exception as e:
        print(f"Error accessing Firestore: {str(e)}")

if __name__ == "__main__":
    display_firestore_data()
