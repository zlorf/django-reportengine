#from reportengine.base import Report, QuerySetReport, ModelReport, SQLReport, DateSQLReport

#from django.conf import settings
#from django.contrib.auth.models import User
#from django.http import HttpResponse
#from django.template import Template, Context
from django.test import TestCase
#from django.test import RequestFactory
import factory
import models
from reports import CustomerReport, CustomerSalesReport
from datetime import datetime, timedelta
from utils import first_names, last_names
import random
import reportengine

class CustomerFactory(factory.Factory):
    FACTORY_FOR = models.Customer
    first_name = 'Kevin'
    last_name = 'Mooney'
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
    total = 100.00
    tax_rate = 0.08
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
    price = 25.00



class BaseTestCase(TestCase):
    sql_filters = {}
    test_total = 0.00
    def setUp(self):
        for i in range(0,100):
            c = CustomerFactory(
                first_name=random.choice(first_names),
                last_name=random.choice(last_names),
                stamp=datetime.now() - timedelta(days=random.randint(1,365*4)),
                age = random.randint(13,90)
            )
            if i == 50:
                self.sql_filters['first_name'] = c.first_name
                self.sql_filters['last_name'] = c.last_name
            sale = SaleFactory(customer=c)
            final_price = 0.00
            for j in range(random.randint(0,5)):
                si = SaleItemFactory(sale=sale)
                final_price += si.price
            sale.total = final_price + (final_price * sale.tax_rate)
            if i == 50:
                self.test_total = sale.total
            sale.save()

    def tearDown(self):
        models.Customer.objects.all().delete()

    
class ReportEngineTestCase(BaseTestCase):

    def test_reportregistration(self):
        len(reportengine._registry)
        self.assertTrue(len(reportengine._registry) == 1)
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
        sir = SalesItemReport()
        rows, metadata = sir.get_rows()
        self.assertEqual(models.SaleItem.objects.count(), len(rows))

    def test_datesqlreport(self):
        self.assertTrue(False)

    def test_report(self):
        self.assertTrue(False)

    def test_fastcsvresponse(self):
        self.assertTrue(False)

    def test_reportrequest(self):
        self.assertTrue(False)
