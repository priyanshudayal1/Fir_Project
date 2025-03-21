import React from "react";
import { FaSync } from "react-icons/fa";
import { motion } from "framer-motion";
import useFIRStore from "../../store/useFIRStore";

const UpdateFIRButton = () => {
  const { updateFIRWithDetails, transcribedText, isLoading } = useFIRStore();

  // Only show the button when we have transcribed text
  if (!transcribedText) return null;

  return (
    <div className="flex justify-center my-8">
      <motion.button
        className="bg-blue-600 text-white px-6 py-3 rounded-lg shadow-md hover:bg-blue-700 flex items-center gap-2"
        onClick={updateFIRWithDetails}
        disabled={isLoading}
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        {isLoading ? (
          <>
            <svg
              className="animate-spin h-5 w-5 text-white"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
            >
              <circle
                className="opacity-25"
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                strokeWidth="4"
              ></circle>
              <path
                className="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
              ></path>
            </svg>
            <span>Updating...</span>
          </>
        ) : (
          <>
            <FaSync />
            <span>Update FIR with Details</span>
          </>
        )}
      </motion.button>
    </div>
  );
};

export default UpdateFIRButton;
