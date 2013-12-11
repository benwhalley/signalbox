Managing data and Exporting Data
=====================================



Exporting study data
---------------------

Signalbox is able to export data to delimeted text, or to Stata (a common statistical package). When using Stata, the system also exports syntax which label data appropriately to help with later analysis. This syntax also computes some useful variables to help with later analyses.

Signalbox understands that within a single clinical trial there may be multiple sub-studies (each set up as a Study object within the system). Because studies may be linked, and require joint analysis, Signalbox allows you to export data for multiple studies at once.

If this is this case, you need to define a `reference study` --- this will typically be the study which manages the primary randomisation, e.g. to Treatment/Control. Selecting a reference study is useful, because Signalbox uses the date of randomisation for that study to compute additional variables, including `days_in_trial`, which can be contrasted with `days_in_study` and indicates the elapsed days since the user was randomised to the reference study.

.. note:: Additional computed variables, including days_in_trial` are only computed when the exported syntax file is run using Stata, and are not present in the raw text data, ``data.txt``.



To export data
~~~~~~~~~~~~~~~

1. Select ``Tools > Export Data``

2. Select the studies you wish to export data for

3. Select a ``reference study`` (optional), and press ``Submit``.

4. A zip archive will begin downloading, containing three files: ``data.txt``, ``make.do`` and ``syntax.do``.

5. Open the zip and, using Stata 11 or later, run ``make.do``.

6. This script will generate three additional data files: ``data.dta``, ``data_values.xlsx``, and ``data_labels.xlsx``. If you have StatTransfer installed it will also convert the datafile to SPSS ``.sav`` format.

.. note::  Based on data held by the system about the questions used to collect the data, Signalbox will add meta data to exported files. The ``data.dta`` file contains multiple value and variable labels and is probably what you want to use; if needed, the StatTransfer program will convert these to an SPSS file including value and variable labels transparently.  The excel file ``data_values.xlsx`` includes the labelled values (i.e. strings for numeric variables); ``data_values.xlsx`` contains the values themselves.



Long vs. wide format
~~~~~~~~~~~~~~~~~~~~

Signalbox exports data in a long-ish format. Individual :class:`Answers` are grouped by :class:`Reply` and saved one-reply-per-row in the txt file.

However, because different replies will have measured different variables, the resulting file will have many columns (one per variable measured in any of the replies) and lots of blank values (where a reply did not measure a variable, it will be blank).

Many analyses will require you to compute summary scores and restructure the file into a wide format (e.g. the ``reshape`` command in Stata).


Formats and labels
~~~~~~~~~~~~~~~~~~~

The export syntax attempts to correctly import python date/time objects as dates, and format them correctly. If this isn't happening for you then please file a bug report.



See also :doc:`exporting_data`




Serialising data
~~~~~~~~~~~~~~~~


Before deciding to export questionnaires, try using the markdown editing feature (:doc:`questionnaires`) and see if that gives you enough of what you want.

If it doesn't, read this first: `https://docs.djangoproject.com/en/dev/topics/serialization/ <https://docs.djangoproject.com/en/dev/topics/serialization/>`_.



Then see: `http://stackoverflow.com/questions/1499898/django-create-fixtures-without-specifying-a-primary-key <http://stackoverflow.com/questions/1499898/django-create-fixtures-without-specifying-a-primary-key>`_.

So, to export use:

    app/manage.py dumpdata --indent 2 --natural > data.json

Then use a regex like this to replace all pk's with null to be sure they don't clash with others in the db:

    "pk": (?<path>\d+),




