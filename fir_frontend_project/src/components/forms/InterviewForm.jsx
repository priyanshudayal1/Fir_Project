import { useInterviewStore } from "../../store/useInterview";
import React, {
  useState,
  useEffect,
  useRef,
  useCallback,
  useMemo,
} from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  FaMicrophone,
  FaStop,
  FaPlay,
  FaArrowRight,
  FaTimes,
  FaVolumeUp,
  FaCheck,
} from "react-icons/fa";
import useFIRStore from "../../store/useFIRStore";

const InterviewForm = ({ language, questions, onComplete, onAnswer }) => {
  const [welcomeAudioUrl, setWelcomeAudioUrl] = useState(null);
  const [isPlayingWelcome, setIsPlayingWelcome] = useState(false);
  const [hasPlayedWelcome, setHasPlayedWelcome] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  
  // New state for tracking recordings for each question
  const [questionRecordings, setQuestionRecordings] = useState({});
  const [activeQuestionIndex, setActiveQuestionIndex] = useState(null);
  const [recordedTimes, setRecordedTimes] = useState({});
  const [playingQuestionIndex, setPlayingQuestionIndex] = useState(null);
  const [audioProgress, setAudioProgress] = useState(0);
  
  const welcomeAudioRef = useRef(null);
  const recordingTimerRef = useRef(null);
  const audioRefs = useRef({});
  
  const {
    isRecording,
    setIsRecording,
    setAudioChunks,
    mediaRecorder,
    setMediaRecorder,
    error,
    setError,
    questionAudios,
    cacheQuestionAudio,
    isPlayingQuestion,
    setIsPlayingQuestion,
  } = useFIRStore();

  // Welcome message content based on language
  const welcomeMessages = useMemo(
    () => ({
      english:
        "I am AI police wala. I'll now ask you a series of questions about the incident. Please answer clearly and provide as much detail as possible to help us file your complaint accurately.",
      hindi:
        "मैं एआई पुलिस वाला हूँ। मैं अब आपसे घटना के बारे में कुछ प्रश्न पूछूंगा। कृपया स्पष्ट रूप से उत्तर दें और आपकी शिकायत सही ढंग से दर्ज करने में हमारी मदद के लिए जितना हो सके विवरण प्रदान करें।",
      punjabi:
        "ਮੈਂ ਏਆਈ ਪੁਲਿਸ ਵਾਲਾ ਹਾਂ। ਮੈਂ ਹੁਣ ਤੁਹਾਨੂੰ ਘਟਨਾ ਬਾਰੇ ਕੁਝ ਸਵਾਲ ਪੁੱਛਾਂਗਾ। ਕਿਰਪਾ ਕਰਕੇ ਸਪਸ਼ਟ ਤੌਰ 'ਤੇ ਜਵਾਬ ਦਿਓ ਅਤੇ ਤੁਹਾਡੀ ਸ਼ਿਕਾਇਤ ਨੂੰ ਸਹੀ ਢੰਗ ਨਾਲ ਦਰਜ ਕਰਨ ਵਿੱਚ ਸਾਡੀ ਮਦਦ ਲਈ ਜਿੰਨੀ ਹੋ ਸਕੇ ਵੇਰਵਾ ਪ੍ਰਦਾਨ ਕਰੋ।",
    }),
    []
  );

  // Function to play welcome message
  const playWelcomeMessage = useCallback(async () => {
    try {
      setError(null);

      if (!language || !welcomeMessages[language]) {
        return;
      }

      setIsPlayingWelcome(true);

      const audioBlob = await useInterviewStore
        .getState()
        .generateWelcomeSpeech(welcomeMessages[language], language);

      const audioUrl = URL.createObjectURL(audioBlob);

      // Clean up previous URL if exists
      if (welcomeAudioUrl) {
        URL.revokeObjectURL(welcomeAudioUrl);
      }

      setWelcomeAudioUrl(audioUrl);

      // Create and configure the welcome audio element if needed
      if (!welcomeAudioRef.current) {
        welcomeAudioRef.current = new Audio();
        welcomeAudioRef.current.preload = "auto";

        welcomeAudioRef.current.addEventListener("ended", () => {
          setIsPlayingWelcome(false);
          setHasPlayedWelcome(true);
        });

        welcomeAudioRef.current.addEventListener("error", (e) => {
          console.error("Welcome audio error:", e);
          setIsPlayingWelcome(false);
          // setError("Failed to play welcome message");
          setHasPlayedWelcome(true);
        });
      }

      // Play the welcome audio
      welcomeAudioRef.current.src = audioUrl;
      await welcomeAudioRef.current.play();
    } catch (error) {
      console.error("Error playing welcome message:", error);
      setIsPlayingWelcome(false);
      // setError("Failed to play welcome message");
      setHasPlayedWelcome(true);
    }
  }, [
    language,
    welcomeMessages,
    welcomeAudioUrl,
    setError,
    setIsPlayingWelcome,
  ]);

  // Play question TTS
  const playQuestionTTS = useCallback(async (questionIndex) => {
    try {
      if (isPlayingWelcome) return;

      setError(null);
      setPlayingQuestionIndex(questionIndex);
      setIsPlayingQuestion(true);

      const questionText = typeof questions[questionIndex] === "object"
        ? questions[questionIndex].question
        : questions[questionIndex];

      // Create audio element if it doesn't exist
      if (!audioRefs.current[questionIndex]) {
        audioRefs.current[questionIndex] = new Audio();
        audioRefs.current[questionIndex].preload = "auto";
      }

      const audioElement = audioRefs.current[questionIndex];
      
      // Clean up any existing audio
      audioElement.pause();
      if (audioElement.src) {
        URL.revokeObjectURL(audioElement.src);
        audioElement.src = "";
      }

      // Try to use cached audio first
      if (questionAudios[questionIndex]) {
        try {
          const audioBlob = questionAudios[questionIndex];
          const audioUrl = URL.createObjectURL(audioBlob);

          await new Promise((resolve, reject) => {
            const handleCanPlay = () => {
              cleanup();
              resolve();
            };

            const handleError = (e) => {
              cleanup();
              reject(new Error(`Failed to load cached audio: ${e.message}`));
            };

            const cleanup = () => {
              audioElement.removeEventListener("canplaythrough", handleCanPlay);
              audioElement.removeEventListener("error", handleError);
            };

            audioElement.addEventListener("canplaythrough", handleCanPlay);
            audioElement.addEventListener("error", handleError);

            audioElement.src = audioUrl;
            audioElement.load();
          });

          await audioElement.play();

          audioElement.onended = () => {
            URL.revokeObjectURL(audioUrl);
            setIsPlayingQuestion(false);
            setPlayingQuestionIndex(null);
          };

          return;
        } catch (playError) {
          console.error("Error playing cached audio:", playError);
          // Continue to generate new audio if cached playback fails
        }
      }

      // Generate new audio
      const audioBlob = await useInterviewStore
        .getState()
        .generateQuestionSpeech(questionText, language);

      // Cache the audio blob
      cacheQuestionAudio(questionIndex, audioBlob);

      // Play the new audio
      const audioUrl = URL.createObjectURL(audioBlob);

      await new Promise((resolve, reject) => {
        const handleCanPlay = () => {
          cleanup();
          resolve();
        };

        const handleError = (e) => {
          cleanup();
          reject(new Error(`Failed to load generated audio: ${e.message}`));
        };

        const cleanup = () => {
          audioElement.removeEventListener("canplaythrough", handleCanPlay);
          audioElement.removeEventListener("error", handleError);
        };

        audioElement.addEventListener("canplaythrough", handleCanPlay);
        audioElement.addEventListener("error", handleError);

        audioElement.src = audioUrl;
        audioElement.load();
      });

      await audioElement.play();

      audioElement.onended = () => {
        URL.revokeObjectURL(audioUrl);
        setIsPlayingQuestion(false);
        setPlayingQuestionIndex(null);
      };
    } catch (error) {
      console.error("TTS Error:", error);
      setIsPlayingQuestion(false);
      setPlayingQuestionIndex(null);

      // Clean up any partial audio state
      if (audioRefs.current[questionIndex]) {
        audioRefs.current[questionIndex].pause();
        if (audioRefs.current[questionIndex].src) {
          URL.revokeObjectURL(audioRefs.current[questionIndex].src);
          audioRefs.current[questionIndex].src = "";
        }
      }
    }
  }, [questions, language, questionAudios, cacheQuestionAudio, setError, setIsPlayingQuestion, isPlayingWelcome]);

  // Play welcome message when component mounts and language is available
  useEffect(() => {
    if (language && !hasPlayedWelcome) {
      playWelcomeMessage();
    }
  }, [language, hasPlayedWelcome, playWelcomeMessage]);

  // Clean up welcome audio URL when component unmounts
  useEffect(() => {
    return () => {
      if (welcomeAudioUrl) {
        URL.revokeObjectURL(welcomeAudioUrl);
      }
    };
  }, [welcomeAudioUrl]);

  // Add recording timer for active question
  useEffect(() => {
    if (isRecording && activeQuestionIndex !== null) {
      recordingTimerRef.current = setInterval(() => {
        setRecordedTimes(prev => ({
          ...prev,
          [activeQuestionIndex]: (prev[activeQuestionIndex] || 0) + 1
        }));
      }, 1000);
    } else {
      clearInterval(recordingTimerRef.current);
    }
    return () => clearInterval(recordingTimerRef.current);
  }, [isRecording, activeQuestionIndex]);

  // Format time helper
  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, "0")}:${secs
      .toString()
      .padStart(2, "0")}`;
  };

  // Start recording for a specific question
  const startRecording = async (questionIndex) => {
    try {
      // Stop any ongoing recording
      if (isRecording) {
        stopRecording();
      }

      // Request microphone access with better error handling
      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: { 
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true
        } 
      });
      
      // Set up media recorder with higher bitrate for better quality
      const options = { mimeType: 'audio/webm;codecs=opus', audioBitsPerSecond: 128000 };
      
      // Check for browser support of the specified mimetype
      if (!MediaRecorder.isTypeSupported(options.mimeType)) {
        console.warn(`${options.mimeType} is not supported, using default codec`);
        // Fall back to default
        const recorder = new MediaRecorder(stream);
        initializeRecorder(recorder, stream, questionIndex);
      } else {
        const recorder = new MediaRecorder(stream, options);
        initializeRecorder(recorder, stream, questionIndex);
      }
    } catch (error) {
      console.error("Error starting recording:", error);
      setError(`Could not access microphone: ${error.message}`);
    }
  };

  // Helper function to initialize recorder
  const initializeRecorder = (recorder, stream, questionIndex) => {
    const chunks = [];
    
    // Set up data available handler
    recorder.ondataavailable = (e) => {
      if (e.data && e.data.size > 0) {
        chunks.push(e.data);
        console.log(`Received audio chunk: ${e.data.size} bytes`);
      } else {
        console.warn("Empty audio chunk received");
      }
    };

    // Set up stop handler with validation
    recorder.onstop = () => {
      if (chunks.length === 0) {
        console.error("No audio chunks collected");
        setError("No audio data was recorded. Please try again.");
        return;
      }
      
      // Log total size of all chunks
      const totalBytes = chunks.reduce((sum, chunk) => sum + chunk.size, 0);
      console.log(`Total audio data: ${totalBytes} bytes in ${chunks.length} chunks`);
      
      if (totalBytes === 0) {
        setError("Recording was empty. Please try speaking louder or check your microphone.");
        return;
      }
      
      // Create blob with explicit type
      const blob = new Blob(chunks, { type: 'audio/webm' });
      console.log(`Created audio blob: ${blob.size} bytes, type: ${blob.type}`);
      
      if (blob.size < 100) {
        console.warn("Audio blob is suspiciously small");
        setError("Recording appears to be too small. Please try again and speak clearly.");
        return;
      }
      
      // Store the recording for this question
      setQuestionRecordings(prev => ({
        ...prev,
        [questionIndex]: blob
      }));
      
      setAudioChunks(chunks);

      // Create and set up audio element for playback
      if (!audioRefs.current[`recording_${questionIndex}`]) {
        audioRefs.current[`recording_${questionIndex}`] = new Audio();
      }
      
      const audioElement = audioRefs.current[`recording_${questionIndex}`];
      
      // Clean up any existing audio URL
      if (audioElement.src) {
        URL.revokeObjectURL(audioElement.src);
      }
      
      const audioUrl = URL.createObjectURL(blob);
      audioElement.src = audioUrl;
      
      // Test playability of the blob
      audioElement.addEventListener('canplaythrough', () => {
        console.log(`Audio for question ${questionIndex} is playable`);
      }, { once: true });
      
      audioElement.addEventListener('error', (e) => {
        console.error(`Error loading audio for question ${questionIndex}:`, e);
      }, { once: true });
      
      // Set up event listeners for playback tracking
      audioElement.addEventListener("ended", () => {
        setPlayingQuestionIndex(null);
        setAudioProgress(0);
      });
      
      audioElement.addEventListener("timeupdate", () => {
        const progress = (audioElement.currentTime / audioElement.duration) * 100;
        setAudioProgress(progress);
      });
    };

    // Handle recording errors
    recorder.onerror = (event) => {
      console.error("Recorder error:", event);
      setError(`Recording error: ${event.name}`);
      
      // Clean up stream on error
      if (stream) {
        stream.getTracks().forEach(track => track.stop());
      }
    };

    // Configure for frequent data events on longer recordings
    try {
      // Request data every second instead of waiting until stop
      recorder.start(1000);
      console.log(`Started recording for question ${questionIndex}`);
      
      setMediaRecorder(recorder);
      setIsRecording(true);
      setActiveQuestionIndex(questionIndex);
      
      // Initialize the recorded time for this question
      setRecordedTimes(prev => ({
        ...prev,
        [questionIndex]: 0
      }));
    } catch (error) {
      console.error("Error starting recorder:", error);
      setError(`Could not start recording: ${error.message}`);
      
      // Clean up stream if recorder fails to start
      if (stream) {
        stream.getTracks().forEach(track => track.stop());
      }
    }
  };

  // Stop the current recording
  const stopRecording = () => {
    if (mediaRecorder && mediaRecorder.state === "recording") {
      mediaRecorder.stop();
      setIsRecording(false);
      setActiveQuestionIndex(null);
      mediaRecorder.stream.getTracks().forEach((track) => track.stop());
    }
  };

  // Play recording for a specific question
  const playRecording = (questionIndex) => {
    if (!questionRecordings[questionIndex]) return;
    
    const audioKey = `recording_${questionIndex}`;
    
    // If already playing this recording, stop it
    if (playingQuestionIndex === questionIndex) {
      audioRefs.current[audioKey].pause();
      setPlayingQuestionIndex(null);
      return;
    }
    
    // Stop any currently playing audio
    if (playingQuestionIndex !== null) {
      const currentAudioKey = `recording_${playingQuestionIndex}`;
      if (audioRefs.current[currentAudioKey]) {
        audioRefs.current[currentAudioKey].pause();
      }
    }
    
    // Play the selected recording
    const audioElement = audioRefs.current[audioKey];
    if (audioElement) {
      // Reset if ended
      if (audioElement.ended) {
        audioElement.currentTime = 0;
      }
      
      audioElement.play()
        .then(() => {
          setPlayingQuestionIndex(questionIndex);
        })
        .catch((error) => {
          console.error("Error playing recorded audio:", error);
          setError("Failed to play recorded audio");
        });
    }
  };

  // Handle form completion - process recordings sequentially instead of in parallel
  const handleCompleteInterview = async () => {
    // Check if we have recordings for all questions
    const missingRecordings = questions.filter((_, index) => !questionRecordings[index]);
    
    if (missingRecordings.length > 0) {
      setError(`Please record answers for all ${questions.length} questions before completing the interview.`);
      return;
    }
    
    try {
      setIsProcessing(true);
      setError(null);
      
      // Validate all recordings before processing
      const invalidRecordings = Object.entries(questionRecordings).filter(
        ([_, blob]) => !blob || blob.size < 1000 // Increase minimum size check
      );
      
      if (invalidRecordings.length > 0) {
        const invalidQuestions = invalidRecordings.map(([index]) => Number(index) + 1).join(', ');
        setError(`Empty or too small recordings detected for questions: ${invalidQuestions}. Please re-record these answers.`);
        setIsProcessing(false);
        return;
      }
      
      console.log("Processing recordings:", Object.entries(questionRecordings).map(
        ([index, blob]) => `Q${Number(index) + 1}: ${blob.size} bytes, type: ${blob.type}`
      ));
      
      // Process recordings one at a time instead of in parallel
      const transcriptionResults = [];
      
      // Set up sequential processing with progress updates
      for (let index = 0; index < questions.length; index++) {
        try {
          // Update processing message to show current question
          setError(`Processing question ${index + 1} of ${questions.length}...`);
          
          const blob = questionRecordings[index];
          
          // Double-check validity
          if (!blob || blob.size < 1000) {
            console.error(`Recording for question ${index + 1} is empty or too small (${blob?.size || 0} bytes)`);
            transcriptionResults[index] = `[Error: Recording was too short or empty]`;
            continue;
          }
          
          // Convert webm to mp3 if needed (some servers handle mp3 better than webm)
          const processedBlob = blob;
          
          // Make individual request with retries
          let retryCount = 0;
          let transcription = null;
          
          while (retryCount < 2 && !transcription) {
            try {
              transcription = await useInterviewStore.getState().transcribeAudio(processedBlob, language);
              
              if (!transcription || transcription.trim() === '') {
                throw new Error("Empty transcription result");
              }
              
              console.log(`Transcription for question ${index + 1} successful:`, transcription.substring(0, 50) + '...');
            } catch (transcriptionError) {
              retryCount++;
              console.error(`Transcription attempt ${retryCount} failed for question ${index + 1}:`, transcriptionError);
              
              if (retryCount >= 2) {
                transcription = `[Error: Failed to transcribe after ${retryCount} attempts]`;
              } else {
                // Short delay before retry
                await new Promise(resolve => setTimeout(resolve, 1000));
              }
            }
          }
          
          transcriptionResults[index] = transcription;
          
          // Store each answer as we go
          onAnswer(index, transcription);
          
          // Short delay between requests to avoid overwhelming the server
          if (index < questions.length - 1) {
            await new Promise(resolve => setTimeout(resolve, 500));
          }
        } catch (questionError) {
          console.error(`Processing error for question ${index + 1}:`, questionError);
          transcriptionResults[index] = `[Error: ${questionError.message || "Unknown error"}]`;
          
          // Continue with next question despite errors
          continue;
        }
      }
      
      // Construct the final statement
      const statement = questions.map((question, index) => {
        const questionText = typeof question === "object" ? question.question : question;
        return `Q: ${questionText}\nA: ${transcriptionResults[index] || "[No transcription available]"}`;
      }).join("\n\n");
      
      // Clear any processing error messages
      setError(null);
      
      // Complete the interview
      await onComplete(statement);
      
    } catch (error) {
      console.error("Error processing answers:", error);
      setError(`Failed to process your responses: ${error.message || "Unknown error"}. Please try again.`);
    } finally {
      setIsProcessing(false);
    }
  };

  // Clean up all audio resources on unmount
  useEffect(() => {
    return () => {
      // Clean up all audio elements
      Object.values(audioRefs.current).forEach(audio => {
        if (audio) {
          audio.pause();
          if (audio.src) {
            URL.revokeObjectURL(audio.src);
          }
        }
      });
      
      // Clean up welcome audio
      if (welcomeAudioRef.current) {
        welcomeAudioRef.current.pause();
        if (welcomeAudioRef.current.src) {
          URL.revokeObjectURL(welcomeAudioRef.current.src);
        }
      }
    };
  }, []);

  // UI for the interview form
  return (
    <motion.div
      className="p-6 bg-white rounded-lg shadow-sm"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
    >
      {/* Welcome message indicator */}
      <AnimatePresence>
        {isPlayingWelcome && (
          <motion.div
            className="mb-4 p-3 bg-blue-50 border border-blue-200 rounded-lg flex items-center gap-3"
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
          >
            <div className="flex flex-shrink-0 items-center justify-center w-10 h-10 bg-blue-100 rounded-full">
              <FaVolumeUp className="text-blue-500" />
            </div>
            <div className="flex-grow">
              <p className="text-blue-700 font-medium">Welcome Message</p>
              <div className="flex mt-1 space-x-1">
                <div
                  className="w-2 h-2 bg-blue-500 rounded-full animate-bounce"
                  style={{ animationDelay: "0ms" }}
                ></div>
                <div
                  className="w-2 h-2 bg-blue-500 rounded-full animate-bounce"
                  style={{ animationDelay: "150ms" }}
                ></div>
                <div
                  className="w-2 h-2 bg-blue-500 rounded-full animate-bounce"
                  style={{ animationDelay: "300ms" }}
                ></div>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Questions List */}
      <div className="mb-6">
        <h3 className="text-lg font-semibold text-gray-800 mb-4">
          Please answer all {questions.length} questions to complete your interview
        </h3>
        
        <div className="space-y-6">
          {questions.map((question, index) => {
            const questionText = typeof question === "object" ? question.question : question;
            const hasRecording = !!questionRecordings[index];
            const isActiveQuestion = activeQuestionIndex === index;
            const isPlayingRecording = playingQuestionIndex === index;
            
            return (
              <motion.div 
                key={index}
                className={`p-4 rounded-lg border ${hasRecording ? 'border-green-200 bg-green-50' : 'border-gray-200'}`}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
              >
                <div className="flex items-start gap-4">
                  <div className="flex-shrink-0 w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center text-blue-500 font-semibold mt-1">
                    {index + 1}
                  </div>
                  
                  <div className="flex-grow">
                    <div className="flex justify-between items-start mb-2">
                      <h4 className="text-gray-700 font-medium">{questionText}</h4>
                      
                      <motion.button
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                        onClick={() => playQuestionTTS(index)}
                        disabled={isPlayingQuestion || isPlayingWelcome}
                        className="ml-2 text-blue-500 hover:text-blue-600"
                      >
                        <FaVolumeUp />
                      </motion.button>
                    </div>
                    
                    {/* Recording controls */}
                    <div className="mt-3">
                      {!isRecording && !hasRecording ? (
                        <motion.button
                          className="flex items-center gap-2 px-4 py-2 bg-blue-500 text-white rounded-lg"
                          whileHover={{ scale: 1.05 }}
                          whileTap={{ scale: 0.95 }}
                          onClick={() => startRecording(index)}
                          disabled={isPlayingQuestion || isRecording}
                        >
                          <FaMicrophone />
                          <span>Record Answer</span>
                        </motion.button>
                      ) : isActiveQuestion ? (
                        <div className="flex items-center gap-3">
                          <div className="flex items-center gap-2 px-4 py-2 bg-red-100 text-red-600 rounded-lg">
                            <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse" />
                            <span>{formatTime(recordedTimes[index] || 0)}</span>
                          </div>
                          
                          <motion.button
                            className="flex items-center gap-2 px-4 py-2 bg-red-500 text-white rounded-lg"
                            whileHover={{ scale: 1.05 }}
                            whileTap={{ scale: 0.95 }}
                            onClick={stopRecording}
                          >
                            <FaStop />
                            <span>Stop</span>
                          </motion.button>
                        </div>
                      ) : hasRecording ? (
                        <div className="flex items-center gap-3">
                          <div className="flex items-center gap-2">
                            <motion.button
                              className="flex items-center gap-2 px-4 py-2 bg-blue-500 text-white rounded-lg"
                              whileHover={{ scale: 1.05 }}
                              whileTap={{ scale: 0.95 }}
                              onClick={() => playRecording(index)}
                            >
                              {isPlayingRecording ? <FaStop /> : <FaPlay />}
                              <span>{isPlayingRecording ? "Stop" : "Play"}</span>
                            </motion.button>
                            
                            <span className="text-sm text-gray-500 ml-2">
                              {formatTime(recordedTimes[index] || 0)}
                            </span>
                            
                            <FaCheck className="text-green-500 ml-2" />
                          </div>
                          
                          <motion.button
                            className="flex items-center gap-2 px-3 py-1 border border-blue-300 text-blue-600 rounded-lg"
                            whileHover={{ scale: 1.05 }}
                            whileTap={{ scale: 0.95 }}
                            onClick={() => startRecording(index)}
                            disabled={isPlayingQuestion || isRecording}
                          >
                            <FaMicrophone />
                            <span>Re-record</span>
                          </motion.button>
                        </div>
                      ) : (
                        <div className="text-gray-400 italic">
                          Waiting for recording...
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              </motion.div>
            );
          })}
        </div>
      </div>

      {/* Complete Interview button */}
      <div className="flex justify-center mt-8">
        <motion.button
          className="py-3 px-8 bg-gradient-to-r from-blue-500 to-blue-600 text-white rounded-lg shadow-md flex items-center justify-center gap-2 w-full max-w-md"
          whileHover={{ scale: 1.02, y: -2 }}
          whileTap={{ scale: 0.98 }}
          onClick={handleCompleteInterview}
          disabled={isProcessing || isRecording || Object.keys(questionRecordings).length !== questions.length}
        >
          {isProcessing ? (
            <>
              <motion.div
                className="w-5 h-5 border-3 border-white border-t-transparent rounded-full"
                animate={{ rotate: 360 }}
                transition={{
                  duration: 1,
                  repeat: Infinity,
                  ease: "linear",
                }}
              />
              <span>Processing All Responses...</span>
            </>
          ) : (
            <>
              {Object.keys(questionRecordings).length === questions.length ? (
                "Complete Interview"
              ) : (
                `Record All ${questions.length} Answers to Continue (${Object.keys(questionRecordings).length}/${questions.length})`
              )}
            </>
          )}
        </motion.button>
      </div>

      {/* Error display */}
      <AnimatePresence>
        {error && (
          <motion.div
            className="mt-4 p-4 bg-red-50 border-l-4 border-red-500 text-red-700 rounded-r-lg"
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: 20 }}
          >
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 bg-red-500 rounded-full" />
              <p>{error}</p>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
};

export default InterviewForm;
