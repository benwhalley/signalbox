Recruiting participants and study memberships
======================================================


XXX TODO XXX

Add overview here



XXX TODO XXX

Update content below

.. _membership_types:

A :class:`~app.signalbox.models.Membership` links participants -- a :class:`~django.auth.models.User` -- with :class:`~app.signalbox.models.Study` objects. There are two types of memberships possible within a Signalbox study:


:Regular:
    This the normal situation, where a participant is simply taking part in a study.

:Related:
    A second kind, where someone is participating in a study not on their own account, but instead to provide data about another participants (e.g. patients, who are the real object of study). An example of this is where a clinician might take part in a sub-study within a trial to complete assessments of patient progress (or, in fact, report on multiple patients).



Adding participants
--------------------

In clinical trials, participants may be recruited outside of the web system and added by administrators or researchers (rather than signing up directly online). Where this is the case, participants must be added to studies manually.
Participants should be added via the add-participant wizard, available from the `Research Tools` menu, or at `</admin/signalbox/participant/new/>`_.

Once a participant has been added via the wizard, you are redirected to their dashboard page, from where you can add them to a study.

.. image:: /images/admin_userhome.png
    :width: 40 em


Where the membership is the `related` type, it's necessary to fill out the additional ``relates_to`` field on the add membership view. To be in the normal situation:

- The participant is the object of study
- The ``relates_to`` field is blank

And in the `related` type of membership:

- The participant is someone providing data about the individual being studied.
- The ``relates_to`` field denotes the individual being studied




Randomisation/allocation methods
--------------------------------------------------------

When a :term:`user` signs up for a study (or are added by a :term:`researcher`), then the system may automatically allocate them to a :py:class:`StudyCondition`


At present, allocation is made by weighted, adaptive randomisation.


Weighted adaptive randomisation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Participants are allocated to :class:`~signalbox.models.StudyCondition`s within a :class:`-signalbox.models.Study` in the proportions specified by the ``weight`` property of each :class:`~signalbox.models.StudyCondition`.

For example, if there are 3 :class:`~signalbox.models.StudyCondition`s attached to a :class:`~signalbox.models.Study` and have weights 2, 2 and 3, then participants will be allocated accordingly.

.. autofunction:: signalbox.allocation.weighted_randomisation


In addition, the `randomisation_probability` field on studies determines how deterministic this allocation is.  Where `randomisation_probability` = 1 then all allocations will be made at random (respecting group weights). However, when `randomisation_probability` = .5, half of allocations will be made deterministically to minimise the imbalances between groups.

More complex adaptive randomisation schemes are not currently available.





Pausing or deactivating observations for a membership
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If a participant decides to leave the study, but is happy for data provided so far to be used, the best method to pause further observations is to deselect the ``active``  checkbox on their membership page. This will prevent all further observations being sent *for that study*.

.warning:: This will not stop all observations for this *participant* — only those due for this study (i.e. for the membership). If a participant withdraws from a trial which has multiple sub-studies, be sure to deactivate all of their memberships.



Randomisation dates and date-shifting observations
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In the case that a person has been randomised to a trial prior to being added to the system, it may be necessary to alter the automatically-generated ``randomisation_date`` field on the membership. This can be done through the admin interface: first find the correct membership at `</admin/signalbox/membership/>`_ and then edit the property directly.

In other cases a participant may be added to the study and observations added automatically. Sometimes, a participant may need to pause participation in the study, or may not have been added to the study early enough and may need to skip some of the observations a script creates. In these cases, a view is provided to `shift` the dates of observations which already exist for a membership, to correct the dates forward or backward. This is available at `</admin/signalbox/membership/dateshift/(membership_number)>`_, or via link on the edit-membership view.




