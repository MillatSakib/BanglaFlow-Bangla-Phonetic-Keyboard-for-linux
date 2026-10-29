"""Unit tests for the pure phonetic engine."""

from banglaflow.phonetic import PhoneticEngine
from banglaflow.unicode_utils import validate_bengali


def test_required_spec_examples():
    engine = PhoneticEngine(map_dari=True)

    # 1. ami -> আমি (\u0986\u09AE\u09BF)
    assert engine.convert("ami") == "\u0986\u09AE\u09BF"

    # 2. bangla -> বাংলা (\u09AC\u09BE\u0982\u09B2\u09BE)
    assert engine.convert("bangla") == "\u09AC\u09BE\u0982\u09B2\u09BE"

    # 3. banglay -> বাংলায় (\u09AC\u09BE\u0982\u09B2\u09BE\u09DF)
    assert engine.convert("banglay") == "\u09AC\u09BE\u0982\u09B2\u09BE\u09DF"

    # 4. likhi -> লিখি (\u09B2\u09BF\u0996\u09BF)
    assert engine.convert("likhi") == "\u09B2\u09BF\u0996\u09BF"

    # 5. bhaSha -> ভাষা (\u09AD\u09BE\u09B7\u09BE)
    assert engine.convert("bhaSha") == "\u09AD\u09BE\u09B7\u09BE"

    # 6. amar -> আমার (\u0986\u09AE\u09BE\u09B0)
    assert engine.convert("amar") == "\u0986\u09AE\u09BE\u09B0"


def test_vowels_independent_and_dependent():
    engine = PhoneticEngine()

    # Independent at word start
    assert engine.convert("o") == "অ"
    assert engine.convert("a") == "আ"
    assert engine.convert("i") == "ই"
    assert engine.convert("I") == "ঈ"
    assert engine.convert("u") == "উ"
    assert engine.convert("U") == "ঊ"
    assert engine.convert("rri") == "ঋ"
    assert engine.convert("e") == "এ"
    assert engine.convert("OI") == "ঐ"
    assert engine.convert("O") == "ও"
    assert engine.convert("OU") == "ঔ"

    # Dependent Kar after consonant
    assert engine.convert("ka") == "কা"
    assert engine.convert("ki") == "কি"
    assert engine.convert("kI") == "কী"
    assert engine.convert("ku") == "কু"
    assert engine.convert("kU") == "কূ"
    assert engine.convert("krri") == "কৃ"
    assert engine.convert("ke") == "কে"
    assert engine.convert("kOI") == "কৈ"
    assert engine.convert("kO") == "কো"
    assert engine.convert("ko") == "ক"  # Inherent vowel o produces base consonant
    assert engine.convert("kOU") == "কৌ"


def test_common_conjuncts():
    engine = PhoneticEngine()

    # ক্ষ (kkh / ksh)
    assert engine.convert("kkhoma") == "ক্ষমা"
    # জ্ঞ (ggan / jn)
    assert engine.convert("ggan") == "জ্ঞান"
    # ন্ত (nt)
    assert engine.convert("shanto") == "শান্ত"
    # ন্দ (nd)
    assert engine.convert("sundor") == "সুন্দর"
    # ম্প (mp)
    assert engine.convert("somporko") == "সম্পরক"
    # স্ত (st)
    assert engine.convert("rasta") == "রাস্তা"
    # ত্র (tr)
    assert engine.convert("chatro") == "ছাত্র"
    # দ্র (dr)
    assert engine.convert("druto") == "দ্রুত"
    # প্র (pr)
    assert engine.convert("prothom") == "প্রথম"
    # ব্র (br) - র-ফলা
    assert engine.convert("broto") == "ব্রত"
    # গ্র (gr) - র-ফলা
    assert engine.convert("gram") == "গ্রাম"
    # ঋ-কার + ষ্ট
    assert engine.convert("brriShTi") == "বৃষ্টি"


def test_reph_and_phala():
    engine = PhoneticEngine()

    # Reph: rr before consonant -> র্ক, র্ম, ইত্যাদি
    assert engine.convert("torrko") == "তর্ক"
    assert engine.convert("korrmo") == "কর্ম"
    assert engine.convert("somporrko") == "সম্পর্ক"
    # Bakya: ky -> ক্য (ক + ্ + য)
    assert engine.convert("bakyo") == "বাক্য"


def test_punctuation_and_symbols():
    engine = PhoneticEngine(map_dari=True)

    assert engine.convert("Taka $100.") == "টাকা ৳১০০।"
    assert engine.convert("ki?") == "কি?"
    assert engine.convert("bah!") == "বাহ!"
    assert engine.convert("ami, tumi.") == "আমি, তুমি।"


def test_all_outputs_pass_bengali_validator():
    engine = PhoneticEngine(map_dari=True)
    words = [
        "ami", "tumi", "she", "amader", "bangla", "bangladesh",
        "shonar", "desh", "dhaka", "khulna", "rajshahi", "shanti",
        "kkhoma", "shikkha", "bhaSha", "bhasha", "bakyo", "sahityo"
    ]
    for w in words:
        out = engine.convert(w)
        valid, reason = validate_bengali(out)
        assert valid, f"Output '{out}' for input '{w}' failed validation: {reason}"
