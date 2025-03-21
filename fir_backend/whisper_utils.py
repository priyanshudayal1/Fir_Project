import whisper
import torch
from transformers import pipeline
import re
from datetime import datetime
import os
from gpt import callGPT  # Import the callGPT function from gpt.py

# Check if CUDA (GPU) is available
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Using device: {device}")

# Load Whisper Model (use "medium" for better multilingual support)
model = whisper.load_model("medium", device=device)

# Load Sentiment Analysis Model with GPU support
sentiment_analyzer = pipeline("sentiment-analysis", device=device)

# Load Zero-Shot Classifier with GPU support
classifier = pipeline("zero-shot-classification", device=device)

def extract_personal_info(transcribed_text, language='english'):
    """Extracts personal information from the transcribed text using GPT API."""
    
    # Prepare system prompt based on language
    system_prompts = {
        'english': """You are an AI assistant helping with information extraction from a First Information Report (FIR) or police complaint transcript. 
Extract all relevant personal information and incident details in a structured format. Be precise and extract only what is explicitly stated in the text.""",
        
        'hindi': """आप एक AI सहायक हैं जो प्रथम सूचना रिपोर्ट (FIR) या पुलिस शिकायत से जानकारी निकालने में मदद कर रहे हैं। 
संरचित प्रारूप में सभी प्रासंगिक व्यक्तिगत जानकारी और घटना विवरण निकालें। सटीक रहें और केवल वही निकालें जो पाठ में स्पष्ट रूप से बताया गया है।""",
        
        'punjabi': """ਤੁਸੀਂ ਇੱਕ AI ਸਹਾਇਕ ਹੋ ਜੋ ਪਹਿਲੀ ਸੂਚਨਾ ਰਿਪੋਰਟ (FIR) ਜਾਂ ਪੁਲਿਸ ਸ਼ਿਕਾਇਤ ਤੋਂ ਜਾਣਕਾਰੀ ਕੱਢਣ ਵਿੱਚ ਸਹਾਇਤਾ ਕਰ ਰਹੇ ਹੋ।
ਸੰਰਚਿਤ ਫਾਰਮੈਟ ਵਿੱਚ ਸਾਰੀ ਢੁਕਵੀਂ ਨਿੱਜੀ ਜਾਣਕਾਰੀ ਅਤੇ ਘਟਨਾ ਦੇ ਵੇਰਵੇ ਕੱਢੋ। ਸਟੀਕ ਰਹੋ ਅਤੇ ਸਿਰਫ ਉਹੀ ਕੱਢੋ ਜੋ ਟੈਕਸਟ ਵਿੱਚ ਸਪਸ਼ਟ ਤੌਰ 'ਤੇ ਕਿਹਾ ਗਿਆ ਹੈ।"""
    }
    
    # Prepare user prompt
    user_prompts = {
        'english': f"""Extract the following information from the text below and provide it in a structured JSON format with these keys:
- victim_name
- father_or_husband_name
- dob (date of birth)
- nationality
- occupation
- address
- incident_date
- incident_time
- incident_location
- witness_details
- accused_description
- stolen_properties
- total_value
- delay_reason
- incident_details (summary of the incident)

If information for any field is not available, provide an empty string for that field.

TEXT:
{transcribed_text}""",

        'hindi': f"""नीचे दिए गए पाठ से निम्नलिखित जानकारी निकालें और इसे इन कुंजियों के साथ एक संरचित JSON प्रारूप में प्रदान करें:
- victim_name (पीड़ित का नाम)
- father_or_husband_name (पिता या पति का नाम)
- dob (जन्म तिथि)
- nationality (राष्ट्रीयता)
- occupation (व्यवसाय)
- address (पता)
- incident_date (घटना की तारीख)
- incident_time (घटना का समय)
- incident_location (घटना स्थल)
- witness_details (गवाह विवरण)
- accused_description (आरोपी का विवरण)
- stolen_properties (चोरी की संपत्ति)
- total_value (कुल मूल्य)
- delay_reason (देरी का कारण)
- incident_details (घटना का सारांश)

यदि किसी भी फ़ील्ड के लिए जानकारी उपलब्ध नहीं है, तो उस फ़ील्ड के लिए खाली स्ट्रिंग प्रदान करें।

पाठ:
{transcribed_text}""",

        'punjabi': f"""ਹੇਠਾਂ ਦਿੱਤੇ ਟੈਕਸਟ ਤੋਂ ਹੇਠ ਲਿਖੀ ਜਾਣਕਾਰੀ ਕੱਢੋ ਅਤੇ ਇਸਨੂੰ ਇਹਨਾਂ ਕੁੰਜੀਆਂ ਨਾਲ ਇੱਕ ਸੰਰਚਿਤ JSON ਫਾਰਮੈਟ ਵਿੱਚ ਪ੍ਰਦਾਨ ਕਰੋ:
- victim_name (ਪੀੜਤ ਦਾ ਨਾਮ)
- father_or_husband_name (ਪਿਤਾ ਜਾਂ ਪਤੀ ਦਾ ਨਾਮ)
- dob (ਜਨਮ ਮਿਤੀ)
- nationality (ਨਾਗਰਿਕਤਾ)
- occupation (ਕਿੱਤਾ)
- address (ਪਤਾ)
- incident_date (ਘਟਨਾ ਦੀ ਮਿਤੀ)
- incident_time (ਘਟਨਾ ਦਾ ਸਮਾਂ)
- incident_location (ਘਟਨਾ ਸਥਾਨ)
- witness_details (ਗਵਾਹ ਵੇਰਵੇ)
- accused_description (ਦੋਸ਼ੀ ਦਾ ਵੇਰਵਾ)
- stolen_properties (ਚੋਰੀ ਹੋਈ ਜਾਇਦਾਦ)
- total_value (ਕੁੱਲ ਮੁੱਲ)
- delay_reason (ਦੇਰੀ ਦਾ ਕਾਰਨ)
- incident_details (ਘਟਨਾ ਦਾ ਸਾਰ)

ਜੇਕਰ ਕਿਸੇ ਵੀ ਫੀਲਡ ਲਈ ਜਾਣਕਾਰੀ ਉਪਲਬਧ ਨਹੀਂ ਹੈ, ਤਾਂ ਉਸ ਫੀਲਡ ਲਈ ਖਾਲੀ ਸਟਰਿੰਗ ਪ੍ਰਦਾਨ ਕਰੋ।

ਟੈਕਸਟ:
{transcribed_text}"""
    }
    
    try:
        # Select prompts based on language (default to English if language not found)
        system_prompt = system_prompts.get(language.lower(), system_prompts['english'])
        user_prompt = user_prompts.get(language.lower(), user_prompts['english'])
        
        # Call GPT API
        response = callGPT(system_prompt, user_prompt)
        
        # Parse the JSON response
        import json
        
        # Check if the response contains a JSON block
        if '{' in response and '}' in response:
            # Extract JSON content if it's embedded in other text
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            json_str = response[json_start:json_end]
            
            try:
                extracted_info = json.loads(json_str)
                
                # Ensure all expected fields are present
                expected_fields = [
                    "victim_name", "father_or_husband_name", "dob", "nationality", 
                    "occupation", "address", "incident_date", "incident_time", 
                    "incident_location", "witness_details", "accused_description", 
                    "stolen_properties", "total_value", "delay_reason", "incident_details"
                ]
                
                for field in expected_fields:
                    if field not in extracted_info:
                        extracted_info[field] = ""
                
                return extracted_info
                
            except json.JSONDecodeError:
                # If JSON parsing fails, fall back to regex-based extraction
                print("JSON parsing failed, falling back to regex extraction")
                return fallback_extract_personal_info(transcribed_text, language)
        else:
            # If no JSON in response, fall back to regex-based extraction
            print("No JSON found in response, falling back to regex extraction")
            return fallback_extract_personal_info(transcribed_text, language)
            
    except Exception as e:
        print(f"GPT extraction failed with error: {str(e)}")
        # Fall back to regex-based extraction
        return fallback_extract_personal_info(transcribed_text, language)


