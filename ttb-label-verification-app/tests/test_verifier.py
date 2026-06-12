from verifier import check_government_warning, find_best_score, verify_label


def test_exact_brand_match_passes():
    assert find_best_score("OLD TOM DISTILLERY", "Label: OLD TOM DISTILLERY Bourbon") == 1.0


def test_minor_case_difference_passes():
    score = find_best_score("Stone's Throw", "STONE'S THROW Kentucky Bourbon")
    assert score >= 0.9


def test_government_warning_present_passes():
    text = "GOVERNMENT WARNING: (1) ACCORDING TO THE SURGEON GENERAL, WOMEN SHOULD NOT DRINK ALCOHOLIC BEVERAGES DURING PREGNANCY BECAUSE OF THE RISK OF BIRTH DEFECTS. (2) CONSUMPTION OF ALCOHOLIC BEVERAGES IMPAIRS YOUR ABILITY TO DRIVE A CAR OR OPERATE MACHINERY, AND MAY CAUSE HEALTH PROBLEMS."
    result = check_government_warning(text)
    assert result.status == "Pass"


def test_missing_warning_fails():
    result = check_government_warning("OLD TOM DISTILLERY 750 mL")
    assert result.status == "Fail"


def test_verify_label_overall_pass():
    text = """OLD TOM DISTILLERY
Kentucky Straight Bourbon Whiskey
45% Alc./Vol. (90 Proof)
750 mL
Bottled by Old Tom Distillery, Louisville, KY
GOVERNMENT WARNING: (1) ACCORDING TO THE SURGEON GENERAL, WOMEN SHOULD NOT DRINK ALCOHOLIC BEVERAGES DURING PREGNANCY BECAUSE OF THE RISK OF BIRTH DEFECTS. (2) CONSUMPTION OF ALCOHOLIC BEVERAGES IMPAIRS YOUR ABILITY TO DRIVE A CAR OR OPERATE MACHINERY, AND MAY CAUSE HEALTH PROBLEMS.
"""
    data = {
        "brand_name": "OLD TOM DISTILLERY",
        "class_type": "Kentucky Straight Bourbon Whiskey",
        "alcohol_content": "45% Alc./Vol. (90 Proof)",
        "net_contents": "750 mL",
        "producer_address": "Old Tom Distillery, Louisville, KY",
    }
    report = verify_label(text, data)
    assert report["overall_status"] == "Pass"
