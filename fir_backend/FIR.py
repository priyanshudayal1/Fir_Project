from datetime import datetime
import json

# Update FIR templates to use gray/black text color and white background
FIR_TEMPLATES = {
    'english': """
<div class="w-full max-w-4xl mx-auto p-8 bg-white shadow-lg rounded-lg">
    <div class="text-center mb-8">
        <p class="text-sm text-gray-700 mb-2">FORM – IF1 - (Integrated Form)</p>
        <h1 class="text-3xl font-bold mb-2 text-gray-900">FIRST INFORMATION REPORT</h1>
        <p class="text-gray-700">(Under Section 154 Cr.P.C)</p>
    </div>

    <div class="grid grid-cols-1 gap-6">
        <div class="border-b border-gray-200 pb-4">
            <div class="flex flex-wrap gap-4">
                <p class="text-gray-900">1. Dist.: <span id="fir-district" class="font-medium">_______</span></p>
                <p class="text-gray-900">P.S.: <span id="fir-police-station" class="font-medium">_______</span></p>
                <p class="text-gray-900">Year: <span id="fir-year" class="font-medium">{year}</span></p>
                <p class="text-gray-900">F.I.R. No.: <span id="fir-number" class="font-medium">AUTO-GENERATED</span></p>
                <p class="text-gray-900">Date: <span id="fir-date" class="font-medium">{current_date}</span></p>
            </div>
        </div>

        <div class="border-b border-gray-200 pb-4">
            <div class="grid grid-cols-1 gap-2">
                <p class="text-gray-900">2.(i) Act: <span id="fir-act1" class="ml-2">{act1}</span> Sections: <span id="fir-sections1" class="ml-2">{sections1}</span></p>
                <p class="text-gray-900">(ii) Act: <span id="fir-act2" class="ml-2">{act2}</span> Sections: <span id="fir-sections2" class="ml-2">{sections2}</span></p>
                <p class="text-gray-900">(iii) Act: <span id="fir-act3" class="ml-2">{act3}</span> Sections: <span id="fir-sections3" class="ml-2">{sections3}</span></p>
                <p class="text-gray-900">(iv) Other Acts & Sections: <span id="fir-other-acts" class="ml-2">{other_acts}</span></p>
            </div>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-6 border-b border-gray-200 pb-4">
            <div>
                <h3 class="font-semibold mb-3 text-gray-800">3. (a) Occurrence of Offence:</h3>
                <div class="pl-4">
                    <p class="mb-2 text-gray-900">Day: <span id="fir-incident-day" class="ml-2">{incident_day}</span></p>
                    <p class="mb-2 text-gray-900">Date: <span id="fir-incident-date" class="ml-2">{incident_date}</span></p>
                    <p class="text-gray-900">Time: <span id="fir-incident-time" class="ml-2">{incident_time}</span></p>
                </div>
            </div>
            <div>
                <h3 class="font-semibold mb-3 text-gray-800">(b) Information received at P.S.:</h3>
                <div class="pl-4">
                    <p class="mb-2 text-gray-900">Date: <span id="fir-receipt-date" class="ml-2">{current_date}</span></p>
                    <p class="text-gray-900">Time: <span id="fir-receipt-time" class="ml-2">{current_time}</span></p>
                </div>
                <h3 class="font-semibold mb-3 mt-4 text-gray-800">(c) General Diary Reference:</h3>
                <div class="pl-4">
                    <p class="mb-2 text-gray-900">Entry No(s): <span id="fir-gd-entry" class="ml-2">_______</span></p>
                    <p class="text-gray-900">Time: <span id="fir-gd-time" class="ml-2">_______</span></p>
                </div>
            </div>
        </div>

        <div class="border-b border-gray-200 pb-4">
            <p class="text-gray-900">4. Type of Information: <span id="fir-info-type" class="ml-2">Written / Oral</span></p>
        </div>

        <div class="border-b border-gray-200 pb-4">
            <h3 class="font-semibold mb-3 text-gray-800">5. Place of Occurrence:</h3>
            <div class="pl-4 space-y-2">
                <p class="text-gray-900">(a) Direction and Distance from P.S.: <span id="fir-distance-ps" class="ml-2">{distance_ps}</span></p>
                <p class="text-gray-900">Beat No.: <span id="fir-beat-no" class="ml-2">{beat_no}</span></p>
                <p class="text-gray-900">(b) Address: <span id="fir-incident-location" class="ml-2">{incident_location}</span></p>
                <p class="text-gray-900">(c) Outside PS Jurisdiction: <span id="fir-outside-ps" class="ml-2">{outside_ps}</span></p>
            </div>
        </div>

        <div class=" p-4 rounded-lg mb-6">
            <h3 class="font-semibold mb-3 text-gray-800">6. Complainant/Informant:</h3>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4 pl-4">
                <p class="text-gray-900">(a) Name: <span id="fir-victim-name" class="ml-2">{victim_name}</span></p>
                <p class="text-gray-900">(b) Father's/Husband's Name: <span id="fir-father-husband-name" class="ml-2">{father_or_husband_name}</span></p>
                <p class="text-gray-900">(c) Date/Year of Birth: <span id="fir-dob" class="ml-2">{dob}</span></p>
                <p class="text-gray-900">(d) Nationality: <span id="fir-nationality" class="ml-2">{nationality}</span></p>
                <p class="text-gray-900">(e) Passport Details: <span id="fir-passport" class="ml-2">{passport_details}</span></p>
                <p class="text-gray-900">(f) Occupation: <span id="fir-occupation" class="ml-2">{occupation}</span></p>
                <p class="text-gray-900">(g) Address: <span id="fir-address" class="ml-2">{address}</span></p>
            </div>
        </div>

        <div class=" p-4 rounded-lg mb-6">
            <h3 class="font-semibold mb-3 text-gray-800">7. Details of Accused:</h3>
            <p id="fir-accused-details" class="pl-4 text-gray-700 whitespace-pre-line">{accused_details}</p>
        </div>

        <div class=" p-4 rounded-lg mb-6">
            <h3 class="font-semibold mb-3 text-gray-800">8. Reasons for Delay in Reporting:</h3>
            <p id="fir-delay-reason" class="pl-4 text-gray-700">{delay_reason}</p>
        </div>

        <div class=" p-4 rounded-lg mb-6">
            <h3 class="font-semibold mb-3 text-gray-800">9. Particulars of Properties Stolen/Involved:</h3>
            <p id="fir-stolen-properties" class="pl-4 text-gray-700">{stolen_properties}</p>
            
            <h3 class="font-semibold mt-4 mb-3 text-gray-800">10. Total Value of Properties:</h3>
            <p id="fir-total-value" class="pl-4 text-gray-700">{total_value}</p>
            
            <h3 class="font-semibold mt-4 mb-3 text-gray-800">11. Inquest Report/U.D. Case No.:</h3>
            <p id="fir-inquest-report" class="pl-4 text-gray-700">{inquest_report}</p>
        </div>

        <div class=" p-4 rounded-lg mb-6">
            <h3 class="font-semibold mb-3 text-gray-800">12. F.I.R. Contents:</h3>
            <p id="fir-complaint-details" class="pl-4 text-gray-700 whitespace-pre-line">{complaint_details}</p>
        </div>

        <div class="border-t border-gray-200 pt-6 mt-6">
            <h3 class="font-semibold mb-3 text-gray-800">13. Action Taken:</h3>
            <p class="mb-4 text-gray-700">Since the above report reveals commission of offence(s) u/s as mentioned at Item No. 2</p>
            
            <div class="grid grid-cols-1 md:grid-cols-2 gap-8 mt-8">
                <div>
                    <p class="font-semibold mb-2 text-gray-900">Officer-in-Charge</p>
                    <p class="text-gray-900">Name: <span id="fir-officer-name" class="ml-2">_______</span></p>
                    <p class="text-gray-900">Rank: <span id="fir-officer-rank" class="ml-2">_______</span></p>
                    <p class="text-gray-900">No.: <span id="fir-officer-no" class="ml-2">_______</span></p>
                </div>
                <div>
                    <p class="font-semibold mb-2 text-gray-900">14. Complainant's Signature</p>
                    <p class="text-gray-600">Signature/Thumb Impression</p>
                    <p class="mt-4 text-gray-900">15. Date & Time of despatch to court:</p>
                    <p class="text-gray-900"><span id="fir-court-dispatch" class="ml-2">_______</span></p>
                </div>
            </div>
        </div>
    </div>
</div>
""",
    'hindi': """
<div class="w-full max-w-4xl mx-auto p-8 bg-white shadow-lg rounded-lg">
    <div class="text-center mb-8">
        <p class="text-sm text-gray-700 mb-2">फॉर्म – IF1 - (एकीकृत फॉर्म)</p>
        <h1 class="text-3xl font-bold mb-2 text-gray-900">प्रथम सूचना रिपोर्ट</h1>
        <p class="text-gray-700">(धारा 154 दंड प्रक्रिया संहिता के अंतर्गत)</p>
    </div>

    <div class="grid grid-cols-1 gap-6">
        <div class="border-b border-gray-200 pb-4">
            <div class="flex flex-wrap gap-4">
                <p class="text-gray-900">1. जिला: <span id="fir-district" class="font-medium">_______</span></p>
                <p class="text-gray-900">पुलिस स्टेशन: <span id="fir-police-station" class="font-medium">_______</span></p>
                <p class="text-gray-900">वर्ष: <span id="fir-year" class="font-medium">{year}</span></p>
                <p class="text-gray-900">एफ.आई.आर. संख्या: <span id="fir-number" class="font-medium">स्वतः-जनित</span></p>
                <p class="text-gray-900">दिनांक: <span id="fir-date" class="font-medium">{current_date}</span></p>
            </div>
        </div>

        <div class="border-b border-gray-200 pb-4">
            <div class="grid grid-cols-1 gap-2">
                <p class="text-gray-900">2.(i) अधिनियम: <span id="fir-act1" class="ml-2">{act1}</span> धाराएं: <span id="fir-sections1" class="ml-2">{sections1}</span></p>
                <p class="text-gray-900">(ii) अधिनियम: <span id="fir-act2" class="ml-2">{act2}</span> धाराएं: <span id="fir-sections2" class="ml-2">{sections2}</span></p>
                <p class="text-gray-900">(iii) अधिनियम: <span id="fir-act3" class="ml-2">{act3}</span> धाराएं: <span id="fir-sections3" class="ml-2">{sections3}</span></p>
                <p class="text-gray-900">(iv) अन्य अधिनियम और धाराएं: <span id="fir-other-acts" class="ml-2">{other_acts}</span></p>
            </div>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-6 border-b border-gray-200 pb-4">
            <div>
                <h3 class="font-semibold mb-3 text-gray-800">3. (क) अपराध का घटित होना:</h3>
                <div class="pl-4">
                    <p class="mb-2 text-gray-900">दिन: <span id="fir-incident-day" class="ml-2">{incident_day}</span></p>
                    <p class="mb-2 text-gray-900">दिनांक: <span id="fir-incident-date" class="ml-2">{incident_date}</span></p>
                    <p class="text-gray-900">समय: <span id="fir-incident-time" class="ml-2">{incident_time}</span></p>
                </div>
            </div>
            <div>
                <h3 class="font-semibold mb-3 text-gray-800">(ख) पुलिस स्टेशन में सूचना प्राप्त:</h3>
                <div class="pl-4">
                    <p class="mb-2 text-gray-900">दिनांक: <span id="fir-receipt-date" class="ml-2">{current_date}</span></p>
                    <p class="text-gray-900">समय: <span id="fir-receipt-time" class="ml-2">{current_time}</span></p>
                </div>
                <h3 class="font-semibold mb-3 mt-4 text-gray-800">(ग) सामान्य डायरी संदर्भ:</h3>
                <div class="pl-4">
                    <p class="mb-2 text-gray-900">प्रविष्टि संख्या: <span id="fir-gd-entry" class="ml-2">_______</span></p>
                    <p class="text-gray-900">समय: <span id="fir-gd-time" class="ml-2">_______</span></p>
                </div>
            </div>
        </div>

        <div class="border-b border-gray-200 pb-4">
            <p class="text-gray-900">4. सूचना का प्रकार: <span id="fir-info-type" class="ml-2">लिखित / मौखिक</span></p>
        </div>

        <div class="border-b border-gray-200 pb-4">
            <h3 class="font-semibold mb-3 text-gray-800">5. घटना स्थल:</h3>
            <div class="pl-4 space-y-2">
                <p class="text-gray-900">(क) पुलिस स्टेशन से दिशा और दूरी: <span id="fir-distance-ps" class="ml-2">{distance_ps}</span></p>
                <p class="text-gray-900">बीट नंबर: <span id="fir-beat-no" class="ml-2">{beat_no}</span></p>
                <p class="text-gray-900">(ख) पता: <span id="fir-incident-location" class="ml-2">{incident_location}</span></p>
                <p class="text-gray-900">(ग) पुलिस स्टेशन क्षेत्र के बाहर: <span id="fir-outside-ps" class="ml-2">{outside_ps}</span></p>
            </div>
        </div>

        <div class=" p-4 rounded-lg mb-6">
            <h3 class="font-semibold mb-3 text-gray-800">6. शिकायतकर्ता/सूचनाकर्ता:</h3>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4 pl-4">
                <p class="text-gray-900">(क) नाम: <span id="fir-victim-name" class="ml-2">{victim_name}</span></p>
                <p class="text-gray-900">(ख) पिता/पति का नाम: <span id="fir-father-husband-name" class="ml-2">{father_or_husband_name}</span></p>
                <p class="text-gray-900">(ग) जन्म तिथि/वर्ष: <span id="fir-dob" class="ml-2">{dob}</span></p>
                <p class="text-gray-900">(घ) राष्ट्रीयता: <span id="fir-nationality" class="ml-2">{nationality}</span></p>
                <p class="text-gray-900">(ङ) पासपोर्ट विवरण: <span id="fir-passport" class="ml-2">{passport_details}</span></p>
                <p class="text-gray-900">(च) व्यवसाय: <span id="fir-occupation" class="ml-2">{occupation}</span></p>
                <p class="text-gray-900">(छ) पता: <span id="fir-address" class="ml-2">{address}</span></p>
            </div>
        </div>

        <div class=" p-4 rounded-lg mb-6">
            <h3 class="font-semibold mb-3 text-gray-800">7. आरोपी का विवरण:</h3>
            <p id="fir-accused-details" class="pl-4 text-gray-700 whitespace-pre-line">{accused_details}</p>
        </div>

        <div class=" p-4 rounded-lg mb-6">
            <h3 class="font-semibold mb-3 text-gray-800">8. रिपोर्ट में देरी के कारण:</h3>
            <p id="fir-delay-reason" class="pl-4 text-gray-700">{delay_reason}</p>
        </div>

        <div class=" p-4 rounded-lg mb-6">
            <h3 class="font-semibold mb-3 text-gray-800">9. चोरी/शामिल संपत्ति का विवरण:</h3>
            <p id="fir-stolen-properties" class="pl-4 text-gray-700">{stolen_properties}</p>
            
            <h3 class="font-semibold mt-4 mb-3 text-gray-800">10. संपत्ति का कुल मूल्य:</h3>
            <p id="fir-total-value" class="pl-4 text-gray-700">{total_value}</p>
            
            <h3 class="font-semibold mt-4 mb-3 text-gray-800">11. पंचनामा रिपोर्ट/यू.डी. केस संख्या:</h3>
            <p id="fir-inquest-report" class="pl-4 text-gray-700">{inquest_report}</p>
        </div>

        <div class=" p-4 rounded-lg mb-6">
            <h3 class="font-semibold mb-3 text-gray-800">12. एफ.आई.आर. की विषयवस्तु:</h3>
            <p id="fir-complaint-details" class="pl-4 text-gray-700 whitespace-pre-line">{complaint_details}</p>
        </div>

        <div class="border-t border-gray-200 pt-6 mt-6">
            <h3 class="font-semibold mb-3 text-gray-800">13. की गई कार्रवाई:</h3>
            <p class="mb-4 text-gray-700">चूंकि उपरोक्त रिपोर्ट से मद संख्या 2 में उल्लिखित धारा के तहत अपराध का पता चलता है</p>
            
            <div class="grid grid-cols-1 md:grid-cols-2 gap-8 mt-8">
                <div>
                    <p class="font-semibold mb-2 text-gray-900">प्रभारी अधिकारी</p>
                    <p class="text-gray-900">नाम: <span id="fir-officer-name" class="ml-2">_______</span></p>
                    <p class="text-gray-900">पद: <span id="fir-officer-rank" class="ml-2">_______</span></p>
                    <p class="text-gray-900">क्रमांक: <span id="fir-officer-no" class="ml-2">_______</span></p>
                </div>
                <div>
                    <p class="font-semibold mb-2 text-gray-900">14. शिकायतकर्ता के हस्ताक्षर</p>
                    <p class="text-gray-600">हस्ताक्षर/अंगूठे का निशान</p>
                    <p class="mt-4 text-gray-900">15. न्यायालय में प्रेषण का दिनांक और समय:</p>
                    <p class="text-gray-900"><span id="fir-court-dispatch" class="ml-2">_______</span></p>
                </div>
            </div>
        </div>
    </div>
</div>
""",
    'punjabi': """
<div class="w-full max-w-4xl mx-auto p-8 bg-white shadow-lg rounded-lg">
    <div class="text-center mb-8">
        <p class="text-sm text-gray-700 mb-2">ਫਾਰਮ – IF1 - (ਏਕੀਕ੍ਰਿਤ ਫਾਰਮ)</p>
        <h1 class="text-3xl font-bold mb-2 text-gray-900">ਪਹਿਲੀ ਸੂਚਨਾ ਰਿਪੋਰਟ</h1>
        <p class="text-gray-700">(ਧਾਰਾ 154 ਦੰਡ ਪ੍ਰਕਿਰਿਆ ਸੰਹਿਤਾ ਦੇ ਤਹਿਤ)</p>
    </div>

    <div class="grid grid-cols-1 gap-6">
        <div class="border-b border-gray-200 pb-4">
            <div class="flex flex-wrap gap-4">
                <p class="text-gray-900">1. ਜ਼ਿਲ੍ਹਾ: <span id="fir-district" class="font-medium">_______</span></p>
                <p class="text-gray-900">ਪੁਲਿਸ ਸਟੇਸ਼ਨ: <span id="fir-police-station" class="font-medium">_______</span></p>
                <p class="text-gray-900">ਸਾਲ: <span id="fir-year" class="font-medium">{year}</span></p>
                <p class="text-gray-900">ਐਫ.ਆਈ.ਆਰ. ਨੰਬਰ: <span id="fir-number" class="font-medium">ਸਵੈ-ਜਨਿਤ</span></p>
                <p class="text-gray-900">ਮਿਤੀ: <span id="fir-date" class="font-medium">{current_date}</span></p>
            </div>
        </div>

        <div class="border-b border-gray-200 pb-4">
            <div class="grid grid-cols-1 gap-2">
                <p class="text-gray-900">2.(i) ਐਕਟ: <span id="fir-act1" class="ml-2">{act1}</span> ਧਾਰਾਵਾਂ: <span id="fir-sections1" class="ml-2">{sections1}</span></p>
                <p class="text-gray-900">(ii) ਐਕਟ: <span id="fir-act2" class="ml-2">{act2}</span> ਧਾਰਾਵਾਂ: <span id="fir-sections2" class="ml-2">{sections2}</span></p>
                <p class="text-gray-900">(iii) ਐਕਟ: <span id="fir-act3" class="ml-2">{act3}</span> ਧਾਰਾਵਾਂ: <span id="fir-sections3" class="ml-2">{sections3}</span></p>
                <p class="text-gray-900">(iv) ਹੋਰ ਐਕਟ ਅਤੇ ਧਾਰਾਵਾਂ: <span id="fir-other-acts" class="ml-2">{other_acts}</span></p>
            </div>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-6 border-b border-gray-200 pb-4">
            <div>
                <h3 class="font-semibold mb-3 text-gray-800">3. (ੳ) ਅਪਰਾਧ ਦਾ ਵਾਪਰਨਾ:</h3>
                <div class="pl-4">
                    <p class="mb-2 text-gray-900">ਦਿਨ: <span id="fir-incident-day" class="ml-2">{incident_day}</span></p>
                    <p class="mb-2 text-gray-900">ਮਿਤੀ: <span id="fir-incident-date" class="ml-2">{incident_date}</span></p>
                    <p class="text-gray-900">ਸਮਾਂ: <span id="fir-incident-time" class="ml-2">{incident_time}</span></p>
                </div>
            </div>
            <div>
                <h3 class="font-semibold mb-3 text-gray-800">(ਅ) ਪੁਲਿਸ ਸਟੇਸ਼ਨ ਵਿੱਚ ਸੂਚਨਾ ਪ੍ਰਾਪਤ:</h3>
                <div class="pl-4">
                    <p class="mb-2 text-gray-900">ਮਿਤੀ: <span id="fir-receipt-date" class="ml-2">{current_date}</span></p>
                    <p class="text-gray-900">ਸਮਾਂ: <span id="fir-receipt-time" class="ml-2">{current_time}</span></p>
                </div>
                <h3 class="font-semibold mb-3 mt-4 text-gray-800">(ੲ) ਆਮ ਡਾਇਰੀ ਸੰਦਰਭ:</h3>
                <div class="pl-4">
                    <p class="mb-2 text-gray-900">ਐਂਟਰੀ ਨੰਬਰ: <span id="fir-gd-entry" class="ml-2">_______</span></p>
                    <p class="text-gray-900">ਸਮਾਂ: <span id="fir-gd-time" class="ml-2">_______</span></p>
                </div>
            </div>
        </div>

        <div class="border-b border-gray-200 pb-4">
            <p class="text-gray-900">4. ਸੂਚਨਾ ਦੀ ਕਿਸਮ: <span id="fir-info-type" class="ml-2">ਲਿਖਤੀ / ਜ਼ਬਾਨੀ</span></p>
        </div>

        <div class="border-b border-gray-200 pb-4">
            <h3 class="font-semibold mb-3 text-gray-800">5. ਘਟਨਾ ਸਥਾਨ:</h3>
            <div class="pl-4 space-y-2">
                <p class="text-gray-900">(ੳ) ਪੁਲਿਸ ਸਟੇਸ਼ਨ ਤੋਂ ਦਿਸ਼ਾ ਅਤੇ ਦੂਰੀ: <span id="fir-distance-ps" class="ml-2">{distance_ps}</span></p>
                <p class="text-gray-900">ਬੀਟ ਨੰਬਰ: <span id="fir-beat-no" class="ml-2">{beat_no}</span></p>
                <p class="text-gray-900">(ਅ) ਪਤਾ: <span id="fir-incident-location" class="ml-2">{incident_location}</span></p>
                <p class="text-gray-900">(ੲ) ਪੁਲਿਸ ਸਟੇਸ਼ਨ ਖੇਤਰ ਤੋਂ ਬਾਹਰ: <span id="fir-outside-ps" class="ml-2">{outside_ps}</span></p>
            </div>
        </div>

        <div class=" p-4 rounded-lg mb-6">
            <h3 class="font-semibold mb-3 text-gray-800">6. ਸ਼ਿਕਾਇਤਕਰਤਾ/ਸੂਚਨਾਕਰਤਾ:</h3>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4 pl-4">
                <p class="text-gray-900">(ੳ) ਨਾਮ: <span id="fir-victim-name" class="ml-2">{victim_name}</span></p>
                <p class="text-gray-900">(ਅ) ਪਿਤਾ/ਪਤੀ ਦਾ ਨਾਮ: <span id="fir-father-husband-name" class="ml-2">{father_or_husband_name}</span></p>
                <p class="text-gray-900">(ੲ) ਜਨਮ ਮਿਤੀ/ਸਾਲ: <span id="fir-dob" class="ml-2">{dob}</span></p>
                <p class="text-gray-900">(ਸ) ਰਾਸ਼ਟਰੀਅਤਾ: <span id="fir-nationality" class="ml-2">{nationality}</span></p>
                <p class="text-gray-900">(ਹ) ਪਾਸਪੋਰਟ ਵੇਰਵੇ: <span id="fir-passport" class="ml-2">{passport_details}</span></p>
                <p class="text-gray-900">(ਕ) ਕਿੱਤਾ: <span id="fir-occupation" class="ml-2">{occupation}</span></p>
                <p class="text-gray-900">(ਖ) ਪਤਾ: <span id="fir-address" class="ml-2">{address}</span></p>
            </div>
        </div>

        <div class=" p-4 rounded-lg mb-6">
            <h3 class="font-semibold mb-3 text-gray-800">7. ਦੋਸ਼ੀ ਦੇ ਵੇਰਵੇ:</h3>
            <p id="fir-accused-details" class="pl-4 text-gray-700 whitespace-pre-line">{accused_details}</p>
        </div>

        <div class=" p-4 rounded-lg mb-6">
            <h3 class="font-semibold mb-3 text-gray-800">8. ਰਿਪੋਰਟ ਵਿੱਚ ਦੇਰੀ ਦੇ ਕਾਰਨ:</h3>
            <p id="fir-delay-reason" class="pl-4 text-gray-700">{delay_reason}</p>
        </div>

        <div class=" p-4 rounded-lg mb-6">
            <h3 class="font-semibold mb-3 text-gray-800">9. ਚੋਰੀ/ਸ਼ਾਮਲ ਜਾਇਦਾਦ ਦੇ ਵੇਰਵੇ:</h3>
            <p id="fir-stolen-properties" class="pl-4 text-gray-700">{stolen_properties}</p>
            
            <h3 class="font-semibold mt-4 mb-3 text-gray-800">10. ਜਾਇਦਾਦ ਦਾ ਕੁੱਲ ਮੁੱਲ:</h3>
            <p id="fir-total-value" class="pl-4 text-gray-700">{total_value}</p>
            
            <h3 class="font-semibold mt-4 mb-3 text-gray-800">11. ਪੰਚਨਾਮਾ ਰਿਪੋਰਟ/ਯੂ.ਡੀ. ਕੇਸ ਨੰਬਰ:</h3>
            <p id="fir-inquest-report" class="pl-4 text-gray-700">{inquest_report}</p>
        </div>

        <div class=" p-4 rounded-lg mb-6">
            <h3 class="font-semibold mb-3 text-gray-800">12. ਐਫ.ਆਈ.ਆਰ. ਦੀ ਵਿਸ਼ਾ-ਵਸਤੂ:</h3>
            <p id="fir-complaint-details" class="pl-4 text-gray-700 whitespace-pre-line">{complaint_details}</p>
        </div>

        <div class="border-t border-gray-200 pt-6 mt-6">
            <h3 class="font-semibold mb-3 text-gray-800">13. ਕੀਤੀ ਗਈ ਕਾਰਵਾਈ:</h3>
            <p class="mb-4 text-gray-700">ਕਿਉਂਕਿ ਉਪਰੋਕਤ ਰਿਪੋਰਟ ਤੋਂ ਮੱਦ ਨੰਬਰ 2 ਵਿੱਚ ਦਰਜ ਧਾਰਾ ਤਹਿਤ ਅਪਰਾਧ ਦਾ ਪਤਾ ਲੱਗਦਾ ਹੈ</p>
            
            <div class="grid grid-cols-1 md:grid-cols-2 gap-8 mt-8">
                <div>
                    <p class="font-semibold mb-2 text-gray-900">ਇੰਚਾਰਜ ਅਧਿਕਾਰੀ</p>
                    <p class="text-gray-900">ਨਾਮ: <span id="fir-officer-name" class="ml-2">_______</span></p>
                    <p class="text-gray-900">ਅਹੁਦਾ: <span id="fir-officer-rank" class="ml-2">_______</span></p>
                    <p class="text-gray-900">ਨੰਬਰ: <span id="fir-officer-no" class="ml-2">_______</span></p>
                </div>
                <div>
                    <p class="font-semibold mb-2 text-gray-900">14. ਸ਼ਿਕਾਇਤਕਰਤਾ ਦੇ ਹਸਤਾਖਰ</p>
                    <p class="text-gray-600">ਹਸਤਾਖਰ/ਅੰਗੂਠੇ ਦਾ ਨਿਸ਼ਾਨ</p>
                    <p class="mt-4 text-gray-900">15. ਅਦਾਲਤ ਵਿੱਚ ਭੇਜਣ ਦੀ ਮਿਤੀ ਅਤੇ ਸਮਾਂ:</p>
                    <p class="text-gray-900"><span id="fir-court-dispatch" class="ml-2">_______</span></p>
                </div>
            </div>
        </div>
    </div>
</div>
"""
}


