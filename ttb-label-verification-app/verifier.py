import re
from dataclasses import dataclass, asdict
from difflib import SequenceMatcher
from typing import Dict, List, Optional

STANDARD_WARNING = (
    "GOVERNMENT WARNING: (1) ACCORDING TO THE SURGEON GENERAL, WOMEN SHOULD NOT "
    "DRINK ALCOHOLIC BEVERAGES DURING PREGNANCY BECAUSE OF THE RISK OF BIRTH "
    "DEFECTS. (2) CONSUMPTION OF ALCOHOLIC BEVERAGES IMPAIRS YOUR ABILITY TO DRIVE "
    "A CAR OR OPERATE MACHINERY, AND MAY CAUSE HEALTH PROBLEMS."
)

FIELD_LABELS = {
    "brand_name": "Brand Name",
    "class_type": "Class/Type",
    "alcohol_content": "Alcohol Content",
    "net_contents": "Net Contents",
    "producer_address": "Producer/Bottler Name and Address",
    "country_of_origin": "Country of Origin",
}

@dataclass
class CheckResult:
    field: str
    expected: str
    status: str
    confidence: float
    message: str


def normalize_text(value: str) -> str:
    if not value:
        return ""
    value = value.upper()
    value = value.replace("\u2019", "'").replace("\u2018", "'")
    value = re.sub(r"[^A-Z0-9.%/()' -]+", " ", value)
    value = re.sub(r"\s+", " ", value).strip()
    return value


def similarity(a: str, b: str) -> float:
    a_norm = normalize_text(a)
    b_norm = normalize_text(b)
    if not a_norm or not b_norm:
        return 0.0
    if a_norm in b_norm:
        return 1.0
    return SequenceMatcher(None, a_norm, b_norm).ratio()


def find_best_score(expected: str, label_text: str) -> float:
    expected_norm = normalize_text(expected)
    label_norm = normalize_text(label_text)
    if not expected_norm or not label_norm:
        return 0.0
    if expected_norm in label_norm:
        return 1.0
    # Compare against sliding windows so a field can match inside a long label.
    words = label_norm.split()
    expected_words = expected_norm.split()
    window = max(1, len(expected_words) + 3)
    best = similarity(expected_norm, label_norm)
    for i in range(len(words)):
        candidate = " ".join(words[i:i + window])
        best = max(best, similarity(expected_norm, candidate))
    return round(best, 3)


def classify_score(score: float, required: bool = True) -> str:
    if score >= 0.90:
        return "Pass"
    if score >= 0.72:
        return "Review"
    return "Fail" if required else "Not Found"


def verify_expected_fields(label_text: str, application_data: Dict[str, str]) -> List[CheckResult]:
    results: List[CheckResult] = []
    for key, label in FIELD_LABELS.items():
        expected = (application_data.get(key) or "").strip()
        if not expected:
            continue
        score = find_best_score(expected, label_text)
        status = classify_score(score, required=(key != "country_of_origin"))
        if status == "Pass":
            msg = f"{label} appears to match the label text."
        elif status == "Review":
            msg = f"{label} may match, but the wording differs and should be reviewed."
        else:
            msg = f"{label} was not found or appears inconsistent with the label text."
        results.append(CheckResult(label, expected, status, score, msg))
    return results


def check_government_warning(label_text: str) -> CheckResult:
    label_norm = normalize_text(label_text)
    warning_norm = normalize_text(STANDARD_WARNING)
    all_caps_present = "GOVERNMENT WARNING:" in label_text
    score = find_best_score(STANDARD_WARNING, label_text)
    if warning_norm in label_norm and all_caps_present:
        return CheckResult("Government Health Warning", STANDARD_WARNING, "Pass", 1.0, "Required government warning text appears present with the required all-caps heading.")
    if score >= 0.82:
        return CheckResult("Government Health Warning", STANDARD_WARNING, "Review", score, "Warning statement appears similar but may not be exact. Review capitalization, wording, and formatting.")
    return CheckResult("Government Health Warning", STANDARD_WARNING, "Fail", score, "Required government warning statement was not found or is materially different.")


def extract_common_patterns(label_text: str) -> Dict[str, Optional[str]]:
    abv = re.search(r"\b\d{1,2}(?:\.\d+)?\s*%\s*(?:ALC\.?/VOL\.?|ABV)?\b", label_text, re.IGNORECASE)
    proof = re.search(r"\b\d{2,3}\s*PROOF\b", label_text, re.IGNORECASE)
    net = re.search(r"\b(?:750\s?ML|375\s?ML|1\s?L|1\.75\s?L|12\s?FL\.?\s?OZ|16\s?FL\.?\s?OZ)\b", label_text, re.IGNORECASE)
    return {
        "detected_alcohol_content": " ".join(x.group(0) for x in [abv, proof] if x) or None,
        "detected_net_contents": net.group(0) if net else None,
    }


def verify_label(label_text: str, application_data: Dict[str, str]) -> Dict:
    field_results = verify_expected_fields(label_text, application_data)
    warning_result = check_government_warning(label_text)
    all_results = field_results + [warning_result]
    counts = {"Pass": 0, "Review": 0, "Fail": 0, "Not Found": 0}
    for item in all_results:
        counts[item.status] = counts.get(item.status, 0) + 1
    overall = "Pass"
    if counts.get("Fail", 0) > 0:
        overall = "Fail"
    elif counts.get("Review", 0) > 0 or counts.get("Not Found", 0) > 0:
        overall = "Review"
    return {
        "overall_status": overall,
        "summary": counts,
        "detected_patterns": extract_common_patterns(label_text),
        "results": [asdict(r) for r in all_results],
    }
