import requests
import os

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
        response.raise_for_status()
        response_data = response.json()
        # Removing debug print that's causing issues with JSON responses
        return response_data.get("choices")[0].get("message").get("content")
    except requests.RequestException as e:
        error_message = f"Failed to make the request. Error: {e}"
        print(error_message)
        raise RuntimeError(error_message)
