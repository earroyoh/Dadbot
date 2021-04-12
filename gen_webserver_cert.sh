#!/bin/bash
# Usage: gen_webserver_cert.sh FQDN IP
#
cat <<EOF > dadbot.csr.conf
[ req ]
default_bits = 4096
prompt = no
default_md = SHA512
req_extensions = req_ext
distinguished_name = dn

[ dn ]
C = ES
ST = Madrid
L = Madrid
O = Self-O
OU = Self-OU
CN = dadbot-web.svc.cluster.local

[ req_ext ]
keyUsage = digitalSignature, keyEncipherment
extendedKeyUsage = serverAuth, clientAuth
subjectAltName = @alt_names

[ alt_names ]
DNS.1 = dadbot-web
DNS.2 = $1
DNS.3 = $1.svc
DNS.4 = $1.svc.cluster
DNS.5 = $1.svc.cluster.local
DNS.6 = localhost
IP.1 = $2
IP.2 = 127.0.0.1

[ v3_ext ]
authorityKeyIdentifier=keyid,issuer:always
basicConstraints=CA:FALSE
EOF

openssl genrsa -out dadbot.key 4096
openssl req -new -key dadbot.key -out dadbot.csr -config dadbot.csr.conf
openssl x509 -req -in dadbot.csr \
-CA /etc/kubernetes/pki/ca.crt \
-CAkey /etc/kubernetes/pki/ca.key \
-CAcreateserial -out dadbot.crt -days 100 \
-extensions v3_ext -extfile dadbot.csr.conf
