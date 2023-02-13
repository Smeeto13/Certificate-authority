import os

def prompt(ask):

    print(ask)

    response = input("(yes/no)").lower()

    while response not in ["yes", "no", "y", "n"]:
        print("Invalid response. Please enter 'yes' or 'no'.")
        response = input("Do you want to proceed? (yes/no) ").lower()

    if response in ["yes", "y"]:
        return True
    else:
        return False

def slotGen(name, cfg, type):
    if type == "ECCP384":
        os.system(f"openssl ecparam -genkey -name secp384r1 -out {name}/{name}.key")
    elif type == "RSA2048":
        os.system(f"openssl genrsa -out {name}/{name}.key 2048")
    
    os.system(f"openssl req -new -config {name}/{cfg}.cnf -key {name}/{name}.key -nodes -out {name}.csr")

def slotIssue(name, cfg, passwd):
    os.system(f"openssl ca -config Root-CA.cnf -in {name}.csr -out {name}/{name}.crt -extensions v3_req -extfile {name}/{cfg}.cnf -notext -passin pass:{passwd}")
    os.system(f"openssl pkcs12 -export -out {name}/{name}.pfx -inkey {name}/{name}.key -in {name}/{name}.crt -certfile certificates/CA.pem -passout pass:{passwd}")
    os.system(f"rm {name}.csr")

def main():
    passwd = ""
    if prompt("Generate CA?"):
        passwd = input("PEM Password: ")
        os.system("mkdir certificates")
        os.system(f"openssl req -new -x509 -sha256 -days 3650 -config Root-CA.cnf -extensions v3_req -set_serial 1 -keyout CA.key -out certificates/CA.pem -passout pass:{passwd}")
        os.system("echo 02 > serial")
    
    if prompt("Generate 9A?"):
        if passwd == "":
            passwd = input("PEM Password: ")
        slotGen("9A", "9a", "ECCP384") 
        slotIssue("9A", "9a", passwd)        

    if prompt("Generate 9C"):
        if passwd == "":
            passwd = input("PEM Password: ")
        slotGen("9C", "9c", "ECCP384")
        slotIssue("9C", "9c", passwd)
    
    if prompt("Generate 9E"):
        if passwd == "":
            passwd = input("PEM Password: ")
        slotGen("9E", "9e", "RSA2048")
        slotIssue("9E", "9e", passwd)
    
    if prompt("Generate CRL"):
        if passwd == "":
            passwd = input("PEM Password: ")
        os.system(f"openssl ca -config Root-CA.cnf -keyfile CA.key -cert certificates/CA.pem -gencrl -out CA-CRL.pem -passin pass:{passwd}")


main()