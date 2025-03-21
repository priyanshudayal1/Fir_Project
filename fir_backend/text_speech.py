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
        
        try:
            # Generate speech using selected backend
            if self.use_huggingface and language.lower() in self.hf_pipelines:
                self._generate_speech_huggingface(text, language.lower(), output_file)
            else:
                self._generate_speech_gtts(text, language.lower(), output_file)
            
            # Verify the file was created and has content
            if not os.path.exists(output_file) or os.path.getsize(output_file) == 0:
                raise Exception("Failed to generate audio file")
            
            # Play the audio if requested
            if play:
                self.play_audio(output_file)
            
            return output_file
            
        except Exception as e:
            # Clean up failed file if it exists
            if output_file and os.path.exists(output_file):
                try:
                    os.remove(output_file)
                except:
                    pass
            raise Exception(f"TTS generation failed: {str(e)}")
    
    def _generate_speech_gtts(self, text, language, output_file):
        """Generate speech using gTTS."""
        try:
            lang_code = self.LANGS[language]
            tts = gTTS(text=text, lang=lang_code, slow=False)
            tts.save(output_file)
            # Check if the file was created successfully
            if not os.path.exists(output_file) or os.path.getsize(output_file) == 0:
                raise Exception("gTTS failed to produce valid audio file")
            print(f"Generated speech using gTTS: {output_file}")
        except Exception as e:
            raise Exception(f"gTTS generation failed: {str(e)}")
    
    def _generate_speech_huggingface(self, text, language, output_file):
        """Generate speech using HuggingFace TTS pipeline."""
        try:
            self.hf_pipelines[language].generate(text)
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
            
            # Check if the file was created successfully
            if not os.path.exists(output_file) or os.path.getsize(output_file) == 0:
                raise Exception("HuggingFace TTS failed to create valid audio file")
            
            print(f"Generated speech using HuggingFace: {output_file}")
        except Exception as e:
            raise Exception(f"HuggingFace TTS generation failed: {str(e)}")
    
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