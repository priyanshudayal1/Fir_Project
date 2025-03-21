import React from "react";
import { FaBalanceScale } from "react-icons/fa";
import { motion } from "framer-motion";
import useFIRStore from "../../store/useFIRStore";

const CrimePredictions = () => {
  const { crimePredictions } = useFIRStore();

  if (!crimePredictions || crimePredictions.length === 0) return null;

  // Sort by highest score first
  const sortedPredictions = [...crimePredictions].sort(
    (a, b) => b.score - a.score
  );
  const highestScore = sortedPredictions[0]?.score || 0;

  return (
    <motion.div
      className="p-6 bg-white rounded-lg shadow-sm mb-6"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <h2 className="text-xl font-semibold text-gray-800 mb-4 flex items-center gap-2">
        <FaBalanceScale className="text-blue-500" /> Crime Type Analysis
      </h2>

      <div className="space-y-4">
        {sortedPredictions.map((item, index) => (
          <motion.div
            key={item.crime}
            className="space-y-1"
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: index * 0.1 }}
          >
            <div className="flex justify-between text-sm">
              <span className="font-medium text-gray-700">{item.crime}</span>
              <span className="text-gray-500">
                {Math.round(item.score * 100)}%
              </span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2.5 overflow-hidden">
              <motion.div
                className={`h-2.5 rounded-full ${
                  index === 0 ? "bg-blue-600" : "bg-blue-400"
                }`}
                style={{ width: "0%" }}
                animate={{ width: `${(item.score / highestScore) * 100}%` }}
                transition={{ duration: 0.8, ease: "easeOut" }}
              />
            </div>
          </motion.div>
        ))}
      </div>

      {sortedPredictions.length > 0 && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
          className="mt-4 text-sm text-gray-500 bg-blue-50 p-3 rounded-md"
        >
          <p className="font-medium text-blue-700">
            Primary Crime Type: {sortedPredictions[0].crime}
          </p>
          <p className="text-xs mt-1">
            This analysis is based on AI pattern recognition and should be
            verified by legal experts.
          </p>
        </motion.div>
      )}
    </motion.div>
  );
};

export default CrimePredictions;
