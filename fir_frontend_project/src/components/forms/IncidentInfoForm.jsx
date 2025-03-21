import React from "react";
import {
  FaMapMarkerAlt,
  FaCalendarAlt,
  FaClock,
  FaInfoCircle,
} from "react-icons/fa";
import { motion } from "framer-motion";
import useFIRStore from "../../store/useFIRStore";

const IncidentInfoForm = () => {
  const { incidentDetails, updateIncidentDetails, transcribedText } =
    useFIRStore();

  // If no transcribed text, don't show the form yet
  if (!transcribedText) return null;

  const handleInputChange = (field) => (e) => {
    updateIncidentDetails(field, e.target.value);
  };

  return (
    <motion.div
      className="p-6 bg-white rounded-lg shadow-sm mb-6"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <h2 className="text-xl font-semibold text-gray-800 mb-4 flex items-center gap-2">
        <FaMapMarkerAlt className="text-blue-500" /> Incident Information
      </h2>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1 flex items-center gap-1">
            <FaCalendarAlt className="text-gray-500" /> Date
          </label>
          <input
            type="date"
            value={incidentDetails.date}
            onChange={handleInputChange("date")}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1 flex items-center gap-1">
            <FaClock className="text-gray-500" /> Time
          </label>
          <input
            type="time"
            value={incidentDetails.time}
            onChange={handleInputChange("time")}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <div className="md:col-span-3">
          <label className="block text-sm font-medium text-gray-700 mb-1 flex items-center gap-1">
            <FaMapMarkerAlt className="text-gray-500" /> Location
          </label>
          <textarea
            value={incidentDetails.location}
            onChange={handleInputChange("location")}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Enter detailed location description"
            rows={2}
          ></textarea>
        </div>
      </div>

      <motion.div
        className="flex items-start gap-2 mt-4 p-3 bg-blue-50 text-blue-800 rounded-md text-sm"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.3 }}
      >
        <FaInfoCircle className="text-blue-600 mt-0.5 flex-shrink-0" />
        <p>
          Precise incident details help law enforcement accurately document and
          investigate the case.
        </p>
      </motion.div>
    </motion.div>
  );
};

export default IncidentInfoForm;
