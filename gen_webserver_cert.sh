#!/bin/bash
# Usage: gen_dadbot.cert.sh NAMESPACE IP
#
cat <<EOF > dadbot.csr.conf
[ req ]
default_bits = 2048
prompt = no
default_md = sha256
req_extensions = req_ext
distinguished_name = dn

[ dn ]
C = ES
ST = Madrid
L = Madrid
O = Self-O
OU = Self-OU
CN = dadbot.svc.cluster.local

[ req_ext ]
subjectAltName = @alt_names

[ alt_names ]
DNS.1 = dadbot
DNS.2 = dadbot.$1
DNS.3 = dadbot.$1.svc
DNS.4 = dadbot.$1.svc.cluster
DNS.5 = dadbot.$1.svc.cluster.local
DNS.6 = localhost
IP.1 = $2
IP.2 = 127.0.0.1

[ v3_ext ]
authorityKeyIdentifier=keyid,issuer:always
basicConstraints=CA:FALSE
keyUsage=keyEncipherment,dataEncipherment
extendedKeyUsage=serverAuth,clientAuth
subjectAltName=@alt_names
EOF

openssl genrsa -out dadbot.key 2048
openssl req -new -key dadbot.key -out dadbot.csr -config dadbot.csr.conf
openssl x509 -req -in dadbot.csr \
-CA /etc/kubernetes/pki/ca.crt \
-CAkey /etc/kubernetes/pki/ca.key \
-CAcreateserial -out dadbot.crt -days 100 \
-extensions v3_ext -extfile dadbot.csr.conf

cat <<EOF > helm_csr.conf
[ req ]
default_bits = 2048
prompt = no
default_md = sha256
req_extensions = req_ext
distinguished_name = dn

[ dn ]
C = ES
ST = Madrid
L = Madrid
O = Self-O
OU = Self-OU
CN = helm.svc.cluster.local

[ req_ext ]
subjectAltName = @alt_names

[ alt_names ]
DNS.1 = helm
DNS.2 = helm.$1
DNS.3 = helm.$1.svc
DNS.4 = helm.$1.svc.cluster
DNS.5 = helm.$1.svc.cluster.local
IP.1 = $2

[ v3_ext ]
authorityKeyIdentifier=keyid,issuer:always
basicConstraints=CA:FALSE
keyUsage=keyEncipherment,dataEncipherment
extendedKeyUsage=serverAuth,clientAuth
subjectAltName=@alt_names
EOF

openssl genrsa -out helm.key 2048
openssl req -new -key helm.key -out helm.csr -config helm_csr.conf
openssl x509 -req -in helm.csr \
-CA /etc/kubernetes/pki/ca.crt \
-CAkey /etc/kubernetes/pki/ca.key \
-CAcreateserial -out helm.crt -days 100 \
-extensions v3_ext -extfile helm_csr.conf

export HELM_TLS_CA_CERT=/etc/kubernetes/pki/ca.crt
export HELM_TLS_CERT=helm.crt
export HELM_TLS_KEY=helm.key
export HELM_TLS_ENABLE="true"
export HELM_TLS_VERIFY="true"
