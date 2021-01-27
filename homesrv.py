#!/usr/bin/env python3

import argparse
import pathlib
import platform
import readline
import subprocess
import sys

# PACKAGE_MANAGERS = {
#     "apt-get": "apt-get install ?",
#     "pacman": "pacman -S ?",
#     "dnf": "dnf install ?",
#     "yum": "yum install ?",
#     "apk": "apk add ?"
# }

def init(args):
    os = platform.system()
    if os != "Linux":
        print("Homesrv is only designed to work on Linux operating systems.")
        sys.exit(1)

    distro, release = find_distro()
    if distro is None:
        print("Cannot determine your Linux distribution.")
        sys.exit(2)
    print(distro, release)

    # pm = find_package_manager()
    # if pm is None:
    #     print("Cannot determine your Linux distribution's package manager.")
    #     sys.exit(2)
    # print(pm)

    def_config_location = str(pathlib.Path(pathlib.Path.home(), ".config", "homesrv"))
    print(f"By default, configuration files for apps will be stored here: {def_config_location}")
    print("If you wish to change this, type a new location below. Otherwise, press Enter to accept the default.")
    config_location = input("> ") or def_config_location
    print(f"Config files will be stored in: {config_location}")
    print()

    def_userdata_location = "/var/lib/homesrv"
    print(f"By default, user data stored by apps will be kept here: {def_userdata_location}")
    print("If you wish to change this, type a new location below. Otherwise, press Enter to accept the default.")
    userdata_location = input("> ") or def_userdata_location
    print(f"User data will be stored in: {userdata_location}")

    app_list = prompt_list_selection(
        "Below is a list of available apps to install. Options with \"[*]\" beside them will be installed. " \
        "Options with \"[ ]\" beside them will not be installed.",
        [
            "Portainer (Docker management)",
            "Nextcloud (File sync)",
            "Jellyfin (Media streaming)",
            "Miniflux (RSS reader)"
        ],
        [True, True, False, False]
    )
    print(app_list)


def install(args):
    raise NotImplementedError

def start(args):
    raise NotImplementedError

def stop(args):
    raise NotImplementedError

def restart(args):
    raise NotImplementedError


def find_distro():
    """Determine which Linux distro is being used."""
    try:
        distro_out = subprocess.run(["lsb_release", "-ds"], capture_output=True, encoding="utf-8").stdout
        distro_out = distro_out.strip().replace('"', '').replace("'", "").lower()
        release_out = subprocess.run(["lsb_release", "-cs"], capture_output=True, encoding="utf-8").stdout
        release_out = release_out.strip().replace('"', '').replace("'", "").lower()
        return (distro_out, release_out)
    except subprocess.CalledProcessError:
        return None

# def find_package_manager():
#     """Determine which Linux package manager is being used."""
#     for pm in PACKAGE_MANAGERS.keys():
#         if subprocess.call(["which", pm], stdout=subprocess.PIPE, stderr=subprocess.PIPE) == 0:
#             return pm
#     return None

# def install_packages(package_manager, pkglist):
#     """Given a list of package names, will install the packages using the system's
#     package manager.
#     """
#     pkg_text = " ".join(pkglist)
#     return subprocess.call(PACKAGE_MANAGERS[package_manager].replace("?", pkg_text), shell=True) == 0

def prompt_yn(prompt):
    """Prompt the user for a yes/no answer. Response options will be added to the end
    of the prompt.
    """
    result = None
    while result is None:
        inpt = input(f"{prompt} (y/n) ")
        inpt = inpt.lower()
        if inpt == "y" or inpt == "yes":
            result = True
        elif inpt == "n" or inpt == "no":
            result = False
    return result

def prompt_list_selection(prompt, options_list, initial_state):
    """Give the user a list of options, and allow them to select/deselect each option
    until satisfied.
    """
    state = initial_state
    inpt = ""
    while inpt.lower() != "done":
        print()
        print(prompt)
        for i, opt in enumerate(options_list):
            sel = "*" if state[i] else " "
            print(f" [{sel}] {i+1}. {opt}")
        print("Type a number below to toggle that item between selected and unselected. When you are satisfied, type \"done\".")
        inpt = input("> ")
        try:
            inpt_int = int(inpt) - 1
            if inpt_int >= 0 and inpt_int < len(options_list):
                state[inpt_int] = not state[inpt_int]
        except ValueError:
            pass
    return state


def install_docker(distro, release):
        try:
            if distro == "debian" or distro == "ubuntu":
                subprocess.run("apt-get update")
                subprocess.run("apt-get install apt-transport-https ca-certificates curl gnupg-agent software-properties-common")

                subprocess.run(f"curl -fsSL https://download.docker.com/linux/{distro}/gpg | apt-key add -")
                subprocess.run(f"add-apt-repository \"deb [arch=amd64] https://download.docker.com/linux/{distro} {release} stable")

                subprocess.run("apt-get update")
                subprocess.run("apt-get install docker-ce docker-ce-cli containerd.io")

            elif distro == "centos":
                subprocess.run("yum install -y yum-utils")
                subprocess.run("yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo")

                subprocess.run("yum install docker-ce docker-ce-cli containerd.io")

                subprocess.run("systemctl enable docker.service")
                subprocess.run("systemctl enable containerd.service")
                subprocess.run("systemctl start docker.service")


            elif distro == "fedora":
                subprocess.run("dnf -y install dnf-plugins-core")
                subprocess.run("dnf config-manager --add-repo https://download.docker.com/linux/fedora/docker-ce.repo")

                subprocess.run("dnf install docker-ce docker-ce-cli containerd.io")

                subprocess.run("systemctl enable docker.service")
                subprocess.run("systemctl enable containerd.service")
                subprocess.run("systemctl start docker.service")

        except subprocess.CalledProcessError:
            print("Unable to install Docker. Exiting.")
            sys.exit(3)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Manage your home server.")
    parser.set_defaults(func=init)
    subparsers = parser.add_subparsers()

    parser_init = subparsers.add_parser('init', help="Initialize the home server (first-time setup).")
    parser_init.set_defaults(func=init)

    parser_install = subparsers.add_parser('install', help="Install new apps after the initial setup.")
    parser_init.set_defaults(func=install)

    parser_start = subparsers.add_parser('start', help="Start apps by listing them.")
    parser_start.set_defaults(func=start)

    parser_stop = subparsers.add_parser('stop', help="Stop apps by listing them.")
    parser_stop.set_defaults(func=stop)

    parser_restart = subparsers.add_parser('restart', help="Restart apps by listing them.")
    parser_restart.set_defaults(func=restart)

    args = parser.parse_args()
    args.func(args)
