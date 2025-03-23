import React, { useState, useRef, useEffect } from "react";

const FIRDraftDisplay = ({ firDraft}) => {
  const contentRef = useRef(null);
  const [contentUpdated, setContentUpdated] = useState(false);

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

  return (
    <div className="w-full max-w-4xl mx-auto">
      <div className="bg-white shadow-lg rounded-lg overflow-hidden">
        <div className="p-6 bg-gray-100">
          <h2 className="text-2xl font-bold text-gray-900">
            First Information Report
          </h2>
        </div>

        <ContentContainer key={contentUpdated} />
      </div>
    </div>
  );
};

export default FIRDraftDisplay;
