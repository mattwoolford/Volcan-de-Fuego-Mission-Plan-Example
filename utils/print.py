from termcolor import cprint


def eprint(error):
    print_error(error)


def print_error(error, blink=True):
    cprint(f" {error} ",
           "white",
           "on_light_red",
           attrs=list(filter(lambda x: x is not None, ["bold", "blink" if blink else None])))


def print_success(message, blink=False):
    cprint(f" {message} ",
           "white",
           "on_light_green",
           attrs=list(filter(lambda x: x is not None, ["bold", "blink" if blink else None])))


def print_warning(message, blink=False):
    cprint(f" {message} ",
           "black",
           "on_light_yellow",
           attrs=list(filter(lambda x: x is not None, ["bold", "blink" if blink else None])))


def sprint(message):
    print_success(message)


def wprint(message):
    print_warning(message)
