=====================================
SignalBox's Roles and Responsibilities
=====================================


Role and Permissions
------------------------


Signalbox defines 4 roles, each of which have set of permissions.

- Researchers
- Research assistants
- Assessors
- Clinicians

In addition, the documentation refers to:

- Participants/Patients

However participants are not a distinct group within the system - a participant just needs to be a registered :class:`User` of the site. Note researchers, clinicians etc. may also be participants. Also see :ref:`Membership types <membership_types>` .


.. note:: All users of the system are stored as django :class:`django.auth.User` objects. We use the standard django authentication mechnisms to log people in and track session state (this uses a cookie for identification, but all the data gets stored in the DB). SignalBox roles are defined using Django's :class:`~django.auth.models.Group` models (see `<https://docs.djangoproject.com/en/1.3/topics/auth/>`_ for more details.)

.. note:: for many studies, the only types of users which will be required are Researchers and Participants.



Role based permissions
------------------------

Permissions for many views within the site are determined by group memberships.


Researchers
...............

Researchers have pretty much full access to data and functionality within the site. They don't need to be a ``superuser`` within the django auth system though. Examples of things only researchers need to be able to do are resolving duplicate replies for observations (i.e. picking a canonical reply, see :doc:`replies`), and exporting data (:doc:`exporting_data`).



Research assistants
........................

For large trials, Research Assistant's help administer participants and memberships, but do not have full access to participant data. Research assistants can:

- Add a new user to the system (e.g. enter details for a patient who has just been recruited)
- Add a user to a study (create a membership)
- See a list of observations outstanding
- Enter data for a specific observation
- Add notes to a patient (on the patient dashboard page)


Assessors
............

Assessors are responsible for collating data from patients, often in interviews, and are typically blind to the condition a participant has been assigned to. Assessors have only limited access to the site, because much of the data stored from participant self reports would reveal which condition a participant was in.

Assessors can:

- Find a given participant
- See that observations which are due for participants
- See observations which are overdue
- Enter data for an observation


.. warning: Assessors should NOT be able to see any information which might give away a patient as being in a particular condition in a blinded study. We think this is most likely to happen if they see that i) a participant has :class:`TreatmentRecord` objects attached to them or ii) they see an observation created by a script which is only attached to a treatment StudyCondition. We should err on the side of caution (i.e. show as little as possible), but the ``breaks_blind`` field on the :class:`Script` class is intended to flag observations which could break the blind



Clinicians
................

Clinicians treating patients may use the system in several ways:

1. By adding treatment records and other clinical data
2. By taking part in sub-studies in which they record data about other participants (see :ref:`Membership types <membership_types>`).

In theory clinicians may or may not be blind to the allocation of patients (although in the Reframed study they will not be blind).

Clinicians should have no access to research data (i.e. information about observations due/overdue). They will need to:

- Find a particular participant
- Add a TreatmentRecord for a treatment session
- Complete an ad-hoc questionnaire attached to a TreatmentRecord
- Send messages to patients
- Add notes to patients (patient_dashboard)















