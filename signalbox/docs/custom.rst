Settings and customisation
========================================


Settings
-----------------------------------

The following settings will be loaded from environment variables, overriding these defaults:
::
    DB_URL                      'postgres://localhost/sbox'
    DEBUG                       0 (False)
    USE_VERSIONING              0
    FRONTEND                    frontend

    AWS_STORAGE_BUCKET_NAME     thesignalbox
    AWS_ACCESS_KEY_ID
    AWS_SECRET_ACCESS_KEY

    TWILIO_ID
    TWILIO_TOKEN

    EMAIL_HOST                  localhost
    EMAIL_PORT                  25
    EMAIL_HOST_USER
    EMAIL_HOST_PASSWORD


 Booleans are set using 0/1 in the environment variable.



Customising your installation
------------------------------------

Signalbox allows customisation of the front-end of a site (and much else besides). The ``FRONTEND`` env var determines which django app/module is loaded and used to define per-deployment settings or templates.

Either edit files within the ``frontend`` folder, or duplicate it for editing and set the ``FRONTEND`` variable to your new name. Within this app, you must include a ``settings.py`` file, which can contain the following settings:


.. automodule:: app.frontend.settings

