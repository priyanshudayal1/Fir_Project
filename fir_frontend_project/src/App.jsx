import React from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Toaster } from "react-hot-toast";
import Header from "./components/layout/Header";
import AudioUploader from "./components/forms/AudioUploader";
import TranscriptDisplay from "./components/ui/TranscriptDisplay";
import CrimePredictions from "./components/ui/CrimePredictions";
import LegalSections from "./components/ui/LegalSections";
import TechyLoader from "./components/ui/TechyLoader";
import useFIRStore from "./store/useFIRStore";
import InterviewForm from "./components/forms/InterviewForm";
import SingleAudioUploader from "./components/forms/SingleAudioUploader";
import FIRDraftDisplay from "./components/ui/FIRDraftDisplay";

const INTERVIEW_QUESTIONS = {
  english: [
    "Can you tell me your full name, please?",
    "Could you also share your father's or husband's name?",
    "What is your date of birth and nationality?",
    "Can you please tell me about the incident? Start from the beginning and include important details like the date, time, what exactly happened, and where it took place.",
    {
      question: "Do you know who committed the crime?",
      followUp: {
        yes: [
          "Please share any details about their appearance or behavior.",
          "Were the accused wearing anything identifiable or distinct?",
          "Do you know the name or any information that can help identify the accused?",
        ],
      },
    },
  ],
  hindi: [
    "कृपया अपना पूरा नाम बताएं?",
    "क्या आप अपने पिता या पति का नाम भी बता सकते हैं?",
    "आपकी जन्मतिथि और राष्ट्रीयता क्या है?",
    "कृपया मुझे घटना के बारे में बताएं? शुरुआत से बताएं और महत्वपूर्ण विवरण जैसे तारीख, समय, क्या हुआ और कहाँ हुआ, शामिल करें।",
    {
      question: "क्या आप जानते हैं कि अपराध किसने किया?",
      followUp: {
        yes: [
          "कृपया उनकी दिखावट या व्यवहार के बारे में कोई जानकारी साझा करें।",
          "क्या आरोपी कुछ पहचान योग्य या विशिष्ट पहने हुए थे?",
          "क्या आप नाम या कोई ऐसी जानकारी जानते हैं जो आरोपी की पहचान में मदद कर सके?",
        ],
      },
    },
  ],
  punjabi: [
    "ਕਿਰਪਾ ਕਰਕੇ ਆਪਣਾ ਪੂਰਾ ਨਾਮ ਦੱਸੋ?",
    "ਕੀ ਤੁਸੀਂ ਆਪਣੇ ਪਿਤਾ ਜਾਂ ਪਤੀ ਦਾ ਨਾਮ ਵੀ ਦੱਸ ਸਕਦੇ ਹੋ?",
    "ਤੁਹਾਡੀ ਜਨਮ ਮਿਤੀ ਅਤੇ ਰਾਸ਼ਟਰੀਅਤਾ ਕੀ ਹੈ?",
    "ਕਿਰਪਾ ਕਰਕੇ ਮੈਨੂੰ ਘਟਨਾ ਬਾਰੇ ਦੱਸੋ? ਸ਼ੁਰੂ ਤੋਂ ਦੱਸੋ ਅਤੇ ਮਹੱਤਵਪੂਰਨ ਵੇਰਵੇ ਜਿਵੇਂ ਤਾਰੀਖ, ਸਮਾਂ, ਕੀ ਹੋਇਆ ਅਤੇ ਕਿੱਥੇ ਹੋਇਆ, ਸ਼ਾਮਲ ਕਰੋ।",
    {
      question: "ਕੀ ਤੁਸੀਂ ਜਾਣਦੇ ਹੋ ਕਿ ਅਪਰਾਧ ਕਿਸਨੇ ਕੀਤਾ?",
      followUp: {
        yes: [
          "ਕਿਰਪਾ ਕਰਕੇ ਉਹਨਾਂ ਦੀ ਦਿੱਖ ਜਾਂ ਵਿਵਹਾਰ ਬਾਰੇ ਕੋਈ ਜਾਣਕਾਰੀ ਸਾਂਝੀ ਕਰੋ।",
          "ਕੀ ਦੋਸ਼ੀ ਕੁਝ ਪਛਾਣਨਯੋਗ ਜਾਂ ਵਿਸ਼ੇਸ਼ ਪਹਿਨੇ ਹੋਏ ਸਨ?",
          "ਕੀ ਤੁਸੀ ਨਾਮ ਜਾਂ ਕੋਈ ਅਜਿਹੀ ਜਾਣਕਾਰੀ ਜਾਣਦੇ ਹੋ ਜੋ ਦੋਸ਼ੀ ਦੀ ਪਛਾਣ ਵਿੱਚ ਮਦਦ ਕਰ ਸਕਦੀ ਹੈ?",
        ],
      },
    },
  ],
};

