#!/bin/bash

echo "Choose a FQDN from the following available hosts: "
ls /var/www
echo "Enter the FQDN for the domain you want client certificates (nginx auth): "
read SITE_NAME
SITE_NAME=$(echo $SITE_NAME | sed -e 's/^[ \t]*//' | tr "[:upper:]" "[:lower:]")
SITE_PATH=/var/www/$SITE_NAME

if [ ! -d "$SITE_PATH" ]; then
  echo "No vhosts fond by that name: $SITE_NAME"
  exit
fi

cd "$SITE_PATH/CA"

echo "Select a crt certificate to be revoked: "
cd certs/users
ls *.crt

cd "$SITE_PATH/CA"

read CLIENT_CERT_NAME

CLIENT_CERT_NAME=$(echo $CLIENT_CERT_NAME | sed -e 's/^[ \t]*//')

 # certificate revocation
openssl ca -revoke certs/users/$CLIENT_CERT_NAME -keyfile private/cakey.pem -cert certs/cacert.pem -config openssl.cnf

openssl ca -name CA_default -gencrl \
	-keyfile private/cakey.pem \
	-cert certs/cacert.pem \
	-out crl/ca.crl \
	-crldays 30 \
	-config openssl.cnf

#sudo systemctl reload nginx


