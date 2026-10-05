def nutrient_status(n, p, k):
    """Crop Recommendation dataset na N/P/K range par aadharit thresholds."""
    def level(value, low, high):
        if value < low:
            return "Low"
        elif value > high:
            return "High"
        return "Medium"

    return {
        "N": level(n, 40, 80),
        "P": level(p, 30, 70),
        "K": level(k, 30, 70),
    }


def ph_interpretation(ph):
    if ph < 5.5:
        return "Acidic", "Soil is acidic. Most crops prefer pH 6.0–7.5; consider a soil test and locally recommended lime application."
    elif ph > 7.5:
        return "Alkaline", "Soil is alkaline. This can limit nutrient availability for many crops; consider a soil test for correction options."
    return "Neutral", "pH is in a generally suitable range for most crops."


def generate_summary(status, ph_label):
    notes = []
    for nutrient, level in status.items():
        if level == "Low":
            notes.append(f"{nutrient} availability may be limiting.")
        elif level == "High":
            notes.append(f"{nutrient} is on the higher side; avoid over-application.")
    if not notes:
        notes.append("N, P, and K levels appear balanced.")
    notes.append(f"Soil pH is {ph_label.lower()}.")
    notes.append("Consider getting a soil test and follow locally recommended nutrient management.")
    return " ".join(notes)


def analyze_soil(n, p, k, ph, moisture=None, soil_type=None):
    status = nutrient_status(n, p, k)
    ph_label, ph_note = ph_interpretation(ph)
    return {
        "nutrient_status": status,
        "ph_label": ph_label,
        "ph_note": ph_note,
        "moisture": moisture,
        "soil_type": soil_type,
        "summary": generate_summary(status, ph_label),
    }