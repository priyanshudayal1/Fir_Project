from gpt import callGPT
import re
import json
import os
import logging
from openai import AzureOpenAI
import time

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Azure OpenAI Configuration
AZURE_OPENAI_KEY = '12c6ced676b749258b582edd76600aa4'
AZURE_OPENAI_ENDPOINT = "https://lexiai1.openai.azure.com/"
AZURE_DEPLOYMENT_NAME = 'lexiai1'

client = AzureOpenAI(
    api_key=AZURE_OPENAI_KEY,
    api_version="2024-05-01-preview",
    azure_endpoint=AZURE_OPENAI_ENDPOINT
)

ASSISTANT_CREDS_FILE = "assistant_credentials.json"

def read_section_summary():
    """
    Reads the section_summary.txt file containing legal sections information.
    Returns the content as a string.
    """
    try:
        # Get the path to the section_summary.txt file
        current_dir = os.path.dirname(os.path.abspath(__file__))
        section_summary_path = os.path.join(current_dir, "section_summary.txt")
        
        # Read the file content
        with open(section_summary_path, 'r', encoding='utf-8') as file:
            section_data = file.read()
        
        return section_data
    except Exception as e:
        error_msg = f"Error reading section_summary.txt: {str(e)}"
        logger.error(error_msg)
        return None

def get_or_create_assistant():
    """Gets existing assistant ID"""
    try:
        return 'asst_LfvdEgCE71TjiG1jVIu6Ok9i'  # Using the fixed assistant ID
    except Exception as e:
        error_msg = f"Error in getting assistant: {str(e)}"
        logger.error(error_msg)
        raise

