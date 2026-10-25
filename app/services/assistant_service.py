# Keyword-based symptom matcher. Rule-based: no AI model invents causes,
# it only returns pre-written, structured guidance per matched category.

RULES = [
    {
        "keywords": ["boll", "ochha", "kapas ochu", "production low", "low yield", "yield ochu"],
        "category": "Low Boll / Yield Production",
        "possible_causes": [
            "Inadequate pollination or flower drop",
            "Nutrient deficiency (especially potassium or boron)",
            "Water stress (too little or too much irrigation)",
            "Pest damage to flowers/bolls (e.g., bollworm)",
        ],
        "need_info": ["Crop age", "Irrigation schedule", "Recent fertilizer applied", "A photo of the plant/boll"],
    },
    {
        "keywords": ["curl", "curling", "vaadi", "leaves curl", "pandda"],
        "category": "Leaf Curling",
        "possible_causes": [
            "Cotton Leaf Curl Virus (spread by whitefly)",
            "Herbicide drift damage",
            "Water stress",
        ],
        "need_info": ["A clear close-up photo of an affected leaf", "Whether nearby plants show the same symptom"],
    },
    {
        "keywords": ["yellow", "pilа", "piлу", "yellowing"],
        "category": "Yellowing Leaves",
        "possible_causes": [
            "Nitrogen deficiency",
            "Overwatering or poor drainage",
            "Natural aging of lower leaves",
        ],
        "need_info": ["Which leaves are yellow (old/new)", "Recent rainfall or irrigation", "A photo"],
    },
    {
    "keywords": ["pest", "keeda", "jivat", "insect", "hole", "chewed",
                 "ant", "mungh", "kidi", "bug", "worm"],
        "category": "Pest / Insect Damage",
        "possible_causes": [
            "Leaf hopper / jassid feeding",
            "Bollworm or other chewing insect",
        ],
        "need_info": ["A photo showing the damage pattern", "Whether insects are visible on the plant"],
    },
    {
        "keywords": ["slow growth", "growth dhimu", "not growing", "stunted", "vikas"],
        "category": "Slow / Stunted Growth",
        "possible_causes": [
            "Soil nutrient deficiency",
            "Compacted or poor-quality soil",
            "Root damage or waterlogging",
        ],
        "need_info": ["Soil type", "Last soil test or fertilizer used", "Crop age"],
    },
    {
        "keywords": ["flower", "khari", "falling", "flower drop"],
        "category": "Flowers Falling",
        "possible_causes": [
            "Heat or water stress during flowering",
            "Nutrient imbalance",
            "Pest damage to flower buds",
        ],
        "need_info": ["Recent weather conditions", "Irrigation frequency"],
    },
]


def match_symptom(message: str):
    """Keyword match: returns the best-matching rule dict, or None."""
    text = message.lower()
    for rule in RULES:
        if any(kw in text for kw in rule["keywords"]):
            return rule
    return None


def build_response(message: str, farm_context: dict = None):
    """Builds a structured, non-committal response. Never invents a confirmed
    diagnosis or a treatment dosage — only points to next steps and the
    existing Plant Analysis / Soil Analysis modules."""
    rule = match_symptom(message)

    if rule is None:
        return (
            "I couldn't match your message to a known symptom category. "
            "You can describe it differently, or use the **Plant Analysis** "
            "page to upload a photo, or the **Soil Analysis** page for "
            "nutrient-related questions."
        )

    lines = [f"**Possible topic: {rule['category']}**\n"]
    lines.append("Possible causes (not a confirmed diagnosis):")
    for c in rule["possible_causes"]:
        lines.append(f"- {c}")
    lines.append("\nTo help narrow this down, it would help to know:")
    for info in rule["need_info"]:
        lines.append(f"- {info}")

    if farm_context and farm_context.get("last_plant_analysis"):
        la = farm_context["last_plant_analysis"]
        lines.append(
            f"\nℹ️ Your most recent Plant Analysis for this farm found: "
            f"**{la['predicted_class']}** ({la['confidence']}% confidence, "
            f"{la['created_at']}). This may or may not be related."
        )

    lines.append(
        "\nFor a more specific answer, use **Plant Analysis** (upload a photo) "
        "or **Soil Analysis**, and consult a local agricultural expert before "
        "taking any action."
    )
    return "\n".join(lines)