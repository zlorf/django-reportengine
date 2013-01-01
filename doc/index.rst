.. Django Reportengine documentation master file, created by
   sphinx-quickstart on Tue Jan  1 15:59:51 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Django Reportengine
===============================================

Contents:

.. toctree::
   :maxdepth: 2

Introduction
---------------

Django Reportengine is a report framework that makes it easy to
create reports based on Django querysets, or to create your own
highly customized reports.

It can generate CVS, XLS, XML or Django Admin Interface results 
for reports.

It can also asynchronously create reports and direct the user to 
them when the report is complete.



Quickstart
------------

Here's the quickstart::
    
    pip install django-reportengine
    
Then, create a report::
    
    from reportengine.base import ModelReport

    class MyReport(ModelReport):
        model = MyModel 


This will return a report of all objects of type `MyModel.`

Report Engine
---------------
.. automodule:: reportengine
    :members:

Report Classes
---------------
.. automodule:: reportengine.base
    :members:

Filter Controls
----------------
.. automodule:: reportengine.filtercontrols
    :members:



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

