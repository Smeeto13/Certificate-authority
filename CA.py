import os
import getpass

def selection_menu(options):
    """
    Displays a selection menu and returns the user's choice.
    The options should be a list of strings.
    """
    for i, option in enumerate(options):
        print(f"{i+1}. {option}")
    choice = 0
    while choice < 1 or choice > len(options):
        try:
            choice = int(input(f"Choose an option (1-{len(options)}): "))
        except ValueError:
            pass
    return choice

def passIn(): #Gets password with 6 or more characters
    print("Show/Hide Password input?")
    passCheck = False
    selection = selection_menu(["Show","Hide"])
    while passCheck == False:
        if selection == 1:
            passwd = input("PEM Password: ")
        else:
            passwd = getpass.getpass("PEM Password: ")
        
        if len(passwd) >= 6:
            passCheck = True
        else:
            print("Password too short!")
    return passwd

def selectCNF(allowNone):
    print("pick a config:")
    configs = os.listdir("cnf")
    if allowNone:
        configs.append("No CNF (CSR Signing only)")
    selection = selection_menu(configs)
    return configs[selection-1]

def selectCSR():
    print("pick a config:")
    CSRs = os.listdir("csr")
    selection = selection_menu(CSRs)
    return CSRs[selection-1]

def slotGen(slot, passwd): #Preconfigured steps for generating PFX for YubiKey PIV slots
    match slot:
        case 1:
            name = "9A"
            csr = f"{name}.csr"
            cfg = "9a.cnf"
            keyGen(name, csr, cfg, "ECCP384")
            crtIssue(name, csr, cfg, passwd)
            pfxOut(name, passwd)
        case 2:
            name = "9C"
            csr = f"{name}.csr"
            cfg = "9c.cnf"
            keyGen(name, csr, cfg, "ECCP384")
            crtIssue(name, csr, cfg, passwd)
            pfxOut(name, passwd)
        case 3:
            name = "9E"
            csr = f"{name}.csr"
            cfg = "9e.cnf"
            keyGen(name, csr, cfg, "RSA2048")
            crtIssue(name, csr, cfg, passwd)
            pfxOut(name, passwd)

def keyGen(name, csr, cfg, type): #Generates key and CSR
    os.system(f"mkdir -p out/{name}")
    if type == "ECCP384":
        os.system(f"openssl ecparam -genkey -name secp384r1 -out out/{name}/{name}.key")
    elif type == "RSA2048":
        os.system(f"openssl genrsa -out out/{name}/{name}.key 2048")
    
    os.system(f"openssl req -new -config cnf/{cfg} -key out/{name}/{name}.key -nodes -out csr/{csr}")

def crtIssue(name, csr, cfg, passwd): #Issues certificate using CSR and optional config
    os.system(f"mkdir -p out/{name}")
    if cfg == "No CNF (CSR Signing only)":
        os.system(f"openssl ca -config Root-CA.cnf -in csr/{csr} -out out/{name}/{name}.crt -extensions copy -notext -passin pass:{passwd}")
    else:
        os.system(f"openssl ca -config Root-CA.cnf -in csr/{csr} -out out/{name}/{name}.crt -extensions v3_req -extfile cnf/{cfg} -notext -passin pass:{passwd}")
    os.system(f"rm csr/{csr}")

def pfxOut(name,passwd): #Combines Key, CRT and CA CRT into PFX file
    os.system(f"openssl pkcs12 -export -out out/{name}/{name}.pfx -inkey out/{name}/{name}.key -in out/{name}/{name}.crt -certfile certificates/CA.pem -passout pass:{passwd}")

def customCRT(passwd): #Create Key and CRT or sign existing CSR
    print("Generate new key or use provided CSR?")
    selection = selection_menu(["New Key","Sign existing CSR"])
    name = input("Name: ")
    if selection == 1: #Generate Key and issue CRT then export to PFX
        cfg = selectCNF(False)
        csr = f"{name}.csr"
        print("Key Type:")
        selection = selection_menu(["RSA2048","ECCP384"])
        if selection == 1:
            keyGen(name, csr, cfg, "RSA2048")
        else:
            keyGen(name, csr, cfg, "ECCP384")
        crtIssue(name, csr, cfg, passwd)
        pfxOut(name,passwd)
    else: #Only issue certificate
        cfg = selectCNF(True)
        csr = selectCSR()
        crtIssue(name, csr, cfg, passwd)
    
def crtRevoke(passwd):
    print("Select certificate Serial: ")
    crts = os.listdir("certificates")
    selection = selection_menu(crts)
    os.system(f"openssl ca -revoke certificates/{crts[selection-1]} -config Root-CA.cnf -passin pass:{passwd}")

def main():
    #Create directories if not already present:
    os.system("mkdir -p cnf")
    os.system("mkdir -p csr")
    os.system("mkdir -p out")
    os.system("mkdir -p certificates")
    
    passwd = passIn()

    quit = False

    #Main Menu
    while quit == False:
        selection = selection_menu(["Generate CA","Generate YubiKey Slot","Generate Custom Certificate","Revoke","Generate CRL","Quit"])
        match selection:
            case 1: #Gen CA
                os.system(f"openssl req -new -x509 -sha256 -days 3650 -config Root-CA.cnf -extensions v3_req -set_serial 1 -keyout CA.key -out certificates/CA.pem -passout pass:{passwd}")
                os.system("openssl x509 -outform der -in certificates/CA.pem -out CA.crt")
                os.system("echo 02 > serial")

            case 2: #Gen YubiKey Slot
                selection = selection_menu(["9A - Authentication","9C - Digital Signature","9E - Card Authentication"])
                slotGen(selection, passwd)

            case 3: #Gen Custom Crt
                customCRT(passwd)

            case 4: #Revoke
                crtRevoke(passwd)
 
            case 5: #Gen CRL
                os.system(f"openssl ca -config Root-CA.cnf -keyfile CA.key -cert certificates/CA.pem -gencrl -out out/CRL.pem -passin pass:{passwd}")
    
            case 6: #Quit
                quit = True

main()