#################################################
# Create a page object that renders dispay page
#################################################
import fpms.modules.wlanpi_oled as oled

from fpms.modules.pages.display import *
from fpms.modules.themes import THEME
from fpms.modules.constants import (
    STATUS_BAR_HEIGHT,
    SMART_FONT,
    FONT11,
    FONT12,
    FONTB11,
    FONTB12,
    MAX_PAGE_LINES,
)

class Page(object):

    def __init__(self, g_vars):

        # grab a screeb obj
        self.display_obj = Display(g_vars)

    def draw_page(self, g_vars, menu):

        # Drawing already in progress - return
        if g_vars['drawing_in_progress']:
            return

        # signal we are drawing
        g_vars['drawing_in_progress'] = True

        ################################################
        # show menu list based on current menu position
        ################################################

        # FIXME: This feels clunky. Would be best to access menu locations
        #       via evaluated location rather than crawling over menu

        menu_structure = menu
        location_search = []
        depth = 0
        section_name = [g_vars['home_page_name']]

        # Crawl the menu structure until we hit the current specified location
        while g_vars['current_menu_location'] != location_search:

            # List that will be used to build menu items to display
            menu_list = []

            # Current menu location choice specified in list format:
            #  g_vars['current_menu_location'] = [2,1]
            #
            # As we move though menu depths, inpsect next level of
            # menu structure
            node = g_vars['current_menu_location'][depth]

            # figure out the number of menu options at this menu level
            number_menu_choices = len(menu_structure)

            if node == number_menu_choices:

                # we've fallen off the end of menu choices, fix item by zeroing
                node = 0
                g_vars['current_menu_location'][depth] = 0

            location_search.append(node)

            item_counter = 0

            for menu_item in menu_structure:

                item_name = menu_item['name']

                # this is the currently selected item, pre-pend name with '*'
                if (item_counter == node):
                    section_name.append(item_name)
                    item_name = "*" + item_name

                # this item contains a list of options, append name with '>'
                if (type(menu_item['action']) is list):
                    if len(item_name) > 16:
                        item_name = item_name[:14] + ".."
                    item_name = item_name + ">"

                menu_list.append((item_name))

                item_counter = item_counter + 1

            depth = depth + 1

            # move down to next level of menu structure & repeat for new level
            menu_structure = menu_structure[node]['action']

        option_number_selected = node
        g_vars['option_selected'] = menu_structure

        # if we're at the top of the menu tree, show the home page title
        if depth == 1:
            page_name = g_vars['home_page_name']
        else:
            # otherwise show the name of the parent menu item
            page_name = section_name[-2]

        page_title = page_name.upper()

        # shorten title if necessary
        if len(page_title) > 15:
            page_title = page_title[:13] + ".."

        # Clear display prior to painting new item
        self.display_obj.clear_display(g_vars)

        # paint the page title
        g_vars['draw'].rectangle((0, 0, PAGE_WIDTH, STATUS_BAR_HEIGHT), fill=THEME.page_title_background.value)
        title_size = FONTB12.getsize(page_title)
        g_vars['draw'].text(((PAGE_WIDTH - title_size[0])/2, 0), page_title,  font=FONTB12, fill=THEME.page_title_foreground.value)

        # draw back nav indicator
        g_vars['draw'].line([(4, (STATUS_BAR_HEIGHT/2)), (8, 4)], fill=THEME.page_title_foreground.value, width=1)
        g_vars['draw'].line([(4, (STATUS_BAR_HEIGHT/2)), (8, STATUS_BAR_HEIGHT-4)], fill=THEME.page_title_foreground.value, width=1)

        # vertical starting point for menu (under title) & incremental offset for
        # subsequent items
        y = STATUS_BAR_HEIGHT + 1
        y_offset = 14

        # define display window limit for menu table
        table_window = MAX_PAGE_LINES

        # determine the menu list to show based on current selection and window limits
        if (len(menu_list) > table_window):

            # We've got more items than we can fit in our window, need to slice to fit
            if (option_number_selected >= table_window):
                menu_list = menu_list[(option_number_selected - (table_window - 1)): option_number_selected + 1]
            else:
                # We have enough space for the menu items, so no special treatment required
                menu_list = menu_list[0: table_window]

        # paint the menu items, highlighting selected menu item
        for menu_item in menu_list:

            nav = False
            sel = False

            rect_fill = THEME.page_item_background.value
            text_fill = THEME.page_item_foreground.value
            nav_fill  = THEME.page_item_foreground.value
            icon_fill = THEME.page_icon_foreground.value
            font_type = FONTB11

            # this is a menu item that has more options: remove > character
            if (menu_item[-1] == '>'):
                nav = True
                menu_item = menu_item[:-1]

            # this is selected menu item: highlight it and remove * character
            if (menu_item[0] == '*'):
                sel = True
                rect_fill = THEME.page_selected_item_background.value
                text_fill = THEME.page_selected_item_foreground.value
                nav_fill  = THEME.page_selected_item_foreground.value
                icon_fill = THEME.page_selected_item_foreground.value
                menu_item = menu_item[1:len(menu_item)]

            g_vars['draw'].rectangle((0, y, PAGE_WIDTH, y+y_offset), fill=rect_fill)
            g_vars['draw'].text((12, y), menu_item,  font=font_type, fill=text_fill)

            if nav:
                # draw list icon
                g_vars['draw'].line([(2, y+(y_offset/2)-2), (2, y+(y_offset/2)-2)], fill=icon_fill, width=1)
                g_vars['draw'].line([(2, y+(y_offset/2)),   (2, y+(y_offset/2))  ], fill=icon_fill, width=1)
                g_vars['draw'].line([(2, y+(y_offset/2)+2), (2, y+(y_offset/2)+2)], fill=icon_fill, width=1)
                g_vars['draw'].line([(4, y+(y_offset/2)-2), (8, y+(y_offset/2)-2)], fill=icon_fill, width=1)
                g_vars['draw'].line([(4, y+(y_offset/2)),   (8, y+(y_offset/2))  ], fill=icon_fill, width=1)
                g_vars['draw'].line([(4, y+(y_offset/2)+2), (8, y+(y_offset/2)+2)], fill=icon_fill, width=1)
                # draw nav indicator
                g_vars['draw'].line([(PAGE_WIDTH - 4, y+(y_offset/2)), (PAGE_WIDTH - 8, y+3)], fill=icon_fill, width=1)
                g_vars['draw'].line([(PAGE_WIDTH - 4, y+(y_offset/2)), (PAGE_WIDTH - 8, y+y_offset-3)], fill=icon_fill, width=1)
            else:
                # draw action icon
                if sel:
                    g_vars['draw'].ellipse((3, y+(y_offset/2)-2, 7, y+(y_offset/2)+2), fill=icon_fill)
                else:
                    g_vars['draw'].ellipse((3, y+(y_offset/2)-2, 7, y+(y_offset/2)+2), outline=icon_fill)

            y += y_offset

        oled.drawImage(g_vars['image'])

        g_vars['drawing_in_progress'] = False
