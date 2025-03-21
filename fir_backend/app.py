import os
import logging
import shutil
import mimetypes
from datetime import datetime
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from whisper_utils import transcribe_audio, analyze_sentiment_and_crime
from legal_section_extractor import extract_legal_sections
from transcript_processor import process_interview_transcript
from FIR import generate_fir
from text_speech import TextToSpeech

app = Flask(__name__)
CORS(app)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

tts_engine = TextToSpeech(use_huggingface=False)

ffmpeg_path = shutil.which("ffmpeg")
if not ffmpeg_path:
    logging.error("FFmpeg not found! Ensure it's installed and added to system PATH.")
    raise SystemExit("FFmpeg not found! Install FFmpeg and add it to PATH.")

def get_unique_filename(original_filename):
    """Generate a unique filename by adding timestamp"""
    name, ext = os.path.splitext(original_filename)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{name}_{timestamp}{ext}"

@app.route("/generate_speech", methods=["POST"])
def generate_speech():
    try:
        data = request.json
        text = data.get("text")
        language = data.get("language", "english")

        if not text:
            return jsonify({"error": "No text provided"}), 400

        try:
            output_file = tts_engine.text_to_speech(
                text=text,
                language=language,
                play=False
            )

            # Ensure the file exists before attempting to send
            if not os.path.exists(output_file):
                raise FileNotFoundError("TTS engine failed to generate audio file")

            response = send_file(
                output_file,
                mimetype="audio/mpeg",
                as_attachment=True,
                download_name=f"speech_{int(datetime.now().timestamp())}.mp3"
            )

            # Add cleanup of temporary file after sending
            @response.call_on_close
            def cleanup():
                try:
                    if os.path.exists(output_file):
                        os.remove(output_file)
                except Exception as e:
                    logging.error(f"Failed to cleanup TTS file {output_file}: {e}")

            return response

        except Exception as tts_error:
            logging.error(f"Speech generation error: {str(tts_error)}")
            return jsonify({"error": f"Failed to generate speech: {str(tts_error)}"}), 500

    except Exception as e:
        logging.error(f"Speech Error: {str(e)}")
        return jsonify({"error": f"Speech request failed: {str(e)}"}), 500

@app.route("/tts", methods=["POST"])
def text_to_speech():
    try:
        data = request.json
        text = data.get("text")
        language = data.get("language", "english")

        if not text:
            return jsonify({"error": "No text provided"}), 400

        try:
            output_file = tts_engine.text_to_speech(
                text=text,
                language=language,
                play=False
            )

            # Ensure the file exists before attempting to send
            if not os.path.exists(output_file):
                raise FileNotFoundError("TTS engine failed to generate audio file")

            response = send_file(
                output_file,
                mimetype="audio/mpeg",
                as_attachment=True,
                download_name=f"tts_{int(datetime.now().timestamp())}.mp3"
            )

            # Add cleanup of temporary file after sending
            @response.call_on_close
            def cleanup():
                try:
                    if os.path.exists(output_file):
                        os.remove(output_file)
                except Exception as e:
                    logging.error(f"Failed to cleanup TTS file {output_file}: {e}")

            return response

        except Exception as tts_error:
            logging.error(f"TTS generation error: {str(tts_error)}")
            return jsonify({"error": f"Failed to generate speech: {str(tts_error)}"}), 500

    except Exception as e:
        logging.error(f"TTS Error: {str(e)}")
        return jsonify({"error": f"TTS request failed: {str(e)}"}), 500

@app.route("/transcribe", methods=["POST"])
def transcribe():
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file uploaded"}), 400

        file = request.files["file"]
        if not file.filename:
            return jsonify({"error": "Empty file name"}), 400
            
        language = request.form.get("language", "english")
        file_path = os.path.join(UPLOAD_FOLDER, get_unique_filename(file.filename))
        file.save(file_path)

        result = transcribe_audio(file_path, language)
        if not result.get("success", False):
            error_msg = result.get("error", "Transcription failed")
            logging.error(f"Transcription failed: {error_msg}")
            return jsonify({"error": error_msg}), 500

        return jsonify({
            "text": result["text"],
            "personal_info": result.get("personal_info", {}),
            "language": result.get("language", language)
        })

    except Exception as e:
        logging.error(f"Transcription Error: {str(e)}")
        return jsonify({"error": f"Server error during transcription: {str(e)}"}), 500

