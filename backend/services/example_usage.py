"""
Example usage of CatalystLLMClient with automatic OAuth token management.

This demonstrates how the application can use the client without worrying about OAuth.
"""
import os
from llm_client import CatalystLLMClient


def main():
    """Example usage of CatalystLLMClient."""
    
    # Initialize client - OAuth is handled automatically
    client = CatalystLLMClient()
    
    # Example chat completion
    try:
        response = client.chat_completion(
            system_prompt="You are a helpful assistant.",
            user_prompt="What is the capital of France?",
            temperature=0.7,
            max_tokens=100
        )
        print("Response:", response)
        
        # Example JSON completion
        json_response = client.chat_completion_json(
            system_prompt="You are a data analyst.",
            user_prompt="Generate a JSON object with name and age",
            temperature=0.5
        )
        print("JSON Response:", json_response)
        
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    # Ensure environment variables are set
    required_vars = ["ZOHO_CLIENT_ID", "ZOHO_CLIENT_SECRET", "ZOHO_REFRESH_TOKEN"]
    missing = [var for var in required_vars if not os.getenv(var)]
    
    if missing:
        print(f"Missing required environment variables: {', '.join(missing)}")
        print("Please set them in your .env file or environment.")
    else:
        main()
