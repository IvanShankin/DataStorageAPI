@echo off
setlocal enabledelayedexpansion

echo.
echo =========================================================
echo  DEV CERTIFICATE GENERATOR (mTLS)
echo.
echo  WARNING:
echo  - FOR DEVELOPMENT / LOCAL TESTING ONLY
echo  - DO NOT USE IN PRODUCTION
echo  - GENERATED ca.key MUST NEVER LEAVE YOUR MACHINE
echo =========================================================
echo.

REM ---------------------------------------------------------
REM Base directories
REM ---------------------------------------------------------
set BASE_DIR=%~dp0
set CERTS_DIR=%BASE_DIR%certs

set CA_DIR=%CERTS_DIR%\ca
set SERVER_DIR=%CERTS_DIR%\server
set CLIENT_DIR=%CERTS_DIR%\client
set TMP_DIR=%CERTS_DIR%\_tmp

mkdir "%CA_DIR%" "%SERVER_DIR%" "%CLIENT_DIR%" "%TMP_DIR%" >nul 2>&1

REM ---------------------------------------------------------
REM OpenSSL config: server
REM ---------------------------------------------------------
(
echo [ req ]
echo default_bits       = 2048
echo distinguished_name = req_distinguished_name
echo req_extensions     = req_ext
echo prompt             = no
echo.
echo [ req_distinguished_name ]
echo CN = server
echo.
echo [ req_ext ]
echo subjectAltName = @alt_names
echo extendedKeyUsage = serverAuth
echo keyUsage = digitalSignature, keyEncipherment
echo.
echo [ alt_names ]
echo IP.1  = 127.0.0.1
echo DNS.1 = localhost
) > "%TMP_DIR%\server_openssl.cnf"

REM ---------------------------------------------------------
REM OpenSSL config: client
REM ---------------------------------------------------------
(
echo [client_cert]
echo extendedKeyUsage = clientAuth
echo keyUsage = digitalSignature
) > "%TMP_DIR%\client_openssl.cnf"

REM ---------------------------------------------------------
REM 1. Root CA
REM ---------------------------------------------------------
echo [info]: Creating Root CA...
openssl genrsa -out "%CA_DIR%\ca.key" 4096

openssl req -x509 -new -nodes ^
  -key "%CA_DIR%\ca.key" ^
  -sha256 -days 3650 ^
  -out "%CA_DIR%\int_ca.crt" ^
  -subj "/C=SE/O=DataStorageService/OU=CA/CN=DataStorage Root CA"

REM ---------------------------------------------------------
REM Create server CA chain from int_ca.crt
REM ---------------------------------------------------------
echo [info]: Creating server CA chain...
copy "%CA_DIR%\int_ca.crt" "%CA_DIR%\server_ca_chain.pem" >nul
echo Created: %SERVER_DIR%\server_ca_chain.pem
echo.

REM ---------------------------------------------------------
REM 2. Server certificate
REM ---------------------------------------------------------
echo [info]: Creating server certificate...

openssl genrsa -out "%TMP_DIR%\server.key" 2048

openssl req -new ^
  -key "%TMP_DIR%\server.key" ^
  -out "%TMP_DIR%\server.csr" ^
  -subj "/C=SE/O=DataStorageService/OU=Storage/CN=127.0.0.1"

openssl x509 -req ^
  -in "%TMP_DIR%\server.csr" ^
  -CA "%CA_DIR%\int_ca.crt" ^
  -CAkey "%CA_DIR%\ca.key" ^
  -CAcreateserial ^
  -out "%SERVER_DIR%\server_cert.pem" ^
  -days 825 ^
  -sha256 ^
  -extfile "%TMP_DIR%\server_openssl.cnf" ^
  -extensions req_ext

move "%TMP_DIR%\server.key" "%SERVER_DIR%\server_key.pem" >nul

echo.

REM ---------------------------------------------------------
REM 3. Client certificate
REM ---------------------------------------------------------
echo [info]: Creating client certificate...

openssl genrsa -out "%TMP_DIR%\client.key" 2048

openssl req -new ^
  -key "%TMP_DIR%\client.key" ^
  -out "%TMP_DIR%\client.csr" ^
  -subj "/C=SE/O=Shop/OU=Client/CN=shop-1"

openssl x509 -req ^
  -in "%TMP_DIR%\client.csr" ^
  -CA "%CA_DIR%\int_ca.crt" ^
  -CAkey "%CA_DIR%\ca.key" ^
  -CAcreateserial ^
  -out "%CLIENT_DIR%\client_cert.pem" ^
  -days 825 ^
  -sha256 ^
  -extfile "%TMP_DIR%\client_openssl.cnf" ^
  -extensions client_cert

move "%TMP_DIR%\client.key" "%CLIENT_DIR%\client_key.pem" >nul

echo.

REM ---------------------------------------------------------
REM Cleanup
REM ---------------------------------------------------------
echo [info]: Cleaning temporary files...
rmdir /s /q "%TMP_DIR%" >nul 2>&1
del "%CA_DIR%\ca.srl" 2>nul
echo.

REM ---------------------------------------------------------
REM Verification
REM ---------------------------------------------------------
echo [info]: Verifying certificates...
echo.
echo --- CA ---
openssl x509 -in "%CA_DIR%\int_ca.crt" -noout -subject
echo.
echo --- Server ---
openssl x509 -in "%SERVER_DIR%\server_cert.pem" -noout -text | findstr "Subject: Extended Key Usage"
echo.
echo --- Client ---
openssl x509 -in "%CLIENT_DIR%\client_cert.pem" -noout -text | findstr "Subject: Extended Key Usage"
echo.

REM ---------------------------------------------------------
REM Summary
REM ---------------------------------------------------------
echo =========================================================
echo  Certificates created successfully
echo.
echo  CA:
echo    %CA_DIR%\int_ca.crt
echo    %CA_DIR%\ca.key   [KEEP SECRET]
echo.
echo  Server files:
echo    %SERVER_DIR%\server_cert.pem
echo    %SERVER_DIR%\server_key.pem
echo    %SERVER_DIR%\server_ca_chain.pem
echo.
echo  Client files:
echo    %CLIENT_DIR%\client_cert.pem
echo    %CLIENT_DIR%\client_key.pem
echo.
echo  DO NOT USE THESE CERTIFICATES IN PRODUCTION
echo =========================================================
echo.
pause