@app.route("/update_fir", methods=["POST"])
def update_fir():
    try:
        data = request.json
        language = data.get("language", "english")
        
        # Generate updated FIR with received field values
        fir_text = generate_fir(
            victim_name=data.get("victim_name"),
            father_or_husband_name=data.get("father_or_husband_name"),
            dob=data.get("dob"),
            nationality=data.get("nationality"),
            occupation=data.get("occupation"),
            address=data.get("address"),
            incident_date=data.get("incident_date"),
            incident_time=data.get("incident_time"),
            incident_location=data.get("incident_location"),
            complaint_details=data.get("complaint_details"),
            accused_details=data.get("accused_details"),
            stolen_properties=data.get("stolen_properties"),
            total_value=data.get("total_value"),
            inquest_report=data.get("inquest_report"),
            delay_reason=data.get("delay_reason"),
            language=language
        )
        
        return jsonify({
            "status": "success",
            "fir_draft": fir_text
        })
        
    except Exception as e:
        logging.error(f"Error updating FIR: {str(e)}")
        return jsonify({"error": f"Failed to update FIR: {str(e)}"}), 500

@app.route("/upload_audio", methods=["POST"])
def upload_audio():
    logging.info("Received request at /upload_audio")
    
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    language = request.form.get("language", "english")
    file_path = os.path.join(UPLOAD_FOLDER, get_unique_filename(file.filename))
    file.save(file_path)
    logging.info(f"File saved at {file_path}, language: {language}")

    try:
        # Check if the file is a text file (interview transcript) or audio file
        mime_type = mimetypes.guess_type(file_path)[0]
        if mime_type and mime_type.startswith('text/'):
            # For text files, no need to make a copy - use the file directly
            logging.info(f"Processing interview transcript with language: {language}")
            
            # Process interview transcript using our GPT-based transcript processor with language support
            personal_info = process_interview_transcript(file_path, language)
            
            # Read the transcript content
            with open(file_path, 'r', encoding='utf-8') as f:
                transcribed_text = f.read()
                
            success = True
        else:
            # Handle audio file using whisper with language support
            logging.info(f"Transcribing audio with language: {language}")
            result = transcribe_audio(file_path, language)
            success = result.get("success", False)
            transcribed_text = result.get("text", "")
            personal_info = result.get("personal_info", {})
            
        if not success:
            return jsonify({"error": "Failed to process input"}), 500

        # Analyze sentiment and detect crime
        logging.info("Analyzing sentiment and crime type")
        analysis_result = analyze_sentiment_and_crime(transcribed_text)
        if "error" in analysis_result:
            return jsonify({"error": "Failed to analyze content"}), 500

        # Extract legal sections using our enhanced GPT-based extractor with language support
        logging.info(f"Extracting legal sections with language: {language}")
        legal_sections_result = extract_legal_sections(transcribed_text, personal_info, language)
        if "error" in legal_sections_result:
            return jsonify({"error": "Failed to extract legal sections"}), 500

        legal_sections = legal_sections_result.get("legal_sections", "")
        legal_data = legal_sections_result.get("legal_data", {})
        
        # Use extracted legal sections data for the FIR if available
        act1 = legal_data.get("act1", "")
        sections1 = legal_data.get("sections1", "")
        act2 = legal_data.get("act2", "")
        sections2 = legal_data.get("sections2", "")
        act3 = legal_data.get("act3", "")
        sections3 = legal_data.get("sections3", "")

        # Generate FIR draft with enhanced information
        logging.info(f"Generating FIR draft with language: {language}")
        fir_text = generate_fir(
            victim_name=personal_info.get("victim_name", "Unknown"),
            father_or_husband_name=personal_info.get("father_or_husband_name", ""),
            dob=personal_info.get("dob", ""),
            nationality=personal_info.get("nationality", ""),
            occupation=personal_info.get("occupation", ""),
            address=personal_info.get("address", ""),
            incident_date=personal_info.get("incident_date", ""),
            incident_time=personal_info.get("incident_time", ""),
            incident_location=personal_info.get("incident_location", ""),
            complaint_details=personal_info.get("incident_details", transcribed_text),
            accused_details=personal_info.get("accused_description", ""),
            stolen_properties=personal_info.get("stolen_properties", ""),
            total_value=personal_info.get("total_value", "[Not Provided]"),
            delay_reason=personal_info.get("delay_reason", "[Not Provided]"),
            act1=act1,
            sections1=sections1,
            act2=act2,
            sections2=sections2,
            act3=act3,
            sections3=sections3,
            language=language,
            personal_info=personal_info
        )

        response = {
            "status": "success",
            "transcribed_text": transcribed_text,
            "personal_info": personal_info,
            "sentiment": analysis_result["sentiment"],
            "crime_predictions": analysis_result["crime_predictions"],
            "legal_sections": legal_sections,
            "legal_data": legal_data,
            "fir_draft": fir_text,
            "language": language
        }
        
        return jsonify(response)

    except Exception as e:
        logging.error(f"Error processing file: {str(e)}")
        return jsonify({"error": f"Processing failed: {str(e)}"}), 500

