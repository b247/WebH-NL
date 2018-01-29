#!/bin/bash

#Change to your company details
country=RO
organization=b247.eu.org
email=webmaster@b247.eu.org

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

mkdir -p "$SITE_PATH/CA"
cd "$SITE_PATH/CA"

mkdir -p certs crl newcerts private
mkdir -p certs/users

echo "Full name of the person that requires a certificate, ex: John Doe: "
read CLIENT_NAME
CLIENT_CERT_NAME=$(echo $CLIENT_NAME.$SITE_NAME | sed -e 's/^[ \t]*//' | sed -e 's/ /_/g' | sed -e 's/\./_/g' | tr "[:upper:]" "[:lower:]")

echo "email (the certificate will be transmited to $CLIENT_NAME using this): "
read CLIENT_EMAIL

echo "certficate import pass (the password used by $CLIENT_NAME to import the certificate into the browser): "
read CLIENT_PASS

echo "I will generate now a client access ($CLIENT_CERT_NAME.p12) certificate for $SITE_NAME, person: $CLIENT_NAME"

# generate CA if not exists
if [ ! -f "private/cakey.pem" ]; then
	cp /etc/ssl/openssl.cnf openssl.cnf
	touch index.txt
	echo 01 > serial
	echo 01 > crlnumber
	openssl genrsa -des3 -out private/cakey.pem 4096 -noout
	chmod 400 private/cakey.pem
	openssl req -new -x509 -key private/cakey.pem -out certs/cacert.pem -days 3650 -set_serial 0 \
  	-subj "/C=$country/O=$organization/CN=$organization/emailAddress=$email"

  	openssl ca -name CA_default -gencrl \
	-keyfile private/cakey.pem \
	-cert certs/cacert.pem \
	-out crl/ca.crl \
	-crldays 30 \
	-config openssl.cnf
fi

openssl genrsa -des3 -passout pass:$CLIENT_PASS -out certs/users/$CLIENT_CERT_NAME.key 4096 -config openssl.cnf

openssl req -passin pass:$CLIENT_PASS -new -key certs/users/$CLIENT_CERT_NAME.key \
-out certs/users/$CLIENT_CERT_NAME.csr \
-config openssl.cnf \
-subj "/O=$SITE_NAME/CN=$CLIENT_EMAIL/emailAddress=$CLIENT_EMAIL"

openssl x509 -req -days 3560 -in certs/users/$CLIENT_CERT_NAME.csr \
 -CA certs/cacert.pem \
 -CAkey private/cakey.pem \
 -CAserial serial \
 -CAcreateserial \
 -out certs/users/$CLIENT_CERT_NAME.crt

openssl pkcs12 -passin pass:$CLIENT_PASS -passout pass:$CLIENT_PASS -export -clcerts -in certs/users/$CLIENT_CERT_NAME.crt \
 -inkey certs/users/$CLIENT_CERT_NAME.key \
 -out certs/users/$CLIENT_CERT_NAME.p12

echo "Your client certificate $CLIENT_CERT_NAME.p12 for $SITE_NAME access.\
<br/>The certificate must be imported to browser(s) in order to gain access to $SITE_NAME \
<br/>Password for the certificate import is: CLIENT_PASS" | \
 mail -A $SITE_PATH/certs/users/$CLIENT_CERT_NAME.p12  -s "$SITE_NAME personal certificate" $CLIENT_EMAIL
