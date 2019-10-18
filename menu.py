from os import system, name
import curses
import threading

from cursesmenu.items import SubmenuItem as SubmenuItem_, FunctionItem
from cursesmenu import SelectionMenu as SelectionMenu_, CursesMenu as CursesMenu_

from utils import get_audio, play, save

root = None


class SubmenuItem(SubmenuItem_):

    def action(self):
        global root
        root.stdscr.clear()
        self.submenu.start()


class CursesMenu(CursesMenu_):
    stdscr = curses.initscr()


class SelectionMenu(SelectionMenu_):

    def _wrap_start(self):
        if self.parent is None:
            curses.wrapper(self._main_loop)
        else:
            self._main_loop(self.stdscr)
            CursesMenu.currently_active_menu = None
            self.stdscr.clear()
            self.stdscr.refresh()
            CursesMenu.currently_active_menu = self.previous_active_menu

def play_wrapper(id):
    def inner(*_, **__):
        nonlocal id
        play(id)
    return inner

def save_wrapper(id):
    def inner(*_, **__):
        nonlocal id
        save(id)
    return inner


def restore():
    curses.curs_set(1)
    if name in ['nt', 'windows']:
        system('cls')
        print('FUCK YOU ANYWAY! USE PROPER OS!')
    else:
        system('clear')


def placeholder(*args, **kwargs):
    global root, voices_menu
    words = []
    while True:
        try:
            word = input('type text to search:\n')
            if not word:
                break
            words.append(word)
        except KeyboardInterrupt:
            break
    print('fetching...')
    voices = SelectionMenu([])
    i = 0
    for text, id in get_audio(words):
        i += 1
        sel = SelectionMenu([], 'Choose phrase')
        si = SubmenuItem(text[:60], sel, voices)
        sel.append_item(FunctionItem(f"Play \"{text[:80]}\"", play_wrapper(id)))
        sel.append_item(FunctionItem(f"Save \"{text[:80]}\"", save_wrapper(id)))
        voices.append_item(si)
    voices.title = f'Tip for long outputs: to exit press `1` and arrow up'
    string = '+'.join(words)
    submenu_item = SubmenuItem(f'Found {string} voices: {i}', voices, root)
    
    root.append_item(submenu_item)

root = SelectionMenu([], title='Welcome to GLaDOS voice management system')
root.append_item(FunctionItem("Search for GLaDOS voices", placeholder))

try:
    root.show(show_exit_option=True)
except :
    restore()
