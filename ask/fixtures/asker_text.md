---
finish_on_last_page: true
name: The Dose Index
redirect_url: /accounts/profile/
show_progress: false
slug: dose
steps_are_sequential: true
success_message: ''
---

# The Dose Index Calculator

~~~{#dose_mrc .likert-list .required  }
How does the patient's breathing affect their daily life?
<small class="muted">(These items are based on the MRC Dyspnoea Score system)</small>
>>>
0=Not troubled by breathlessness except on strenuous exercise 
0=Short of breath when hurrying or walking up a slight hill 
1=Walks slower than contemporaries on level ground because of breathlessness,  or has to stop for breath when walking at own pace 
2=Stops for breath after walking about 100 metres or after a few minutes on level ground 
3=Too breathless to leave the house, or breathless when dressing or undressing 
~~~

~~~{#dose_fev1 .likert .required  }
Airflow Obstruction (FEV1% predicted)
>>>
1=30-49% 
0=More than 50% 
2=Less than 30% 
~~~

~~~{#dose_smokes .likert .required  }
Smoking status
>>>
0=Non-smoker 
1=Current smoker 
~~~

~~~{#dose_exacerbations .likert-list .required  }
Number of exacerbation per year
>>>
0=0 
1=1 
2=2 
*3[2]=3 
4[2]=4 or more
~~~



# Recommendations


~~~{#kynvpzxzzm4hprmkpkie8o .instruction  }

>>>

dose <- sum(dose_mrc dose_fev1 dose_smokes dose_exacerbations)
~~~

~~~{#mcgukw746mmwa37anmug7j .instruction  }
### Total score
The patient's total Dose Index is **{{scores.dose.score|apnumber}}**. 

### Recommendations
{% if answers.dose_mrc > 0 %}- <span class="text-info">Pulmonary rehabilitation</span> is indicated, based on the patient's MRC Dyspnoea score{%endif%}

{% if answers.dose_mrc > 0 %}- <span class="text-info">Long acting broncodilators</span>  are also indicated based on the patients dyspnoea score.{% endif %}

{% if answers.dose_exacerbations > 0 and  answers.dose_fev1 > 0 %}- <span class="text-info">Inhaled corticosteroids</span>  are indicated, based on the occurence of exacerbations and the patient's airway restriction.{%endif%}

{% if answers.dose_smokes > 0 %}- <span class="text-info">Smoking cessation</span> is always indicated{% endif %}

~~~
