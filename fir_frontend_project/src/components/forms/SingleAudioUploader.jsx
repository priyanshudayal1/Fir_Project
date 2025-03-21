import React, { useState, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { FaFileAudio, FaUpload, FaTrash, FaSpinner } from "react-icons/fa";
import { useSingleAudioUploadStore } from "../../store/useSingleAudioUpload";
import toast from "react-hot-toast";
import TranscriptDisplay from "../ui/TranscriptDisplay";
import CrimePredictions from "../ui/CrimePredictions";
import LegalSections from "../ui/LegalSections";
import useFIRStore from "../../store/useFIRStore";
import FIRDraftDisplay from "../ui/FIRDraftDisplay";

const SingleAudioUploader = ({ language }) => {
  const [audioFile, setAudioFile] = useState(null);
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef(null);

  const {
    uploadAudio,
    isUploading,
    uploadProgress,
    processingResults,
    resetState,
  } = useSingleAudioUploadStore();

  const { setTranscribedText, setCrimePredictions, setLegalSections } =
    useFIRStore();

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      validateAndSetFile(file);
    }
  };

  const validateAndSetFile = (file) => {
    // Check if file is an audio file
    if (!file.type.startsWith("audio/")) {
      toast.error("Please upload an audio file");
      return;
    }

    // Check file size (max 50MB)
    if (file.size > 50 * 1024 * 1024) {
      toast.error("File size should be less than 50MB");
      return;
    }

    setAudioFile(file);
    toast.success("Audio file selected successfully");
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      validateAndSetFile(e.dataTransfer.files[0]);
    }
  };

  const handleUpload = async () => {
    if (!audioFile) {
      toast.error("Please select an audio file first");
      return;
    }

    try {
      await uploadAudio(audioFile, language);

      // Update global FIR store with the processing results
      if (processingResults) {
        setTranscribedText(processingResults.transcribed_text || "");
        setCrimePredictions(processingResults.crime_predictions || []);
        setLegalSections(processingResults.legal_sections || "");
      }

      toast.success("Audio processed successfully");
    } catch (error) {
      console.error("Error uploading file:", error);
      toast.error("Failed to process audio file");
    }
  };

  const handleRemoveFile = () => {
    setAudioFile(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  return (
    <div className="space-y-8">
      {!processingResults ? (
        <motion.div
          className="bg-white p-6 rounded-xl shadow-sm"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <h2 className="text-2xl font-semibold text-gray-800 mb-4">
            Upload Audio Recording
          </h2>

          <p className="text-gray-600 mb-6">
            Upload an audio recording of the incident to generate an FIR. The
            system will analyze the audio, extract key details, and create a
            comprehensive report.
          </p>

          {/* Drag and drop area */}
          <div
            className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
              isDragging
                ? "border-blue-500 bg-blue-50"
                : "border-gray-300 hover:border-blue-400 hover:bg-blue-50/50"
            }`}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            onClick={() => fileInputRef.current.click()}
          >
            <input
              type="file"
              ref={fileInputRef}
              onChange={handleFileChange}
              accept="audio/*"
              className="hidden"
            />

            <div className="flex flex-col items-center">
              <motion.div
                className="w-16 h-16 rounded-full bg-blue-100 flex items-center justify-center text-blue-500 mb-4"
                animate={{ scale: isDragging ? 1.1 : 1 }}
              >
                <FaFileAudio size={28} />
              </motion.div>

              <p className="text-gray-700 font-medium mb-2">
                {isDragging
                  ? "Drop file here"
                  : "Drag and drop audio file here"}
              </p>
              <p className="text-gray-500 text-sm mb-4">or click to browse</p>

              <p className="text-xs text-gray-400">
                Supported formats: MP3, WAV, M4A, WEBM, etc. (Max 50MB)
              </p>
            </div>
          </div>

          {/* Selected file preview */}
          <AnimatePresence>
            {audioFile && (
              <motion.div
                className="mt-6 p-4 bg-gray-50 rounded-lg"
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, height: 0 }}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center text-blue-500">
                      <FaFileAudio />
                    </div>
                    <div>
                      <p className="font-medium text-gray-800 truncate max-w-xs">
                        {audioFile.name}
                      </p>
                      <p className="text-xs text-gray-500">
                        {(audioFile.size / (1024 * 1024)).toFixed(2)} MB
                      </p>
                    </div>
                  </div>

                  <button
                    className="text-red-500 hover:text-red-700"
                    onClick={handleRemoveFile}
                  >
                    <FaTrash />
                  </button>
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Upload button */}
          <div className="mt-8 flex justify-center">
            <motion.button
              className={`px-8 py-3 rounded-lg shadow-md flex items-center gap-2 ${
                !audioFile || isUploading
                  ? "bg-gray-300 cursor-not-allowed"
                  : "bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 text-white"
              }`}
              disabled={!audioFile || isUploading}
              onClick={handleUpload}
              whileHover={audioFile && !isUploading ? { scale: 1.03 } : {}}
              whileTap={audioFile && !isUploading ? { scale: 0.98 } : {}}
            >
              {isUploading ? (
                <>
                  <FaSpinner className="animate-spin" />
                  <span>Processing...</span>
                </>
              ) : (
                <>
                  <FaUpload />
                  <span>Upload and Generate FIR</span>
                </>
              )}
            </motion.button>
          </div>

          {/* Upload progress bar */}
          <AnimatePresence>
            {isUploading && (
              <motion.div
                className="mt-6"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
              >
                <p className="text-sm text-gray-600 mb-2">
                  {uploadProgress < 100
                    ? "Uploading audio file..."
                    : "Processing audio..."}
                </p>
                <div className="w-full h-2 bg-gray-200 rounded-full overflow-hidden">
                  <motion.div
                    className="h-full bg-blue-500"
                    initial={{ width: 0 }}
                    animate={{ width: `${uploadProgress}%` }}
                    transition={{ duration: 0.5 }}
                  />
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </motion.div>
      ) : (
        // Results display section with proper organization and styling
        <div className="space-y-6">
          {/* Transcribed Text Section */}
          <motion.div
            className="bg-white p-6 rounded-xl shadow-sm"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
          >
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-2xl font-semibold text-gray-800">
                Generated FIR Results
              </h2>
              <motion.button
                className="text-gray-500 hover:text-gray-700 px-3 py-1 rounded border border-gray-300 text-sm flex items-center gap-1"
                onClick={resetState}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                <span>Upload Another</span>
              </motion.button>
            </div>

            {/* Transcribed Text Component */}
            <TranscriptDisplay />
          </motion.div>

          {/* Crime Predictions and Legal Sections in Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <CrimePredictions />
            <LegalSections />
          </div>

          {/* FIR Draft Section */}
          <motion.div
            className="bg-white p-6 rounded-xl shadow-sm"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
          >
            <FIRDraftDisplay
              firDraft={processingResults?.fir_draft}
              firFields={processingResults?.fir_fields || {}}
              onFieldChange={() => {}} // Add field change handler if needed
            />
          </motion.div>
        </div>
      )}
    </div>
  );
};

export default SingleAudioUploader;
