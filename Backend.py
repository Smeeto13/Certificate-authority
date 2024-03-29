""" Copyright 2023, 2024 Sophie Smeeton
This file is part of Certificate-authority-Tool

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.  """

import os


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

    def set_pass(self, passwd):
        """Set's the password to use for the CA key and PFX exports"""

        self.passwd = passwd

    def create_ca(self):
        """Create a self signed CA"""
        if not os.path.isfile("CA.key"):
            os.system(
                f"openssl req -new -x509 -sha256 -days 3650 -config Root-CA.cnf -extensions v3_req -set_serial 1 -keyout CA.key -out certificates/CA.pem -passout pass:{self.passwd}")
            os.system(
                "openssl x509 -outform der -in certificates/CA.pem -out out/CA.crt")
            os.system("echo 02 > serial")
        else:
            print("\"CA.key\" already exists")

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
                f"openssl ca -config {ca_config} -in csr/{csr} -out out/{name}/{name}.crt -extensions copy -notext -passin pass:{self.passwd}")
        else:
            os.system(
                f"openssl ca -config {ca_config} -in csr/{csr} -out out/{name}/{name}.crt -extensions v3_req -extfile cnf/{cfg} -notext -passin pass:{self.passwd}")
        os.system(f"rm csr/{csr}")

    def pfx_out(self, name):
        """Combines Key, CRT and CA CRT into PFX file"""

        os.system(
            f"openssl pkcs12 -export -out out/{name}/{name}.pfx -inkey out/{name}/{name}.key -in out/{name}/{name}.crt -certfile certificates/CA.pem -passout pass:{self.passwd}")

    def crt_revoke(self, revoke, ca_config="Root-CA.cnf"):
        """Revoke a certificate, specify ca_config to revoke a certificate from a intermediate CA"""
        os.system(
            f"openssl ca -revoke certificates/{revoke} -config {ca_config} -passin pass:{self.passwd}")

    def create_crl(self, ca_config="Root-CA.cnf"):
        """generates the crl for a CA"""
        os.system(
            f"openssl ca -config {ca_config} -gencrl -out out/CRL.pem -passin pass:{self.passwd}")
