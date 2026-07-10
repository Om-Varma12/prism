"""
OAuth token manager for Zoho Catalyst QuickML API.

Automatically manages OAuth access tokens using refresh token flow.
Handles token refresh, expiry tracking, and automatic retry on token expiry.
"""
import os
import time
import requests
from typing import Optional
from dataclasses import dataclass


@dataclass
class TokenData:
    """Container for OAuth token data."""
    access_token: str
    expires_at: float  # Unix timestamp
    refresh_token: str


class TokenManager:
    """
    Manages OAuth access tokens for Zoho Catalyst QuickML API.
    
    Automatically handles token refresh, expiry tracking, and retry logic.
    """
    
    def __init__(self):
        """Initialize token manager with environment variables."""
        self.client_id = os.getenv("ZOHO_CLIENT_ID")
        self.client_secret = os.getenv("ZOHO_CLIENT_SECRET")
        self.refresh_token = os.getenv("ZOHO_REFRESH_TOKEN")
        self._token_data: Optional[TokenData] = None
        
        # Validate required environment variables
        if not all([self.client_id, self.client_secret, self.refresh_token]):
            raise ValueError(
                "Missing required environment variables: "
                "ZOHO_CLIENT_ID, ZOHO_CLIENT_SECRET, ZOHO_REFRESH_TOKEN"
            )
    
    def get_access_token(self) -> str:
        """
        Get a valid access token, refreshing if necessary.
        
        Returns:
            Valid access token string
        """
        # Check if we need to refresh
        if self._token_data is None or self._is_token_expired():
            self._refresh_token()
        
        return self._token_data.access_token
    
    def _is_token_expired(self, buffer_seconds: int = 300) -> bool:
        """
        Check if the current token is expired or about to expire.
        
        Args:
            buffer_seconds: Seconds before expiry to consider token as expired
            
        Returns:
            True if token is expired or will expire soon
        """
        if self._token_data is None:
            return True
        
        return time.time() >= (self._token_data.expires_at - buffer_seconds)
    
    def _refresh_token(self) -> None:
        """
        Refresh the access token using the refresh token.
        
        Raises:
            RuntimeError: If token refresh fails
        """
        url = "https://accounts.zoho.in/oauth/v2/token"
        
        params = {
            "grant_type": "refresh_token",
            "refresh_token": self.refresh_token,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }
        
        try:
            response = requests.post(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            access_token = data.get("access_token")
            expires_in = data.get("expires_in", 3600)  # Default to 1 hour
            
            if not access_token:
                raise RuntimeError("No access token in response")
            
            # Calculate expiry timestamp
            expires_at = time.time() + expires_in
            
            self._token_data = TokenData(
                access_token=access_token,
                expires_at=expires_at,
                refresh_token=self.refresh_token
            )
            
        except requests.RequestException as e:
            raise RuntimeError(f"Failed to refresh access token: {e}")
    
    def make_authenticated_request(
        self,
        method: str,
        url: str,
        headers: Optional[dict] = None,
        json: Optional[dict] = None,
        params: Optional[dict] = None,
        timeout: int = 30
    ) -> requests.Response:
        """
        Make an authenticated request with automatic token refresh and retry.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            url: Request URL
            headers: Additional headers
            json: JSON body for POST requests
            params: Query parameters
            timeout: Request timeout in seconds
            
        Returns:
            Response object
            
        Raises:
            RuntimeError: If request fails after token refresh retry
        """
        if headers is None:
            headers = {}
        
        # Add authorization header
        headers["Authorization"] = f"Zoho-oauthtoken {self.get_access_token()}"
        
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                json=json,
                params=params,
                timeout=timeout
            )
            
            # Check for invalid token error
            if response.status_code == 401 or self._is_invalid_token_response(response):
                # Refresh token and retry once
                self._refresh_token()
                headers["Authorization"] = f"Zoho-oauthtoken {self.get_access_token()}"
                
                response = requests.request(
                    method=method,
                    url=url,
                    headers=headers,
                    json=json,
                    params=params,
                    timeout=timeout
                )
            
            return response
            
        except requests.RequestException as e:
            raise RuntimeError(f"Request failed: {e}")
    
    def _is_invalid_token_response(self, response: requests.Response) -> bool:
        """
        Check if response indicates an invalid OAuth token.
        
        Args:
            response: Response object
            
        Returns:
            True if response indicates invalid token
        """
        try:
            data = response.json()
            return data.get("code") == "INVALID_OAUTHTOKEN"
        except (ValueError, KeyError):
            return False
