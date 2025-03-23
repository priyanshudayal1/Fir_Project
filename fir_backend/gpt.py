import requests
import os
import json
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

API_KEY = '12c6ced676b749258b582edd76600aa4'

headers = {
    "Content-Type": "application/json",
    "api-key": API_KEY,
}

ENDPOINT = "https://lexiai1.openai.azure.com/openai/deployments/lexiaiapi/chat/completions?api-version=2024-08-01-preview"

def callGPT(system_prompt, user_prompt):
    payload = {
        "messages": [
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": user_prompt
            }
        ],
        "max_tokens": 4096
    }

    try:
        response = requests.post(ENDPOINT, headers=headers, json=payload)
        
        # Log the request details for debugging
        logger.debug(f"Request URL: {ENDPOINT}")
        logger.debug(f"Request Headers: {headers}")
        logger.debug(f"Request Payload: {json.dumps(payload, indent=2)}")
        
        # If response is not successful, get detailed error information
        if not response.ok:
            error_info = {}
            try:
                error_info = response.json()
            except json.JSONDecodeError:
                error_info = {"text": response.text}
            
            error_message = (
                f"API request failed with status {response.status_code}:\n"
                f"Response: {json.dumps(error_info, indent=2)}\n"
                f"Error Type: {type(response.error).__name__ if hasattr(response, 'error') else 'Unknown'}"
            )
            logger.error(error_message)
            raise requests.RequestException(error_message)
        
        response_data = response.json()
        return response_data.get("choices")[0].get("message").get("content")
        
    except requests.RequestException as e:
        error_message = f"Failed to make the request:\nError: {str(e)}\nStatus Code: {e.response.status_code if hasattr(e, 'response') else 'N/A'}"
        logger.error(error_message)
        raise RuntimeError(error_message)
    except Exception as e:
        error_message = f"An unexpected error occurred: {str(e)}"
        logger.error(error_message)
        raise RuntimeError(error_message)
