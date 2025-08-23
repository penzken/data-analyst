import requests
from datetime import datetime, timedelta
import json

class KiotVietFNBAuth:
    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret
        self.token_url = "https://api.fnb.kiotviet.vn/identity/connect/token"
        self.access_token = None
        self.token_expires_at = None
    
    def get_access_token(self):
        """
        Get access token from KiotViet FNB API
        Returns the access token string
        """
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        data = {
            "scope": "PublicApi.Access.FNB",
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }
        
        try:
            response = requests.post(self.token_url, headers=headers, data=data)
            response.raise_for_status()  # Raises an HTTPError for bad responses
            
            token_data = response.json()
            self.access_token = token_data["access_token"]
            
            # Calculate expiration time
            expires_in_seconds = token_data["expires_in"]
            self.token_expires_at = datetime.now() + timedelta(seconds=expires_in_seconds)
            
            print(f"Token obtained successfully!")
            print(f"Token type: {token_data['token_type']}")
            print(f"Expires in: {expires_in_seconds} seconds")
            print(f"Expires at: {self.token_expires_at}")
            
            return self.access_token
            
        except requests.exceptions.RequestException as e:
            print(f"Error getting access token: {e}")
            return None
        except KeyError as e:
            print(f"Unexpected response format: {e}")
            return None
    
    def is_token_valid(self):
        """
        Check if the current token is still valid
        """
        if not self.access_token or not self.token_expires_at:
            return False
        
        # Add 5 minute buffer before expiration
        return datetime.now() < (self.token_expires_at - timedelta(minutes=5))
    
    def get_valid_token(self):
        """
        Get a valid access token, refreshing if necessary
        """
        if not self.is_token_valid():
            return self.get_access_token()
        return self.access_token
    
    def get_auth_headers(self):
        """
        Get headers with authorization token for API calls
        """
        token = self.get_valid_token()
        if token:
            return {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
        return None

# Example usage
if __name__ == "__main__":
    # Replace with your actual credentials
    CLIENT_ID = "dc1d7025-0578-4426-bdae-a4fd1f69676a"
    CLIENT_SECRET = "2503C3E89A758864C880BDF5B9B0F6FA87CE23AE"
    
    # Initialize the auth client
    auth_client = KiotVietFNBAuth(CLIENT_ID, CLIENT_SECRET)
    
    # Get access token
    token = auth_client.get_access_token()
    
    if token:
        print(f"\nAccess Token: {token[:50]}...")  # Print first 50 chars for security
        
        # Get headers for subsequent API calls
        headers = auth_client.get_auth_headers()
        print(f"\nAuth headers ready for API calls:")
        print(f"Authorization: Bearer {token[:20]}...")
        
        # Example of how to use the token for subsequent API calls
        # response = requests.get("https://api.fnb.kiotviet.vn/your-endpoint", headers=headers)
    else:
        print("Failed to obtain access token")