def fallback_extract_personal_info(transcribed_text, language='english'):
    """Fallback function that extracts personal information using regex patterns."""
    info = {
        "victim_name": "",
        "father_or_husband_name": "",
        "dob": "",
        "nationality": "",
        "occupation": "",
        "address": "",
        "incident_date": "",
        "incident_time": "",
        "incident_location": "",
        "witness_details": "",
        "accused_description": "",
        "stolen_properties": "",
        "total_value": "",
        "delay_reason": "",
        "incident_details": transcribed_text
    }
    
    # Language-specific patterns
    patterns = {
        'english': {
            'name': r"(?:my name is|I am|I'm|name:?\s+is|myself)\s+([A-Za-z\s]+?)(?:[\.,]|\s+and|\s+aged|\s+living)",
            'father': r"(?:my father's name is|father'?s? name:?\s+is|father is|my father,)\s+([A-Za-z\s]+?)(?:[\.,]|and)",
            'husband': r"(?:my husband's name is|husband'?s? name:?\s+is|husband is|my husband,)\s+([A-Za-z\s]+?)(?:[\.,]|and)",
            'dob': r"(?:born on|date of birth|dob:?|born|birth date)(?:\s+is)?\s+([0-9]{1,2}(?:st|nd|rd|th)?\s+(?:January|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sept?|Oct|Nov|Dec)(?:\s+[0-9]{4})?)",
            'nationality': r"(?:my nationality is|nationality:?|I am a citizen of|citizen of)\s+([A-Za-z]+)",
            'occupation': r"(?:(?:I am|I'm|working as)(?: a| an)?\s+|occupation:?\s+|by profession,?\s+(?:I am|I'm)(?: a| an)?\s+|employed as(?: a| an)?\s+)([^.,]{3,30})(?:[\.,]|and|at)",
            'address': r"(?:I live at|address:?|residing at|residence:?|staying at)\s+([^.]{10,100})(?:\.|\n)",
            'location': r"(?:incident|crime|theft|attack|robbery) (?:occurred|happened|took place) (?:at|in|near|around)\s+([^\.]+?)(?:on|at|when|where|\.|\band\b)",
            'witness': r"([A-Za-z\s]+)(?:saw|witnessed|observed|was present)",
            'accused': r"(?:The accused|perpetrator|suspect|attacker|thief) (?:was|were|is|appeared to be|looked like|had|wore|was wearing)\s+([^\.]{5,100})(?:\.|\n)",
            'stolen': r"(?:stole|took|robbed|snatched|made away with|fled with|missing items include)\s+([^\.]{5,100})(?:\.|\n)",
            'value': r"(?:valued at|worth|amounting to|costing|estimated value of|total value)\s+(?:Rs\.?|₹|INR)?\s*([0-9,]+)"
        },
        'hindi': {
            'name': r"(?:मेरा नाम|मैं)\s+([^\.\,]+)[\.\,]",
            'father': r"(?:मेरे पिता का नाम|पिता का नाम|पिता जी का नाम)\s+([^\.\,]+)[\.\,]",
            'husband': r"(?:मेरे पति का नाम|पति का नाम)\s+([^\.\,]+)[\.\,]",
            'dob': r"(?:जन्म तिथि|जन्म दिनांक)\s+([0-9]{1,2}\s+(?:जनवरी|फरवरी|मार्च|अप्रैल|मई|जून|जुलाई|अगस्त|सितंबर|अक्टूबर|नवंबर|दिसंबर)(?:\s+[0-9]{4})?)",
            'nationality': r"(?:मेरी राष्ट्रीयता|नागरिकता)\s+([^\.\,]+)",
            'occupation': r"(?:मैं|मेरा पेशा|व्यवसाय)\s+([^\.\,]{3,30})(?:हूँ|हूं|है|में|का)",
            'address': r"(?:मैं|पता|निवास)\s+([^\.]{10,100})(?:में रहता हूँ|में रहती हूँ|पर रहता हूँ|पर रहती हूँ|\में निवास करता|में निवास करती)",
            'location': r"(?:पास|में|के निकट)\s+([^\.]+?)(?:जब|जहाँ|\.)",
            'witness': r"([^\.\,]+)(?:ने देखा|गवाह)",
            'accused': r"(?:आरोपी|संदिग्ध|हमलावर)\s+([^\.]{5,100})(?:\.|\n)",
            'stolen': r"(?:चोरी|लूट|छीन)\s+([^\.]{5,100})(?:\.|\n)",
            'value': r"(?:कीमत|मूल्य|लागत)\s+(?:रु\.?|₹)?\s*([0-9,]+)"
        },
        'punjabi': {
            'name': r"(?:ਮੇਰਾ ਨਾਮ|ਮੈਂ)\s+([^\.\,]+)[\.\,]",
            'father': r"(?:ਮੇਰੇ ਪਿਤਾ ਦਾ ਨਾਮ|ਪਿਤਾ ਦਾ ਨਾਮ|ਪਿਤਾ ਜੀ ਦਾ ਨਾਮ)\s+([^\.\,]+)[\.\,]",
            'husband': r"(?:ਮੇਰੇ ਪਤੀ ਦਾ ਨਾਮ|ਪਤੀ ਦਾ ਨਾਮ)\s+([^\.\,]+)[\.\,]",
            'dob': r"(?:ਜਨਮ ਮਿਤੀ|ਜਨਮ ਦਿਨ)\s+([0-9]{1,2}\s+(?:ਜਨਵਰੀ|ਫਰਵਰੀ|ਮਾਰਚ|ਅਪ੍ਰੈਲ|ਮਈ|ਜੂਨ|ਜੁਲਾਈ|ਅਗਸਤ|ਸਤੰਬਰ|ਅਕਤੂਬਰ|ਨਵੰਬਰ|ਦਸੰਬਰ)(?:\s+[0-9]{4})?)",
            'nationality': r"(?:ਮੇਰੀ ਨਾਗਰਿਕਤਾ|ਕੌਮੀਅਤ)\s+([^\.\,]+)",
            'occupation': r"(?:ਮੈਂ|ਮੇਰਾ ਕਿੱਤਾ|ਪੇਸ਼ਾ)\s+([^\.\,]{3,30})(?:ਹਾਂ|ਹੈ|ਵਿੱਚ|ਦਾ)",
            'address': r"(?:ਮੈਂ|ਪਤਾ|ਨਿਵਾਸ)\s+([^\.]{10,100})(?:ਵਿੱਚ ਰਹਿੰਦਾ ਹਾਂ|ਵਿੱਚ ਰਹਿੰਦੀ ਹਾਂ|'ਤੇ ਰਹਿੰਦਾ ਹਾਂ|'ਤੇ ਰਹਿੰਦੀ ਹਾਂ|ਵਿੱਚ ਨਿਵਾਸ ਕਰਦਾ|ਵਿੱਚ ਨਿਵਾਸ ਕਰਦੀ)",
            'location': r"(?:ਨੇੜੇ|ਵਿੱਚ|ਕੋਲ)\s+([^\.]+?)(?:ਜਦੋਂ|ਜਿੱਥੇ|\.)",
            'witness': r"([^\.\,]+)(?:ਨੇ ਵੇਖਿਆ|ਗਵਾਹ)",
            'accused': r"(?:ਦੋਸ਼ੀ|ਸ਼ੱਕੀ|ਹਮਲਾਵਰ)\s+([^\.]{5,100})(?:\.|\\n)",
            'stolen': r"(?:ਚੋਰੀ|ਲੁੱਟ|ਖੋਹ)\s+([^\.]{5,100})(?:\.|\\n)",
            'value': r"(?:ਕੀਮਤ|ਮੁੱਲ|ਲਾਗਤ)\s+(?:ਰੁ\.?|₹)?\s*([0-9,]+)"
        }
    }
    
    patterns_for_lang = patterns.get(language.lower(), patterns['english'])
    
    # Extract name
    name_match = re.search(patterns_for_lang['name'], transcribed_text, re.IGNORECASE)
    if name_match:
        info["victim_name"] = name_match.group(1).strip()
    
    # Extract father's or husband's name
    father_match = re.search(patterns_for_lang['father'], transcribed_text, re.IGNORECASE)
    husband_match = re.search(patterns_for_lang['husband'], transcribed_text, re.IGNORECASE)
    if father_match:
        info["father_or_husband_name"] = father_match.group(1).strip()
    elif husband_match:
        info["father_or_husband_name"] = husband_match.group(1).strip()
    
    # Extract date of birth
    dob_match = re.search(patterns_for_lang['dob'], transcribed_text, re.IGNORECASE)
    if dob_match:
        info["dob"] = dob_match.group(1).strip()
    
    # Extract nationality
    nationality_match = re.search(patterns_for_lang['nationality'], transcribed_text, re.IGNORECASE)
    if nationality_match:
        info["nationality"] = nationality_match.group(1).strip()
    
    # Extract occupation
    occupation_match = re.search(patterns_for_lang['occupation'], transcribed_text, re.IGNORECASE)
    if occupation_match:
        info["occupation"] = occupation_match.group(1).strip()
    
    # Extract address
    address_match = re.search(patterns_for_lang['address'], transcribed_text, re.IGNORECASE)
    if address_match:
        info["address"] = address_match.group(1).strip()
        
    # Extract date and time - using universal patterns as they're typically numeric
    date_match = re.search(r"(\d+(?:st|nd|rd|th)?\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d+)(?:\s+\d{4})?", transcribed_text, re.IGNORECASE)
    time_match = re.search(r"(?:at|around|approximately)\s+(\d{1,2}(?::\d{2})?\s*(?:am|pm|AM|PM|a\.m\.|p\.m\.|hours))", transcribed_text, re.IGNORECASE)
    
    if date_match:
        info["incident_date"] = date_match.group(1).strip()
    if time_match:
        info["incident_time"] = time_match.group(1).strip()
    
    # Extract location
    location_match = re.search(patterns_for_lang['location'], transcribed_text, re.IGNORECASE)
    if location_match:
        info["incident_location"] = location_match.group(1).strip()
    
    # Extract witness details
    witness_match = re.search(patterns_for_lang['witness'], transcribed_text, re.IGNORECASE)
    if witness_match:
        info["witness_details"] = witness_match.group(1).strip()
    
    # Extract accused description
    accused_match = re.search(patterns_for_lang['accused'], transcribed_text, re.IGNORECASE)
    if accused_match:
        info["accused_description"] = accused_match.group(1).strip()
    
    # Extract stolen properties
    stolen_match = re.search(patterns_for_lang['stolen'], transcribed_text, re.IGNORECASE)
    if stolen_match:
        info["stolen_properties"] = stolen_match.group(1).strip()
    else:
        # Fallback to keywords approach if regex doesn't find anything
        stolen_keywords = {
            'english': ['phone', 'mobile', 'wallet', 'bag', 'purse', 'money', 'jewelry', 'cash', 'gold', 'silver', 'laptop', 'watch'],
            'hindi': ['फोन', 'मोबाइल', 'पर्स', 'बटुआ', 'पैसे', 'गहने', 'नगदी', 'सोना', 'चांदी', 'लैपटॉप', 'घड़ी'],
            'punjabi': ['ਫੋਨ', 'ਮੋਬਾਈਲ', 'ਪਰਸ', 'ਬਟੂਆ', 'ਪੈਸੇ', 'ਗਹਿਣੇ', 'ਨਕਦੀ', 'ਸੋਨਾ', 'ਚਾਂਦੀ', 'ਲੈਪਟਾਪ', 'ਘੜੀ']
        }
        
        stolen_items = []
        for keyword in stolen_keywords.get(language.lower(), stolen_keywords['english']):
            if keyword.lower() in transcribed_text.lower():
                stolen_items.append(keyword)
        
        if stolen_items:
            info["stolen_properties"] = ", ".join(stolen_items)
    
    # Extract total value
    value_match = re.search(patterns_for_lang['value'], transcribed_text, re.IGNORECASE)
    if value_match:
        info["total_value"] = value_match.group(1).strip()
    
    # Extract delay reason
    delay_reason_match = re.search(r"(?:delay|late|couldn't report|could not report|waited)(?:[^.]{5,100})(?:\.|\n)", transcribed_text, re.IGNORECASE)
    if delay_reason_match:
        info["delay_reason"] = delay_reason_match.group(0).strip()
    
    return info

