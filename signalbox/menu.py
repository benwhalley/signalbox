from django.core.urlresolvers import reverse
from menus.base import Menu, NavigationNode
from menus.menu_pool import menu_pool
from django.utils.translation import ugettext_lazy as _

class SignalBoxMenu(Menu):

    def get_nodes(self, request):
        nodes = []

        if request.user.is_staff:
            nodes.insert(0, NavigationNode("Admin site", reverse('admin:index'), 1))
        return nodes

menu_pool.register_menu(SignalBoxMenu)