@app.route("/upload_single_audio_file", methods=["POST"])
def upload_single_audio_file():
    logging.info("Received request at /upload_single_audio_file")
    
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    
    try:
        file = request.files["file"]
        language = request.form.get("language", "english")
        file_path = os.path.join(UPLOAD_FOLDER, get_unique_filename(file.filename))
        file.save(file_path)
        logging.info(f"File saved at {file_path}, language: {language}")
        
        # Transcribe the audio file
        logging.info(f"Transcribing audio with language: {language}")
        result = transcribe_audio(file_path, language)
        
        if not result.get("success", False):
            error_msg = result.get("error", "Transcription failed")
            logging.error(f"Transcription failed: {error_msg}")
            return jsonify({"error": error_msg}), 500
            
        transcribed_text = result.get("text", "")
        personal_info = result.get("personal_info", {})
        
        # Analyze sentiment and detect crime
        logging.info("Analyzing sentiment and crime type")
        analysis_result = analyze_sentiment_and_crime(transcribed_text)
        if "error" in analysis_result:
            return jsonify({"error": "Failed to analyze content"}), 500
            
        # Extract legal sections
        logging.info(f"Extracting legal sections with language: {language}")
        legal_sections_result = extract_legal_sections(transcribed_text, personal_info, language)
        if "error" in legal_sections_result:
            return jsonify({"error": "Failed to extract legal sections"}), 500
            
        legal_sections = legal_sections_result.get("legal_sections", "")
        legal_data = legal_sections_result.get("legal_data", {})
        
        # Use extracted legal sections data for the FIR
        act1 = legal_data.get("act1", "")
        sections1 = legal_data.get("sections1", "")
        act2 = legal_data.get("act2", "")
        sections2 = legal_data.get("sections2", "")
        act3 = legal_data.get("act3", "")
        sections3 = legal_data.get("sections3", "")
        
        # Generate FIR draft
        logging.info(f"Generating FIR draft with language: {language}")
        fir_text = generate_fir(
            victim_name=personal_info.get("victim_name", "Unknown"),
            father_or_husband_name=personal_info.get("father_or_husband_name", ""),
            dob=personal_info.get("dob", ""),
            nationality=personal_info.get("nationality", ""),
            occupation=personal_info.get("occupation", ""),
            address=personal_info.get("address", ""),
            incident_date=personal_info.get("incident_date", ""),
            incident_time=personal_info.get("incident_time", ""),
            incident_location=personal_info.get("incident_location", ""),
            complaint_details=personal_info.get("incident_details", transcribed_text),
            accused_details=personal_info.get("accused_description", ""),
            stolen_properties=personal_info.get("stolen_properties", ""),
            total_value=personal_info.get("total_value", "[Not Provided]"),
            delay_reason=personal_info.get("delay_reason", "[Not Provided]"),
            act1=act1,
            sections1=sections1,
            act2=act2,
            sections2=sections2,
            act3=act3,
            sections3=sections3,
            language=language,
            personal_info=personal_info
        )
        
        # Return the complete results
        response = {
            "status": "success",
            "transcribed_text": transcribed_text,
            "personal_info": personal_info,
            "sentiment": analysis_result["sentiment"],
            "crime_predictions": analysis_result["crime_predictions"],
            "legal_sections": legal_sections,
            "legal_data": legal_data,
            "fir_draft": fir_text,
            "language": language
        }
        
        return jsonify(response)
        
    except Exception as e:
        logging.error(f"Error processing file in upload_single_audio_file: {str(e)}")
        return jsonify({"error": f"Processing failed: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(debug=True)
