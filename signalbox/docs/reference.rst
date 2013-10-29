Reference for database/application structures
====================================================


Ask application
----------------


Models
~~~~~~~~~

.. automodule:: ask.models
    :members:



.. _question-types:

Types of questions (Field classes)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

SignalboxField stores the additional information signalbox needs to properly display and process questions.

.. autoclass:: ask.models.fields.SignalboxField


Notes on all question types
~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Question text: this is displayed in syntax (see :doc:`../markdown`).

..warning:: Note that some characters are stripped and used to format the question text in html – for example, text surrounded by two * characters will be italicised, and lines starting with a number and a period (e.g. "1. ") will be turned into a numbered list.


Types of question
~~~~~~~~~~~~~~~~~

Each of the following question classes extends the standard django form fields to allow for different types of questions:

.. automodule:: ask.models.fields
    :members:
    :show-inheritance:



Signalbox application
----------------------


Models
~~~~~~~~~

.. automodule:: signalbox.models
    :members:

