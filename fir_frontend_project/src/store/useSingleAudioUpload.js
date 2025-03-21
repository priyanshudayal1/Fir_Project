import { create } from "zustand";
import axios from "axios";

const API_BASE_URL = "http://localhost:5000";

export const useSingleAudioUploadStore = create((set, get) => ({
  isUploading: false,
  uploadProgress: 0,
  processingResults: null,
  error: null,

  uploadAudio: async (audioFile, language) => {
    try {
      set({ isUploading: true, uploadProgress: 0, error: null });

      // Create form data
      const formData = new FormData();
      formData.append("file", audioFile);
      formData.append("language", language || "english");

      // Upload the file with progress tracking
      const response = await axios.post(
        `${API_BASE_URL}/upload_single_audio_file`,
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
          },
          onUploadProgress: (progressEvent) => {
            // Calculate the progress percentage
            const percentCompleted = Math.round(
              (progressEvent.loaded * 100) / progressEvent.total
            );
            set({ uploadProgress: percentCompleted });

            // After upload is complete, set progress to 99% to indicate processing
            if (percentCompleted === 100) {
              set({ uploadProgress: 99 });
            }
          },
        }
      );

      // Set the results and complete the progress
      set({
        processingResults: response.data,
        uploadProgress: 100,
        isUploading: false,
      });

      return response.data;
    } catch (error) {
      console.error("Error uploading audio:", error);

      set({
        error:
          error.response?.data?.error || "Failed to upload and process audio",
        isUploading: false,
      });

      throw error;
    }
  },

  resetState: () => {
    set({
      isUploading: false,
      uploadProgress: 0,
      processingResults: null,
      error: null,
    });
  },
}));
