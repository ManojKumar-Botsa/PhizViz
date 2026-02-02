"""Detection-only macro inference. No document execution."""


def detect_macros(filename: str, explicit_macro_flag=None):
    """
    Returns a simple dictionary indicating whether macros are suspected.
    - Trusts an explicit client-provided flag when given.
    - Otherwise infers from filename conventions (e.g., .docm).
    """
    lower = (filename or "").lower()

    if explicit_macro_flag is not None:
        return {
            "suspected_macros": bool(explicit_macro_flag),
            "reason": "Client provided macro presence hint."
        }

    if lower.endswith(".docm"):
        return {
            "suspected_macros": True,
            "reason": "Macro-enabled Word document (.docm)."
        }

    return {
        "suspected_macros": False,
        "reason": "No macro indicators from filename."
    }

