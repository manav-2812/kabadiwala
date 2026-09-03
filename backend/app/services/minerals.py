from typing import Dict, List, Any

# Recovery efficiencies: 0.85 for base metals, 0.70 for precious / critical
EFFICIENCIES: Dict[str, float] = {
    "cu": 0.85, # Copper
    "sn": 0.85, # Tin
    "pb": 0.85, # Lead
    "al": 0.85, # Aluminium
    "fe": 0.85, # Iron
    "au": 0.70, # Gold
    "ag": 0.70, # Silver
    "pd": 0.70, # Palladium
    "co": 0.70, # Cobalt
    "li": 0.70, # Lithium
    "nd": 0.70  # Neodymium (rare earth)
}

ELEMENT_NAMES: Dict[str, Dict[str, str]] = {
    "cu": {"name_en": "Copper", "name_hi": "तांबा", "name_pa": "ਤਾਂਬਾ", "strategic": True, "color": "#B87333"},
    "au": {"name_en": "Gold", "name_hi": "सोना", "name_pa": "ਸੋਨਾ", "strategic": True, "color": "#FFD700"},
    "ag": {"name_en": "Silver", "name_hi": "चांदी", "name_pa": "ਚਾਂਦੀ", "strategic": True, "color": "#C0C0C0"},
    "co": {"name_en": "Cobalt", "name_hi": "कोबाल्ट", "name_pa": "ਕੋਬਾਲਟ", "strategic": True, "color": "#0047AB"},
    "li": {"name_en": "Lithium", "name_hi": "लिथियम", "name_pa": "ਲਿਥੀਅਮ", "strategic": True, "color": "#9370DB"},
    "nd": {"name_en": "Neodymium", "name_hi": "नियोडिमियम", "name_pa": "ਨਿਓਡੀਮੀਅਮ", "strategic": True, "color": "#20B2AA"},
    "sn": {"name_en": "Tin", "name_hi": "टिन", "name_pa": "ਟਿਨ", "strategic": False, "color": "#708090"},
    "pd": {"name_en": "Palladium", "name_hi": "पैलेडियम", "name_pa": "ਪੈਲੇਡੀਅਮ", "strategic": True, "color": "#4682B4"},
    "al": {"name_en": "Aluminium", "name_hi": "एल्युमिनियम", "name_pa": "ਐਲੂਮੀਨੀਅਮ", "strategic": False, "color": "#A9A9A9"},
    "fe": {"name_en": "Iron", "name_hi": "लोहा", "name_pa": "ਲੋਹਾ", "strategic": False, "color": "#8B4513"}
}

def calculate_recoverable_minerals(
    items_composition: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    items_composition: list of dicts with:
