import React from "react";
import { FaUser, FaIdCard } from "react-icons/fa";
import { motion } from "framer-motion";
import useFIRStore from "../../store/useFIRStore";

const VictimInfoForm = () => {
  const { victimInfo, updateVictimInfo, transcribedText } = useFIRStore();

  // If no transcribed text, don't show the form yet
  if (!transcribedText) return null;

  const handleInputChange = (field) => (e) => {
    updateVictimInfo(field, e.target.value);
  };

  return (
    <motion.div
      className="p-6 bg-white rounded-lg shadow-sm mb-6"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <h2 className="text-xl font-semibold text-gray-800 mb-4 flex items-center gap-2">
        <FaUser className="text-blue-500" /> Victim Information
      </h2>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Full Name
          </label>
          <input
            type="text"
            value={victimInfo.name}
            onChange={handleInputChange("name")}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Enter full name"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Father's/Husband's Name
          </label>
          <input
            type="text"
            value={victimInfo.fatherOrHusbandName}
            onChange={handleInputChange("fatherOrHusbandName")}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Enter name"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Date of Birth
          </label>
          <input
            type="date"
            value={victimInfo.dob}
            onChange={handleInputChange("dob")}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Nationality
          </label>
          <input
            type="text"
            value={victimInfo.nationality}
            onChange={handleInputChange("nationality")}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Enter nationality"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Occupation
          </label>
          <input
            type="text"
            value={victimInfo.occupation}
            onChange={handleInputChange("occupation")}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Enter occupation"
          />
        </div>

        <div className="md:col-span-2">
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Address
          </label>
          <textarea
            value={victimInfo.address}
            onChange={handleInputChange("address")}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Enter complete address"
            rows={3}
          ></textarea>
        </div>
      </div>

      <motion.div
        className="flex items-start gap-2 mt-4 p-3 bg-blue-50 text-blue-800 rounded-md text-sm"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.3 }}
      >
        <FaIdCard className="text-blue-600 mt-0.5 flex-shrink-0" />
        <p>
          Providing complete victim information improves the accuracy and legal
          validity of the FIR.
        </p>
      </motion.div>
    </motion.div>
  );
};

export default VictimInfoForm;
