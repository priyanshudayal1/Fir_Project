import React, { useState, useRef, useEffect } from "react";
import { AnimatePresence } from "framer-motion";
import { FaEdit, FaChevronDown, FaChevronUp } from "react-icons/fa";
import toast from "react-hot-toast";

const FIRDraftDisplay = ({ firDraft, firFields, onFieldChange }) => {
  const [expandedSection, setExpandedSection] = useState(null);
  const contentRef = useRef(null);
  const [contentUpdated, setContentUpdated] = useState(false);

  // Group fields by section for organized rendering
  const sections = {
    basic: {
      title: "Basic Information",
      icon: "📝",
      fields: ["district", "police-station"],
    },
    legal: {
      title: "Legal Information",
      icon: "⚖️",
      fields: [
        "act1",
        "sections1",
        "act2",
        "sections2",
        "act3",
        "sections3",
        "other-acts",
      ],
    },
    incident: {
      title: "Incident Details",
      icon: "🕒",
      fields: [
        "incident-day",
        "incident-date",
        "incident-time",
        "distance-ps",
        "beat-no",
        "incident-location",
        "outside-ps",
      ],
    },
    station: {
      title: "Police Station Details",
      icon: "🏢",
      fields: ["gd-entry", "gd-time", "info-type"],
    },
    property: {
      title: "Property Details",
      icon: "💰",
      fields: ["stolen-properties", "total-value", "inquest-report"],
    },
    officer: {
      title: "Officer Details",
      icon: "👮",
      fields: ["officer-name", "officer-rank", "officer-no", "court-dispatch"],
    },
  };

  const fieldLabels = {
    // Basic Information
    district: "District",
    "police-station": "Police Station",

    // Legal Information
    act1: "Act 1",
    sections1: "Sections 1",
    act2: "Act 2",
    sections2: "Sections 2",
    act3: "Act 3",
    sections3: "Sections 3",
    "other-acts": "Other Acts & Sections",

    // Incident Details
    "incident-day": "Day of Incident",
    "incident-date": "Date of Incident",
    "incident-time": "Time of Incident",
    "distance-ps": "Distance from Police Station",
    "beat-no": "Beat Number",
    "incident-location": "Incident Location",
    "outside-ps": "Outside PS Jurisdiction",

    // Police Station Details
    "gd-entry": "General Diary Entry No",
    "gd-time": "General Diary Entry Time",
    "info-type": "Type of Information",

    // Property Details
    "stolen-properties": "Properties Stolen/Involved",
    "total-value": "Total Value of Properties",
    "inquest-report": "Inquest Report/U.D. Case No.",

    // Officer Details
    "officer-name": "Officer Name",
    "officer-rank": "Officer Rank",
    "officer-no": "Officer Number",
    "court-dispatch": "Court Dispatch Date & Time",
  };

  const handleFieldChange = (fieldId, value) => {
    // First update the value in the parent component
    onFieldChange(fieldId, value);

    // Then update the DOM directly if the content is rendered
    if (contentRef.current) {
      const spanId = `fir-${fieldId}`;
      const span = contentRef.current.querySelector(`span[id="${spanId}"]`);

      if (span) {
        span.textContent = value || "[Not Provided]";
        toast.success(`Updated ${fieldLabels[fieldId]}`);
      } else {
        console.warn(
          `Element with ID ${spanId} not found in the rendered FIR content`
        );
      }
    }
  };

  // Force a re-render of the content when firDraft changes
  useEffect(() => {
    setContentUpdated((prev) => !prev);
  }, [firDraft]);

  // Content container to display raw HTML safely with ref
  const ContentContainer = () => {
    return (
      <div
        ref={contentRef}
        className="text-gray-900 bg-white p-6 border-b border-gray-200"
        dangerouslySetInnerHTML={{ __html: firDraft }}
      />
    );
  };

  const EditableField = ({ fieldId, value }) => {
    // Determine input type based on field
    const getInputType = (id) => {
      if (id.includes("date")) return "date";
      if (id.includes("time")) return "time";
      if (
        [
          "stolen-properties",
          "total-value",
          "inquest-report",
          "other-acts",
        ].includes(id)
      )
        return "textarea";
      return "text";
    };

    const inputType = getInputType(fieldId);

    return (
      <div className="mb-4">
        <label className="block text-sm font-medium text-gray-700 mb-1">
          {fieldLabels[fieldId]}
        </label>
        {inputType === "textarea" ? (
          <textarea
            value={value || ""}
            onChange={(e) => handleFieldChange(fieldId, e.target.value)}
            className="w-full p-2 border border-gray-300 rounded focus:ring-gray-500 focus:border-gray-500 min-h-[100px] text-gray-900 bg-white"
          />
        ) : (
          <input
            type={inputType}
            value={value || ""}
            onChange={(e) => handleFieldChange(fieldId, e.target.value)}
            className="w-full p-2 border border-gray-300 rounded focus:ring-gray-500 focus:border-gray-500 text-gray-900 bg-white"
          />
        )}
      </div>
    );
  };

  return (
    <div className="w-full max-w-4xl mx-auto">
      <div className="bg-white shadow-lg rounded-lg overflow-hidden">
        <div className="p-6 bg-gray-100">
          <h2 className="text-2xl font-bold text-gray-900">
            First Information Report
          </h2>
        </div>

        <ContentContainer key={contentUpdated} />

        <div className="p-6">
          <h3 className="text-xl font-semibold mb-4">Edit FIR Details</h3>
          {Object.entries(sections).map(([key, section]) => (
            <div
              key={key}
              className="mb-6 border border-gray-200 rounded-lg overflow-hidden"
            >
              <button
                onClick={() =>
                  setExpandedSection(expandedSection === key ? null : key)
                }
                className="w-full px-4 py-3 bg-gray-50 flex items-center justify-between hover:bg-gray-100"
              >
                <span className="flex items-center gap-2">
                  <span>{section.icon}</span>
                  <span className="font-medium text-gray-900">
                    {section.title}
                  </span>
                </span>
                {expandedSection === key ? <FaChevronUp /> : <FaChevronDown />}
              </button>

              <AnimatePresence>
                {expandedSection === key && (
                  <div className="p-4">
                    {section.fields.map((fieldId) => (
                      <EditableField
                        key={fieldId}
                        fieldId={fieldId}
                        value={firFields[fieldId]}
                      />
                    ))}
                  </div>
                )}
              </AnimatePresence>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default FIRDraftDisplay;
