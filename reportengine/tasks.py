from celery.decorators import task
from models import ReportRequest
import reportengine

@task()
def async_report(token):
   
    try:
        report_request = ReportRequest.objects.get(token=token)
    except ReportRequest.DoesNotExist:
        # Error?
        return 
    # THis is like 90% the same 
    reportengine.autodiscover() ## Populate the reportengine registry
    report_request.build_report()

@task()
def cleanup_stale_reports():
    ReportRequest.objects.cleanup_stale_requests()
