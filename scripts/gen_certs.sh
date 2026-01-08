#!/bin/bash
set -e

mkdir -p certs

if [ ! -f certs/localhost.key ]; then
    echo "Generating self-signed certificate for localhost..."
    openssl req -x509 -out certs/localhost.crt -keyout certs/localhost.key \
      -newkey rsa:2048 -nodes -sha256 \
      -subj '/CN=localhost' -extensions EXT -config <( \
       printf "[dn]\nCN=localhost\n[req]\ndistinguished_name = dn\n[EXT]\nsubjectAltName=DNS:localhost\nkeyUsage=digitalSignature\nextendedKeyUsage=serverAuth")
    echo "Certificate generated in certs/"
else
    echo "Certificate already exists."
fi
