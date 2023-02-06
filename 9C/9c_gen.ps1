openssl ecparam -genkey -name secp384r1 -out 9C.key

openssl req -sha256 -new -config 9c.cnf -key 9C.key -nodes -out 9C.csr

openssl x509 -req -in 9C.csr -CA ../CA.crt -CAkey ../CA.key -set_serial 2 -out 9C.crt -days 1825 -extensions v3_req -extfile 9c.cnf

openssl pkcs12 -export -out 9C.pfx -inkey 9C.key -in 9C.crt -certfile ../CA.crt

rm 9C.csr