# filepath: c:\Users\Priyanshu Dayal\Desktop\WORK\FIR_Project\fir_backend\transcript_processor.py
import re
import json
from datetime import datetime
from gpt import callGPT

def parse_interview_transcript(transcript_text, language='english'):
    """
    Parse the interview transcript to extract Q&A pairs, with language support
    """
    qa_pairs = []
    lines = transcript_text.strip().split('\n')
    
    current_question = ""
    current_answer = ""
    
    # Different language prefixes for questions and answers
    q_prefixes = {
        'english': ['Q:', 'Question:'],
        'hindi': ['प्रश्न:', 'Q:', 'सवाल:'],
        'punjabi': ['ਪ੍ਰਸ਼ਨ:', 'Q:', 'ਸਵਾਲ:']
    }
    
    a_prefixes = {
        'english': ['A:', 'Answer:'],
        'hindi': ['उत्तर:', 'A:', 'जवाब:'],
        'punjabi': ['ਜਵਾਬ:', 'A:', 'ਉੱਤਰ:']
    }
    
    # Get prefixes for selected language, defaulting to English
    q_prefix_list = q_prefixes.get(language.lower(), q_prefixes['english'])
    a_prefix_list = a_prefixes.get(language.lower(), a_prefixes['english'])
    
    for line in lines:
        is_question = False
        is_answer = False
        
        # Check if line starts with any question prefix
        for prefix in q_prefix_list:
            if line.startswith(prefix):
                # If we have a previous Q&A pair, save it
                if current_question and current_answer:
                    qa_pairs.append({
                        "question": current_question.strip(),
                        "answer": current_answer.strip()
                    })
                
                # Start a new question
                current_question = line[len(prefix):].strip()
                current_answer = ""
                is_question = True
                break
                
        # If not a question, check if it's an answer
        if not is_question:
            for prefix in a_prefix_list:
                if line.startswith(prefix):
                    current_answer = line[len(prefix):].strip()
                    is_answer = True
                    break
            
            # If not a new answer but we have a current answer, append to it
            if not is_answer and current_answer:
                current_answer += " " + line.strip()
    
    # Add the last Q&A pair if exists
    if current_question and current_answer:
        qa_pairs.append({
            "question": current_question.strip(),
            "answer": current_answer.strip()
        })
    
    return qa_pairs