const App = () => {
  const {
    isLoading,
    selectedLanguage,
    setSelectedLanguage,
    interviewComplete,
    setInterviewComplete,
    updateInterviewAnswer,
    resetForm,
    processCompleteInterview,
    firDraft,
    transcribedText,
  } = useFIRStore();

  // Add state for option selection
  const [selectedOption, setSelectedOption] = React.useState(null); // "interview" or "upload"
  // State for FIR editing
  const [firFields, setFirFields] = React.useState({});

  const handleLanguageSelect = (language) => {
    setSelectedLanguage(language);
    setSelectedOption(null); // Reset option when language changes
    resetForm();
  };

  const handleAnswer = (questionIndex, answer) => {
    updateInterviewAnswer(questionIndex, answer);
  };

  const handleInterviewComplete = async (fullStatement) => {
    await processCompleteInterview(fullStatement);
    setInterviewComplete(true);
  };

  // Handle FIR field changes
  const handleFirFieldChange = (fieldId, value) => {
    setFirFields((prev) => ({
      ...prev,
      [fieldId]: value,
    }));
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50">
      <Toaster position="top-center" />
      <div className="backdrop-blur-sm bg-white/30 min-h-screen">
        <Header />

        <TechyLoader
          isLoading={isLoading}
          message="Processing audio, please wait..."
        >
          <main className="container mx-auto px-4 py-8">
            <motion.div
              className="text-center mb-12"
              initial={{ opacity: 0, y: -20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
            >
              <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
                FIR Generation Assistant
              </h1>
              <p className="mt-4 text-gray-600 max-w-2xl mx-auto">
                Our AI-powered system helps you generate accurate First
                Information Reports (FIR) from audio statements with advanced
                analysis and legal insights.
              </p>
            </motion.div>

            {!selectedLanguage ? (
              <motion.div
                className="max-w-2xl mx-auto p-8 bg-white rounded-xl shadow-sm"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
              >
                <h2 className="text-2xl font-semibold text-gray-800 mb-6 text-center">
                  Select Your Preferred Language
                </h2>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  {Object.keys(INTERVIEW_QUESTIONS).map((lang) => (
                    <motion.button
                      key={lang}
                      className="group relative p-6 border-2 border-blue-200 rounded-xl hover:border-blue-500 hover:bg-blue-50 transition-all"
                      whileHover={{ scale: 1.02, y: -4 }}
                      whileTap={{ scale: 0.98 }}
                      onClick={() => handleLanguageSelect(lang)}
                    >
                      <motion.div
                        className="absolute inset-0 bg-blue-500/5 rounded-xl"
                        initial={false}
                        whileHover={{ scale: 1.1, opacity: 0 }}
                      />
                      <div className="relative z-10">
                        <p className="text-xl font-medium capitalize mb-2 bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
                          {lang}
                        </p>
                        <p className="text-sm text-gray-500">
                          {lang === "english"
                            ? "English language support"
                            : lang === "hindi"
                            ? "हिंदी भाषा समर्थन"
                            : "ਪੰਜਾਬੀ ਭਾਸ਼ਾ ਸਹਾਇਤਾ"}
                        </p>
                      </div>
                    </motion.button>
                  ))}
                </div>
                <motion.p
                  className="mt-6 text-center text-gray-500 text-sm"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: 0.5 }}
                >
                  Choose your preferred language for the FIR process
                </motion.p>
              </motion.div>
            ) : !selectedOption ? (
              // Option selection UI (Interview or Upload)
              <motion.div
                className="max-w-2xl mx-auto p-8 bg-white rounded-xl shadow-sm"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5 }}
              >
                <h2 className="text-2xl font-semibold text-gray-800 mb-6 text-center">
                  Choose FIR Generation Method
                </h2>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <motion.button
                    className="group relative p-6 border-2 border-blue-200 rounded-xl hover:border-blue-500 hover:bg-blue-50 transition-all"
                    whileHover={{ scale: 1.02, y: -4 }}
                    whileTap={{ scale: 0.98 }}
                    onClick={() => setSelectedOption("interview")}
                  >
                    <motion.div
                      className="absolute inset-0 bg-blue-500/5 rounded-xl"
                      initial={false}
                      whileHover={{ scale: 1.1, opacity: 0 }}
                    />
                    <div className="relative z-10">
                      <p className="text-xl font-medium mb-2 bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
                        Interactive Interview
                      </p>
                      <p className="text-sm text-gray-500">
                        Answer questions through an AI-guided interview process
                      </p>
                    </div>
                  </motion.button>

                  <motion.button
                    className="group relative p-6 border-2 border-blue-200 rounded-xl hover:border-blue-500 hover:bg-blue-50 transition-all"
                    whileHover={{ scale: 1.02, y: -4 }}
                    whileTap={{ scale: 0.98 }}
                    onClick={() => setSelectedOption("upload")}
                  >
                    <motion.div
                      className="absolute inset-0 bg-blue-500/5 rounded-xl"
                      initial={false}
                      whileHover={{ scale: 1.1, opacity: 0 }}
                    />
                    <div className="relative z-10">
                      <p className="text-xl font-medium mb-2 bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
                        Upload Audio
                      </p>
                      <p className="text-sm text-gray-500">
                        Upload an existing audio recording of the incident
                      </p>
                    </div>
                  </motion.button>
                </div>

                <motion.button
                  className="mt-6 px-4 py-2 text-gray-600 hover:text-gray-800 flex items-center gap-2 mx-auto"
                  onClick={() => setSelectedLanguage(null)}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                >
                  <span>← Change Language</span>
                </motion.button>
              </motion.div>
            ) : selectedOption === "interview" && !interviewComplete ? (
              // Interview UI
              <div className="max-w-3xl mx-auto">
                <InterviewForm
                  language={selectedLanguage}
                  questions={INTERVIEW_QUESTIONS[selectedLanguage]}
                  onAnswer={handleAnswer}
                  onComplete={handleInterviewComplete}
                />
                <motion.button
                  className="mt-4 px-4 py-2 text-gray-600 hover:text-gray-800 flex items-center gap-2"
                  onClick={() => {
                    setSelectedOption(null);
                  }}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                >
                  <span>← Back to Options</span>
                </motion.button>

                {/* Show analysis components if we have transcribed text */}
                {transcribedText && (
                  <div className="mt-8">
                    <TranscriptDisplay />
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-6">
                      <CrimePredictions />
                      <LegalSections />
                    </div>
                  </div>
                )}
              </div>
            ) : selectedOption === "upload" ? (
              // Single Audio Upload UI with analysis
              <div className="max-w-5xl mx-auto">
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.5 }}
                >
                  <SingleAudioUploader language={selectedLanguage} />
                  <motion.button
                    className="mt-4 px-4 py-2 text-gray-600 hover:text-gray-800 flex items-center gap-2"
                    onClick={() => {
                      setSelectedOption(null);
                    }}
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                  >
                    <span>← Back to Options</span>
                  </motion.button>
                </motion.div>

                {transcribedText && (
                  <motion.div
                    className="mt-8"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ duration: 0.5, delay: 0.4 }}
                  >
                    {/* Transcript Display */}
                    <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
                      <h2 className="text-xl font-semibold text-gray-800 mb-4 flex items-center gap-2">
                        <span className="bg-blue-100 text-blue-800 p-1 rounded">
                          📝
                        </span>
                        Transcript Analysis
                      </h2>
                      <TranscriptDisplay />
                    </div>

                    {/* Analysis Components in Grid */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
                      <motion.div
                        className="bg-white rounded-lg shadow-sm p-6"
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ duration: 0.5, delay: 0.6 }}
                      >
                        <CrimePredictions />
                      </motion.div>
                      <motion.div
                        className="bg-white rounded-lg shadow-sm p-6"
                        initial={{ opacity: 0, x: 20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ duration: 0.5, delay: 0.7 }}
                      >
                        <LegalSections />
                      </motion.div>
                    </div>

                    {/* FIR Draft Section */}
                    {firDraft && (
                      <motion.div
                        className="bg-white rounded-lg shadow-lg p-8 mb-6"
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.5, delay: 0.8 }}
                      >
                        <div className="border-b border-gray-200 pb-4 mb-6">
                          <h2 className="text-2xl font-semibold text-gray-800 flex items-center gap-3">
                            <span className="bg-blue-100 text-blue-800 p-2 rounded-lg">
                              📋
                            </span>
                            First Information Report Draft
                          </h2>
                          <p className="text-gray-600 mt-2">
                            Review and edit the generated FIR based on the
                            analysis above
                          </p>
                        </div>
                        <div className="max-h-[600px] overflow-y-auto custom-scrollbar">
                          <FIRDraftDisplay
                            firDraft={firDraft}
                            firFields={firFields}
                            onFieldChange={handleFirFieldChange}
                          />
                        </div>
                      </motion.div>
                    )}
                  </motion.div>
                )}
              </div>
            ) : (
              // FIR generation UI (after interview is complete)
              <div className="max-w-5xl mx-auto">
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.5, delay: 0.2 }}
                >
                  <AudioUploader />
                </motion.div>

                <motion.div
                  className="mt-8 space-y-6"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ duration: 0.5, delay: 0.4 }}
                >
                  <TranscriptDisplay />

                  {/* Grid layout for Analysis & FIR Draft */}
                  <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
                    {/* Analysis Panel - Left Side */}
                    <div className="lg:col-span-5 space-y-6">
                      <motion.div
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ duration: 0.5, delay: 0.6 }}
                      >
                        <CrimePredictions />
                      </motion.div>
                      <motion.div
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ duration: 0.5, delay: 0.7 }}
                      >
                        <LegalSections />
                      </motion.div>
                    </div>

                    {/* FIR Draft Panel - Right Side */}
                    <motion.div
                      className="lg:col-span-7"
                      initial={{ opacity: 0, x: 20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ duration: 0.5, delay: 0.8 }}
                    >
                      {firDraft && (
                        <div className="bg-white p-6 rounded-lg shadow-sm mb-6">
                          <h2 className="text-xl font-semibold text-gray-800 mb-4 flex items-center gap-2">
                            <span className="bg-blue-100 text-blue-800 p-1 rounded">
                              📋
                            </span>
                            FIR Draft
                          </h2>
                          <div className="max-h-[600px] overflow-y-auto">
                            <FIRDraftDisplay
                              firDraft={firDraft}
                              firFields={firFields}
                              onFieldChange={handleFirFieldChange}
                            />
                          </div>
                        </div>
                      )}
                    </motion.div>
                  </div>
                </motion.div>
              </div>
            )}
          </main>

          <footer className="bg-white/50 backdrop-blur-sm py-6 mt-12 border-t border-gray-200">
            <div className="container mx-auto px-4 text-center">
              <p className="text-gray-600">
                © {new Date().getFullYear()} FIR Assistant | AI-powered legal
                document generation
              </p>
              <p className="text-sm text-gray-500 mt-2">
                Enhancing law enforcement efficiency through technology
              </p>
            </div>
          </footer>
        </TechyLoader>
      </div>
    </div>
  );
};

export default App;
