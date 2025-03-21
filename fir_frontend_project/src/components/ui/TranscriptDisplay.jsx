import React from "react";
import { FaFileAlt, FaQuoteRight } from "react-icons/fa";
import { motion } from "framer-motion";
import useFIRStore from "../../store/useFIRStore";

const TranscriptDisplay = () => {
  const { transcribedText, sentiment } = useFIRStore();

  if (!transcribedText) return null;

  // Determine sentiment color
  const getSentimentColor = () => {
    if (!sentiment) return "gray";

    const label = sentiment.label.toLowerCase();
    if (label.includes("positive")) return "green";
    if (label.includes("negative")) return "red";
    return "yellow";
  };

  const sentimentColor = getSentimentColor();

  return (
    <motion.div
      className="p-6 bg-white rounded-lg shadow-sm mb-6"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-semibold text-gray-800 flex items-center gap-2">
          <FaFileAlt className="text-blue-500" /> Transcribed Statement
        </h2>

        {sentiment && (
          <motion.div
            className={`px-3 py-1 rounded-full flex items-center gap-2 bg-${sentimentColor}-100 text-${sentimentColor}-700`}
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
          >
            <span
              className={`w-2 h-2 rounded-full bg-${sentimentColor}-500`}
            ></span>
            <span className="text-sm font-medium capitalize">
              {sentiment.label}
            </span>
            <span className="text-xs">
              ({Math.round(sentiment.score * 100)}%)
            </span>
          </motion.div>
        )}
      </div>

      <motion.div
        className="bg-gray-50 p-4 rounded-lg border border-gray-200 relative"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.2 }}
      >
        <FaQuoteRight className="absolute top-2 right-2 text-gray-200 text-xl" />
        <p className="text-gray-700 leading-relaxed whitespace-pre-wrap">
          {transcribedText}
        </p>
      </motion.div>
    </motion.div>
  );
};

export default TranscriptDisplay;