def extract_fir_information(qa_pairs, language='english'):
    """
    Use GPT to extract structured information from the interview transcript with enhanced prompting.
    """
    # Define system prompts for different languages with improved extraction capabilities
    system_prompts = {
        'english': """
        You are a specialized AI assistant for police departments that extracts structured information from interview transcripts for First Information Reports (FIR).
        Extract the following information from the provided Q&A transcript with maximum accuracy and detail:
        
        1. victim_name: Full name of the complainant 
        2. father_or_husband_name: Father's or husband's name
        3. dob: Date of birth (format: YYYY-MM-DD if possible)
        4. nationality: Nationality of the complainant
        5. occupation: Occupation information (if available)
        6. address: Complete address information including street, city, state, etc.
        7. incident_date: When the incident occurred (format: YYYY-MM-DD if possible)
        8. incident_time: Time of incident (format: HH:MM if possible)
        9. incident_location: Complete location details of where the incident occurred
        10. accused_description: Detailed description of accused/suspect including physical appearance, clothing, identifying marks, number of suspects, any names mentioned
        11. stolen_properties: Comprehensive list of stolen items with descriptions
        12. total_value: Monetary value of stolen properties (include currency - INR/Rs.)
        13. delay_reason: Reason for delay in reporting (if applicable)
        14. witness_details: Information about any witnesses (if available)
        15. incident_details: A detailed paragraph describing the incident that includes sequence of events, weapons used (if any), injuries sustained (if any), and other relevant details
        
        Provide the information in the following JSON format precisely:
        {
          "victim_name": "Full name",
          "father_or_husband_name": "Full name", 
          "dob": "YYYY-MM-DD or descriptive date",
          "nationality": "Nationality",
          "occupation": "Occupation",
          "address": "Complete address",
          "incident_date": "YYYY-MM-DD or descriptive date",
          "incident_time": "HH:MM or descriptive time",
          "incident_location": "Complete location details",
          "accused_description": "Detailed description",
          "stolen_properties": "Detailed list",
          "total_value": "Amount with currency",
          "delay_reason": "Explanation if applicable",
          "witness_details": "Names and details if available",
          "incident_details": "Detailed paragraph"
        }
        
        If any field is not available in the transcript, use an empty string or null. Be extremely careful to extract all possible information, even if it's mentioned indirectly. Ensure dates are formatted consistently.
        """,
        
        'hindi': """
        आप पुलिस विभागों के लिए एक विशेष AI सहायक हैं जो प्रथम सूचना रिपोर्ट (FIR) के लिए साक्षात्कार प्रतिलेखों से संरचित जानकारी निकालता है।
        प्रदान किए गए Q&A प्रतिलेख से निम्नलिखित जानकारी अधिकतम सटीकता और विस्तार के साथ निकालें:
        
        1. victim_name: शिकायतकर्ता का पूरा नाम
        2. father_or_husband_name: पिता या पति का नाम
        3. dob: जन्म तिथि (प्रारूप: YYYY-MM-DD यदि संभव हो)
        4. nationality: शिकायतकर्ता की राष्ट्रीयता
        5. occupation: व्यवसाय की जानकारी (यदि उपलब्ध हो)
        6. address: सड़क, शहर, राज्य आदि सहित पूरी पता जानकारी
        7. incident_date: घटना कब हुई (प्रारूप: YYYY-MM-DD यदि संभव हो)
        8. incident_time: घटना का समय (प्रारूप: HH:MM यदि संभव हो)
        9. incident_location: घटना के स्थान का पूरा विवरण
        10. accused_description: आरोपी/संदिग्ध का विस्तृत विवरण, जिसमें शारीरिक दिखावट, कपड़े, पहचान चिह्न, संदिग्धों की संख्या, उल्लेखित कोई नाम शामिल हैं
        11. stolen_properties: विवरण के साथ चोरी की वस्तुओं की व्यापक सूची
        12. total_value: चोरी की संपत्ति का मौद्रिक मूल्य (मुद्रा सहित - INR/रुपये)
        13. delay_reason: रिपोर्टिंग में देरी का कारण (यदि लागू हो)
        14. witness_details: किसी भी गवाह के बारे में जानकारी (यदि उपलब्ध हो)
        15. incident_details: घटना का विस्तृत वर्णन जिसमें घटनाओं का क्रम, उपयोग किए गए हथियार (यदि कोई हो), हुई चोटें (यदि कोई हो), और अन्य प्रासंगिक विवरण शामिल हैं
        
        जानकारी को निम्नलिखित JSON प्रारूप में सटीक रूप से प्रदान करें:
        {
          "victim_name": "पूरा नाम",
          "father_or_husband_name": "पूरा नाम", 
          "dob": "YYYY-MM-DD या वर्णनात्मक तिथि",
          "nationality": "राष्ट्रीयता",
          "occupation": "व्यवसाय",
          "address": "पूरा पता",
          "incident_date": "YYYY-MM-DD या वर्णनात्मक तिथि",
          "incident_time": "HH:MM या वर्णनात्मक समय",
          "incident_location": "पूरा स्थान विवरण",
          "accused_description": "विस्तृत विवरण",
          "stolen_properties": "विस्तृत सूची",
          "total_value": "मुद्रा के साथ राशि",
          "delay_reason": "स्पष्टीकरण यदि लागू हो",
          "witness_details": "नाम और विवरण यदि उपलब्ध हो",
          "incident_details": "विस्तृत पैराग्राफ"
        }
        
        यदि कोई फ़ील्ड प्रतिलेख में उपलब्ध नहीं है, तो खाली स्ट्रिंग या null का उपयोग करें। सभी संभावित जानकारी निकालने के लिए अत्यधिक सावधानी बरतें, भले ही इसका अप्रत्यक्ष रूप से उल्लेख किया गया हो। सुनिश्चित करें कि तिथियां लगातार स्वरूपित हैं।
        """,
        
        'punjabi': """
        ਤੁਸੀਂ ਪੁਲਿਸ ਵਿਭਾਗਾਂ ਲਈ ਇੱਕ ਖਾਸ AI ਸਹਾਇਕ ਹੋ ਜੋ ਪਹਿਲੀ ਸੂਚਨਾ ਰਿਪੋਰਟ (FIR) ਲਈ ਇੰਟਰਵਿਊ ਟ੍ਰਾਂਸਕ੍ਰਿਪਟਾਂ ਤੋਂ ਢਾਂਚਾਗਤ ਜਾਣਕਾਰੀ ਕੱਢਦਾ ਹੈ।
        ਦਿੱਤੇ ਗਏ Q&A ਟ੍ਰਾਂਸਕ੍ਰਿਪਟ ਤੋਂ ਹੇਠ ਲਿਖੀ ਜਾਣਕਾਰੀ ਨੂੰ ਵੱਧ ਤੋਂ ਵੱਧ ਸਟੀਕਤਾ ਅਤੇ ਵਿਸਥਾਰ ਨਾਲ ਕੱਢੋ:
        
        1. victim_name: ਸ਼ਿਕਾਇਤਕਰਤਾ ਦਾ ਪੂਰਾ ਨਾਮ
        2. father_or_husband_name: ਪਿਤਾ ਜਾਂ ਪਤੀ ਦਾ ਨਾਮ
        3. dob: ਜਨਮ ਮਿਤੀ (ਫਾਰਮੈਟ: YYYY-MM-DD ਜੇ ਸੰਭਵ ਹੋਵੇ)
        4. nationality: ਸ਼ਿਕਾਇਤਕਰਤਾ ਦੀ ਨਾਗਰਿਕਤਾ
        5. occupation: ਕਿੱਤੇ ਬਾਰੇ ਜਾਣਕਾਰੀ (ਜੇ ਉਪਲਬਧ ਹੈ)
        6. address: ਸੜਕ, ਸ਼ਹਿਰ, ਰਾਜ ਆਦਿ ਸਮੇਤ ਪੂਰੀ ਪਤਾ ਜਾਣਕਾਰੀ
        7. incident_date: ਘਟਨਾ ਕਦੋਂ ਹੋਈ (ਫਾਰਮੈਟ: YYYY-MM-DD ਜੇ ਸੰਭਵ ਹੋਵੇ)
        8. incident_time: ਘਟਨਾ ਦਾ ਸਮਾਂ (ਫਾਰਮੈਟ: HH:MM ਜੇ ਸੰਭਵ ਹੋਵੇ)
        9. incident_location: ਘਟਨਾ ਦੇ ਸਥਾਨ ਦਾ ਪੂਰਾ ਵੇਰਵਾ
        10. accused_description: ਦੋਸ਼ੀ/ਸ਼ੱਕੀ ਦਾ ਵਿਸਤਰਿਤ ਵੇਰਵਾ ਜਿਸ ਵਿੱਚ ਸਰੀਰਕ ਦਿੱਖ, ਕੱਪੜੇ, ਪਛਾਣ ਚਿੰਨ੍ਹ, ਸ਼ੱਕੀਆਂ ਦੀ ਗਿਣਤੀ, ਕੋਈ ਨਾਮ ਜੋ ਦੱਸੇ ਗਏ ਹਨ
        11. stolen_properties: ਵੇਰਵੇ ਦੇ ਨਾਲ ਚੋਰੀ ਕੀਤੀਆਂ ਚੀਜ਼ਾਂ ਦੀ ਵਿਆਪਕ ਸੂਚੀ
        12. total_value: ਚੋਰੀ ਕੀਤੀ ਜਾਇਦਾਦ ਦਾ ਮੁਦਰਾ ਮੁੱਲ (ਮੁਦਰਾ ਸਮੇਤ - INR/ਰੁਪਏ)
        13. delay_reason: ਰਿਪੋਰਟਿੰਗ ਵਿੱਚ ਦੇਰੀ ਦਾ ਕਾਰਨ (ਜੇ ਲਾਗੂ ਹੋਵੇ)
        14. witness_details: ਕਿਸੇ ਵੀ ਗਵਾਹ ਬਾਰੇ ਜਾਣਕਾਰੀ (ਜੇ ਉਪਲਬਧ ਹੈ)
        15. incident_details: ਘਟਨਾ ਦਾ ਵਿਸਤਰਿਤ ਵੇਰਵਾ ਜਿਸ ਵਿੱਚ ਘਟਨਾਵਾਂ ਦਾ ਕ੍ਰਮ, ਵਰਤੇ ਗਏ ਹਥਿਆਰ (ਜੇ ਕੋਈ ਹਨ), ਹੋਈਆਂ ਸੱਟਾਂ (ਜੇ ਕੋਈ ਹਨ), ਅਤੇ ਹੋਰ ਢੁਕਵੇਂ ਵੇਰਵੇ ਸ਼ਾਮਲ ਹਨ
        
        ਜਾਣਕਾਰੀ ਨੂੰ ਹੇਠ ਲਿਖੇ JSON ਫਾਰਮੈਟ ਵਿੱਚ ਬਿਲਕੁਲ ਸਹੀ ਢੰਗ ਨਾਲ ਪ੍ਰਦਾਨ ਕਰੋ:
        {
          "victim_name": "ਪੂਰਾ ਨਾਮ",
          "father_or_husband_name": "ਪੂਰਾ ਨਾਮ", 
          "dob": "YYYY-MM-DD ਜਾਂ ਵਰਣਨਾਤਮਕ ਮਿਤੀ",
          "nationality": "ਨਾਗਰਿਕਤਾ",
          "occupation": "ਕਿੱਤਾ",
          "address": "ਪੂਰਾ ਪਤਾ",
          "incident_date": "YYYY-MM-DD ਜਾਂ ਵਰਣਨਾਤਮਕ ਮਿਤੀ",
          "incident_time": "HH:MM ਜਾਂ ਵਰਣਨਾਤਮਕ ਸਮਾਂ",
          "incident_location": "ਪੂਰਾ ਸਥਾਨ ਵੇਰਵਾ",
          "accused_description": "ਵਿਸਤਰਿਤ ਵੇਰਵਾ",
          "stolen_properties": "ਵਿਸਤਰਿਤ ਸੂਚੀ",
          "total_value": "ਮੁਦਰਾ ਦੇ ਨਾਲ ਰਕਮ",
          "delay_reason": "ਵਿਆਖਿਆ ਜੇ ਲਾਗੂ ਹੋਵੇ",
          "witness_details": "ਨਾਮ ਅਤੇ ਵੇਰਵੇ ਜੇ ਉਪਲਬਧ ਹੋਣ",
          "incident_details": "ਵਿਸਤਰਿਤ ਪੈਰਾਗ੍ਰਾਫ"
        }
        
        ਜੇਕਰ ਕੋਈ ਫੀਲਡ ਟ੍ਰਾਂਸਕ੍ਰਿਪਟ ਵਿੱਚ ਉਪਲਬਧ ਨਹੀਂ ਹੈ, ਤਾਂ ਖਾਲੀ ਸਟ੍ਰਿੰਗ ਜਾਂ null ਦੀ ਵਰਤੋਂ ਕਰੋ। ਸਾਰੀ ਸੰਭਾਵਿਤ ਜਾਣਕਾਰੀ ਕੱਢਣ ਲਈ ਬਹੁਤ ਸਾਵਧਾਨੀ ਵਰਤੋ, ਭਾਵੇਂ ਇਸਦਾ ਅਸਿੱਧੇ ਤੌਰ 'ਤੇ ਜ਼ਿਕਰ ਕੀਤਾ ਗਿਆ ਹੋਵੇ। ਯਕੀਨੀ ਬਣਾਓ ਕਿ ਮਿਤੀਆਂ ਇਕਸਾਰ ਢੰਗ ਨਾਲ ਫਾਰਮੈਟ ਕੀਤੀਆਂ ਗਈਆਂ ਹਨ।
        """
    }
    
    # Get system prompt for selected language, defaulting to English
    system_prompt = system_prompts.get(language.lower(), system_prompts['english'])
    
    # Create a formatted version of the Q&A for GPT to process
    formatted_qa = ""
    for pair in qa_pairs:
        formatted_qa += f"Question: {pair['question']}\nAnswer: {pair['answer']}\n\n"
    
    # Define user prompt based on language
    user_prompts = {
        'english': f"Please extract the structured FIR information from the following interview transcript as completely and accurately as possible:\n\n{formatted_qa}",
        'hindi': f"कृपया निम्नलिखित साक्षात्कार प्रतिलेख से संरचित FIR जानकारी को जितना संभव हो उतना पूर्ण और सटीक रूप से निकालें:\n\n{formatted_qa}",
        'punjabi': f"ਕਿਰਪਾ ਕਰਕੇ ਹੇਠ ਲਿਖੇ ਇੰਟਰਵਿਊ ਟ੍ਰਾਂਸਕ੍ਰਿਪਟ ਤੋਂ ਢਾਂਚਾਗਤ FIR ਜਾਣਕਾਰੀ ਨੂੰ ਜਿੰਨਾ ਸੰਭਵ ਹੋ ਸਕੇ ਪੂਰੀ ਅਤੇ ਸਹੀ ਢੰਗ ਨਾਲ ਕੱਢੋ:\n\n{formatted_qa}"
    }
    
    user_prompt = user_prompts.get(language.lower(), user_prompts['english'])
    
    # Call GPT
    try:
        gpt_response = callGPT(system_prompt, user_prompt)
        
        # Parse the JSON response
        # First, find JSON content between curly braces
        json_match = re.search(r'\{.*\}', gpt_response, re.DOTALL)
        if json_match:
            json_str = json_match.group(0)
            data = json.loads(json_str)
            return data
        else:
            print("Error: Could not find valid JSON in the GPT response.")
            return {}
            
    except Exception as e:
        print(f"Error extracting information using GPT: {e}")
        return {}

def process_interview_transcript(transcript_path, language='english'):
    """
    Process the interview transcript file and extract structured information
    """
    try:
        with open(transcript_path, 'r', encoding='utf-8') as file:
            transcript_text = file.read()
        
        # Parse the transcript to get Q&A pairs
        qa_pairs = parse_interview_transcript(transcript_text, language)
        
        # Extract structured information using GPT
        structured_info = extract_fir_information(qa_pairs, language)
        
        return structured_info
        
    except Exception as e:
        print(f"Error processing interview transcript: {e}")
        return {}