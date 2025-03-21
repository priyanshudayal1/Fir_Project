#!/usr/bin/env python3
"""
Text-to-Speech Converter supporting multiple languages (Hindi, English, Punjabi)
This module provides two TTS options:
1. gTTS (Google Text-to-Speech) for simple usage
2. HuggingFace TTS pipeline for more advanced features
"""

import os
import tempfile
from pathlib import Path
from gtts import gTTS
import pygame
import time

# Optional: Use HuggingFace if available
try:
    from transformers import pipeline
    HUGGINGFACE_AVAILABLE = True
except ImportError:
    HUGGINGFACE_AVAILABLE = False


class TextToSpeech:
    """Text-to-Speech converter supporting multiple languages."""
    
    # Language codes for gTTS
    LANGS = {
        'english': 'en',
        'hindi': 'hi', 
        'punjabi': 'pa'
    }
    
    # HuggingFace model mapping - using models that support our target languages
    HF_MODELS = {
        'english': 'facebook/mms-tts-eng',
        'hindi': 'facebook/mms-tts-hin',
        'punjabi': 'facebook/mms-tts-pan'  # pan is the language code for Punjabi
    }
    
    def __init__(self, use_huggingface=False):
        """
        Initialize the TTS engine.
        
        Args:
            use_huggingface (bool): If True, use HuggingFace models; otherwise use gTTS
        """
        self.use_huggingface = use_huggingface and HUGGINGFACE_AVAILABLE
        
        # Initialize pygame for audio playback
        pygame.init()
        pygame.mixer.init()
        
        # Load HuggingFace TTS pipelines if requested
        self.hf_pipelines = {}
        if self.use_huggingface:
            print("Initializing HuggingFace TTS pipelines (this may take some time)...")
            try:
                for lang, model in self.HF_MODELS.items():
                    self.hf_pipelines[lang] = pipeline("text-to-speech", model=model)
                print("HuggingFace TTS pipelines loaded successfully.")
            except Exception as e:
                print(f"Error loading HuggingFace models: {e}")
                self.use_huggingface = False
                print("Falling back to gTTS...")
    
    def text_to_speech(self, text, language='english', output_file=None, play=True):
        """
        Convert text to speech in the specified language.
        
        Args:
            text (str): The text to convert to speech
            language (str): Language code ('english', 'hindi', 'punjabi')
            output_file (str): Path to save audio file (if None, a temporary file is used)
            play (bool): Whether to play the audio immediately
            
        Returns:
            str: Path to the generated audio file
        """
        if language.lower() not in self.LANGS:
            raise ValueError(f"Unsupported language: {language}. Supported languages: {list(self.LANGS.keys())}")
        
        # Create a temporary file if no output file is specified
        if output_file is None:
            temp_dir = tempfile.gettempdir()
            output_file = os.path.join(temp_dir, f"tts_output_{int(time.time())}.mp3")
        
        # Generate speech using selected backend
        if self.use_huggingface and language.lower() in self.hf_pipelines:
            self._generate_speech_huggingface(text, language.lower(), output_file)
        else:
            self._generate_speech_gtts(text, language.lower(), output_file)
        
        # Play the audio if requested
        if play:
            self.play_audio(output_file)
        
        return output_file
    
    def _generate_speech_gtts(self, text, language, output_file):
        """Generate speech using gTTS."""
        lang_code = self.LANGS[language]
        tts = gTTS(text=text, lang=lang_code, slow=False)
        tts.save(output_file)
        print(f"Generated speech using gTTS: {output_file}")
    
    def _generate_speech_huggingface(self, text, language, output_file):
        """Generate speech using HuggingFace TTS pipeline."""
        pipeline = self.hf_pipelines[language]
        speech = pipeline(text)
        
        # The output format depends on the pipeline, typically it's a dictionary with 'audio' key
        if isinstance(speech, dict) and "audio" in speech:
            # Save the audio data to file
            import numpy as np
            import soundfile as sf
            sf.write(output_file, np.array(speech["audio"]), speech.get("sampling_rate", 16000))
        else:
            # Handle other formats if needed
            with open(output_file, "wb") as f:
                f.write(speech)
                
        print(f"Generated speech using HuggingFace: {output_file}")
    
    def play_audio(self, audio_file):
        """Play an audio file using pygame."""
        try:
            pygame.mixer.music.load(audio_file)
            pygame.mixer.music.play()
            # Wait for the audio to finish playing
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
        except Exception as e:
            print(f"Error playing audio: {e}")

    def __del__(self):
        """Clean up pygame resources."""
        try:
            pygame.mixer.quit()
            pygame.quit()
        except:
            pass


