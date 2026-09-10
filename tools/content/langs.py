"""The languages the site is published in.

`code`     the URL prefix and the <html lang> value. "en" has no prefix.
`hreflang` what goes in <link rel="alternate" hreflang>. Kept separate from
           `code` because Google wants the plain ISO 639-1 tag here and the
           two only happen to match today.
`endonym`  the language's name written in the language itself. This is the
           only label the picker shows - a reader looking for Bengali is
           looking for the word "বাংলা", not for "Bengali".
`english`  the English name, for the title= on the picker links.
`sample`   a two-word phrase in the language, used in the small print of the
           picker so a reader can tell at a glance the pages are real.
"""

LANGS = [
    {"code": "en", "hreflang": "en-IN", "endonym": "English",   "english": "English",   "sample": "Read in English"},
    {"code": "hi", "hreflang": "hi-IN", "endonym": "हिन्दी",      "english": "Hindi",     "sample": "हिन्दी में पढ़ें"},
    {"code": "mr", "hreflang": "mr-IN", "endonym": "मराठी",      "english": "Marathi",   "sample": "मराठीत वाचा"},
    {"code": "bn", "hreflang": "bn-IN", "endonym": "বাংলা",       "english": "Bengali",   "sample": "বাংলায় পড়ুন"},
    {"code": "ta", "hreflang": "ta-IN", "endonym": "தமிழ்",       "english": "Tamil",     "sample": "தமிழில் படிக்க"},
    {"code": "te", "hreflang": "te-IN", "endonym": "తెలుగు",      "english": "Telugu",    "sample": "తెలుగులో చదవండి"},
    {"code": "kn", "hreflang": "kn-IN", "endonym": "ಕನ್ನಡ",       "english": "Kannada",   "sample": "ಕನ್ನಡದಲ್ಲಿ ಓದಿ"},
    {"code": "ml", "hreflang": "ml-IN", "endonym": "മലയാളം",     "english": "Malayalam", "sample": "മലയാളത്തിൽ വായിക്കുക"},
    {"code": "gu", "hreflang": "gu-IN", "endonym": "ગુજરાતી",     "english": "Gujarati",  "sample": "ગુજરાતીમાં વાંચો"},
    {"code": "pa", "hreflang": "pa-IN", "endonym": "ਪੰਜਾਬੀ",      "english": "Punjabi",   "sample": "ਪੰਜਾਬੀ ਵਿੱਚ ਪੜ੍ਹੋ"},
    {"code": "or", "hreflang": "or-IN", "endonym": "ଓଡ଼ିଆ",       "english": "Odia",      "sample": "ଓଡ଼ିଆରେ ପଢ଼ନ୍ତୁ"},
    {"code": "as", "hreflang": "as-IN", "endonym": "অসমীয়া",     "english": "Assamese",  "sample": "অসমীয়াত পঢ়ক"},
]

CODES = [l["code"] for l in LANGS]
BY_CODE = {l["code"]: l for l in LANGS}
