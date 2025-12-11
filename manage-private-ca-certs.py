import argparse
import sys

from modules import manage_ca_certs
from modules import manage_tls_certs

if "__main__" in __name__:
    parser = argparse.ArgumentParser(description=f"The script \"{sys.argv[0]}\" helps to manage the private CA and TLS certificates.")
    parser.add_argument("-t", "--cert_type", metavar="", choices=["ca-certs", "tls-certs"], help="Provide the type either \"ca-certs\" or \"tls-certs\"", required=True)
    parser.add_argument("-r", "--ca_name", metavar="", help="Provide the CA name", required=True)
    parser.add_argument("-c", "--common_name", metavar="", help="Provide the common-name or subject-alternative-name in comma-separated format", required=True)
    args = parser.parse_args()

    # The script will instantiate a class based on the cert-type.
    # The class "manage_ca_certs" will be called if the cert-type is ca-certs; otherwise, the class "manage_tls_certs" will be called.

    if args.cert_type == "ca-certs":
        manage_ca_certs(ca_name=args.ca_name.strip(), common_name=args.common_name.strip())

    if args.cert_type == "tls-certs":
        manage_tls_certs(ca_name=args.ca_name.strip(), common_name=args.common_name.strip())
