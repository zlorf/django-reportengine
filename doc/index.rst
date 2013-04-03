.. Django Reportengine documentation master file, created by
   sphinx-quickstart on Tue Jan  1 15:59:51 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Django Reportengine
===============================================

Contents:

.. toctree::
   :maxdepth: 2
   :glob: .

Introduction
---------------

Django Reportengine is a report framework that makes it easy to
create reports based on Django querysets, or to create your own
highly customized reports.

It can generate CVS, XLS, XML or Django Admin Interface results 
for reports.

It can also asynchronously create reports and direct the user to 
them when the report is complete.



Getting Started
----------------

The easiest way to get started with ReportEngine is to install 
from pypi::

    pip install django-reportengine
    
To do anything useful with Report Engine, you'll need to extend 
its base reports.  The simplest of these reports is a model report::
    
    from reportengine.base import ModelReport
    from myapp.models import MyModel

    class MyReport(ModelReport):
        model = MyModel 


This will return a report of all objects of type `MyModel.`

Please see the `Class Reference` for details about implementing more 
complex reports.


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

