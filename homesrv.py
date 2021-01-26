#!/usr/bin/env python3

import platform
import subprocess
import sys

PACKAGE_MANAGERS = {
    "apt-get": "apt-get install ?",
    "pacman": "pacman -S ?",
    "dnf": "dnf install ?",
    "yum": "yum install ?",
    "apk": "apk add ?"
}

def find_package_manager():
    """Determine which Linux package manager is being used."""
    for pm in PACKAGE_MANAGERS.keys():
        if subprocess.call(["which", pm], stdout=subprocess.PIPE, stderr=subprocess.PIPE) == 0:
            return pm
    return None

def install_packages(package_manager, pkglist):
    """Given a list of package names, will install the packages using the system's
    package manager.
    """
    pkg_text = " ".join(pkglist)
    return subprocess.call(PACKAGE_MANAGERS[package_manager].replace("?", pkg_text), shell=True) == 0

def prompt_yn(prompt):
    """Prompt the user for a yes/no answer. Response options will be added to the end
    of the prompt.
    """
    result = None
    while result is None:
        inpt = input(prompt + " (y/n)")
        inpt = inpt.lower()
        if inpt == "y" or inpt == "yes":
            result = True
        elif inpt == "n" or inpt == "no":
            result = False
    return result


def main():
    os = platform.system()
    if os != "Linux":
        print("Homesrv is only designed to work on Linux operating systems.")
        sys.exit(1)

    pm = find_package_manager()
    if pm is None:
        print("Cannot determine your Linux distribution's package manager.")
        sys.exit(2)
    print(pm)

    test = prompt_yn("Does this work?")
    print(test)


if __name__ == "__main__":
    main()
