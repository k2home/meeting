from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _


class PasswordComplexityValidator:
    """Require lowercase, uppercase and a non-alphanumeric character."""

    def validate(self, password, user=None):
        errors = []
        if not any(char.islower() for char in password):
            errors.append(_("Das Passwort muss mindestens einen Kleinbuchstaben enthalten."))
        if not any(char.isupper() for char in password):
            errors.append(_("Das Passwort muss mindestens einen Großbuchstaben enthalten."))
        if not any(not char.isalnum() for char in password):
            errors.append(_("Das Passwort muss mindestens ein Sonderzeichen enthalten."))
        if errors:
            raise ValidationError(errors)

    def get_help_text(self):
        return _("Das Passwort muss mindestens einen Kleinbuchstaben, einen Großbuchstaben und ein Sonderzeichen enthalten.")
