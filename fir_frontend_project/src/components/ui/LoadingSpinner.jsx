import React from "react";
import { motion } from "framer-motion";

const LoadingSpinner = ({ message = "Processing..." }) => {
  return (
    <motion.div
      className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
    >
      <div className="bg-white p-6 rounded-lg shadow-lg flex flex-col items-center max-w-sm">
        <div className="relative">
          <div className="w-16 h-16 border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin"></div>
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="w-8 h-8 bg-white rounded-full"></div>
          </div>
        </div>
        <p className="mt-4 text-gray-700">{message}</p>

        <motion.div
          className="w-full bg-gray-200 h-1.5 mt-4 rounded-full overflow-hidden"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
        >
          <motion.div
            className="h-full bg-blue-500"
            initial={{ width: "0%" }}
            animate={{
              width: ["0%", "100%"],
              transition: {
                repeat: Infinity,
                duration: 1.5,
                ease: "easeInOut",
              },
            }}
          />
        </motion.div>
      </div>
    </motion.div>
  );
};

export default LoadingSpinner;
