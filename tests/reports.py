__author__ = 'Kevin Mooney'
from reportengine import base, register
from reportengine.filtercontrols import StartsWithFilterControl
from models import Customer

class CustomerReport(base.ModelReport):
    """An example of a model report"""
    verbose_name = "User Report"
    slug = "user-report"
    namespace = "system"
    description = "Listing of all Customers in the system"
    labels = ('Date Joined','First Name','Last Name')
    list_filter=['is_active','date_joined',StartsWithFilterControl('username'),'groups']
    date_field = "stamp"
    model=Customer
    per_page = 500

register(CustomerReport)