from gpt import callGPT
import re
import requests
import json

def extract_legal_sections(transcribed_text, personal_info=None, language='english', source_url=None):
    """
    Extract applicable legal sections based on FIR description using GPT API.
    Returns structured data including act names and section numbers.
    
    Parameters:
    - transcribed_text: The incident description text
    - personal_info: Optional dictionary containing personal details
    - language: Language for processing ('english', 'hindi', 'punjabi')
    - source_url: Optional URL to extract acts and sections from
    """
    
    if not transcribed_text.strip():
        return {"error": "Empty text provided."}

    try:
        # Extract legal information from URL if provided
        extracted_legal_info = {}
        if source_url:
            extracted_legal_info = extract_from_url(source_url)
        
        # Default to devgan.in legal database if no source_url is provided
        if not source_url and not extracted_legal_info:
            extracted_legal_info = extract_from_url("https://devgan.in/#bareacts")
        
        # Prepare a structured description including extracted information
        incident_description = transcribed_text
        if personal_info:
            # Different field labels based on language
            field_labels = {
                'english': {
                    'victim': "Victim",
                    'location': "Location",
                    'accused': "Accused Description",
                    'stolen': "Stolen Items",
                    'full_desc': "Full Description"
                },
                'hindi': {
                    'victim': "पीड़ित",
                    'location': "स्थान",
                    'accused': "आरोपी का विवरण",
                    'stolen': "चोरी की वस्तुएँ",
                    'full_desc': "पूरा विवरण"
                },
                'punjabi': {
                    'victim': "ਪੀੜਤ",
                    'location': "ਸਥਾਨ",
                    'accused': "ਦੋਸ਼ੀ ਦਾ ਵੇਰਵਾ",
                    'stolen': "ਚੋਰੀ ਹੋਈਆਂ ਵਸਤੂਆਂ",
                    'full_desc': "ਪੂਰਾ ਵੇਰਵਾ"
                }
            }
            
            # Get labels for the selected language
            labels = field_labels.get(language.lower(), field_labels['english'])
            
            structured_info = []
            if personal_info.get("victim_name"):
                structured_info.append(f"{labels['victim']}: {personal_info['victim_name']}")
            if personal_info.get("incident_location"):
                structured_info.append(f"{labels['location']}: {personal_info['incident_location']}")
            if personal_info.get("accused_description"):
                structured_info.append(f"{labels['accused']}: {personal_info['accused_description']}")
            if personal_info.get("stolen_properties"):
                structured_info.append(f"{labels['stolen']}: {personal_info['stolen_properties']}")
            if personal_info.get("total_value"):
                value_label = "Value" if language.lower() == 'english' else ("मूल्य" if language.lower() == 'hindi' else "ਮੁੱਲ")
                structured_info.append(f"{value_label}: {personal_info['total_value']}")
            
            if structured_info:
                # Format key details section title based on language
                key_details_title = {
                    'english': "Key Details:",
                    'hindi': "मुख्य विवरण:",
                    'punjabi': "ਮੁੱਖ ਵੇਰਵੇ:"
                }.get(language.lower(), "Key Details:")
                
                full_desc_title = {
                    'english': "Full Description:",
                    'hindi': "पूरा विवरण:",
                    'punjabi': "ਪੂਰਾ ਵੇਰਵਾ:"
                }.get(language.lower(), "Full Description:")
                
                incident_description = f"{key_details_title}\n" + "\n".join(structured_info) + f"\n\n{full_desc_title}\n" + transcribed_text

        # Define GPT prompts for different languages
        system_prompts = {
            'english': f"""
            You are a legal information extraction assistant. Your task is to extract legal information from the provided URL.
            Note -- strictly use this source only
            Source: https://devgan.in/#bareacts
            
            You are a legal expert specializing in Indian criminal law. Your task is to identify the most relevant legal sections 
            applicable for a First Information Report (FIR) based on the incident description provided.
            
            Provide only the most relevant legal sections applicable under Indian law (criminal, civil, or any other relevant statutes)
            based on the given incident. Ensure references are from the latest legal framework, including the Bharatiya Nyaya Sanhita (BNS),
            Bharatiya Nagarik Suraksha Sanhita (BNSS), Bharatiya Sakshya Adhiniyam (BSA), and other applicable laws.
            
            Refer to the legal database at devgan.in for accurate and up-to-date information on Indian legal codes and sections.
            
            {"" if not extracted_legal_info else "Use the following extracted legal information as a reference when applicable:\\n" + json.dumps(extracted_legal_info, indent=2) + "\\n\\n"}
            
            YOU MUST STRUCTURE YOUR RESPONSE AS FOLLOWS:
            
            {{
              "act1": "Full name of first applicable act (e.g., Bharatiya Nyaya Sanhita)",
              "sections1": "Section numbers from first act (e.g., 304B, 498A)",
              "act2": "Full name of second applicable act (if any)",
              "sections2": "Section numbers from second act (if any)",
              "act3": "Full name of third applicable act (if any)",
              "sections3": "Section numbers from third act (if any)",
              "description": "Brief one-paragraph description of the applicable sections and why they apply to this case"
            }}
            
            For example, format like:
            {{
              "act1": "Bharatiya Nyaya Sanhita",
              "sections1": "319, 324",
              "act2": "Information Technology Act",
              "sections2": "66D",
              "act3": "",
              "sections3": "",
              "description": "BNS Sections 319 and 324 apply to cases of causing hurt and grievous hurt. IT Act Section 66D applies to identity theft used in commission of the fraud."
            }}
            
            Do not provide any additional explanations, comments, or text outside of this JSON structure.
            """,
            
            'hindi': f"""
            You are a legal information extraction assistant. Your task is to extract legal information from the provided URL.
            Note -- strictly use this source only
            Source: https://devgan.in/#bareacts
            
            आप भारतीय आपराधिक कानून में विशेषज्ञता रखने वाले कानूनी विशेषज्ञ हैं। आपका कार्य प्रदान किए गए घटना विवरण के आधार पर प्रथम सूचना रिपोर्ट (FIR) के लिए सबसे प्रासंगिक कानूनी धाराओं की पहचान करना है।
            
            दी गई घटना के आधार पर भारतीय कानून (आपराधिक, नागरिक, या कोई अन्य प्रासंगिक कानून) के तहत केवल सबसे प्रासंगिक कानूनी धाराएँ प्रदान करें। सुनिश्चित करें कि संदर्भ नवीनतम कानूनी ढांचे से हों, जिसमें भारतीय न्याय संहिता (BNS), भारतीय नागरिक सुरक्षा संहिता (BNSS), भारतीय साक्ष्य अधिनियम (BSA), और अन्य लागू कानून शामिल हों।
            
            सटीक और अद्यतन जानकारी के लिए devgan.in पर भारतीय कानूनी संहिताओं और धाराओं के लिए संदर्भित करें।
            
            {"" if not extracted_legal_info else "निम्नलिखित निकाली गई कानूनी जानकारी का उपयोग संदर्भ के रूप में करें जब लागू हो:\\n" + json.dumps(extracted_legal_info, indent=2) + "\\n\\n"}
            
            आपको अपना जवाब निम्न स्वरूप में देना होगा:
            
            {{
              "act1": "पहले लागू अधिनियम का पूरा नाम (जैसे, भारतीय न्याय संहिता)",
              "sections1": "पहले अधिनियम की धारा संख्याएँ (जैसे, 304B, 498A)",
              "act2": "दूसरे लागू अधिनियम का पूरा नाम (यदि कोई हो)",
              "sections2": "दूसरे अधिनियम की धारा संख्याएँ (यदि कोई हो)",
              "act3": "तीसरे लागू अधिनियम का पूरा नाम (यदि कोई हो)",
              "sections3": "तीसरे अधिनियम की धारा संख्याएँ (यदि कोई हो)",
              "description": "लागू धाराओं का संक्षिप्त एक-पैराग्राफ विवरण और ये इस मामले पर क्यों लागू होती हैं"
            }}
            
            उदाहरण के लिए, इस प्रकार:
            {{
              "act1": "भारतीय न्याय संहिता",
              "sections1": "319, 324",
              "act2": "सूचना प्रौद्योगिकी अधिनियम",
              "sections2": "66D",
              "act3": "",
              "sections3": "",
              "description": "BNS धारा 319 और 324 चोट और गंभीर चोट पहुंचाने के मामलों पर लागू होती है। आईटी अधिनियम धारा 66D धोखाधड़ी करने में प्रयुक्त पहचान चोरी पर लागू होती है।"
            }}
            
            इस JSON संरचना के अलावा किसी भी अतिरिक्त स्पष्टीकरण, टिप्पणियों या पाठ को प्रदान न करें।
            """,
            
            'punjabi': f"""
            You are a legal information extraction assistant. Your task is to extract legal information from the provided URL.
            Note -- strictly use this source only
            Source: https://devgan.in/#bareacts
            
            ਤੁਸੀਂ ਭਾਰਤੀ ਫੌਜਦਾਰੀ ਕਾਨੂੰਨ ਵਿੱਚ ਮਾਹਿਰ ਕਾਨੂੰਨੀ ਮਾਹਿਰ ਹੋ। ਤੁਹਾਡਾ ਕੰਮ ਦਿੱਤੇ ਗਏ ਘਟਨਾ ਵੇਰਵੇ ਦੇ ਆਧਾਰ 'ਤੇ ਪਹਿਲੀ ਸੂਚਨਾ ਰਿਪੋਰਟ (FIR) ਲਈ ਸਭ ਤੋਂ ਢੁਕਵੀਆਂ ਕਾਨੂੰਨੀ ਧਾਰਾਵਾਂ ਦੀ ਪਛਾਣ ਕਰਨਾ ਹੈ।
            
            ਦਿੱਤੀ ਗਈ ਘਟਨਾ ਦੇ ਆਧਾਰ 'ਤੇ ਭਾਰਤੀ ਕਾਨੂੰਨ (ਅਪਰਾਧਿਕ, ਨਾਗਰਿਕ, ਜਾਂ ਕੋਈ ਹੋਰ ਢੁਕਵਾਂ ਕਾਨੂੰਨ) ਦੇ ਤਹਿਤ ਸਿਰਫ਼ ਸਭ ਤੋਂ ਢੁਕਵੀਆਂ ਕਾਨੂੰਨੀ ਧਾਰਾਵਾਂ ਪ੍ਰਦਾਨ ਕਰੋ। ਯਕੀਨੀ ਬਣਾਓ ਕਿ ਹਵਾਲੇ ਨਵੀਨਤਮ ਕਾਨੂੰਨੀ ਢਾਂਚੇ ਤੋਂ ਹਨ, ਜਿਸ ਵਿੱਚ ਭਾਰਤੀ ਨਿਆਂ ਸੰਹਿਤਾ (BNS), ਭਾਰਤੀ ਨਾਗਰਿਕ ਸੁਰੱਖਿਆ ਸੰਹਿਤਾ (BNSS), ਭਾਰਤੀ ਸਬੂਤ ਅਧਿਨਿਯਮ (BSA), ਅਤੇ ਹੋਰ ਲਾਗੂ ਕਾਨੂੰਨ ਸ਼ਾਮਲ ਹਨ।
            
            ਸਹੀ ਅਤੇ ਨਵੀਨਤਮ ਜਾਣਕਾਰੀ ਲਈ devgan.in 'ਤੇ ਭਾਰਤੀ ਕਾਨੂੰਨੀ ਕੋਡਾਂ ਅਤੇ ਧਾਰਾਵਾਂ ਦਾ ਹਵਾਲਾ ਦਿਓ।
            
            {"" if not extracted_legal_info else "ਜਦੋਂ ਲਾਗੂ ਹੋਵੇ ਹੇਠਾਂ ਦਿੱਤੀ ਕੱਢੀ ਗਈ ਕਾਨੂੰਨੀ ਜਾਣਕਾਰੀ ਦੀ ਵਰਤੋਂ ਹਵਾਲੇ ਵਜੋਂ ਕਰੋ:\\n" + json.dumps(extracted_legal_info, indent=2) + "\\n\\n"}
            
            ਤੁਹਾਨੂੰ ਆਪਣਾ ਜਵਾਬ ਇਸ ਢੰਗ ਨਾਲ ਬਣਾਉਣਾ ਚਾਹੀਦਾ ਹੈ:
            
            {{
              "act1": "ਪਹਿਲੇ ਲਾਗੂ ਐਕਟ ਦਾ ਪੂਰਾ ਨਾਮ (ਜਿਵੇਂ, ਭਾਰਤੀ ਨਿਆਂ ਸੰਹਿਤਾ)",
              "sections1": "ਪਹਿਲੇ ਐਕਟ ਦੀਆਂ ਧਾਰਾ ਨੰਬਰ (ਜਿਵੇਂ, 304B, 498A)",
              "act2": "ਦੂਜੇ ਲਾਗੂ ਐਕਟ ਦਾ ਪੂਰਾ ਨਾਮ (ਜੇ ਕੋਈ ਹੈ)",
              "sections2": "ਦੂਜੇ ਐਕਟ ਦੀਆਂ ਧਾਰਾ ਨੰਬਰ (ਜੇ ਕੋਈ ਹੈ)",
              "act3": "ਤੀਜੇ ਲਾਗੂ ਐਕਟ ਦਾ ਪੂਰਾ ਨਾਮ (ਜੇ ਕੋਈ ਹੈ)",
              "sections3": "ਤੀਜੇ ਐਕਟ ਦੀਆਂ ਧਾਰਾ ਨੰਬਰ (ਜੇ ਕੋਈ ਹੈ)",
              "description": "ਲਾਗੂ ਧਾਰਾਵਾਂ ਦਾ ਸੰਖੇਪ ਇੱਕ-ਪੈਰਾ ਵਰਣਨ ਅਤੇ ਇਹ ਇਸ ਮਾਮਲੇ 'ਤੇ ਕਿਉਂ ਲਾਗੂ ਹੁੰਦੀਆਂ ਹਨ"
            }}
            
            ਉਦਾਹਰਨ ਦੇ ਤੌਰ 'ਤੇ, ਇਸ ਤਰ੍ਹਾਂ:
            {{
              "act1": "ਭਾਰਤੀ ਨਿਆਂ ਸੰਹਿਤਾ",
              "sections1": "319, 324",
              "act2": "ਸੂਚਨਾ ਤਕਨਾਲੋਜੀ ਐਕਟ",
              "sections2": "66D",
              "act3": "",
              "sections3": "",
              "description": "BNS ਧਾਰਾ 319 ਅਤੇ 324 ਸੱਟ ਅਤੇ ਗੰਭੀਰ ਸੱਟ ਪਹੁੰਚਾਉਣ ਦੇ ਮਾਮਲਿਆਂ 'ਤੇ ਲਾਗੂ ਹੁੰਦੀਆਂ ਹਨ। ਆਈਟੀ ਐਕਟ ਧਾਰਾ 66D ਧੋਖਾਧੜੀ ਕਰਨ ਲਈ ਵਰਤੀ ਗਈ ਪਛਾਣ ਚੋਰੀ 'ਤੇ ਲਾਗੂ ਹੁੰਦੀ ਹੈ।"
            }}
            
            ਇਸ JSON ਢਾਂਚੇ ਤੋਂ ਬਾਹਰ ਕੋਈ ਵੀ ਵਾਧੂ ਵਿਆਖਿਆਵਾਂ, ਟਿੱਪਣੀਆਂ, ਜਾਂ ਟੈਕਸਟ ਨਾ ਦਿਓ।
            """
        }
        
        # Get system prompt for selected language
        system_prompt = system_prompts.get(language.lower(), system_prompts['english'])
        
        # User prompts for different languages
        user_prompts = {
            'english': f"Based on the following incident description, identify the most relevant legal sections that should be included in the FIR. Structure your response in the JSON format described in your instructions:\n\n{incident_description}",
            'hindi': f"निम्नलिखित घटना विवरण के आधार पर, सबसे प्रासंगिक कानूनी धाराओं की पहचान करें जो FIR में शामिल की जानी चाहिए। अपने जवाब को निर्देशों में वर्णित JSON प्रारूप में संरचित करें:\n\n{incident_description}",
            'punjabi': f"ਹੇਠਾਂ ਦਿੱਤੇ ਘਟਨਾ ਵੇਰਵੇ ਦੇ ਆਧਾਰ 'ਤੇ, ਸਭ ਤੋਂ ਢੁਕਵੀਆਂ ਕਾਨੂੰਨੀ ਧਾਰਾਵਾਂ ਦੀ ਪਛਾਣ ਕਰੋ ਜੋ FIR ਵਿੱਚ ਸ਼ਾਮਲ ਕੀਤੀਆਂ ਜਾਣੀਆਂ ਚਾਹੀਦੀਆਂ ਹਨ। ਆਪਣੇ ਜਵਾਬ ਨੂੰ ਨਿਰਦੇਸ਼ਾਂ ਵਿੱਚ ਦੱਸੇ ਗਏ JSON ਫਾਰਮੈਟ ਵਿੱਚ ਢਾਲੋ:\n\n{incident_description}"
        }
        
        # Get user prompt for selected language
        user_prompt = user_prompts.get(language.lower(), user_prompts['english'])
        
        # Call GPT API
        response = callGPT(system_prompt, user_prompt)
        
        # Try to extract JSON from the response
        try:
            # First, find JSON content between curly braces
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                import json
                json_str = json_match.group(0)
                legal_data = json.loads(json_str)
                
                # Create a formatted string for frontend display
                legal_sections_formatted = []
                
                if legal_data.get("act1") and legal_data.get("sections1"):
                    legal_sections_formatted.append(f"{legal_data['act1']} - Section {legal_data['sections1']}")
                
                if legal_data.get("act2") and legal_data.get("sections2"):
                    legal_sections_formatted.append(f"{legal_data['act2']} - Section {legal_data['sections2']}")
                
                if legal_data.get("act3") and legal_data.get("sections3"):
                    legal_sections_formatted.append(f"{legal_data['act3']} - Section {legal_data['sections3']}")
                
                if legal_data.get("description"):
                    legal_sections_formatted.append(f"\nDescription: {legal_data['description']}")
                
                # Return both structured data and formatted string
                return {
                    "legal_sections": "\n".join(legal_sections_formatted),
                    "legal_data": legal_data
                }
            else:
                # If JSON extraction fails, return the raw response
                return {"legal_sections": response}
        except Exception as json_error:
            # If JSON parsing fails, return the raw response
            return {"legal_sections": response, "parse_error": str(json_error)}

    except Exception as e:
        return {"error": f"Request failed: {str(e)}"}


