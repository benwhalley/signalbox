"""Customised widgets for use in Askers."""

import django
import floppyforms


class InstructionWidget(floppyforms.widgets.HiddenInput):
    input_type = 'hidden'
    is_hidden = False


class InlineRadioSelect(floppyforms.widgets.RadioSelect):
    template_name = 'floppyforms/widgets/radio-list-inline.html'


class SliderInput(floppyforms.widgets.HiddenInput):
    template_name = 'floppyforms/widgets/slider.html'
    is_hidden = False

class RangeSliderInput(floppyforms.widgets.HiddenInput):
    template_name = 'floppyforms/widgets/range-slider.html'
    is_hidden = False

class InlineCheckboxSelectMultiple(floppyforms.widgets.CheckboxSelectMultiple):
    template_name = 'floppyforms/widgets/checkbox-list-inline.html'

class WebcamWidget(floppyforms.widgets.HiddenInput):
    template_name = 'floppyforms/widgets/webcam.html'
    input_type = 'hidden'
    is_hidden = False
