openssl genrsa -out 9E.key 2048

openssl req -sha256 -new -config 9e.cnf -key 9E.key -nodes -out 9E.csr

openssl x509 -req -in 9E.csr -CA ../CA.crt -CAkey ../CA.key -CAcreateserial -out 9E.crt -days 1825 -extensions v3_req -extfile 9e.cnf

openssl pkcs12 -export -out 9E.pfx -inkey 9E.key -in 9E.crt -certfile ../CA.crt

rm 9E.csr