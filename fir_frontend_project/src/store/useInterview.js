import { create } from "zustand";
import axios from "axios";

export const useInterviewStore = create((set, get) => ({
  error: null,
  isProcessing: false,
  setError: (error) => set({ error }),
  setIsProcessing: (isProcessing) => set({ isProcessing }),

  // TTS API calls
  generateWelcomeSpeech: async (welcomeMessage, language) => {
    try {
      const response = await axios.post(
        "http://localhost:5000/generate_speech",
        {
          text: welcomeMessage,
          language: language,
        },
        {
          responseType: "blob",
        }
      );
      return new Blob([response.data], { type: "audio/mp3" });
    } catch (error) {
      set({ error: "Failed to generate welcome message" });
      throw error;
    }
  },

  generateQuestionSpeech: async (questionText, language) => {
    try {
      const response = await axios.post(
        "http://localhost:5000/tts",
        {
          text: questionText,
          language: language,
        },
        {
          responseType: "blob",
        }
      );

      if (response.data.size === 0) {
        throw new Error("Received empty audio data from server");
      }

      return response.data;
    } catch (error) {
      set({ error: "Failed to generate question audio" });
      throw error;
    }
  },

  // Speech-to-text API call
  transcribeAudio: async (audioBlob, language) => {
    try {
      set({ isProcessing: true });
      const formData = new FormData();
      formData.append("file", audioBlob);
      formData.append("language", language);

      const response = await axios.post(
        "http://localhost:5000/transcribe",
        formData
      );

      return response.data.text;
    } catch (error) {
      set({ error: "Failed to transcribe audio" });
      throw error;
    } finally {
      set({ isProcessing: false });
    }
  },
}));
