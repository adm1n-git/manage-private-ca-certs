import re
import os
import sys
import json

class manage_tls_certs:
    def __init__(self, ca_name: str, common_name: str) -> None:
        self.ca_name = ca_name
        self.urls = common_name.split(",")
        self.ca_path = re.sub(r"[^\w]", r"_", self.ca_name).lower()

        # The script will be terminated with the exit code 1 if the CA path doesn't exist. Otherwise, the method "create_tls_certs" will be invoked.
        # The script does overwrite the existing TLS certificate and keys on the database. 

        if not os.path.exists(self.ca_path):
            result = {
                "status": "failed",
                "message": f"The CA ({self.ca_name}) is not registered yet in the database."
            }
            self.display_result(result)
            sys.exit(1)
            
        else:
            self.create_tls_certs()

    def create_tls_certs(self) -> None:

        # The command will create a TLS private key with the key size of 4096 bits.
        # The script will verify the TLS private key file exists after the command execution. Otherwise, the script will be terminated with exit code 1.

        command = f"openssl genrsa -out \"{self.ca_path}/tls-certs/{self.urls[0]}.key\" 4096"
        os.system(command)

        if not os.path.exists(f"{self.ca_path}/tls-certs/{self.urls[0]}.key"):
            result = {
                "status": "failed",
                "message": f"The TLS private key generation has failed for the FQDN ({self.urls[0]})."            }
            self.display_result(result)
            sys.exit(1)

        # The TLS certificate common-name and subject-alternate-name will be prepared to the OpenSSL supported formats.
        # Common Name: /C=US/ST=California/L=SF/O=Example Corp/CN=example.com
        # Subject Alternate Name: subjectAltName=DNS:example.com,DNS:www.example.com,IP:192.168.1.10

        common_name = f"/CN={self.urls[0]}"
        subject_alternate_names = "subjectAltName="

        for url in self.urls:
            pattern = re.compile(r"[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}")
            if not re.search(pattern, url):
                subject_alternate_names += f"DNS:{url},"
            else:
                subject_alternate_names += f"IP:{url},"

        else:
            subject_alternate_names = subject_alternate_names.strip(",")

        # The command will create a CSR file with common-name and subject-alternate-name.
        # The script will verify the CSR file exists after the command execution. Otherwise, the script will be terminated with exit code 1.

        command = f"openssl req -new -key \"{self.ca_path}/tls-certs/{self.urls[0]}.key\" -out \"{self.ca_path}/tls-certs/{self.urls[0]}.csr\" -subj \"{common_name}\" -addext \"{subject_alternate_names}\""
        os.system(command)

        if not os.path.exists(f"{self.ca_path}/tls-certs/{self.urls[0]}.key"):
            result = {
                "status": "failed",
                "message": f"The CSR file generation has failed for the FQDN ({self.urls[0]})."            }
            self.display_result(result)
            sys.exit(1)

        # The command will create a TLS certificate using the CA private-key, the CA certificate and the CSR.
        # The script will verify the TLS certificate exists after the command execution. Otherwise, the script will be terminated with exit code 1.

        command = f"openssl x509 -req -in \"{self.ca_path}/tls-certs/{self.urls[0]}.csr\" -CA \"{self.ca_path}/ca/ca.pem\" -CAkey \"{self.ca_path}/ca/ca.key\" -CAcreateserial -out \"{self.ca_path}/tls-certs/{self.urls[0]}.pem\" -days 365 -sha256 2>/dev/null"
        os.system(command)

        if not os.path.exists(f"{self.ca_path}/tls-certs/{self.urls[0]}.pem"):
            result = {
                "status": "failed",
                "message": f"The TLS certificate generation has failed for the FQDN ({self.urls[0]})."            }
            self.display_result(result)
            sys.exit(1)

        # The script will verify the TLS private key and the certificate exist before the script is completed with an "ok" note.

        if os.path.exists(f"{self.ca_path}/tls-certs/{self.urls[0]}.key") and os.path.exists(f"{self.ca_path}/tls-certs/{self.urls[0]}.pem"):
            result = {
                "status": "ok",
                "message": f"The TLS certificate has been created for the FQDN ({self.urls[0]})."
            }
            self.display_result(result)

    @staticmethod
    def display_result(result):

        # The JSON object will be printed with the indent of 4.

        print(json.dumps(result, indent=4))