def transcribe_audio(audio_path, language='english'):
    """Convert audio to text using Whisper."""
    try:
        # Language codes for Whisper
        language_codes = {
            'english': 'en',
            'hindi': 'hi',
            'punjabi': 'pa'
        }
        
        if not audio_path or not os.path.exists(audio_path):
            return {
                "success": False,
                "error": f"Audio file not found at path: {audio_path}"
            }

        # Check file size and format
        if os.path.getsize(audio_path) == 0:
            return {
                "success": False,
                "error": "Audio file is empty"
            }
            
        # Use GPU if available for transcription
        try:
            result = model.transcribe(
                audio_path, 
                fp16=(device == "cuda"),
                language=language_codes.get(language.lower(), 'en')
            )
        except Exception as e:
            return {
                "success": False,
                "error": f"Whisper transcription failed: {str(e)}"
            }

        if not result or not result.get("text"):
            return {
                "success": False,
                "error": "No transcription result produced"
            }

        transcribed_text = result["text"]
        # Extract personal information from transcribed text
        personal_info = extract_personal_info(transcribed_text, language)
        
        return {
            "success": True,
            "text": transcribed_text,
            "personal_info": personal_info,
            "language": language
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Error during transcription process: {str(e)}"
        }

def analyze_sentiment_and_crime(transcription_result):
    """Analyzes sentiment and predicts crime type from transcribed text."""
    
    # Handle transcription errors
    if isinstance(transcription_result, dict):
        if not transcription_result.get("success", False):
            return {"error": transcription_result.get("error", "Transcription failed")}
        transcribed_text = transcription_result.get("text", "")
    else:
        transcribed_text = str(transcription_result)

    if not transcribed_text.strip():
        return {"error": "Empty text provided."}

    try:
        # 🔹 Step 1: Sentiment Analysis
        sentiment_result = sentiment_analyzer(transcribed_text)[0]  # Extract first result

        # 🔹 Step 2: Crime Type Prediction
        crime_labels = ["Theft", "Assault", "Fraud", "Harassment", "Murder", "Kidnapping"]
        intent_result = classifier(transcribed_text, crime_labels, multi_label=True)

        # Extract top crime predictions
        crime_predictions = [
            {"crime": label, "score": round(score, 4)}
            for label, score in zip(intent_result["labels"], intent_result["scores"])
        ]

        return {
            "sentiment": sentiment_result,
            "crime_predictions": crime_predictions
        }

    except Exception as e:
        return {"error": f"Analysis failed: {str(e)}"}
