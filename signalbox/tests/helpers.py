# coding: utf-8
from django.contrib.auth.models import User
from signalbox.models import Membership, Study, Observation
from signalbox.allocation import allocate

LONG_YUCKY_UNICODE = u"""Testing «ταБЬℓσ»: 1<2 & 4+1>3, now 20% off! ٩(-̮̮̃-̃)
۶ ٩(●̮̮̃•̃)۶ ٩(͡๏̯͡๏)۶ ٩(-̮̮̃•̃).Bãｃòｎ ｉｐｓûｍ Ꮷｏｌòｒ ｓïｔ âｍêｔ òｃｃａé
ｃáｔ ｋïéｌｂäｓâ ｃåｐïｃｏｌà, ｃｈùｃｋ ｐｏｒｋ ｂéｌｌｙ íｎ àｌïｑûïｐ ｍ
éａｔｌòåｆ ｍòｌｌíｔ êｎíｍ ëｘ ｐｒòｓｃïüｔｔò âｎｄｏüｉｌｌｅ ｂèëｆ ｒíｂ
ｓ. Eｘ ｓｔｒïｐ ｓｔｅａｋ ｐｏｒｋ ｌòｉｎ, ｓèｄ ｂｒëｓãｏｌá ｓｐèｃｋ ｏ
ｃｃàｅｃâｔ ｔｏｎｇｕｅ. Iｄ ｐｒｏｓｃｉûｔｔｏ éｓｓé ｓｉｒｌòïｎ ëｔ òｆｆ
ｉｃｉá ｌåｂｏｒìｓ ｆｒãｎｋｆúｒｔéｒ ｃａｐïｃòｌâ ｔｕｒｄúｃｋｅｎ. Qûïｓ
ｔàｉｌ ｓｕｎｔ ｅìûｓｍòᏧ.
Tｈê Fｉｓｈ-Fòｏｔｍàｎ ｂｅｇａｎ ｂｙ ｐｒｏᏧüｃìｎｇ ｆｒòｍ ùｎᏧｅｒ ｈìｓ
åｒｍ â ｇｒèàｔ ｌêｔｔëｒ, ｎèãｒｌｙ áｓ ｌåｒｇê ãｓ ｈｉｍｓéｌｆ, ãｎｄ ｔ
ｈíｓ ｈè ｈäｎᏧêｄ ｏｖëｒ ｔｏ ｔｈè òｔｈëｒ, ｓａｙｉｎｇ, ïｎ á ｓｏｌｅｍ
ｎ ｔｏｎé, 'Fòｒ ｔｈë Dùｃｈèｓｓ. Aｎ ìｎｖïｔàｔｉｏｎ ｆｒｏｍ ｔｈｅ Qｕè
ｅｎ ｔｏ ｐｌａｙ ｃｒòｑüｅｔ.' Tｈè Fｒòｇ-Fòｏｔｍàｎ ｒêｐｅàｔêｄ, íｎ ｔ
ｈë ｓàｍè ｓòｌêｍｎ ｔｏｎｅ, ｏｎｌｙ ｃｈâｎｇìｎｇ ｔｈè ｏｒｄｅｒ òｆ ｔ
ｈｅ ｗòｒｄｓ ã ｌｉｔｔｌè, 'Fｒòｍ ｔｈê Qｕééｎ. Aｎ ｉｎｖíｔåｔｉｏｎ ｆò
ｒ ｔｈｅ Dｕｃｈêｓｓ ｔｏ ｐｌàｙ ｃｒòｑｕｅｔ.'"""


def make_user(details, profile_details=None):
    """Accept a dict of details and return a saved User object -> User.

    To make a user, require:
        - username
        - email
        - password

    Optionally allow a second dict containing fields for the UserProfile
    """

    password = details.pop('password')
    user = User(**details)
    user.set_password(password)
    user.save()

    if profile_details:
        profile = user.get_profile()
        [setattr(profile, k, v) for k,v in profile_details.items()]


    return user
