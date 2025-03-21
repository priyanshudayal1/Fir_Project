import requests
import json

# Perplexity AI API Key
API_KEY = "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"

# Perplexity API Endpoint
URL = "https://api.perplexity.ai/chat/completions"

# Headers for API Request
HEADERS = {
    "accept": "application/json",
    "content-type": "application/json",
    "Authorization": f"Bearer {API_KEY}"
}

def fetch_legal_sections(transcribed_text, personal_info=None):
    """Fetches applicable legal sections based on FIR description using Perplexity AI."""
    
    if not transcribed_text.strip():
        return {"error": "Empty text provided."}

    try:
        # Prepare a structured description including extracted information
        incident_description = transcribed_text
        if personal_info:
            structured_info = []
            if personal_info.get("victim_name"):
                structured_info.append(f"Victim: {personal_info['victim_name']}")
            if personal_info.get("incident_location"):
                structured_info.append(f"Location: {personal_info['incident_location']}")
            if personal_info.get("accused_description"):
                structured_info.append(f"Accused Description: {personal_info['accused_description']}")
            if personal_info.get("stolen_properties"):
                structured_info.append(f"Stolen Items: {personal_info['stolen_properties']}")
            
            if structured_info:
                incident_description = "Key Details:\n" + "\n".join(structured_info) + "\n\nFull Description:\n" + transcribed_text

        # Request Payload
        payload = {
            "model": "sonar-pro",
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "Provide only the most relevant legal sections for FIR applicable under Indian law (criminal, civil, or any other relevant statutes) "
                        "based on the given incident. Ensure references are from the latest legal framework, including the Bharatiya Nyaya Sanhita (BNS), "
                        "Bharatiya Nagarik Suraksha Sanhita (BNSS), Bharatiya Sakshya Adhiniyam (BSA), and other applicable laws. "
                        "Only provide section numbers and their corresponding law, nothing else. Note: Do not use old IPC, CRPC, or Evidence Act."
                    )
                },
                {"role": "user", "content": incident_description}
            ]
        }

        # Make API Request
        response = requests.post(URL, headers=HEADERS, json=payload)

        # Handle API Response
        if response.status_code == 200:
            result = response.json()
            return {"legal_sections": result["choices"][0]["message"]["content"]}
        else:
            return {"error": f"API Error: {response.text}"}

    except Exception as e:
        return {"error": f"Request failed: {str(e)}"}
