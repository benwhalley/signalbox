from signalbox.select_time_widget import SelectTimeWidget
from django.forms.widgets import MultiWidget
from django.forms.extras.widgets import SelectDateWidget

class SplitSelectDateTimeWidget(MultiWidget):
    """
    MultiWidget = A widget that is composed of multiple widgets.

    This class combines SelectTimeWidget and SelectDateWidget so we have something 
    like SpliteDateTimeWidget (in django.forms.widgets), but with Select elements.
    """
    def __init__(self, attrs=None, hour_step=None, minute_step=None, second_step=None, twelve_hr=None, years=None):
        """ pass all these parameters to their respective widget constructors..."""
        widgets = (SelectDateWidget(attrs=attrs, years=years), SelectTimeWidget(attrs=attrs, hour_step=hour_step, minute_step=minute_step, second_step=second_step, twelve_hr=twelve_hr))
        super(SplitSelectDateTimeWidget, self).__init__(widgets, attrs)

    def decompress(self, value):
        if value:
            return [value.date(), value.time().replace(microsecond=0)]
        return [None, None]

    def format_output(self, rendered_widgets):
        """
        Given a list of rendered widgets (as strings), it inserts an HTML
        linebreak between them.
        
        Returns a Unicode string representing the HTML for the whole lot.
        """
        rendered_widgets.insert(-1, '<br/>')
        return u''.join(rendered_widgets)
