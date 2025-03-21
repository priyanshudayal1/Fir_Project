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
} from "react-icons/fa";
import useFIRStore from "../../store/useFIRStore";

const InterviewForm = ({ language, questions, onComplete, onAnswer }) => {
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [isProcessing, setIsProcessing] = useState(false);
  const [recordedTime, setRecordedTime] = useState(0);
  const [welcomeAudioUrl, setWelcomeAudioUrl] = useState(null);
  const [isPlayingWelcome, setIsPlayingWelcome] = useState(false);
  const [hasPlayedWelcome, setHasPlayedWelcome] = useState(false);
  const [isPlaying, setIsPlaying] = useState(false);
  const [audioProgress, setAudioProgress] = useState(0);

  const recordingTimerRef = useRef(null);
  const questionAudioRef = useRef(null);
  const recordedAudioRef = useRef(null);
  const welcomeAudioRef = useRef(null);

  const {
    isRecording,
    setIsRecording,
    setAudioChunks,
    recordedAudio,
    setRecordedAudio,
    mediaRecorder,
    setMediaRecorder,
    error,
    setError,
    questionAudios,
    cacheQuestionAudio,
    isPlayingQuestion,
    setIsPlayingQuestion,
  } = useFIRStore();

  const currentQuestion = questions[currentQuestionIndex];

  // Welcome message content based on language
  // Replace the current welcomeMessages declaration with this:
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

  const playQuestionTTS = useCallback(async () => {
    try {
      // Don't try to play questions while welcome is playing
      if (isPlayingWelcome) return;

      setError(null);

      // Create new audio element if needed
      if (!questionAudioRef.current) {
        const audio = new Audio();
        audio.preload = "auto";
        questionAudioRef.current = audio;
      }

      // Clean up any existing audio playback
      questionAudioRef.current.pause();
      if (questionAudioRef.current.src) {
        URL.revokeObjectURL(questionAudioRef.current.src);
        questionAudioRef.current.src = "";
      }

      const questionText =
        typeof currentQuestion === "object"
          ? currentQuestion.question
          : currentQuestion;

      setIsPlayingQuestion(true);

      // Try cached audio first
      if (questionAudios[currentQuestionIndex]) {
        try {
          const audioBlob = questionAudios[currentQuestionIndex];
          const audioUrl = URL.createObjectURL(audioBlob);

          await new Promise((resolve, reject) => {
            let loadTimeout;

            const handleCanPlay = () => {
              clearTimeout(loadTimeout);
              cleanup();
              resolve();
            };

            const handleError = (e) => {
              clearTimeout(loadTimeout);
              cleanup();
              reject(new Error(`Failed to load cached audio: ${e.message}`));
            };

            const cleanup = () => {
              questionAudioRef.current.removeEventListener(
                "canplaythrough",
                handleCanPlay
              );
              questionAudioRef.current.removeEventListener(
                "error",
                handleError
              );
            };

            // Set timeout for loading
            loadTimeout = setTimeout(() => {
              cleanup();
              reject(new Error("Audio loading timed out"));
            }, 5000);

            questionAudioRef.current.addEventListener(
              "canplaythrough",
              handleCanPlay
            );
            questionAudioRef.current.addEventListener("error", handleError);

            questionAudioRef.current.src = audioUrl;
            questionAudioRef.current.load();
          });

          await questionAudioRef.current.play();

          questionAudioRef.current.onended = () => {
            URL.revokeObjectURL(audioUrl);
            setIsPlayingQuestion(false);
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
      cacheQuestionAudio(currentQuestionIndex, audioBlob);

      // Play the new audio
      const audioUrl = URL.createObjectURL(audioBlob);

      await new Promise((resolve, reject) => {
        let loadTimeout;

        const handleCanPlay = () => {
          clearTimeout(loadTimeout);
          cleanup();
          resolve();
        };

        const handleError = (e) => {
          clearTimeout(loadTimeout);
          cleanup();
          reject(new Error(`Failed to load generated audio: ${e.message}`));
        };

        const cleanup = () => {
          questionAudioRef.current.removeEventListener(
            "canplaythrough",
            handleCanPlay
          );
          questionAudioRef.current.removeEventListener("error", handleError);
        };

        // Set timeout for loading
        loadTimeout = setTimeout(() => {
          cleanup();
          reject(new Error("Audio loading timed out"));
        }, 5000);

        questionAudioRef.current.addEventListener(
          "canplaythrough",
          handleCanPlay
        );
        questionAudioRef.current.addEventListener("error", handleError);

        questionAudioRef.current.src = audioUrl;
        questionAudioRef.current.load();
      });

      await questionAudioRef.current.play();

      questionAudioRef.current.onended = () => {
        URL.revokeObjectURL(audioUrl);
        setIsPlayingQuestion(false);
      };
    } catch (error) {
      console.error("TTS Error:", error);
      setError("Failed to play audio. Please try again.");
      setIsPlayingQuestion(false);

      // Clean up any partial audio state
      if (questionAudioRef.current) {
        questionAudioRef.current.pause();
        if (questionAudioRef.current.src) {
          URL.revokeObjectURL(questionAudioRef.current.src);
          questionAudioRef.current.src = "";
        }
      }
    }
  }, [
    currentQuestion,
    language,
    currentQuestionIndex,
    questionAudios,
    cacheQuestionAudio,
    setError,
    setIsPlayingQuestion,
    isPlayingWelcome,
  ]);

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
          // Play the first question after welcome message ends
          setTimeout(() => {
            playQuestionTTS();
          }, 500);
        });

        welcomeAudioRef.current.addEventListener("error", (e) => {
          console.error("Welcome audio error:", e);
          setIsPlayingWelcome(false);
          setError("Failed to play welcome message");

          // Still try to play the question if welcome fails
          setTimeout(() => {
            playQuestionTTS();
          }, 500);
        });
      }

      // Play the welcome audio
      welcomeAudioRef.current.src = audioUrl;
      await welcomeAudioRef.current.play();
    } catch (error) {
      console.error("Error playing welcome message:", error);
      setIsPlayingWelcome(false);
      setError("Failed to play welcome message");

      // Still try to play the question if welcome fails
      setTimeout(() => {
        playQuestionTTS();
      }, 500);
    }
  }, [
    language,
    welcomeMessages,
    welcomeAudioUrl,
    setError,
    setIsPlayingWelcome,
    playQuestionTTS,
  ]);

  // Add recording timer
  useEffect(() => {
    if (isRecording) {
      recordingTimerRef.current = setInterval(() => {
        setRecordedTime((prev) => prev + 1);
      }, 1000);
    } else {
      clearInterval(recordingTimerRef.current);
    }
    return () => clearInterval(recordingTimerRef.current);
  }, [isRecording]);

  // Play welcome message when component mounts and language is available
  useEffect(() => {
    if (language && !hasPlayedWelcome) {
      playWelcomeMessage();
      setHasPlayedWelcome(true);
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

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, "0")}:${secs
      .toString()
      .padStart(2, "0")}`;
  };

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const recorder = new MediaRecorder(stream);
      const chunks = [];

      recorder.ondataavailable = (e) => {
        if (e.data.size > 0) {
          chunks.push(e.data);
        }
      };

      recorder.onstop = () => {
        const blob = new Blob(chunks, { type: "audio/webm" });
        setRecordedAudio(blob);
        setAudioChunks(chunks);

        // Clean up any existing audio URL before creating a new one
        if (recordedAudioRef.current?.src) {
          URL.revokeObjectURL(recordedAudioRef.current.src);
          recordedAudioRef.current.src = "";
        }

        // Create and set new audio URL with proper cleanup
        if (recordedAudioRef.current) {
          const audioUrl = URL.createObjectURL(blob);
          recordedAudioRef.current.src = audioUrl;

          // Clean up URL when audio ends or errors
          const cleanup = () => {
            if (recordedAudioRef.current) {
              URL.revokeObjectURL(audioUrl);
              recordedAudioRef.current.removeEventListener("ended", cleanup);
              recordedAudioRef.current.removeEventListener("error", cleanup);
            }
          };

          recordedAudioRef.current.addEventListener("ended", cleanup);
          recordedAudioRef.current.addEventListener("error", cleanup);
        }
      };

      setMediaRecorder(recorder);
      recorder.start();
      setIsRecording(true);
      setRecordedTime(0);
    } catch (error) {
      console.error("Error starting recording:", error);
      setError("Could not access microphone. Please check permissions.");
    }
  };

  const stopRecording = () => {
    if (mediaRecorder && mediaRecorder.state === "recording") {
      mediaRecorder.stop();
      setIsRecording(false);
      mediaRecorder.stream.getTracks().forEach((track) => track.stop());
    }
  };

  // Enhanced playRecordedAudio with play/pause toggle
  const playRecordedAudio = () => {
    if (!recordedAudio || !recordedAudioRef.current) return;

    if (isPlaying) {
      // If playing, pause it
      recordedAudioRef.current.pause();
      setIsPlaying(false);
      return;
    }

    // Reset the audio element if it's finished
    if (recordedAudioRef.current.ended) {
      recordedAudioRef.current.currentTime = 0;
    }

    // Create and set new audio URL if not already set
    if (!recordedAudioRef.current.src) {
      const audioUrl = URL.createObjectURL(recordedAudio);
      recordedAudioRef.current.src = audioUrl;

      // Add cleanup for the URL
      recordedAudioRef.current.onended = () => {
        URL.revokeObjectURL(audioUrl);
        setIsPlaying(false);
        setAudioProgress(0);
      };

      // Add progress tracking
      recordedAudioRef.current.ontimeupdate = () => {
        const progress =
          (recordedAudioRef.current.currentTime /
            recordedAudioRef.current.duration) *
          100;
        setAudioProgress(progress);
      };
    }

    // Play the audio
    recordedAudioRef.current
      .play()
      .then(() => {
        setIsPlaying(true);
      })
      .catch((error) => {
        console.error("Error playing recorded audio:", error);
        setError("Failed to play recorded audio");
        setIsPlaying(false);
      });
  };

  // Initialize audio elements in useEffect with proper cleanup and error handling
  useEffect(() => {
    const audio = new Audio();
    const recordedAudio = new Audio();

    const handleAudioError = (e) => {
      console.error("Audio error:", {
        error: e,
        currentSrc: e.target?.currentSrc,
        readyState: e.target?.readyState,
        networkState: e.target?.networkState,
      });
      setError("Error loading audio. Please try again.");
      setIsPlayingQuestion(false);
    };

    // Add error handling for audio elements
    audio.addEventListener("error", handleAudioError);
    recordedAudio.addEventListener("error", handleAudioError);

    // Set audio properties
    audio.preload = "auto";
    recordedAudio.preload = "auto";

    questionAudioRef.current = audio;
    recordedAudioRef.current = recordedAudio;

    return () => {
      // Remove event listeners
      audio.removeEventListener("error", handleAudioError);
      recordedAudio.removeEventListener("error", handleAudioError);

      // Cleanup audio elements
      if (questionAudioRef.current) {
        questionAudioRef.current.pause();
        questionAudioRef.current.src = "";
        URL.revokeObjectURL(questionAudioRef.current.src);
        questionAudioRef.current = null;
      }
      if (recordedAudioRef.current) {
        recordedAudioRef.current.pause();
        recordedAudioRef.current.src = "";
        URL.revokeObjectURL(recordedAudioRef.current.src);
        recordedAudioRef.current = null;
      }
    };
  }, [setError, setIsPlayingQuestion]);

  // Cleanup function for audio elements
  useEffect(() => {
    return () => {
      if (recordedAudioRef.current) {
        recordedAudioRef.current.pause();
        if (recordedAudioRef.current.src) {
          URL.revokeObjectURL(recordedAudioRef.current.src);
        }
        setIsPlaying(false);
        setAudioProgress(0);
      }
    };
  }, []);

  // Question TTS playback with caching

  // Play question when component mounts or question changes, but only after welcome message is done
  useEffect(() => {
    if (currentQuestion && !isPlayingWelcome && hasPlayedWelcome) {
      playQuestionTTS();
    }
  }, [currentQuestion, playQuestionTTS, isPlayingWelcome, hasPlayedWelcome]);

  const handleNextQuestion = async () => {
    if (!recordedAudio) return;

    try {
      setIsProcessing(true);
      setError(null);

      const transcribedText = await useInterviewStore
        .getState()
        .transcribeAudio(recordedAudio, language);

      onAnswer(currentQuestionIndex, transcribedText);

      // Handle follow-up questions if needed
      if (typeof currentQuestion === "object" && currentQuestion.followUp) {
        const isYes =
          transcribedText.toLowerCase().includes("yes") ||
          transcribedText.toLowerCase().includes("हाँ") ||
          transcribedText.toLowerCase().includes("ਹਾਂ");

        if (isYes && currentQuestion.followUp.yes) {
          setCurrentQuestionIndex((prev) => prev + 1);
        } else {
          const statement = Object.entries(
            useFIRStore.getState().interviewAnswers
          )
            .map(
              ([index, answer]) =>
                `Q: ${
                  questions[index].question || questions[index]
                }\nA: ${answer}`
            )
            .join("\n\n");
          await onComplete(statement);
        }
      } else if (currentQuestionIndex === questions.length - 1) {
        const statement = Object.entries(
          useFIRStore.getState().interviewAnswers
        )
          .map(
            ([index, answer]) =>
              `Q: ${
                questions[index].question || questions[index]
              }\nA: ${answer}`
          )
          .join("\n\n");
        await onComplete(statement);
      } else {
        setCurrentQuestionIndex((prev) => prev + 1);
      }

      setRecordedAudio(null);
      setAudioChunks([]);
    } catch (error) {
      console.error("Error processing answer:", error);
      setError("Failed to process your response. Please try again.");
    } finally {
      setIsProcessing(false);
      setRecordedTime(0);
    }
  };

  // Enhanced UI components
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

      {/* Question header with progress indicator */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-4">
            <h3 className="text-lg font-semibold text-gray-800">
              Question {currentQuestionIndex + 1} of {questions.length}
            </h3>
            <div className="h-2 w-32 bg-gray-200 rounded-full overflow-hidden">
              <motion.div
                className="h-full bg-blue-500"
                initial={{ width: 0 }}
                animate={{
                  width: `${
                    ((currentQuestionIndex + 1) / questions.length) * 100
                  }%`,
                }}
                transition={{ duration: 0.5 }}
              />
            </div>
          </div>
          {/* ...existing buttons... */}
        </div>

        {/* Question text with loading animation */}
        <div className="relative">
          <p className="text-gray-700 text-xl mb-2">
            {typeof currentQuestion === "object"
              ? currentQuestion.question
              : currentQuestion}
          </p>
          {isPlayingQuestion && (
            <motion.div
              className="absolute -left-6 top-1/2 transform -translate-y-1/2"
              animate={{ scale: [1, 1.2, 1] }}
              transition={{ duration: 1, repeat: Infinity }}
            >
              <div className="w-3 h-3 bg-blue-500 rounded-full" />
            </motion.div>
          )}
        </div>
      </div>

      {/* Recording interface */}
      <div className="flex flex-col items-center gap-6">
        {!isRecording && !recordedAudio ? (
          <motion.button
            className="relative w-24 h-24 rounded-full bg-gradient-to-r from-blue-500 to-blue-600 flex items-center justify-center text-white text-3xl shadow-lg"
            whileHover={{
              scale: 1.05,
              boxShadow: "0 8px 20px rgba(59, 130, 246, 0.3)",
            }}
            whileTap={{ scale: 0.95 }}
            onClick={startRecording}
            disabled={isPlayingQuestion || isPlayingWelcome}
          >
            <FaMicrophone />
            <motion.div
              className="absolute w-full h-full rounded-full border-4 border-blue-300"
              animate={{
                scale: [1, 1.2, 1],
                opacity: [0.3, 0, 0.3],
              }}
              transition={{ duration: 2, repeat: Infinity }}
            />
          </motion.button>
        ) : isRecording ? (
          <div className="flex flex-col items-center gap-6">
            <div className="relative">
              <motion.div
                className="w-32 h-32 rounded-full bg-red-100 flex items-center justify-center"
                animate={{
                  scale: [1, 1.05, 1],
                  boxShadow: [
                    "0 0 0 0 rgba(239, 68, 68, 0.2)",
                    "0 0 0 15px rgba(239, 68, 68, 0)",
                    "0 0 0 0 rgba(239, 68, 68, 0.2)",
                  ],
                }}
                transition={{
                  duration: 2,
                  repeat: Infinity,
                  ease: "easeInOut",
                }}
              >
                <div className="w-24 h-24 rounded-full bg-red-200 flex items-center justify-center">
                  <div className="text-2xl font-bold text-red-600">
                    {formatTime(recordedTime)}
                  </div>
                </div>
              </motion.div>
              <motion.div
                className="absolute inset-0 border-4 border-red-300 rounded-full"
                animate={{
                  scale: [1, 1.2, 1],
                  opacity: [0.7, 0, 0.7],
                }}
                transition={{
                  duration: 1.5,
                  repeat: Infinity,
                  ease: "easeInOut",
                }}
              />
              <motion.div
                className="absolute inset-0 border-2 border-red-300 rounded-full"
                animate={{
                  scale: [1.1, 1.3, 1.1],
                  opacity: [0.5, 0, 0.5],
                }}
                transition={{
                  duration: 2,
                  repeat: Infinity,
                  ease: "easeInOut",
                  delay: 0.5,
                }}
              />
            </div>
            <motion.button
              className="bg-red-500 hover:bg-red-600 text-white py-3 px-8 rounded-xl shadow-lg flex items-center gap-2"
              onClick={stopRecording}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              <FaStop />
              <span className="font-semibold">Stop Recording</span>
            </motion.button>
          </div>
        ) : (
          <div className="flex flex-col items-center gap-4 w-full max-w-md">
            <div className="w-full bg-gray-50 p-4 rounded-lg">
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  <motion.button
                    className="w-10 h-10 rounded-full bg-blue-500 flex items-center justify-center text-white"
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    onClick={playRecordedAudio}
                  >
                    {isPlaying ? <FaStop /> : <FaPlay />}
                  </motion.button>
                  <span className="text-sm text-gray-500">
                    {formatTime(recordedTime)}
                  </span>
                </div>
              </div>
              {/* Audio progress bar */}
              <div className="h-2 bg-gray-200 rounded-full overflow-hidden mb-4">
                <motion.div
                  className="h-full bg-blue-500"
                  initial={{ width: 0 }}
                  animate={{ width: `${audioProgress}%` }}
                  transition={{ duration: 0.1 }}
                />
              </div>
              {/* Audio waveform visualization */}
              <div className="h-12 bg-gray-100 rounded-lg overflow-hidden flex items-center justify-around px-2">
                {Array.from({ length: 40 }).map((_, i) => (
                  <motion.div
                    key={i}
                    className="w-1 bg-blue-500 rounded-full"
                    animate={{
                      height: isPlaying
                        ? [
                            `${20 + Math.sin(i * 0.5) * 20}%`,
                            `${20 + Math.cos(i * 0.5) * 20}%`,
                          ]
                        : "40%",
                    }}
                    transition={{
                      duration: 1,
                      repeat: Infinity,
                      repeatType: "reverse",
                      delay: i * 0.05,
                    }}
                  />
                ))}
              </div>
            </div>
            <motion.button
              className="w-full py-3 px-6 bg-gradient-to-r from-blue-500 to-blue-600 text-white rounded-lg shadow-md flex items-center justify-center gap-2"
              whileHover={{ scale: 1.02, y: -2 }}
              whileTap={{ scale: 0.98 }}
              onClick={handleNextQuestion}
              disabled={isProcessing}
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
                  <span>Processing...</span>
                </>
              ) : (
                <>
                  {currentQuestionIndex === questions.length - 1 ? (
                    "Complete Interview"
                  ) : (
                    <>
                      Next Question <FaArrowRight />
                    </>
                  )}
                </>
              )}
            </motion.button>
          </div>
        )}
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