def main():
    """Sample usage of the TextToSpeech class."""
    # Example usage
    tts = TextToSpeech(use_huggingface=False)  # Set to True to use HuggingFace models
    
    # English example
        # English example
    tts.text_to_speech("Hello, this is a comprehensive test of the text to speech system. We are testing how well it handles longer paragraphs with multiple sentences and various punctuation marks. The system should be able to properly vocalize this entire passage with appropriate pauses, intonation, and natural-sounding speech patterns. This will help us ensure that the TTS functionality works correctly for real-world applications.", 
                      language="english")
    
    # Hindi example
    tts.text_to_speech("नमस्ते, यह पाठ से भाषण प्रणाली का एक विस्तृत परीक्षण है। हम परीक्षण कर रहे हैं कि यह सिस्टम कैसे लंबे अनुच्छेदों को संभालता है जिनमें कई वाक्य और विभिन्न विराम चिह्न हैं। इस प्रणाली को उचित ठहराव, स्वरोत्तार और प्राकृतिक लगने वाले भाषण पैटर्न के साथ इस पूरे मार्ग को ठीक से वोकलाइज़ करने में सक्षम होना चाहिए। यह हमें यह सुनिश्चित करने में मदद करेगा कि टीटीएस कार्यक्षमता वास्तविक दुनिया के अनुप्रयोगों के लिए सही ढंग से काम करती है।", 
                      language="hindi")
    
    # Punjabi example
    tts.text_to_speech("ਸਤ ਸ੍ਰੀ ਅਕਾਲ, ਇਹ ਟੈਕਸਟ ਤੋਂ ਸਪੀਚ ਸਿਸਟਮ ਦਾ ਇੱਕ ਵਿਆਪਕ ਟੈਸਟ ਹੈ। ਅਸੀਂ ਇਹ ਟੈਸਟ ਕਰ ਰਹੇ ਹਾਂ ਕਿ ਇਹ ਸਿਸਟਮ ਕਿਵੇਂ ਲੰਬੇ ਪੈਰਾਗ੍ਰਾਫਾਂ ਨੂੰ ਸੰਭਾਲਦਾ ਹੈ ਜਿਨ੍ਹਾਂ ਵਿੱਚ ਕਈ ਵਾਕ ਅਤੇ ਵੱਖ-ਵੱਖ ਵਿਰਾਮ ਚਿੰਨ੍ਹ ਹਨ। ਇਸ ਸਿਸਟਮ ਨੂੰ ਉਚਿਤ ਵਿਰਾਮ, ਸੁਰ ਅਤੇ ਕੁਦਰਤੀ ਲੱਗਣ ਵਾਲੇ ਭਾਸ਼ਣ ਪੈਟਰਨ ਦੇ ਨਾਲ ਇਸ ਪੂਰੇ ਪੈਸੇਜ ਨੂੰ ਸਹੀ ਢੰਗ ਨਾਲ ਉਚਾਰਣ ਕਰਨ ਦੇ ਯੋਗ ਹੋਣਾ ਚਾਹੀਦਾ ਹੈ। ਇਹ ਸਾਨੂੰ ਇਹ ਯਕੀਨੀ ਬਣਾਉਣ ਵਿੱਚ ਮਦਦ ਕਰੇਗਾ ਕਿ TTS ਕਾਰਜਕੁਸ਼ਲਤਾ ਅਸਲ ਦੁਨੀਆਂ ਦੀਆਂ ਐਪਲੀਕੇਸ਼ਨਾਂ ਲਈ ਸਹੀ ਢੰਗ ਨਾਲ ਕੰਮ ਕਰਦੀ ਹੈ।", 
                      language="punjabi")


if __name__ == "__main__":
    main()