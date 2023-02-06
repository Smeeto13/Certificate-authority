openssl ecparam -genkey -name secp384r1 -out 9A.key

openssl req -sha256 -new -config 9a.cnf -key 9A.key -nodes -out 9A.csr

openssl x509 -req -in 9A.csr -CA ../CA.crt -CAkey ../CA.key -CAcreateserial -out 9A.crt -days 1825 -extensions v3_req -extfile 9a.cnf

openssl pkcs12 -export -out 9A.pfx -inkey 9A.key -in 9A.crt -certfile ../CA.crt

rm 9A.csr