import re
import os
import sys
import json

class manage_ca_certs:
    def __init__(self, ca_name: str, common_name: str) -> None:
        self.ca_name = ca_name
        self.common_name = common_name
        self.ca_path = re.sub(r"[^\w]", r"_", self.ca_name).lower()

        # The script will be terminated with the exit code 0 if the CA path already exists. Otherwise, the method "prepare_cert_paths" will be invoked.
        # The script doesn't overwrite the existing CA certificate and keys on the database. Unless those CA folders are deleted manually.

        if os.path.exists(self.ca_path):
            result = {
                "status": "ok",
                "message": f"The CA ({self.ca_name}) is already registered on the database."
            }
            self.display_result(result)
            sys.exit(0)
            
        else:
            self.prepare_cert_paths()

    def prepare_cert_paths(self):

        # The method will verify the CA and other required folders are available. The folders will be created if the path doesn't exist.
        # The script will invoke the method "create_ca_certs" once the for loop exhausts.

        for dir in (f"{self.ca_path}", f"{self.ca_path}/ca", f"{self.ca_path}/tls-certs"):
            if not os.path.exists(dir):
                os.mkdir(dir)
        else:
            self.create_ca_certs()

    def create_ca_certs(self):

        # The command will create a CA private key with the key size of 4096 bits.
        # The script will verify the CA private key file exists after the command execution. Otherwise, the script will be terminated with exit code 1.

        command = f"openssl genrsa -out \"{self.ca_path}/ca/ca.key\" 4096"
        os.system(command)

        if not os.path.exists(f"{self.ca_path}/ca/ca.key"):
            result = {
                "status": "failed",
                "message": f"The CA private key generation has failed for the CA ({self.ca_name})."            
                }
            self.display_result(result)
            sys.exit(1)

        # The command will create a CA certificate from the CA private key generated in the previous step.
        # The script will verify the CA certificate file exists after the command execution. Otherwise, the script will be terminated with exit code 1.
        
        command = f"openssl req -x509 -new -nodes -key \"{self.ca_path}/ca/ca.key\" -sha256 -days 365 -out \"{self.ca_path}/ca/ca.pem\" -subj \"/CN={self.common_name}\""
        os.system(command)

        if not os.path.exists(f"{self.ca_path}/ca/ca.pem"):
            result = {
                "status": "failed",
                "message": f"The CA certificate generation has failed for the CA ({self.ca_name})."
            }
            self.display_result(result)
            sys.exit(1)

        # The script will verify the CA private key and the certificate exists before the script is completed with an "ok" note.

        if os.path.exists(f"{self.ca_path}/ca/ca.key") and os.path.exists(f"{self.ca_path}/ca/ca.pem"):
            result = {
                "status": "ok",
                "message": f"The CA ({self.ca_name}) has successfully been registered on the database."
            }
            self.display_result(result)

    @staticmethod
    def display_result(result):

        # The JSON object will be printed with the indent of 4.

        print(json.dumps(result, indent=4))
