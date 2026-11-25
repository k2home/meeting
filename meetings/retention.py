from datetime import date

from .models import OrganizationSettings


def effective_retention_years(topic=None):
    if topic is not None and topic.retention_years:
        return topic.retention_years
    organization = OrganizationSettings.objects.only("retention_years").filter(pk=1).first()
    return organization.retention_years if organization else 10


def retention_expiry_date(reference_date, years):
    """Return 31 December of the Nth calendar year after the reference year."""
    if not reference_date or not years:
        return None
    return date(reference_date.year + int(years), 12, 31)


def topic_deletion_date(topic):
    if topic.status != "archived" or not topic.archived_at:
        return None
    years = getattr(topic, "retention_effective_years", None) or effective_retention_years(topic)
    return retention_expiry_date(topic.archived_at, years)


def protocol_deletion_date(meeting, topic):
    if not meeting.finalized_at:
        return None
    years = getattr(topic, "retention_effective_years", None) or effective_retention_years(topic)
    return retention_expiry_date(meeting.date, years)
