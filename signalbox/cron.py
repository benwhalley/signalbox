from signalbox.utils import execute_the_todo_list, send_reminders_due_now
import kronos
import logging
logger = logging.getLogger(__name__)


@kronos.register('*/2 * * * *')
def send():
    todolistresult = execute_the_todo_list()
    [logger.info("Sent:\t %s" % i.id, ) for i, j in todolistresult]
    return str([i.id for i, j in todolistresult])

@kronos.register('*/60 * * * *')
def remind():
    reminderlistresult = send_reminders_due_now()
    [logger.info("Sent:\t %s" % i.id, ) for i, j in reminderlistresult]
    return str([i.id for i, j in reminderlistresult])
