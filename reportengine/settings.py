from django.conf import settings

ASYNC_REPORTS = getattr(settings, "ASYNC_REPORTS", False)
STALE_REPORT_SECONDS = getattr(settings, "STALE_REPORT_SECONDS", 6*60*60)
MAX_ROWS_FOR_QUICK_EXPORT = getattr(settings, "MAX_ROWS_FOR_QUICK_EXPORT", 1000)
