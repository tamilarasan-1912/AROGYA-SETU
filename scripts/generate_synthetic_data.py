"""Generate synthetic demo triage data across the supported Indian languages.

This data is artificial and must never be presented as clinical validation data.
"""
import csv
import random
from pathlib import Path

random.seed(42)

LANGUAGE_EXAMPLES = {
    "en": ["fever and cough", "mild headache", "persistent vomiting", "chest pain and difficulty breathing"],
    "as": ["জ্বৰ আৰু কাহ", "মূৰৰ বিষ", "বাৰে বাৰে বমি", "বুকুৰ বিষ আৰু উশাহ লোৱাত অসুবিধা"],
    "bn": ["জ্বর এবং কাশি", "হালকা মাথাব্যথা", "বারবার বমি", "বুকে ব্যথা এবং শ্বাসকষ্ট"],
    "brx": ["बुखार आरो खांसी", "फिसा दुख", "बायदि उल्टी", "आथिं दुख आरो सांस लाबोनो जिब जाबाय"],
    "doi": ["बुखार ते खांसी", "हल्का सिर दर्द", "बार बार उल्टी", "छाती च पीड़ ते सांस लैने च दिक्कत"],
    "gu": ["તાવ અને ઉધરસ", "હળવો માથાનો દુખાવો", "વારંવાર ઉલટી", "છાતીમાં દુખાવો અને શ્વાસ લેવામાં તકલીફ"],
    "hi": ["बुखार और खांसी", "हल्का सिरदर्द", "बार बार उल्टी", "सीने में दर्द और सांस लेने में कठिनाई"],
    "kn": ["ಜ್ವರ ಮತ್ತು ಕೆಮ್ಮು", "ಸೌಮ್ಯ ತಲೆನೋವು", "ಪದೇ ಪದೇ ವಾಂತಿ", "ಎದೆ ನೋವು ಮತ್ತು ಉಸಿರಾಟದ ತೊಂದರೆ"],
    "gom": ["ताप आनी खोकलो", "सौम्य डोकेदुखी", "वारंवार उलटी", "छातीत दुखप आनी श्वास घेवपाक त्रास"],
    "ks": ["تَپھ تہٕ کھانسی", "ہلکا سر درد", "بار بار قے", "سینس منز درد تہٕ ساس لیونٛگ منز دقت"],
    "mai": ["ज्वर आ खाँसी", "हल्का माथाक दर्द", "बार बार बान्ति", "छातीमे दर्द आ साँस लेबामे कठिनाइ"],
    "ml": ["പനിയും ചുമയും", "ലഘുവായ തലവേദന", "തുടർച്ചയായ ഛർദ്ദി", "നെഞ്ചുവേദനയും ശ്വാസതടസ്സവും"],
    "mr": ["ताप आणि खोकला", "सौम्य डोकेदुखी", "वारंवार उलटी", "छातीत दुखणे आणि श्वास घेण्यास त्रास"],
    "mni": ["নুমিৎ অমসুং কাহ", "মাথা চুন্নবা", "ৱারৱার ৱান্তি", "থাংগোল অমসুং শ্বাস লাবদা যাম্না ফত্তবা"],
    "ne": ["ज्वरो र खोकी", "हल्का टाउको दुखाइ", "बारम्बार बान्ता", "छाती दुख्ने र सास फेर्न गाह्रो"],
    "or": ["ଜ୍ୱର ଏବଂ କାଶ", "ହାଲୁକା ମୁଣ୍ଡବିନ୍ଧା", "ବାରମ୍ବାର ବାନ୍ତି", "ଛାତି ଯନ୍ତ୍ରଣା ଏବଂ ଶ୍ୱାସକଷ୍ଟ"],
    "pa": ["ਬੁਖਾਰ ਅਤੇ ਖੰਘ", "ਹਲਕਾ ਸਿਰ ਦਰਦ", "ਵਾਰ ਵਾਰ ਉਲਟੀ", "ਛਾਤੀ ਵਿੱਚ ਦਰਦ ਅਤੇ ਸਾਹ ਲੈਣ ਵਿੱਚ ਮੁਸ਼ਕਲ"],
    "sa": ["ज्वरः कासश्च", "मन्दं शिरःशूलम्", "पुनः पुनः वमनम्", "वक्षसि पीडा श्वासकठिनता च"],
    "sat": ["ज्वर आर खाँसी", "माथा बेदना", "बार बार उलटी", "छाती बेदना आर साँस रे आसुबिधा"],
    "snd": ["بخار ۽ کنگهه", "هلڪو مٿي جو سور", "بار بار الٽي", "ڇاتي ۾ سور ۽ ساهه کڻڻ ۾ تڪليف"],
    "ta": ["காய்ச்சல் மற்றும் இருமல்", "லேசான தலைவலி", "தொடர்ந்து வாந்தி", "மார்பு வலி மற்றும் மூச்சுத்திணறல்"],
    "te": ["జ్వరం మరియు దగ్గు", "తేలికపాటి తలనొప్పి", "తరచుగా వాంతులు", "ఛాతీ నొప్పి మరియు శ్వాస తీసుకోవడంలో ఇబ్బంది"],
    "ur": ["بخار اور کھانسی", "ہلکا سر درد", "بار بار قے", "سینے میں درد اور سانس لینے میں دشواری"],
}

rows = []
for language, examples in LANGUAGE_EXAMPLES.items():
    for _ in range(40):
        symptom = random.choice(examples)
        emergency = symptom == examples[-1]
        if emergency:
            label = "LEVEL_1_EMERGENCY"
        elif symptom in (examples[2],):
            label = "LEVEL_2_URGENT"
        elif symptom in (examples[1],):
            label = "LEVEL_4_ROUTINE"
        else:
            label = "LEVEL_3_PRIMARY_CARE"
        rows.append({"text": symptom, "language": language, "label": label})

random.shuffle(rows)
out = Path(__file__).resolve().parents[1] / "data" / "synthetic_triage_generated.csv"
out.parent.mkdir(exist_ok=True)
with out.open("w", newline="", encoding="utf-8") as handle:
    writer = csv.DictWriter(handle, fieldnames=["text", "language", "label"])
    writer.writeheader()
    writer.writerows(rows)

print(f"Generated {len(rows)} synthetic examples at {out}")
