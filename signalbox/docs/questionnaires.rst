
Creating questionnaires
=====================================


The ``Ask`` application deals with creating and displaying questionnaires.

Questionnaires can be spread across multiple pages, and consist of questions. Questions can also be grouped into Instruments, which can be placed in a block into a page. Questions will often refer to ChoiceSets (groups of discreet options), e.g. for likert type responses.


Editing via markdown text format
---------------------------------

To enable rapid editing of questionnaires, a text-based format is available in which titles, questions and choice-sets can be specified, and which are converted into Asker, Question and ChoiceSet objects in the database. This text format is based on [markdown](http://johnmacfarlane.net/pandoc/demo/example9/pandocs-markdown.html).

The text to edit questionnaires comes in two blocks: the header, which specifies details of the questionnaire as a whole, and the body which contains individual questions and choicesets.


The questionnaire header
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The header is formatted as follows::

    ---
    name: "Name of the questionnaire here"
    slug: "examplequestionnaire"
    redirect_url: "http://www.example.com"
    show_progress: false
    step_navigation: true
    steps_are_sequential: true
    success_message: "Thanks for completing this questionnaire."
    ---


The `name` and `slug` attributes identify the questionnaire — the `slug` being a short identifier which can be used in url links.  The other fields are as follows:

`redirect_url`
   The page the user is sent to when the questionnaire is complete

`success_message`
   If the user is redirected to page within the signalbox site, an extra message which will appear in a banner at the head of the page after completion.

`show_progress`
   Whether participants can see how far through the questionnaire they are

`step_navigation`
   Whether links should be included allowing random access to each page within the questionnaire.

`steps_are_sequential`
   If true, and `step_navigation` is enabled, then participants can only navigate 'back' within the questionnaire, and cannot skip forwards.



The questionnaire body
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Questions themselves are defined in what are called 'fenced code blocks' in Markdown. For example::

    ~~~{}
    This the simplest type of 'question' - an instruction. No responses will be collected here.
    ~~~

When this is saved, you'll notice that the system adds some attributes to the block to enable it to be identified in the database later for editing. So, the example above would get transformed into::

    ~~~{#ecVhsaj7889ij .instruction}
    This the simplest type of 'question' - an instruction. No responses will be collected here.
    ~~~

Here, a variable name has been added (`ecVhsaj7889ij`) and the `type` of question specified for clarity. To add other types of questions you will need to manually specify the type, and optionally also the variable name for example::

    ~~~{#howoldareyou .integer}
    How old are you, in years?
    ~~~

This would create an html question which requires an integer answer to be entered in a small text box.  Some questions (including integer questions) have optional attributes. For example::

    ~~~{#howoldareyou .integer min="12" max="120"}
    How old are you, in years?
    ~~~

In the example above we add a min and max attribute to validate against some typos. The text of questions can itself include markdown formatting to create headings, emphaisis or links within a questionnaire. For example::

    ~~~{#howoldareyou .integer min="12" max="120"}
    # Demographic information

    How old are you, ***in years***?
    ~~~

In the example above, a level-1 heading (Demographic information) is inserted, and the text 'in years' is formatted in bold and italic. For more information on [markdown formatting see the guide here](XXX).


Some questions require users to select from a restrcited range of choices, for example a likert-type scale. To specify the choices, specify a choiceset attribute on the question, and define the choiceset in a second, separate block::


    ~~~{#howhappyareyou .likert}
    How happy are you?
    >>>
    1=Very happy
    2=Miserable
    ~~~

Here the possible options are listed following ">>>" on separate lines, in the form `score=label`. Scores must be integers, and are the values saved when the user provides an answer.

To mark one option to be selected by default, insert a star in front of the value::

    ~~~{#range1to4 .choiceset .required}
    1*=Happy is selected by default
    2=2
    3=3
    4=Unhappy
    ~~~

Note this is also a required question.



A complete example
--------------------

A complete example can be found in `ask/fixtures/asker_text.md`.







.. Under construction TODO

Other types of questions available
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

`instruction`
    No answer required, but 'question' text displayed.

`uninterruptible-instruction`
    Like instructions, but when using IVR systems this type prevents the user continuing until the whole message has played.

`short-text`
    A small text input box

`long-text`
    A large <textarea> box.


`likert or likert-list`
    Discreet options selected via radio-buttons (i.e. options are mutually exclusive). `likert-list` produces a vertical list as opposed to a horizontal scale. A required attribute is `choiceset`, to specify the options available (see above).


`checkboxes`
    As for `likert`, but options are no-mutually exclusive (more than one can be selected).

`integer`
    The user can only enter an integer. Optional attributes are `min` and `max`.

`decimal`
    As for integer, but allows only (and validates) decimal numbers.

`pulldown`
    As for likert, but uses a pulldown selector instead of radio buttons.


`required-checkbox`
    Displays the question text next to a checkbox which the user must check to progress to the next page.


`slider or range-slider`
    A slider element which allows users to pick a value between a `min` and a `max` which are specified as additional attributes. E.g.::

        ~~~{#variablename type="slider" min=0 max=100 value=50}
        Slide the slider to a value between 0 and 100 (this slider defaults to 50).
        ~~~

    Or if you want a slider with two movable points to specify a range of values::

        ~~~{#variablename type="slider" min=0 max=100 values=[10,90]}
        Slide the slider to encompass a range of values between 0 and 100 (this slider defaults to the range 10-90).
        ~~~

`date`
    A date picker.

`date-time`
    A date-time picker.

`time`
    A time-of-day picker.

`hangup`
    This question will end an IVR call.

`webcam`
    Experimental support for webcams on user laptops. Allows capturing and sending an image to the server (which is saved in the DB rather than a file).







Creating questions
---------------------

Questions are created by using django form field elements, and extending them with additional information required by signalbox.  The types of questions which can be created are documented here: :ref:`question-types`


The fields and widgets are as described in the floppyforms documentation: http://django-floppyforms.readthedocs.org/en/latest/widgets-reference.html



In addition, for IVR telephone calls, there are:

- Uninterruptible instruction (this speaks the text of the questions, but without allowing the user to 'barge-in'and skip the text by pressing a key, as is the case with a normal instruction question.)
- Listen (records audio of the user)
- Hangup (speaks the text of the question and then ends the current call; it is required that the asker ends with a hangup question)


Repeating questions within a Questionnaire
----------------------------------------------------

Each question must have unique variable name which will be used to identify data collected. If a question is to be repeated within a questionnaire, it should either be duplicated and given a second, different, name, or placed within an Instrument, and that Instrument given a prefix.




Approximate completion times for questionnaires
------------------------------------------------

These are calculated by a method on the Asker (Questionnaire) model:

.. automethod:: ask.models.Asker.approximate_time_to_complete




Displaying previous answers or summary scores in questions
-----------------------------------------------------------

Read about ScoreSheets first.

Summary scores or previous questionnaire responses can be included on later pages, using the curly brace markers {{}}::

    ~~~
    This will include an instruction displaying the users user response to a variable named howoldareyou:

    {{answers.howoldareyou}}

    ~~~

Or to show a summary score::

    ~~~
    {{scores.summary_score_name}}
    ~~~

Be sure to enable a particular summary score for your Questionnaire on the main editing page - it won't be available unless you do.









Instruments and question re-use
------------------------------------

Instruments are packages fo questions which can be placed as a unit within a questionnaire, e.g. for a psychometric scales which will be used in multiple studies.

A useful property of instruments embedded within questionnaires is the ability to make all questions required or not-required with a single checkbox. This can be turned on once testing is over to ensure participants complete all questions.