def format_stolen_properties(properties, language='english'):
    """
    Format stolen properties into a readable string.
    
    Args:
        properties: Can be a string or a list of dictionaries with item details
        language: The language for formatting labels
    
    Returns:
        Formatted string representation of the properties
    """
    # If it's already a string, return it as is
    if isinstance(properties, str):
        return properties
    
    # If it's a list or looks like a JSON string of a list, process it
    try:
        # Try to parse if it's a JSON string
        if isinstance(properties, str):
            try:
                properties = json.loads(properties)
            except json.JSONDecodeError:
                return properties
        
        # If we have a list of dictionaries, format it nicely
        if isinstance(properties, list):
            # Define labels based on language
            item_label = {
                'english': 'Item',
                'hindi': 'वस्तु',
                'punjabi': 'ਆਈਟਮ'
            }.get(language.lower(), 'Item')
            
            details_label = {
                'english': 'Details',
                'hindi': 'विवरण',
                'punjabi': 'ਵੇਰਵਾ'
            }.get(language.lower(), 'Details')
            
            value_label = {
                'english': 'Estimated Value',
                'hindi': 'अनुमानित मूल्य',
                'punjabi': 'ਅਨੁਮਾਨਿਤ ਮੁੱਲ'
            }.get(language.lower(), 'Estimated Value')
            
            # Build the formatted output
            formatted_output = ""
            for i, prop in enumerate(properties, 1):
                formatted_output += f"{i}. {item_label}: {prop.get('item', '')}\n"
                if 'details' in prop:
                    formatted_output += f"   {details_label}: {prop.get('details', '')}\n"
                if 'estimated_value' in prop:
                    formatted_output += f"   {value_label}: {prop.get('estimated_value', '')}\n"
                formatted_output += "\n"
            
            return formatted_output.strip()
    except Exception as e:
        # If any error occurs, return the original
        return str(properties)
    
    # Default fallback
    return str(properties)