def get_assistant_response(query):
    """Get response from the assistant"""
    try:
        # Create thread
        thread = client.beta.threads.create()

        # Add message to thread
        client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=query
        )

        # Run assistant with fixed ID
        run = client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id='asst_LfvdEgCE71TjiG1jVIu6Ok9i'  # Using fixed assistant ID directly
        )

        # Wait for completion
        while True:
            run_status = client.beta.threads.runs.retrieve(
                thread_id=thread.id,
                run_id=run.id
            )
            if run_status.status == 'completed':
                break
            time.sleep(1)

        # Get messages
        messages = client.beta.threads.messages.list(thread_id=thread.id)
        
        # Get assistant's response
        for msg in messages.data:
            if msg.role == "assistant":
                return msg.content[0].text.value

        return None

    except Exception as e:
        error_msg = f"Error getting assistant response: {str(e)}"
        logger.error(error_msg)
        raise

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
        error_msg = "Empty text provided."
        logger.error(error_msg)
        return {"error": error_msg}

    try:
        # Get or create assistant
        assistant_id = get_or_create_assistant()

        # Read the section summary from local file
        section_summary = read_section_summary()
        
        # Extract legal information from URL if provided
        extracted_legal_info = {}
        
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

        # Define GPT prompts for different languages with section summary incorporation
        system_prompts = {
            'english': f"""
            You are a legal information extraction assistant. Your task is to extract legal information from the provided legal sections summary.
            
            You are a legal expert specializing in Indian criminal law. Your task is to identify the most relevant legal sections 
            applicable for a First Information Report (FIR) based on the incident description provided.
            
            Provide only the most relevant legal sections applicable under Indian law (criminal, civil, or any other relevant statutes)
            based on the given incident. Ensure references are from the latest legal framework, including the Bharatiya Nyaya Sanhita (BNS),
            Bharatiya Nagarik Suraksha Sanhita (BNSS), Bharatiya Sakshya Adhiniyam (BSA), and other applicable laws.
            
            Use the following legal sections summary as your primary reference to identify applicable sections:
            
            {section_summary if section_summary else "Unable to access section summary. Please refer to standard legal databases."}
            
            {"" if not extracted_legal_info else "Additionally, consider the following extracted legal information as a reference when applicable:\\n" + json.dumps(extracted_legal_info, indent=2) + "\\n\\n"}
            
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
            You are a legal information extraction assistant. Your task is to extract legal information from the provided legal sections summary.
            
            आप भारतीय आपराधिक कानून में विशेषज्ञता रखने वाले कानूनी विशेषज्ञ हैं। आपका कार्य प्रदान किए गए घटना विवरण के आधार पर प्रथम सूचना रिपोर्ट (FIR) के लिए सबसे प्रासंगिक कानूनी धाराओं की पहचान करना है।
            
            दी गई घटना के आधार पर भारतीय कानून (आपराधिक, नागरिक, या कोई अन्य प्रासंगिक कानून) के तहत केवल सबसे प्रासंगिक कानूनी धाराएँ प्रदान करें। सुनिश्चित करें कि संदर्भ नवीनतम कानूनी ढांचे से हों, जिसमें भारतीय न्याय संहिता (BNS), भारतीय नागरिक सुरक्षा संहिता (BNSS), भारतीय साक्ष्य अधिनियम (BSA), और अन्य लागू कानून शामिल हों।
            
            कानूनी धाराओं की पहचान करने के लिए निम्नलिखित कानूनी धारा सारांश का उपयोग प्राथमिक संदर्भ के रूप में करें:
            
            {section_summary if section_summary else "धारा सारांश तक पहुंचने में असमर्थ। कृपया मानक कानूनी डेटाबेस का संदर्भ लें।"}
            
            {"" if not extracted_legal_info else "इसके अतिरिक्त, लागू होने पर निम्नलिखित निकाली गई कानूनी जानकारी पर विचार करें:\\n" + json.dumps(extracted_legal_info, indent=2) + "\\n\\n"}
            
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
            You are a legal information extraction assistant. Your task is to extract legal information from the provided legal sections summary.
            
            ਤੁਸੀਂ ਭਾਰਤੀ ਫੌਜਦਾਰੀ ਕਾਨੂੰਨ ਵਿੱਚ ਮਾਹਿਰ ਕਾਨੂੰਨੀ ਮਾਹਿਰ ਹੋ। ਤੁਹਾਡਾ ਕੰਮ ਦਿੱਤੇ ਗਏ ਘਟਨਾ ਵੇਰਵੇ ਦੇ ਆਧਾਰ 'ਤੇ ਪਹਿਲੀ ਸੂਚਨਾ ਰਿਪੋਰਟ (FIR) ਲਈ ਸਭ ਤੋਂ ਢੁਕਵੀਆਂ ਕਾਨੂੰਨੀ ਧਾਰਾਵਾਂ ਦੀ ਪਛਾਣ ਕਰਨਾ ਹੈ।
            
            ਦਿੱਤੀ ਗਈ ਘਟਨਾ ਦੇ ਆਧਾਰ 'ਤੇ ਭਾਰਤੀ ਕਾਨੂੰਨ (ਅਪਰਾਧਿਕ, ਨਾਗਰਿਕ, ਜਾਂ ਕੋਈ ਹੋਰ ਢੁਕਵਾਂ ਕਾਨੂੰਨ) ਦੇ ਤਹਿਤ ਸਿਰਫ਼ ਸਭ ਤੋਂ ਢੁਕਵੀਆਂ ਕਾਨੂੰਨੀ ਧਾਰਾਵਾਂ ਪ੍ਰਦਾਨ ਕਰੋ। ਯਕੀਨੀ ਬਣਾਓ ਕਿ ਹਵਾਲੇ ਨਵੀਨਤਮ ਕਾਨੂੰਨੀ ਢਾਂਚੇ ਤੋਂ ਹਨ, ਜਿਸ ਵਿੱਚ ਭਾਰਤੀ ਨਿਆਂ ਸੰਹਿਤਾ (BNS), ਭਾਰਤੀ ਨਾਗਰਿਕ ਸੁਰੱਖਿਆ ਸੰਹਿਤਾ (BNSS), ਭਾਰਤੀ ਸਬੂਤ ਅਧਿਨਿਯਮ (BSA), ਅਤੇ ਹੋਰ ਲਾਗੂ ਕਾਨੂੰਨ ਸ਼ਾਮਲ ਹਨ।
            
            ਕਾਨੂੰਨੀ ਧਾਰਾਵਾਂ ਦੀ ਪਛਾਣ ਕਰਨ ਲਈ ਹੇਠਾਂ ਦਿੱਤੇ ਕਾਨੂੰਨੀ ਧਾਰਾ ਸਾਰ ਦੀ ਵਰਤੋਂ ਮੁੱਖ ਹਵਾਲੇ ਵਜੋਂ ਕਰੋ:
            
            {section_summary if section_summary else "ਧਾਰਾ ਸਾਰ ਤੱਕ ਪਹੁੰਚਣ ਵਿੱਚ ਅਸਮਰਥ। ਕਿਰਪਾ ਕਰਕੇ ਮਿਆਰੀ ਕਾਨੂੰਨੀ ਡੇਟਾਬੇਸ ਦਾ ਹਵਾਲਾ ਦਿਓ।"}
            
            {"" if not extracted_legal_info else "ਇਸ ਤੋਂ ਇਲਾਵਾ, ਲਾਗੂ ਹੋਣ 'ਤੇ ਹੇਠਾਂ ਦਿੱਤੀ ਕੱਢੀ ਗਈ ਕਾਨੂੰਨੀ ਜਾਣਕਾਰੀ 'ਤੇ ਵਿਚਾਰ ਕਰੋ:\\n" + json.dumps(extracted_legal_info, indent=2) + "\\n\\n"}
            
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
        
        # JSON structure that we expect in response
        json_structure_example = '''{
    "act1": "Name of first act",
    "sections1": "Sections from first act",
    "act2": "Name of second act (if applicable)",
    "sections2": "Sections from second act (if applicable)",
    "act3": "Name of third act (if applicable)",
    "sections3": "Sections from third act (if applicable)",
    "description": "Brief explanation of why these sections apply"
}'''
        
        # User prompts for different languages with JSON structure
        user_prompts = {
            'english': f"Based on the following incident description, identify the most relevant legal sections that should be included in the FIR. Return your response in this exact JSON structure:\n{json_structure_example}\n\nIncident Description:\n{transcribed_text}",
            'hindi': f"निम्नलिखित घटना विवरण के आधार पर, FIR में शामिल की जाने वाली सबसे प्रासंगिक कानूनी धाराओं की पहचान करें। अपना जवाब इस सटीक JSON संरचना में दें:\n{json_structure_example}\n\nघटना विवरण:\n{transcribed_text}",
            'punjabi': f"ਹੇਠਾਂ ਦਿੱਤੇ ਘਟਨਾ ਵੇਰਵੇ ਦੇ ਆਧਾਰ 'ਤੇ, FIR ਵਿੱਚ ਸ਼ਾਮਲ ਕੀਤੀਆਂ ਜਾਣ ਵਾਲੀਆਂ ਸਭ ਤੋਂ ਢੁਕਵੀਆਂ ਕਾਨੂੰਨੀ ਧਾਰਾਵਾਂ ਦੀ ਪਛਾਣ ਕਰੋ। ਆਪਣਾ ਜਵਾਬ ਇਸ ਸਹੀ JSON ਢਾਂਚੇ ਵਿੱਚ ਦਿਓ:\n{json_structure_example}\n\nਘਟਨਾ ਵੇਰਵਾ:\n{transcribed_text}"
        }
        
        # Get user prompt for selected language
        user_prompt = user_prompts.get(language.lower(), user_prompts['english'])
        
        # Call GPT API with proper error handling
        try:
            response = get_assistant_response(user_prompt)
            print('response:', response)
        except RuntimeError as e:
            error_msg = f"GPT API Error: {str(e)}"
            logger.error(error_msg)
            return {
                "error": error_msg,
                "details": str(e),
                "status": "api_error"
            }
        
        # Try to extract JSON from the response
        try:
            # First, find JSON content between curly braces
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                try:
                    legal_data = json.loads(json_str)
                except json.JSONDecodeError as je:
                    error_msg = f"JSON parsing error: {str(je)}"
                    logger.error(error_msg)
                    return {
                        "error": error_msg,
                        "raw_response": response,
                        "status": "json_error"
                    }
                
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
                    "legal_data": legal_data,
                    "status": "success"
                }
            else:
                error_msg = "No valid JSON found in GPT response"
                logger.error(error_msg)
                return {
                    "error": error_msg,
                    "raw_response": response,
                    "status": "format_error"
                }
        except Exception as json_error:
            error_msg = f"Error processing GPT response: {str(json_error)}"
            logger.error(error_msg)
            return {
                "error": error_msg,
                "raw_response": response,
                "parse_error": str(json_error),
                "status": "processing_error"
            }

    except Exception as e:
        error_msg = f"General error: {str(e)}"
        logger.error(error_msg)
        return {
            "error": error_msg,
            "status": "general_error"
        }


