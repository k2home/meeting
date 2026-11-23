"""WCAG contrast helpers for organization-defined button colors."""
MINIMUM_CONTRAST = 4.5
DARK_TEXT = "#243247"
BLACK_TEXT = "#000000"
WHITE_TEXT = "#FFFFFF"

def _rgb(value):
    value = (value or "").strip().lstrip("#")
    if len(value) != 6:
        value = "00549F"
    try:
        return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4))
    except ValueError:
        return (0, 84, 159)

def _hex(rgb):
    return "#{:02X}{:02X}{:02X}".format(*(max(0, min(255, round(v))) for v in rgb))

def _luminance(rgb):
    channels = [v / 255 for v in rgb]
    linear = [v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4 for v in channels]
    return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]

def contrast_ratio(foreground, background):
    first, second = sorted((_luminance(_rgb(foreground)), _luminance(_rgb(background))), reverse=True)
    return (first + 0.05) / (second + 0.05)

def accessible_button_colors(background):
    """Preserve the configured background and choose a WCAG AA text color."""
    original = _hex(_rgb(background))
    foreground = max(
        (WHITE_TEXT, DARK_TEXT, BLACK_TEXT),
        key=lambda color: contrast_ratio(color, original),
    )
    ratio = contrast_ratio(foreground, original)
    return {"background": original, "text": foreground,
            "contrast": round(ratio, 2), "meets_wcag_aa": ratio >= MINIMUM_CONTRAST}