def extract_from_url(url):
    """
    Extract legal information from a provided URL using ChatGPT API.
    
    Args:
        url (str): URL of the legal resource to extract information from
        
    Returns:
        dict: Dictionary containing extracted legal information
    """
    try:
        # Define the system prompt for ChatGPT to extract information from devgan.in
        system_prompt = """
        You are a legal information extraction assistant. Your task is to extract legal information from the provided URL.
        Focus specifically on extracting:
        1. Names of legal acts (e.g., "Bharatiya Nyaya Sanhita", "Indian Penal Code", etc.)
        2. Section numbers mentioned (e.g., "304B", "498A", etc.)
        
        If the URL is https://devgan.in/#bareacts or a specific page from devgan.in, you should:
        - Extract information about the major Indian legal acts like Bharatiya Nyaya Sanhita (BNS), Bharatiya Nagarik Suraksha Sanhita (BNSS), 
          Bharatiya Sakshya Adhiniyam (BSA), Indian Penal Code (IPC), Criminal Procedure Code (CrPC), etc.
        - Include commonly used sections for criminal and civil cases.
        
        Format your response as valid JSON with the following structure:
        {
          "source_url": "the URL you analyzed",
          "acts": ["Act 1", "Act 2", ...],
          "sections": ["Section 1", "Section 2", ...]
        }
        
        Provide only the JSON response without additional text or explanation.
        """
        
        # Define the user prompt based on the URL
        if "devgan.in" in url:
            user_prompt = f"""
            Extract legal information from the Devgan's Bare Acts website at {url}.
            
            This is a comprehensive Indian legal database containing information about all major Indian laws, including:
            1. Bharatiya Nyaya Sanhita (BNS) - which replaced the Indian Penal Code
            2. Bharatiya Nagarik Suraksha Sanhita (BNSS) - which replaced the Criminal Procedure Code
            3. Bharatiya Sakshya Adhiniyam (BSA) - which replaced the Indian Evidence Act
            4. Other important legal acts and their sections
            
            Please extract the names of the major acts and their commonly used sections.
            """
        else:
            user_prompt = f"Extract legal information from the following URL: {url}"
            
        # Call GPT API to extract information
        response = callGPT(system_prompt, user_prompt)
        
        # Parse the JSON response
        try:
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                extracted_info = json.loads(json_str)
                
                # Ensure the extracted data has the required fields
                if "acts" not in extracted_info:
                    extracted_info["acts"] = []
                if "sections" not in extracted_info:
                    extracted_info["sections"] = []
                if "source_url" not in extracted_info:
                    extracted_info["source_url"] = url
                    
                return extracted_info
            else:
                # If we couldn't extract JSON, return a default structure
                return {
                    "source_url": url,
                    "acts": [
                        "Bharatiya Nyaya Sanhita",
                        "Bharatiya Nagarik Suraksha Sanhita",
                        "Bharatiya Sakshya Adhiniyam",
                        "Indian Penal Code",
                        "Criminal Procedure Code",
                        "Information Technology Act"
                    ],
                    "sections": ["307", "302", "304", "326", "376", "420", "509", "354", "498A"],
                    "note": "Default data used as extraction failed"
                }
                
        except Exception as json_error:
            # Return default structure if JSON parsing fails
            return {
                "source_url": url,
                "acts": [
                    "Bharatiya Nyaya Sanhita",
                    "Bharatiya Nagarik Suraksha Sanhita",
                    "Bharatiya Sakshya Adhiniyam",
                    "Indian Penal Code",
                    "Criminal Procedure Code",
                    "Information Technology Act"
                ],
                "sections": ["307", "302", "304", "326", "376", "420", "509", "354", "498A"],
                "error": str(json_error)
            }
            
    except Exception as e:
        return {
            "error": f"Failed to extract from URL: {str(e)}",
            "source_url": url
        }