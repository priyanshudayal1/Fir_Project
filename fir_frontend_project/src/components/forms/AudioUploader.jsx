import React, { useState, useEffect } from "react";
import { FaEdit, FaFilePdf } from "react-icons/fa";
import { motion } from "framer-motion";
import useFIRStore from "../../store/useFIRStore";
import axios from "axios";
import FIRDraftDisplay from "../ui/FIRDraftDisplay";

const AudioUploader = () => {
  const [firFields, setFirFields] = useState({});
  const [showFirForm, setShowFirForm] = useState(false);
  const { firDraft } = useFIRStore();

  // Extract FIR field values when FIR draft changes
  useEffect(() => {
    if (firDraft) {
      // Extract values from FIR draft by parsing the HTML content
      const tempDiv = document.createElement("div");
      tempDiv.innerHTML = firDraft;

      // Create a new object to store extracted values
      const extractedFields = {};

      // Find all span elements with IDs
      const spans = tempDiv.querySelectorAll("span[id^='fir-']");

      // Extract values from spans
      spans.forEach((span) => {
        const fieldId = span.id.replace("fir-", "");
        extractedFields[fieldId] = span.textContent || "";
      });

      setFirFields(extractedFields);

      if (!showFirForm) {
        setShowFirForm(true);
      }
    }
  }, [firDraft, showFirForm]);

  // Handle FIR field changes
  const handleFirFieldChange = (fieldId, value) => {
    setFirFields((prev) => ({
      ...prev,
      [fieldId]: value,
    }));
  };

  // Update FIR with modified field values
  const updateFIRWithFields = async () => {
    try {
      // Prepare data to send to the backend
      const updateData = {
        victim_name: firFields["victim-name"],
        father_or_husband_name: firFields["father-husband-name"],
        dob: firFields["dob"],
        nationality: firFields["nationality"],
        occupation: firFields["occupation"],
        address: firFields["address"],
        incident_date: firFields["incident-date"],
        incident_time: firFields["incident-time"],
        incident_location: firFields["incident-location"],
        complaint_details: firFields["complaint-details"],
        accused_details: firFields["accused-details"],
        stolen_properties: firFields["stolen-properties"],
        total_value: firFields["total-value"],
        delay_reason: firFields["delay-reason"],
      };

      // Call API to update FIR with modified values
      const response = await axios.post(
        "http://localhost:5000/update_fir",
        updateData
      );

      // Handle successful update
      if (response.data && response.data.fir_draft) {
        alert("FIR updated successfully");
      }
    } catch (error) {
      console.error("Error updating FIR:", error);
      alert(
        "Failed to update FIR: " +
          (error.response?.data?.error || error.message)
      );
    }
  };

  // Download FIR as PDF with proper styling
  const downloadFIRasPDF = () => {
    // Create a new window for PDF generation
    const printWindow = window.open("", "_blank");

    // Add styled HTML content
    printWindow.document.write(`
      <!DOCTYPE html>
      <html lang="en">
      <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>FIR Document</title>
        <style>
          body {
            font-family: 'Arial', sans-serif;
            line-height: 1.6;
            margin: 40px;
          }
          h1 {
            text-align: center;
            font-size: 24px;
            margin-bottom: 20px;
          }
          .header {
            text-align: center;
            margin-bottom: 30px;
          }
          .fir-section {
            margin-bottom: 20px;
          }
          .field-label {
            font-weight: bold;
          }
          .field-value {
            margin-left: 8px;
          }
          table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 20px;
          }
          th, td {
            border: 1px solid #ddd;
            padding: 8px 12px;
            text-align: left;
          }
          th {
            background-color: #f2f2f2;
          }
          .signature-section {
            margin-top: 50px;
            display: flex;
            justify-content: space-between;
          }
          .signature-box {
            border-top: 1px solid #000;
            width: 200px;
            padding-top: 5px;
            text-align: center;
          }
          @media print {
            body {
              margin: 0.5cm;
            }
            .page-break {
              page-break-before: always;
            }
          }
        </style>
      </head>
      <body>
        <div class="header">
          <h1>FIRST INFORMATION REPORT</h1>
          <p>(Under Section 154 Cr.P.C)</p>
        </div>
        
        <div class="fir-content">
          ${firDraft}
        </div>
        
        <div class="signature-section">
          <div class="signature-box">
            Officer Signature
          </div>
          <div class="signature-box">
            Complainant Signature
          </div>
        </div>
      </body>
      </html>
    `);

    // Trigger print dialog
    setTimeout(() => {
      printWindow.print();
      // Close window after print (optional)
      printWindow.onfocus = () => setTimeout(() => printWindow.close(), 500);
    }, 1000);
  };

  return (
    <motion.div
      className="w-full p-6 bg-white rounded-lg shadow-sm"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
    >
      <motion.h2
        className="text-xl font-semibold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent mb-4 flex items-center gap-2"
        initial={{ opacity: 0, x: -20 }}
        animate={{ opacity: 1, x: 0 }}
      >
        <FaEdit className="text-blue-500" /> FIR Draft
      </motion.h2>

      {/* FIR Form */}
      {showFirForm && (
        <FIRDraftDisplay
          firDraft={firDraft}
          firFields={firFields}
          onFieldChange={handleFirFieldChange}
          onSave={updateFIRWithFields}
        />
      )}

      {/* Download PDF Button */}
      {firDraft && (
        <motion.button
          className="mt-4 bg-blue-500 text-white px-4 py-2 rounded-lg flex items-center gap-2"
          onClick={downloadFIRasPDF}
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
        >
          <FaFilePdf />
          Download as PDF
        </motion.button>
      )}
    </motion.div>
  );
};

export default AudioUploader;
