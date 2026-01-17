"""
Supabase configuration and pre-filtering rules for bike event classification.

Based on BIKE_FLAGGING_IMPLEMENTATION_GUIDE.md
"""

# Supabase project configuration
SUPABASE_PROJECT_ID = "exsoepsvmoseapulforp"

# Pre-filtering rules based on service_name categories

DEFINITELY_EXCLUDE = {
    # Container/waste management (never bike-infrastructure)
    'Altkleidercontainer voll',
    'Altkleidercontainer defekt',
    'Altkleidercontainer-Standort vermüllt',
    'Glascontainer voll',
    'Glascontainer defekt',
    'Glascontainer-Standort vermüllt',

    # Street lighting (rarely bike-specific unless "Radweg" mentioned)
    'Leuchtmittel defekt',
    'Leuchtmittel tagsüber in Betrieb',
    'Lichtmast defekt',

    # Other infrastructure (not bike-related)
    'Parkscheinautomat defekt',
    'Brunnen',
    'Kölner Grün',
    'Spiel- und Bolzplätze',
    'Graffiti',

    # Objects (not infrastructure)
    'Schrottfahrräder',  # Abandoned bikes as objects
    'Schrott-Kfz',       # Abandoned cars
}

HIGH_POTENTIAL = {
    'Defekte Oberfläche',
    'Straßenmarkierung',
    'Defekte Verkehrszeichen',
    'Radfahrerampel defekt',
    'Umlaufsperren / Drängelgitter',
    'Straßenbaustellen',
}

MEDIUM_POTENTIAL = {
    'Wilder Müll',
    'Gully verstopft',
    'Fußgängerampel defekt',
    'Kfz-Ampel defekt',
    'Zu lange Rotzeit',
    'Zu kurze Grünzeit',
    'Schutzzeit zu kurz',
    'Keine grüne Welle',
}


def should_check_with_llm(service_name: str, description: str | None) -> tuple[bool, str]:
    """
    Decide if event needs LLM classification.

    Args:
        service_name: Event category (service_name field)
        description: Event description text

    Returns:
        Tuple of (should_check, reason)
    """
    # No description → cannot classify
    if not description or not description.strip():
        return False, "no_description"

    # Definitely exclude → skip LLM
    if service_name in DEFINITELY_EXCLUDE:
        return False, f"excluded_category: {service_name}"

    # High or medium potential → check with LLM
    if service_name in HIGH_POTENTIAL:
        return True, "high_potential"

    if service_name in MEDIUM_POTENTIAL:
        return True, "medium_potential"

    # Unknown category → check with LLM to be safe
    return True, "unknown_category"
