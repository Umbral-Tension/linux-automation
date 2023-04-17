from collections.abc import Iterable
import colorama
from colorama import Fore
import progress.bar # console progress bar module
import os
import sys

# initialize colorama so colors can be used in console text
colorama.init()
# reset formatting
endc = '\033[0m'
Bar = progress.bar.Bar # allows scripts to access the Bar class by importing jconsole

# return a string that will print the passed parameter in a given color
def white(text):
    return Fore.WHITE + str(text) + endc

def blue(text=''):
    return Fore.BLUE + str(text) + endc

def green(text=''):
    return Fore.GREEN + str(text) + endc

def cyan(text=''):
    return Fore.CYAN + str(text) + endc

def red(text=''):
    return Fore.RED + str(text) + endc

def purple(text=''):
    return Fore.MAGENTA + str(text) + endc

def yellow(text=''):
    return Fore.YELLOW + str(text) + endc

def underline(text=''):
    return '\033[4m' + str(text) + endc

def bold(text=''):
    return '\033[1m' + str(text) + endc

def q(str):
    return f'"{str}"'
    
def yes_no(s=''):
    """Prompt user for a yes or no response."""
    while True:
        response = input(s + ' (Y/N):')
        if response.lower() == 'y':
            return True
        elif response.lower() == 'n':
            return False
        else:
            print('Use the \'Y\'/\'N\' keys to choose Yes or No')
    

def exit_app(exit_message=''):
    """Display exit message, then wait for user to press enter before running exit()"""
    print(red(exit_message))
    input('\nPress Enter to exit the program')
    sys.exit(0)

def cls():
    os.system('cls')

def zen(message='here', title=f'debug info'):
    """Use zenity on linux to display a popup window showing the content of message."""
    os.system(f'zenity --title "{title}" --info --text "{message}"')

def test_(*variables):
    """returns the pretty-print string from test() instead of printing it."""
    return _recursively_add_vars(variables)

def test(*variables):
    """pretty print all items in *variables."""
    colorama.reinit()
    if len(variables) == 0:
        print(bold(blue('here')))
    else:
        print(_recursively_add_vars(variables))


def _recursively_add_vars(iterable, indent_lvl=0):
    """Recurse into iterables and add their values to the printstring that test() will ultimately display.

    This function is only called from within test()"""
    printstring = ''
    base_indent = '    '
    iterable_is_dictionary = isinstance(iterable, dict)
    if iterable_is_dictionary:
        keys = list(iterable.keys())
    # The first call of _recursively...() is always done by test() which always passes in its *variables parameter.
    # *variables is an iterable so there is no 'isIterable' check necessary at this outer scope. 
    for i in range(len(iterable)): 
        
        # the 0th indentation lvl refers to the top lvl variables that were actually passed to the test() function.
        # These will be labeled in the display as "test_var 2: " and so on. 
        if indent_lvl == 0:
            printstring += bold(purple(f'test_var {i}:\n'))

        # curr_value is the single object 'under consideration' (for a given loop iteration of a given function call)
        # It will be checked to see if it is a simple value that's okay to print, or if it is an iterable that needs to
        # be recursed into further. # note: dictionaries cannot be indexed by just i, so a list of the dictionary's
        # keys is made which CAN be indexed by i.
        if iterable_is_dictionary:
            curr_value = iterable[keys[i]]
        else:
            curr_value = iterable[i]
        
        # This is the recursive function's base case. It stops recursing when it finds a string or non-iterable
        # because it makes sense to print these primitives 'as-is'
        # TODO Look into __get_item__ implementation to support recursion into non-standard iterables. Currently only
        #  simple iterables are recursed into eg (list/dict/set/tuple).
        import builtins
        builtin_types = [getattr(builtins, d) for d in dir(builtins) if isinstance(getattr(builtins, d), type)]
        curr_value_is_primitive = isinstance(curr_value, (str, set)) or not isinstance(curr_value, Iterable) \
                                  or (isinstance(curr_value, Iterable) and type(curr_value) not in builtin_types)

        indent_str = base_indent * indent_lvl
        
        if iterable_is_dictionary:  # we always want to print dictionary keys, even if their value is another iterable
            printstring += f'{indent_str}{cyan("key:")}{yellow(keys[i])}{cyan(" value:")} '
            if not curr_value_is_primitive:
                # print type of the current key's value (i.e. the type of the upcoming iterable)
                printstring += f'{bold(type(curr_value))}'
                # don't want to start printing a lower nested iterable on the same line as the upper dictionary key
                printstring += '\n'
        if curr_value_is_primitive:
            if iterable_is_dictionary:  # special formatting required for dictionaries
                printstring += f'{yellow(iterable[keys[i]])}\n'
            else:
                printstring += indent_str + yellow(str(curr_value)) + '\n'
        
        # Continue recursion if curr_value is an iterable. 
        if not curr_value_is_primitive:
            # type info will already have been printed if iterable is a dictionary. 
            if not iterable_is_dictionary:
                printstring += f'{indent_str}{bold(type(curr_value))}\n'
            printstring += _recursively_add_vars(curr_value, indent_lvl=indent_lvl + 1)
    return printstring



def ptest(*variables, inline=False):
    """ Pass all parameters to test() and then pause execution until user presses enter."""
    test(*variables)
    input(red('Process paused. Press any key to un-pause'))


# formatted dir() function 
def dir_(obj):
    import inspect
    from inspect import isclass, isfunction, ismethod, isbuiltin
    reg_dir = dir(obj)
    new_dir = {'classes': [], 'functions': [], 'methods': [], 'attributes': []}

    # TODO figure out how to neatly print part of the doc string for object attributes
    def attr_str(attr, attr_name):
        # doc = attr.__doc__
        # if isinstance(doc, str):
        #     doc = doc[:40].replace('\\n', '  ').replace('\r', '  ').strip()
        #     return (attr_name, doc)
        # else:
        #     return attr_name
        return attr_name

    for x in reg_dir:
        attr = getattr(obj, x)
        if x.startswith('_') or x.isupper():
            continue
        elif isfunction(attr) or isbuiltin(attr):
            new_dir['functions'].append(attr_str(attr, x))
        elif isclass(attr):
            new_dir['classes'].append(attr_str(attr, x))
        elif ismethod(attr):
            new_dir['methods'].append(attr_str(attr, x))
        else:
            new_dir['attributes'].append(attr_str(attr, x))
    return new_dir



    
if __name__ == '__main__':
    pass
