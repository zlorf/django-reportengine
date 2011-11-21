from celery.decorators import task
from models import ReportRequest, ReportRequestRow
import reportengine
import datetime

@task()
def async_report(token):
   
    try:
        report_request = ReportRequest.objects.get(token=token)
    except ReportRequest.DoesNotExist:
        # Error?
        return 


    kwargs = report_request.params

    # THis is like 90% the same 
    reportengine.autodiscover() ## Populate the reportengine registry
    try:
        report = report_request.get_report()
    except Exception, err:
        raise err  
    
    filter_form = report.get_filter_form(kwargs)
    if filter_form.fields:
        if filter_form.is_valid():
            filters = filter_form.cleaned_data
        else:
            filters = {}
    else:
        if report.allow_unspecified_filters:
            filters = kwargs
        else:
            filters = {}
    
    # Remove blank filters
    for k in filters.keys():
        if filters[k] == '':
            del filters[k]
    
    ## Update the mask and run the report!
    mask = report.get_default_mask()
    mask.update(filters)
    rows, aggregates = report.get_rows(mask, order_by=kwargs.get('order_by',None))
    
    ReportRequestRow.objects.filter(report_request=report_request).delete()
    
    for index, row in enumerate(rows):
        report_row = ReportRequestRow(report_request=report_request, row_number=index)
        report_row.data = row
        report_row.save()
    
    report_request.aggregates = aggregates
    report_request.completion_timestamp = datetime.datetime.now()
    report_request.save()

@task()
def cleanup_stale_reports():
    ReportRequest.objects.cleanup_stale_requests()
