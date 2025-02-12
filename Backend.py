""" Copyright 2023, 2024, 2025 Sophie Smeeton
This file is part of Certificate-authority-Tool

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.  """

import os
import uuid

class CertificateAuthority:
    """Behind the scenes operations"""

    def __init__(self) -> None:
        """Initialises variables and create the directory structure"""

        self.passwd = ""

        if os.name == 'posix':
            os.system("mkdir -p csr")
            os.system("mkdir -p out")
            os.system("mkdir -p certificates")
        else:
            os.system("mkdir -f csr")
            os.system("mkdir -f out")
            os.system("mkdir -f certificates")

    def set_sc(self, use_sc):
        """Sets if the CA is stored on a Smart Card"""
        match use_sc:
            case "PKCS11 CA":
                self.use_sc = True
                self.opts = "-engine pkcs11 -keyform engine"
                if os.path.isfile("CA_SN.conf"):
                    with open("CA_SN.conf","r") as ca_sn:
                        self.key_file = ca_sn.read()
                    print(self.key_file)
                else:
                    print("No key ID in CA_SN.conf, Generating new CA")
                    self.create_ca()
            case "Software CA":
                self.use_sc = False
                self.key_file = "CA.key"
                self.opts = f"-passin pass:{self.passwd}"
                if not os.path.isfile("CA.key"):
                    print("No CA key found, Generating new CA")
                    self.create_ca()

    def set_pass(self, passwd):
        """Set's the password to use for the CA key and PFX exports"""

        self.passwd = passwd

    def create_ca(self):
        """Create a self signed CA"""
        if not os.path.isfile("CA.key") and not self.use_sc:
            os.system(
                f"openssl req -new -x509 -sha512 -days 3650 -config Root-CA.cnf -extensions v3_ca -set_serial 1 -keyout CA.key -out certificates/CA.pem -passout pass:{self.passwd}")
        elif self.use_sc and not os.path.isfile("CA_SN.conf"):
            serial_number = uuid.uuid4().hex
            os.system(f"""pkcs11-tool --login --keypairgen --key-type rsa:2048 --label "CA" --id {serial_number}""")
            os.system(f"openssl req -config Root-CA.cnf -engine pkcs11 -keyform engine -key {serial_number} -new -x509 -days 3650 -sha512 -extensions v3_ca -set_serial 1 -out certificates/CA.pem")
            os.system("pkcs15-init -X certificates/CA.pem")
            with open("CA_SN.conf","w") as ca_sn:
                ca_sn.write(serial_number)
            self.key_file = serial_number
        else:
            print("CA key already exists")
        os.system("openssl x509 -outform der -in certificates/CA.pem -out out/CA.crt")
        os.system("echo 02 > serial")

    def key_gen(self, name, csr, cfg, key_type):
        """Generates key and CSR"""

        os.system(f"mkdir -p out/{name}")
        match key_type:
            case "ECCP384":
                os.system(
                    f"openssl ecparam -genkey -name secp384r1 -out out/{name}/{name}.key")
            case "ECCP521":
                os.system(
                    f"openssl ecparam -genkey -name secp521r1 -out out/{name}/{name}.key")
            case "Prime 256":
                os.system(
                    f"openssl ecparam -genkey -name prime256v1 -out out/{name}/{name}.key")
            case "RSA2048":
                os.system(f"openssl genrsa -out out/{name}/{name}.key 2048")
            case "RSA4096":
                os.system(f"openssl genrsa -out out/{name}/{name}.key 4096")

        os.system(
            f"openssl req -new -config cnf/{cfg} -key out/{name}/{name}.key -nodes -out csr/{csr}")

    def crt_issue(self, name, csr, cfg, ca_config="Root-CA.cnf"):
        """Issues certificate using CSR and optional config, specify ca_config to change the issuing CA"""

        os.system(f"mkdir -p out/{name}")
        if cfg == "No CNF (CSR Signing only)":
            os.system(
                f"openssl ca -config {ca_config} -keyfile {self.key_file} -in csr/{csr} -out out/{name}/{name}.crt -extensions copy -notext {self.opts}")
        else:
            os.system(
                f"openssl ca -config {ca_config} -keyfile {self.key_file} -in csr/{csr} -out out/{name}/{name}.crt -extensions v3_req -extfile cnf/{cfg} -notext {self.opts}")
        os.system(f"rm csr/{csr}")

    def pfx_out(self, name):
        """Combines Key, CRT and CA CRT into PFX file"""

        os.system(
            f"openssl pkcs12 -export -out out/{name}/{name}.pfx -inkey out/{name}/{name}.key -in out/{name}/{name}.crt -certfile certificates/CA.pem -passout pass:{self.passwd}")

    def crt_revoke(self, revoke, ca_config="Root-CA.cnf"):
        """Revoke a certificate, specify ca_config to revoke a certificate from a intermediate CA"""
        os.system(
            f"openssl ca -revoke certificates/{revoke} -config {ca_config} -keyfile {self.key_file} {self.opts}")

    def create_crl(self, ca_config="Root-CA.cnf"):
        """generates the crl for a CA"""
        os.system(
            f"openssl ca -config {ca_config} -keyfile {self.key_file} -gencrl -out out/CRL.pem {self.opts}")
