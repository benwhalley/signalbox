---
finish_on_last_page: false
name: Demonstration Questionnaire
redirect_url: /accounts/profile/
show_progress: false
slug: demonstration_asker
step_navigation: true
steps_are_sequential: true
success_message: Questionnaire complete.
---



# Introductory questions


~~~{#testdemo_instruction .instruction  }
# Instructions here

We can use any markdown syntax we like, e.g.

- Lists of items

1. And ordered lists
2. Of other things

Or **bold**, *italic* etc.

~~~

~~~{#testdemo_pulldown .pulldown  }
A pulldown menu
>>>
*1=Blue
2=Green
3=Red
~~~

~~~{#testdemo_scale .likert  }
A likert type question
>>>
0=No
*1=Yes
~~~

~~~{#testdemo_shorttext .short-text  }
A short-text answer

~~~

~~~{#testdemo_longtext .long-text  }
A large text box for which an answer is required.

~~~

~~~{#testdemo_checkbox .checkboxes  }
Checkboxes useful sometimes!
>>>
*1=Blue
2=Green
3=Red
~~~

~~~{#testdemo_list .likert-list  }
A list of radio buttons
>>>
1=Female
0=Male
~~~

~~~{#testdemo_integer .integer  }
This question requires an integer answer (and won't accept letters)

~~~

~~~{#testdemo_slider_choose_range  max="100"  values="[40, 60]"  min="0"  }
A slider to choose a range

~~~

~~~{#testdemo_slider_choose_number  max="100"  value="50"  min="0"  }
A slider to choose a number

~~~

~~~{#testdemo_instrument_insertion .instrument  }


~~~


# Finalise


~~~{#testdemo_anotherpage .instruction  }
Responses from previous pages can be re-displayed, and can even be averaged or summed to provide instant scoring of questionnaires. For example, on the first page you wrote:

>{{answers.demo_longtext}}

~~~
