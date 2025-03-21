import { create } from "zustand";
import axios from "axios";

const useFIRStore = create((set, get) => ({
  // State
  isLoading: false,
  error: null,
  audioFile: null,
  isRecording: false,
  recordingTime: 0,
  mediaRecorder: null,
  audioChunks: [],
  recordedAudio: null,
  recordingIntervalId: null,
  mediaStream: null,
  transcribedText: "",
  sentiment: null,
  crimePredictions: [],
  legalSections: [],
  firDraft: "",
  selectedLanguage: null,
  interviewAnswers: {},
  interviewComplete: false,
  questionAudios: {},
  isPlayingQuestion: false,
  previousAnswers: {},
  showPreviousAnswers: false,
  answerAudios: {},

  // Actions
  setError: (error) => set({ error }),
  setIsRecording: (isRecording) => set({ isRecording }),
  setAudioChunks: (chunks) => set({ audioChunks: chunks }),
  setRecordedAudio: (audio) => set({ recordedAudio: audio }),
  setMediaRecorder: (recorder) => {
    const prevState = get();
    if (prevState.mediaRecorder) {
      try {
        // Clean up old recorder
        if (prevState.mediaRecorder.state === "recording") {
          prevState.mediaRecorder.stop();
        }
        prevState.mediaRecorder.stream
          .getTracks()
          .forEach((track) => track.stop());
      } catch (e) {
        console.error("Error cleaning up old recorder:", e);
      }
    }
    set({ mediaRecorder: recorder });
  },

  startRecording: async () => {
    try {
      // Clean up any existing recording session
      const state = get();
      if (state.mediaRecorder) {
        if (state.mediaRecorder.state === "recording") {
          state.mediaRecorder.stop();
        }
        state.mediaRecorder.stream.getTracks().forEach((track) => track.stop());
      }

      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const recorder = new MediaRecorder(stream);
      const chunks = [];

      recorder.ondataavailable = (e) => {
        if (e.data.size > 0) {
          chunks.push(e.data);
        }
      };

      recorder.onstop = () => {
        // Ensure all chunks are collected
        if (recorder.state === "inactive") {
          const blob = new Blob(chunks, { type: "audio/webm" });
          const audioUrl = URL.createObjectURL(blob);
          set({
            recordedAudio: audioUrl,
            audioChunks: chunks,
            isRecording: false,
          });
        }
      };

      set({
        mediaRecorder: recorder,
        audioChunks: [],
        recordedAudio: null,
      });

      recorder.start();
      set({ isRecording: true });
    } catch (error) {
      console.error("Error starting recording:", error);
      set({ error: "Could not access microphone. Please check permissions." });
    }
  },

  stopRecording: () => {
    const state = get();
    if (state.mediaRecorder && state.mediaRecorder.state === "recording") {
      try {
        state.mediaRecorder.stop();
        state.mediaRecorder.stream.getTracks().forEach((track) => track.stop());
        set({ isRecording: false });
      } catch (error) {
        console.error("Error stopping recording:", error);
        set({
          error: "Failed to stop recording properly",
          isRecording: false,
        });
      }
    }
  },

  deleteRecording: () => {
    const state = get();
    // Clean up media resources
    if (state.mediaRecorder) {
      try {
        if (state.mediaRecorder.state === "recording") {
          state.mediaRecorder.stop();
        }
        state.mediaRecorder.stream.getTracks().forEach((track) => track.stop());
      } catch (e) {
        console.error("Error cleaning up recorder:", e);
      }
    }
    // Clean up audio URL if it exists
    if (state.recordedAudio) {
      try {
        URL.revokeObjectURL(state.recordedAudio);
      } catch (e) {
        console.error("Error revoking audio URL:", e);
      }
    }
    set({
      mediaRecorder: null,
      audioChunks: [],
      recordedAudio: null,
      isRecording: false,
      recordingTime: 0,
    });
  },

  setHasKnownAccused: (value) => set({ hasKnownAccused: value }),
  setPreviousAnswers: (answers) => set({ previousAnswers: answers }),
  setShowPreviousAnswers: (show) => set({ showPreviousAnswers: show }),
  setAnswerAudios: (audios) => set({ answerAudios: audios }),
  setIsPlayingQuestion: (isPlaying) => set({ isPlayingQuestion: isPlaying }),
  setSelectedLanguage: (language) => set({ selectedLanguage: language }),

  updateInterviewAnswer: (questionIndex, answer) =>
    set((state) => ({
      interviewAnswers: {
        ...state.interviewAnswers,
        [questionIndex]: answer,
      },
    })),

  setInterviewComplete: (complete) => set({ interviewComplete: complete }),

  processCompleteInterview: async (fullStatement) => {
    const state = get();

    try {
      set({ isLoading: true, error: null });

      // Create a blob from the full statement text and create a File object
      const textBlob = new Blob([fullStatement], { type: "text/plain" });
      const audioFile = new File([textBlob], "interview_transcript.txt", {
        type: "text/plain",
      });

      const formData = new FormData();
      formData.append("file", audioFile);
      formData.append("language", state.selectedLanguage || "english");

      const response = await axios.post(
        "http://localhost:5000/upload_audio",
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        }
      );

      const data = response.data;

      // Extract victim info from answers
      const nameAnswer = state.interviewAnswers[0] || "";
      const fatherAnswer = state.interviewAnswers[1] || "";
      const dobAnswer = state.interviewAnswers[2] || "";

      // Set the interview responses and generate FIR
      set({
        transcribedText: fullStatement,
        sentiment: data.sentiment,
        crimePredictions: data.crime_predictions,
        legalSections: data.legal_sections,
        firDraft: data.fir_draft,
        victimInfo: {
          name: nameAnswer,
          fatherOrHusbandName: fatherAnswer,
          dob: dobAnswer.split(" ")[0] || "",
          nationality: dobAnswer.split(" ").slice(1).join(" ") || "",
          occupation: "",
          address: "",
        },
        isLoading: false,
      });

      return data;
    } catch (error) {
      set({
        error: error.response?.data?.error || "Failed to process interview",
        isLoading: false,
      });
      console.error("Error processing interview:", error);
      return null;
    }
  },

  // API Call to backend for initial processing
  processAudioFile: async () => {
    const state = useFIRStore.getState();
    const { audioFile, selectedLanguage } = state;

    if (!audioFile) {
      set({ error: "Please select an audio file first" });
      return null;
    }

    try {
      set({ isLoading: true, error: null });

      const formData = new FormData();
      formData.append("file", audioFile);
      formData.append("language", selectedLanguage || "english");

      const response = await axios.post(
        "http://localhost:5000/upload_audio",
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        }
      );

      const data = response.data;

      // Extract victim name and incident details from transcribed text
      const nameMatch = data.transcribed_text.match(/My name is ([^.]+)/i);
      const victimName = nameMatch ? nameMatch[1].trim() : "";

      set({
        transcribedText: data.transcribed_text,
        sentiment: data.sentiment,
        crimePredictions: data.crime_predictions,
        legalSections: data.legal_sections,
        firDraft: data.fir_draft,
        isLoading: false,
        victimInfo: {
          ...state.victimInfo,
          name: victimName,
        },
        incidentDetails: {
          date: data.incident_date || "",
          time: data.incident_time || "",
          location: data.incident_location || "",
        },
      });

      return data;
    } catch (error) {
      set({
        error: error.response?.data?.error || "Failed to process audio file",
        isLoading: false,
      });
      console.error("Error processing audio:", error);
      return null;
    }
  },

  // New function to update FIR with additional information
  updateFIRWithDetails: async () => {
    const state = useFIRStore.getState();
    const { transcribedText, victimInfo, incidentDetails } = state;

    if (!transcribedText) {
      set({
        error: "No transcribed text available. Please upload audio first.",
      });
      return;
    }

    try {
      set({ isLoading: true, error: null });

      // Prepare data to send to backend
      const requestData = {
        transcribed_text: transcribedText,
        victim_name: victimInfo.name,
        father_or_husband_name: victimInfo.fatherOrHusbandName,
        dob: victimInfo.dob,
        nationality: victimInfo.nationality,
        occupation: victimInfo.occupation,
        address: victimInfo.address,
        incident_date: incidentDetails.date,
        incident_time: incidentDetails.time,
        incident_location: incidentDetails.location,
      };

      // Send request to a hypothetical endpoint for updating FIR
      // Note: Backend would need to implement this endpoint
      const response = await axios.post(
        "http://localhost:5000/update_fir",
        requestData
      );

      const data = response.data;

      set({
        firDraft: data.fir_draft,
        isLoading: false,
      });

      return data;
    } catch (error) {
      set({
        error: error.response?.data?.error || "Failed to update FIR details",
        isLoading: false,
      });
      console.error("Error updating FIR:", error);
      return null;
    }
  },

  resetForm: () =>
    set({
      audioFile: null,
      transcribedText: "",
      sentiment: null,
      crimePredictions: [],
      legalSections: [],
      firDraft: "",
      victimInfo: {
        name: "",
        fatherOrHusbandName: "",
        dob: "",
        nationality: "",
        occupation: "",
        address: "",
      },
      incidentDetails: {
        date: "",
        time: "",
        location: "",
      },
      interviewAnswers: {},
      questionAudios: {},
    }),

  cacheQuestionAudio: (index, audioBlob) =>
    set((state) => ({
      questionAudios: {
        ...state.questionAudios,
        [index]: audioBlob,
      },
    })),
}));

export default useFIRStore;
