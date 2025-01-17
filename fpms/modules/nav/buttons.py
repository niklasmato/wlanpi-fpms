import types

from fpms.modules.pages.homepage import *
from fpms.modules.pages.page import *
from fpms.modules.pages.simpletable import *

class Button(object):

    def __init__(self, g_vars, menu):

        self.homepage_obj = HomePage(g_vars)
        self.page_obj = Page(g_vars)


    #######################################
    # Actions taken when butons pressed
    #######################################
    def _at_home_page(self, g_vars):
        if g_vars['display_state'] == 'page' and len(g_vars['current_menu_location']) == 1:
            return True
        else:
            return False


    def _bottom_of_list(self, current_location, menu):

        # pull apart current menu location (e.g. [0, 1, 1])
        menu_selection = menu
        leaf = current_location[-1]
        branch = current_location[0:-1]

        # trim off the branch to reach leaf
        for choice in branch:
            menu_selection = menu_selection[choice]['action']

        # check if the next leaf exists, or whether we are at end of the structure
        try:
            if menu_selection[(leaf + 1)]:
                return False
        except IndexError:
            return True

        # we shouldn't hit this point, but just in case
        return True

    def _display_top_menu(self, g_vars, menu):
        g_vars['display_state'] = 'menu'
        return self.page_obj.draw_page(g_vars, menu)


    def menu_down(self, g_vars, menu):

        if self._at_home_page(g_vars):
            return self._display_top_menu(g_vars, menu)

        # If we are in a table, scroll down (unless at bottom of list)
        if g_vars['display_state'] == 'page':
            if (g_vars['current_scroll_selection'] < (g_vars['table_pages'] -1)):
                g_vars['current_scroll_selection'] += 1
                # Re-run current action immediately to display new page
                g_vars['option_selected']()
                return

        # Menu not currently shown, do nothing
        if g_vars['display_state'] != 'menu':
            return

        if not self._bottom_of_list(g_vars['current_menu_location'], menu):
            # pop the last menu list item, increment & push back on
            current_selection = g_vars['current_menu_location'].pop()
            current_selection = current_selection + 1
            g_vars['current_menu_location'].append(current_selection)

        self.page_obj.draw_page(g_vars, menu)


    def menu_up(self, g_vars, menu):

        if self._at_home_page(g_vars):
            return self._display_top_menu(g_vars, menu)

        # If we are in a table, scroll up (unless at top of list)
        if g_vars['display_state'] == 'page' and g_vars['current_scroll_selection'] > 0:
            g_vars['current_scroll_selection'] -= 1
            # Re-run current action immediately to display new page
            g_vars['option_selected']()
            return

        # Menu not currently shown, do nothing
        if g_vars['display_state'] != 'menu':
            return

        # pop the last menu list item, decrement & push back on
        current_selection = g_vars['current_menu_location'].pop()
        if current_selection != 0:
            current_selection = current_selection - 1
        g_vars['current_menu_location'].append(current_selection)

        self.page_obj.draw_page(g_vars, menu)


    def menu_right(self, g_vars, menu):

        if self._at_home_page(g_vars):
            return self._display_top_menu(g_vars, menu)

        # Check if the "action" field at the current location is an
        # array or a function. If we have an array, append the current
        # selection and re-draw menu
        if (type(g_vars['option_selected']) is list):
            g_vars['current_menu_location'].append(0)
            self.page_obj.draw_page(g_vars, menu)


    def menu_left(self, g_vars, menu):

        # If we're in a table we need to exit, reset table scroll counters, reset
        # result cache and draw the menu for our current level
        if g_vars['display_state'] == 'page':
            g_vars['current_scroll_selection'] = 0
            g_vars['table_list_length'] = 0
            g_vars['display_state'] = 'menu'
            g_vars['result_cache'] = False
            g_vars['scan_file'] = ''
            self.page_obj.draw_page(g_vars, menu)
            return

        if g_vars['display_state'] == 'menu':
            # check to make sure we aren't at top of menu structure
            if len(g_vars['current_menu_location']) == 1:
                # If we're at the top and hit exit (back) button, revert to start-up state
                g_vars['start_up'] = True
                g_vars['current_menu_location'] = [0]
                self.homepage_obj.home_page(g_vars, menu)
            else:
                g_vars['current_menu_location'].pop()
                self.page_obj.draw_page(g_vars, menu)
        else:
            g_vars['display_state'] = 'menu'
            self.page_obj.draw_page(g_vars, menu)


    def menu_center(self, g_vars, menu):

        if self._at_home_page(g_vars):
            # switch between normal and alternate home page
            g_vars['home_page_alternate'] = not g_vars['home_page_alternate']
            # redraw home page immediately
            self.homepage_obj.home_page(g_vars, menu)
        else:
            # Check if the "action" field at the current location is an
            # array or a function. If we have an array, append the current
            # selection and re-draw menu
            if type(g_vars['option_selected']) is list:
                g_vars['current_menu_location'].append(0)
                self.page_obj.draw_page(g_vars, menu)
            elif isinstance(g_vars['option_selected'], types.FunctionType):
                # if we have a function (dispatcher), execute it
                g_vars['display_state'] = 'page'
                g_vars['option_selected']()


    def shortcut(self, g_vars, menu, shortcut):

        g_vars['result_cache'] = False

        if len(shortcut) == 0:
            return

        if isinstance(shortcut[-1], types.FunctionType):
            g_vars['current_menu_location'] = shortcut[:-1]
            g_vars['display_state'] = 'page'
            g_vars['option_selected'] = shortcut[-1]
            g_vars['option_selected']()
        else:
            g_vars['current_menu_location'] = shortcut
            g_vars['current_menu_location'].append(0)
            g_vars['display_state'] = 'menu'
            self.page_obj.draw_page(g_vars, menu)
