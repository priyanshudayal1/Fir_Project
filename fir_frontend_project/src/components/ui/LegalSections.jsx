import React from "react";
import { FaGavel, FaInfoCircle } from "react-icons/fa";
import { motion } from "framer-motion";
import useFIRStore from "../../store/useFIRStore";

const LegalSections = () => {
  const { legalSections } = useFIRStore();

  if (
    !legalSections ||
    typeof legalSections !== "string" ||
    !legalSections.trim()
  ) {
    return null;
  }

  // Process the legal sections string into an array
  const sections = legalSections
    .split("\n")
    .filter((line) => line.trim())
    .map((line) => line.trim());

  return (
    <motion.div
      className="p-6 bg-white rounded-lg shadow-sm mb-6"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <h2 className="text-xl font-semibold text-gray-800 mb-4 flex items-center gap-2">
        <FaGavel className="text-blue-500" /> Applicable Legal Sections
      </h2>

      <div className="bg-gray-50 p-4 rounded-lg border border-gray-200">
        <div className="grid gap-2">
          {sections.map((section, index) => (
            <motion.div
              key={index}
              className="bg-white p-3 rounded shadow-sm border-l-4 border-blue-500"
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.05 }}
            >
              <p className="text-gray-800">{section}</p>
            </motion.div>
          ))}
        </div>
      </div>
    </motion.div>
  );
};

export default LegalSections;