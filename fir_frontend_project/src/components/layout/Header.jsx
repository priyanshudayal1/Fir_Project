import React from "react";
import { FaFileMedical, FaGavel } from "react-icons/fa";
import { motion } from "framer-motion";

const Header = () => {
  return (
    <motion.header
      className="bg-white shadow-sm py-4"
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <div className="container mx-auto px-4 flex justify-between items-center">
        <motion.div
          className="flex items-center gap-2 text-blue-600"
          whileHover={{ scale: 1.05 }}
        >
          <FaFileMedical className="text-2xl" />
          <h1 className="text-2xl font-bold">FIR Assistant</h1>
        </motion.div>
        <motion.div
          className="flex items-center gap-3"
          whileHover={{ scale: 1.05 }}
        >
          <FaGavel className="text-xl text-gray-600" />
          <span className="text-gray-600 font-medium">Digital Legal Aid</span>
        </motion.div>
      </div>
    </motion.header>
  );
};

export default Header;
