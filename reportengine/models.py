from django.db import models
import datetime
import reportengine

from jsonfield import JSONField
from settings import STALE_REPORT_SECONDS 

class ReportRequestManager(models.Manager):
    def completed(self):
        return self.filter(completion_timestamp__isnull=False)
    
    def stale(self):
        cutoff = datetime.datetime.now() - datetime.timedelta(seconds=STALE_REPORT_SECONDS)
        return self.filter(request_made__lte=cutoff)
    
    def cleanup_stale_requests(self):
        return self.stale().delete()

class ReportRequest(models.Model):
    """Session based report request. Report request is made, and the token for the request is stored in the session so only that user can access this report. Task system generates the report and drops it into "content". When content is no longer null, user sees full report and their session token is cleared."""
    # TODO consider cleanup (when should this be happening? after the request is made? What about caching? throttling?)
    namespace = models.CharField(max_length=255)
    slug = models.CharField(max_length=255)
    params = JSONField() #GET params
    request_made = models.DateTimeField(default=datetime.datetime.now)
    completion_timestamp = models.DateTimeField(blank=True, null=True)
    token = models.CharField(max_length=255)
    #content = models.TextField()
    viewed_on = models.DateTimeField(blank=True, null=True)
    #mimetype = models.CharField(max_length=255,null=True)
    aggregates = JSONField(datatype=list)
    
    objects = ReportRequestManager()
    
    def get_report(self):
        return reportengine.get_report(self.namespace, self.slug)()
    
    def build_report(self):
        kwargs = self.params

        # THis is like 90% the same 
        #reportengine.autodiscover() ## Populate the reportengine registry
        try:
            report = self.get_report()
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
        
        ReportRequestRow.objects.filter(report_request=self).delete()
        
        for index, row in enumerate(rows):
            report_row = ReportRequestRow(report_request=self, row_number=index)
            report_row.data = row
            report_row.save()
        
        self.aggregates = aggregates
        self.completion_timestamp = datetime.datetime.now()
        self.save()

class ReportRequestRow(models.Model):
    report_request = models.ForeignKey(ReportRequest, related_name='rows')
    row_number = models.PositiveIntegerField()
    data = JSONField(datatype=list)
