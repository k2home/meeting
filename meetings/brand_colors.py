"""WCAG contrast helpers for organization-defined button colors."""
MINIMUM_CONTRAST = 4.5
DARK_TEXT = "#243247"
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
    """Return a minimally adjusted background and legible foreground (WCAG AA)."""
    original = _rgb(background)
    candidates = [(WHITE_TEXT, contrast_ratio(WHITE_TEXT, _hex(original))),
                  (DARK_TEXT, contrast_ratio(DARK_TEXT, _hex(original)))]
    foreground, ratio = max(candidates, key=lambda item: item[1])
    if ratio >= MINIMUM_CONTRAST:
        return {"background": _hex(original), "text": foreground, "contrast": round(ratio, 2)}
    target = (0, 0, 0) if foreground == WHITE_TEXT else (255, 255, 255)
    low, high = 0.0, 1.0
    for _ in range(24):
        amount = (low + high) / 2
        candidate = tuple(original[i] + (target[i] - original[i]) * amount for i in range(3))
        if contrast_ratio(foreground, _hex(candidate)) >= MINIMUM_CONTRAST:
            high = amount
        else:
            low = amount
    adjusted = tuple(original[i] + (target[i] - original[i]) * high for i in range(3))
    result = _hex(adjusted)
    return {"background": result, "text": foreground, "contrast": round(contrast_ratio(foreground, result), 2)}
