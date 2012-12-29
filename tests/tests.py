#from reportengine.base import Report, QuerySetReport, ModelReport, SQLReport, DateSQLReport

#from django.conf import settings
#from django.contrib.auth.models import User
#from django.http import HttpResponse
#from django.template import Template, Context
from django.test import TestCase
#from django.test import RequestFactory
import factory
from models import Customer
from reports import CustomerReport
from datetime import datetime, timedelta
from utils import first_names, last_names
import random
import reportengine

class CustomerFactory(factory.Factory):
    FACTORY_FOR = Customer
    first_name = 'Kevin'
    last_name = 'Mooney'
    stamp = datetime.now()
    age = 33


class BaseTestCase(TestCase):

    def setUp(self):
        # Create 1000 "Customers"
        for i in range(1,1000):
            CustomerFactory(
                first_name=random.choice(first_names),
                last_name=random.choice(last_names),
                stamp=datetime.now() - timedelta(days=random.randint(1,365*4)),
                age = random.randint(13,90)
            )



    def tearDown(self):
        Customer.objects.all().delete()

    
class ReportEngineTestCase(BaseTestCase):

    def test_reportregistration(self):
        len(reportengine._registry)
        self.assertTrue(len(reportengine._registry) == 1)
        self.assertTrue( (CustomerReport.namespace, CustomerReport.slug) in reportengine._registry )

    def test_modelreport(self):
        self.assertTrue(False)

    def test_sqlreport(self):
        self.assertTrue(False)

    def test_querysetreport(self):
        self.assertTrue(False)

    def test_datesqlreport(self):
        self.assertTrue(False)

    def test_report(self):
        self.assertTrue(False)

    def test_fastcsvresponse(self):
        self.assertTrue(False)

    def test_reportrequest(self):
        self.assertTrue(False)