def generate_fir(victim_name=None, father_or_husband_name=None, dob=None, nationality=None, 
                occupation=None, address=None, incident_date=None, incident_time=None, incident_day=None,
                incident_location=None, complaint_details=None, accused_details=None, 
                stolen_properties=None, total_value=None, inquest_report=None, 
                delay_reason=None, act1=None, sections1=None, act2=None, sections2=None,
                act3=None, sections3=None, other_acts=None, passport_details=None,
                distance_ps=None, beat_no=None, outside_ps=None, personal_info=None,
                language='english'):
    """Generates a structured FIR draft dynamically based on the official FIR format."""
    
    # Use extracted info if available
    if personal_info:
        # Extract basic personal details
        victim_name = personal_info.get("victim_name") or victim_name
        father_or_husband_name = personal_info.get("father_or_husband_name") or father_or_husband_name
        dob = personal_info.get("dob") or dob
        nationality = personal_info.get("nationality") or nationality
        occupation = personal_info.get("occupation") or occupation
        address = personal_info.get("address") or address
        
        # Extract incident details
        incident_date = personal_info.get("incident_date") or incident_date
        incident_time = personal_info.get("incident_time") or incident_time
        incident_location = personal_info.get("incident_location") or incident_location
        
        # Extract other important information
        accused_details = personal_info.get("accused_description") or accused_details
        stolen_properties = personal_info.get("stolen_properties") or stolen_properties
        total_value = personal_info.get("total_value") or total_value
        delay_reason = personal_info.get("delay_reason") or delay_reason
        witness_details = personal_info.get("witness_details", "")
        
        # Enhance complaint details with structured information
        enhanced_details = personal_info.get("incident_details") or ""
        
        # If we have witness details, add them to the complaint details
        if witness_details and witness_details not in enhanced_details:
            witness_header = {
                'english': "\nWitness Details: ",
                'hindi': "\nगवाह विवरण: ",
                'punjabi': "\nਗਵਾਹ ਵੇਰਵੇ: "
            }.get(language.lower(), "\nWitness Details: ")
            
            enhanced_details += f"{witness_header}{witness_details}"
            
        complaint_details = enhanced_details or complaint_details

    # If we have incident_date but not incident_day, try to derive it
    if incident_date and not incident_day:
        try:
            # Try to parse the date in various formats
            # Don't import datetime here - use the one imported at module level
            
            # Try multiple date formats
            date_formats = [
                '%Y-%m-%d', '%d-%m-%Y', '%m/%d/%Y', '%d/%m/%Y', 
                '%d %B %Y', '%d %b %Y',
                '%B %d, %Y', '%b %d, %Y'
            ]
            
            parsed_date = None
            for date_format in date_formats:
                try:
                    parsed_date = datetime.strptime(incident_date, date_format)
                    break
                except ValueError:
                    continue
            
            if parsed_date:
                # Get day of week in the appropriate language
                days_of_week = {
                    'english': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'],
                    'hindi': ['सोमवार', 'मंगलवार', 'बुधवार', 'गुरुवार', 'शुक्रवार', 'शनिवार', 'रविवार'],
                    'punjabi': ['ਸੋਮਵਾਰ', 'ਮੰਗਲਵਾਰ', 'ਬੁੱਧਵਾਰ', 'ਵੀਰਵਾਰ', 'ਸ਼ੁੱਕਰਵਾਰ', 'ਸ਼ਨੀਵਾਰ', 'ਐਤਵਾਰ']
                }
                
                weekday_index = parsed_date.weekday()
                incident_day = days_of_week.get(language.lower(), days_of_week['english'])[weekday_index]
        except Exception:
            # If any error occurs, leave incident_day as is
            pass

    # Format stolen properties if they're structured
    formatted_stolen_properties = format_stolen_properties(stolen_properties, language)

    # Format legal sections information more prominently
    if act1 and sections1:
        # Create a formatted legal sections detail that can be added to the complaint details
        legal_sections_info = {
            'english': f"\n\nApplicable Legal Sections:\n1. {act1} - Section {sections1}",
            'hindi': f"\n\nलागू कानूनी धाराएँ:\n1. {act1} - धारा {sections1}",
            'punjabi': f"\n\nਲਾਗੂ ਕਾਨੂੰਨੀ ਧਾਰਾਵਾਂ:\n1. {act1} - ਧਾਰਾ {sections1}"
        }.get(language.lower(), f"\n\nApplicable Legal Sections:\n1. {act1} - Section {sections1}")
        
        if act2 and sections2:
            legal_sections_info += f"\n2. {act2} - Section {sections2}"
        
        if act3 and sections3:
            legal_sections_info += f"\n3. {act3} - Section {sections3}"
        
        # If the complaint details don't already mention the legal sections, append them
        if complaint_details and "Section" not in complaint_details and "धारा" not in complaint_details and "ਧਾਰਾ" not in complaint_details:
            complaint_details += legal_sections_info

    # Get template for specified language or fallback to English
    template = FIR_TEMPLATES.get(language.lower(), FIR_TEMPLATES['english'])
    
    # Fill in the template
    current_datetime = datetime.now()
    
    # Define default values based on language
    default_placeholder = {
        'english': "",
        'hindi': "",
        'punjabi': ""
    }.get(language.lower(), "")
    
    # Set default values for empty fields with appropriate blank space instead of "[Not Provided]"
    fir_draft = template.format(
        year=current_datetime.year,
        current_date=current_datetime.strftime('%Y-%m-%d'),
        current_time=current_datetime.strftime('%H:%M'),
        victim_name=victim_name or default_placeholder,
        father_or_husband_name=father_or_husband_name or default_placeholder,
        dob=dob or default_placeholder,
        nationality=nationality or default_placeholder,
        occupation=occupation or default_placeholder,
        address=address or default_placeholder,
        incident_date=incident_date or default_placeholder,
        incident_time=incident_time or default_placeholder,
        incident_day=incident_day or default_placeholder,
        incident_location=incident_location or default_placeholder,
        complaint_details=complaint_details or default_placeholder,
        accused_details=accused_details or default_placeholder,
        stolen_properties=formatted_stolen_properties or default_placeholder,
        total_value=total_value or default_placeholder,
        inquest_report=inquest_report or default_placeholder,
        delay_reason=delay_reason or default_placeholder,
        act1=act1 or default_placeholder,
        sections1=sections1 or default_placeholder,
        act2=act2 or default_placeholder,
        sections2=sections2 or default_placeholder,
        act3=act3 or default_placeholder,
        sections3=sections3 or default_placeholder,
        other_acts=other_acts or default_placeholder,
        passport_details=passport_details or default_placeholder,
        distance_ps=distance_ps or default_placeholder,
        beat_no=beat_no or default_placeholder,
        outside_ps=outside_ps or default_placeholder
    )

    return fir_draft
