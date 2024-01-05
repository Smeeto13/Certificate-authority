""" Copyright 2023, 2024 Sophie Smeeton
This file is part of Certificate-authority-Tool

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.  """

import os
import getpass
import Backend


def selection_menu(options):
    """
    Displays a selection menu and returns the user's choice.
    The options should be a list of strings.
    """
    for i, option in enumerate(options):
        print(f"{i}. {option}")
    choice = -1
    while choice < 0 or choice > len(options)-1:
        try:
            choice = int(input(f"Choose an option (1-{len(options)}): "))
        except ValueError:
            pass
    return options[choice]


def pass_in():
    """Gets password with 6 or more characters"""
    print("Show/Hide Password input?")
    pass_check = False
    selection = selection_menu(["Show", "Hide"])
    while pass_check is False:
        if selection == "Show":
            passwd = input("PEM Password: ")
        else:
            passwd = getpass.getpass("PEM Password: ")

        if len(passwd) >= 6:
            pass_check = True
        else:
            print("Password too short!")
    return passwd


def piv_menu():
    """Generate a PFX for PIV slots 9A, 9C, 9D or 9E, slot argument should be one of these, specify ca_config to change the issuing CA"""
    name = selection_menu(
        ["9A - Authentication", "9C - Digital Signature", "9D - Card Authentication"])[0:2]
    csr = f"{name}.csr"
    cfg = f"{name}.cnf"
    key_type = selection_menu(
        ["RSA2048", "ECCP384", "RSA4096", "Prime 256"])

    CA.key_gen(name, csr, cfg, key_type)
    CA.crt_issue(name, csr, cfg)
    CA.pfx_out(name)


def select_cnf(allow_none):
    print("pick a config:")
    configs = os.listdir("cnf")
    if allow_none:
        configs.append("No CNF (CSR Signing only)")
    selection = selection_menu(configs)
    return selection


def select_csr():
    print("pick a CSR:")
    csr_s = os.listdir("csr")
    selection = selection_menu(csr_s)
    return selection


def custom_crt():  # Create Key and CRT or sign existing CSR
    print("Generate new key or use provided CSR?")
    selection = selection_menu(["New Key", "Sign existing CSR"])
    name = input("Name: ")
    if selection == "New Key":  # Generate Key and issue CRT then export to PFX
        cfg = select_cnf(False)
        csr = f"{name}.csr"
        print("Key Type:")
        key_type = selection_menu(
            ["ECCP384", "ECCP521", "Prime 256", "RSA2048", "RSA4096"])
        CA.key_gen(name, csr, cfg, key_type)
        CA.crt_issue(name, csr, cfg)
        CA.pfx_out(name)
    else:  # Only issue certificate
        cfg = select_cnf(True)
        csr = select_csr()
        CA.crt_issue(name, csr, cfg)


CA = Backend.CertificateAuthority()


def main():
    CA.set_pass(pass_in())
    exit_menu = False

    # Main Menu
    while exit_menu is False:
        selection = selection_menu(["Generate CA", "Generate YubiKey/PIV Slot",
                                   "Generate Custom Certificate", "Revoke", "Generate CRL", "Quit"])
        match selection:
            case "Generate CA":
                CA.create_ca()
            case "Generate YubiKey/PIV Slot":
                piv_menu()

            case "Generate Custom Certificate":
                custom_crt()

            case "Revoke":
                print("Select certificate Serial: ")
                crts = os.listdir("certificates")
                crts.sort()
                selection = selection_menu(crts)
                CA.crt_revoke(selection)

            case "Generate CRL":
                CA.create_crl()

            case "Quit":
                exit_menu = True


# Checks if running as a import, only runs if ran directly
if __name__ == "__main__":
    main()
