#from reportengine.base import Report, QuerySetReport, ModelReport, SQLReport, DateSQLReport

#from django.conf import settings
#from django.contrib.auth.models import User
#from django.http import HttpResponse
#from django.template import Template, Context
import decimal
from django.test import TestCase
#from django.test import RequestFactory
import factory
import models
import time
from reports import CustomerReport, CustomerSalesReport, SaleItemReport, CustomerByStamp
from datetime import datetime, timedelta
from utils import first_names, last_names
import random
import reportengine
import json
from reportengine.outputformats import CSVOutputFormat

class CustomerFactory(factory.Factory):
    FACTORY_FOR = models.Customer
    first_name = 'Default'
    last_name = 'Customer'
    stamp = datetime.now()
    age = 33

class PaymentInfoFactory(factory.Factory):
    FACTORY_FOR = models.PaymentInfo
    payment_token = '4111111111111111'

class AddressFactory(factory.Factory):
    FACTORY_FOR = models.Address
    street = '123 Happy Street'
    city = 'Austin'
    state = 'TX'
    postal_code = '78704'
    customer = factory.LazyAttribute(lambda a: CustomerFactory())

class BillingInfoFactory(factory.Factory):
    FACTORY_FOR = models.BillingInfo
    address = factory.LazyAttribute(lambda a: AddressFactory())
    payment_info = factory.LazyAttribute(lambda a: PaymentInfoFactory())


class SaleFactory(factory.Factory):
    FACTORY_FOR = models.Sale

    customer = factory.LazyAttribute(lambda a: CustomerFactory())
    ship_address = factory.LazyAttribute(lambda a: AddressFactory())
    bill_info = factory.LazyAttribute(lambda a: BillingInfoFactory())
    total = decimal.Decimal("100.00")
    tax_rate = decimal.Decimal("0.08")
    purchase_date = datetime.now()

class SaleItemFactory(factory.Factory):
    FACTORY_FOR = models.SaleItem
    sale = factory.LazyAttribute(lambda a: SaleFactory())
    department = "Mens"
    classification = "Apparel"
    sub_classification = "Gloves"
    name = "Isotoners - For Men!"
    option1 = "Blue"
    option2 = "Medium"
    price = decimal.Decimal("25.00")



class BaseTestCase(TestCase):
    sql_filters = {}
    test_total = decimal.Decimal("0.00")
    this_months_customers = 0
    def setUp(self):
        for i in range(0,100):
            c = CustomerFactory(
                first_name=random.choice(first_names),
                last_name=random.choice(last_names),
                stamp=datetime.now() - timedelta(days=random.randint(1,365*4)),
                age = random.randint(13,90)
            )
            if c.stamp >= (datetime.now() - timedelta(days=30)):
                self.this_months_customers += 1
            if i == 1:
                self.sql_filters['first_name'] = c.first_name
                self.sql_filters['last_name'] = c.last_name
            address = AddressFactory(customer=c)
            billing_info = BillingInfoFactory(address=address)
            sale = SaleFactory(customer=c, ship_address=address, bill_info=billing_info)
            final_price = decimal.Decimal("0.00")
            for j in range(random.randint(0,5)):
                si = SaleItemFactory(sale=sale)
                final_price += si.price
            sale.total = final_price + (final_price * sale.tax_rate)
            if i == 1 or (c.first_name == self.sql_filters.get('first_name', '') and
                          c.last_name == self.sql_filters.get('last_name', '')):
                self.test_total += sale.total
            sale.save()

    def tearDown(self):
        models.Customer.objects.all().delete()

    
class ReportEngineTestCase(BaseTestCase):

    def test_reportregistration(self):
        len(reportengine._registry)
        self.assertTrue(len(reportengine._registry) == 2)
        self.assertTrue( (CustomerReport.namespace, CustomerReport.slug) in reportengine._registry )

    def test_modelreport(self):
        cr = CustomerReport()
        rows,metadata = cr.get_rows()
        self.assertTrue(len(rows)==models.Customer.objects.count())

    def test_sqlreport(self):
        csr = CustomerSalesReport()
        rows, metadata = csr.get_rows(self.sql_filters)
        self.assertEqual(rows[0][2], self.test_total)

    def test_querysetreport(self):
        sir = SaleItemReport()
        rows, metadata = sir.get_rows()
        self.assertEqual(models.SaleItem.objects.count(), len(rows))

    def test_datesqlreport(self):
        cbs = CustomerByStamp()
        # shouldn't be required to get default mask.  it should be the... default
        rows,metadata = cbs.get_rows(filters={'date__lt': (datetime.now()+timedelta(days=1)).strftime('%Y-%m-%d'),
                                              'date__gte': (datetime.now()-timedelta(days=30)).strftime('%Y-%m-%d')
                                             })

        self.assertEqual(len(rows), self.this_months_customers)

    def test_report(self):
        class CounterReport(reportengine.base.Report):
            def get_rows(self, *args, **kwargs):
                return [(x,) for x in range(0,10000)], ('total', 10000,)
        cr = CounterReport()
        rows, metadata = cr.get_rows()
        self.assertTrue(len(rows), dict((metadata,))['total'])

    def test_fastcsvresponse(self):
        """
        This should test that the CSV conversion from stored report data for 10,000 lines (100,000?) will
        take less than 15 seconds.
        """
        class RandomNameReport(reportengine.base.Report):
            labels = ('number', 'first_name', 'last_name',)
            def get_rows(self, *args, **kwargs):
                return [
                        (x, random.choice(first_names), random.choice(last_names), ) for x in range(0,100000)
                       ], ('total', 100000,)
        rnr = RandomNameReport()
        csv = CSVOutputFormat()
        ctx = dict()
        rows, metadata = rnr.get_rows()
        ctx['rows'] = rows
        ctx['aggregates'] = []
        ctx['report'] = rnr

        then = time.clock()
        csv.get_response(ctx,None)
        now = time.clock()
        result = now - then

        self.assertLessEqual(result,15)


    def test_reportrequest(self):
        from reportengine.models import ReportRequest
        rr = ReportRequest.objects.create(namespace='system', slug='sale-report', params=json.dumps(self.sql_filters))
        #ALWAYS_EAGER = True, so should run right away.
        result = rr.schedule_task()
        self.assertEqual(True,result.successful())

    def test_reportexportrequest(self):
        from reportengine.models import ReportRequest
        rr = ReportRequest.objects.create(namespace='system', slug='sale-report', params=json.dumps(self.sql_filters))
        #ALWAYS_EAGER = True, so should run right away.
        result = rr.schedule_task()
        self.assertEqual(True,result.successful())

        
