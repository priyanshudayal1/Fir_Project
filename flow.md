# FIR Interview and Processing Flow

## 1. Initial Setup
- User starts the application and selects their preferred language (English, Hindi, or Punjabi)
- A welcome message is played in the selected language explaining the interview process
- The system prepares to conduct a structured interview with 5 main questions

## 2. Interview Questions Flow

### Question 1: Personal Information - Name
- Question: "Can you tell me your full name, please?" (or equivalent in selected language)
- System records the response and transcribes it
- Information is stored for FIR generation

### Question 2: Guardian Information
- Question: "Could you also share your father's or husband's name?"
- Captures family details required for FIR documentation
- Response is processed and stored

### Question 3: Identity Information
- Question: "What is your date of birth and nationality?"
- Collects two important pieces of information:
  - Date of Birth (DOB)
  - Nationality
- Information is parsed and structured for the FIR

### Question 4: Incident Details
- Question: "Can you please tell me about the incident?"
- Asks for comprehensive details including:
  - Date of incident
  - Time of occurrence
  - Location details
  - Sequence of events
  - Any other relevant information
- This is typically the longest and most detailed response

### Question 5: Accused Information
- Question: "Do you know who committed the crime?"
- Conditional follow-up questions based on the response:
  - If Yes:
    - Details about appearance/behavior
    - Identifiable clothing or features
    - Name or identifying information
  - If No:
    - Proceeds to conclude the interview

## 3. Post-Interview Processing

### Audio Processing
- Each response is recorded as audio
- Real-time audio visualization during recording
- Audio files are processed and transcribed
- Transcriptions are stored for analysis

### Information Extraction
- System extracts structured information from responses including:
  - Victim details (name, DOB, nationality)
  - Incident information (date, time, location)
  - Crime details
  - Accused information (if available)

### Legal Analysis
- System analyzes the incident description to:
  - Identify applicable legal sections
  - Determine crime categories
  - Suggest relevant IPC/CrPC sections
  - Generate crime predictions

### FIR Generation
- Combines all collected information
- Generates a structured FIR draft including:
  - Personal information section
  - Incident details
  - Legal sections
  - Additional observations
  - Required administrative details

## 4. Review and Finalization
- Generated FIR is displayed for review
- Options to:
  - Edit specific sections
  - Add additional information
  - Update any incorrect details
  - Print or download the final FIR

## 5. Data Storage
- All information is securely stored including:
  - Original audio recordings
  - Transcripts
  - Generated FIR
  - Supporting documents
- Maintains a proper audit trail of the entire process