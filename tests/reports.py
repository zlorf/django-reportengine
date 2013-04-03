__author__ = 'Kevin Mooney'
from reportengine import base, register
from reportengine.filtercontrols import StartsWithFilterControl
from models import Customer, SaleItem


class CustomerReport(base.ModelReport):
    """An example of a model report"""
    verbose_name = "User Report"
    slug = "user-report"
    namespace = "system"
    description = "Listing of all Customers in the system"
    labels = ('stamp','first_name','last_name')
    list_filter=['is_active','date_joined',StartsWithFilterControl('username'),'groups']
    date_field = "stamp"
    model=Customer
    per_page = 500

register(CustomerReport)


class CustomerSalesReport(base.SQLReport):
    """A SQL Report to show sales by customer"""

    verbose_name = "Sales Report By Person"
    allow_unspecified_filters = True
    slug = "sale-report"
    namespace = "system"
    description = "A listing of all sales reports"

    labels = ('first_name', 'last_name', 'total')

    list_filter=['first_name', 'last_name']

    row_sql = """
        SELECT first_name, last_name, SUM(total) as total FROM tests_sale
        INNER JOIN tests_customer ON tests_sale.customer_id = tests_customer.id
        WHERE first_name = '%(first_name)s' AND last_name = '%(last_name)s'
        GROUP BY tests_customer.id
        ORDER BY total
    """
register(CustomerSalesReport)


class SaleItemReport(base.QuerySetReport):
    verbose_name = "Sales Items, filtered by customer"

    slug = "sales-item-report"
    namespace = "system"
    description = "A listing of all sales items."

    labels = ('name', 'option1', 'option2', 'price')

    def get_queryset(self, *args, **kwargs):
        return SaleItem.objects.all()


class CustomerByStamp(base.DateSQLReport):
    """A Date SQL report to show customers by timestamp"""

    slug = "customer-by-stamp"
    namespace = "system"
    description = "A list of all customers bracketed by start and end dates"

    labels = ('first_name', 'last_name', 'stamp')

    row_sql = """
        SELECT first_name, last_name, stamp FROM tests_customer
        WHERE stamp < '%(date__lt)s' AND stamp >= '%(date__gte)s';
    """


