import React from "react";
import { motion } from "framer-motion";

const TechyLoader = ({ isLoading, message, children }) => {
  return (
    <div className="relative w-full h-full min-h-[300px]">
      {/* Background content that will be shown blurred */}
      <div
        className={`transition-all duration-500 ${
          isLoading ? "blur-md filter brightness-50" : ""
        }`}
      >
        {children}
      </div>

      {/* Loading overlay */}
      {isLoading && (
        <div className="absolute inset-0 flex flex-col items-center justify-center z-50 backdrop-blur-sm bg-black/10">
          <div className="max-w-md w-full bg-white/90 backdrop-blur-md rounded-2xl shadow-2xl p-8 border border-gray-100">
            <div className="flex flex-col items-center">
              {/* Loader animation */}
              <div className="relative w-24 h-24 mb-6">
                {/* Outer spinning circles */}
                <motion.div
                  className="absolute inset-0 border-4 border-transparent border-t-blue-500 border-r-blue-300 rounded-full"
                  animate={{ rotate: 360 }}
                  transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
                />
                <motion.div
                  className="absolute inset-1 border-4 border-transparent border-t-indigo-500 border-l-indigo-300 rounded-full"
                  animate={{ rotate: -360 }}
                  transition={{ duration: 3, repeat: Infinity, ease: "linear" }}
                />

                {/* Digital circuit pattern */}
                <motion.div
                  className="absolute inset-4 rounded-full bg-gradient-to-br from-blue-50 to-indigo-50 flex items-center justify-center overflow-hidden"
                  initial={{ opacity: 0.7 }}
                  animate={{ opacity: [0.7, 0.9, 0.7] }}
                  transition={{ duration: 2, repeat: Infinity }}
                >
                  <div className="absolute w-[150%] h-[150%] flex flex-wrap opacity-30">
                    {Array.from({ length: 36 }).map((_, i) => (
                      <motion.div
                        key={i}
                        className="w-2 h-2 bg-blue-500 m-1 rounded-sm"
                        initial={{ opacity: 0.3 }}
                        animate={{
                          opacity: [0.3, 0.8, 0.3],
                          scale: [1, 1.2, 1],
                        }}
                        transition={{
                          duration: 1.5,
                          repeat: Infinity,
                          delay: i * 0.03,
                          repeatType: "reverse",
                        }}
                      />
                    ))}
                  </div>
                </motion.div>

                {/* Center pulsing dot */}
                <motion.div
                  className="absolute inset-8 rounded-full bg-blue-500 shadow-lg shadow-blue-500/50"
                  animate={{
                    scale: [1, 1.2, 1],
                    opacity: [0.8, 1, 0.8],
                    boxShadow: [
                      "0 0 0 0 rgba(59, 130, 246, 0.4)",
                      "0 0 0 10px rgba(59, 130, 246, 0)",
                      "0 0 0 0 rgba(59, 130, 246, 0.4)",
                    ],
                  }}
                  transition={{ duration: 2, repeat: Infinity }}
                />
              </div>

              {/* Message */}
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3 }}
                className="text-center"
              >
                <h3 className="text-xl font-semibold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent mb-2">
                  {message || "Processing"}
                </h3>

                {/* Animated dots */}
                <div className="flex justify-center space-x-1">
                  <motion.div
                    className="w-2 h-2 bg-blue-500 rounded-full"
                    animate={{ y: [0, -5, 0] }}
                    transition={{ duration: 0.5, repeat: Infinity, delay: 0 }}
                  />
                  <motion.div
                    className="w-2 h-2 bg-blue-500 rounded-full"
                    animate={{ y: [0, -5, 0] }}
                    transition={{ duration: 0.5, repeat: Infinity, delay: 0.1 }}
                  />
                  <motion.div
                    className="w-2 h-2 bg-blue-500 rounded-full"
                    animate={{ y: [0, -5, 0] }}
                    transition={{ duration: 0.5, repeat: Infinity, delay: 0.2 }}
                  />
                </div>
              </motion.div>

              {/* Digital noise background effect */}
              <div className="mt-6 w-full rounded-lg h-1 bg-gray-100 overflow-hidden">
                <motion.div
                  className="h-full bg-gradient-to-r from-blue-400 via-indigo-500 to-blue-400 rounded-lg"
                  initial={{ width: "5%" }}
                  animate={{ width: ["5%", "95%", "35%", "85%", "60%", "95%"] }}
                  transition={{
                    duration: 5,
                    repeat: Infinity,
                    ease: "easeInOut",
                    times: [0, 0.2, 0.3, 0.5, 0.8, 1],
                  }}
                />
              </div>

              {/* Tech-themed status text */}
              <div className="mt-4 flex text-xs font-mono text-gray-500 items-center space-x-2">
                <span className="inline-block w-2 h-2 bg-green-400 rounded-full animate-pulse"></span>
                <p>System operational</p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default TechyLoader;
