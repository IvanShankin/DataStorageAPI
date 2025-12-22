# Мануал по созданию PKI и mTLS-сертификатов для API (uvicorn + FastAPI)

## Предварительные условия

Работа выполняется в каталоге, где будут создаваться сертификаты (например `certs/`).


## Конфигурационные файлы OpenSSL

---

### `server_openssl.cnf` (обязателен для серверного сертификата)

```ini
[ req ]
default_bits       = 2048
distinguished_name = req_distinguished_name
req_extensions     = req_ext
prompt             = no

[ req_distinguished_name ]
CN = server_shop

[ req_ext ]
subjectAltName = @alt_names
extendedKeyUsage = serverAuth

[ alt_names ]
IP.1  = 127.0.0.1
DNS.1 = localhost
```

---

### `client_openssl.cnf` (обязателен для клиентского сертификата)

```ini
[client_cert]
extendedKeyUsage = clientAuth
```

---

## Шаг 1. Создание Root CA

### 1.1 Генерация ключа CA

```bash
openssl genrsa -out ca.key 4096
```

**Результат:**

```
ca.key   — приватный ключ CA (СЕКРЕТ)
```

---

### 1.2 Самоподписанный сертификат CA

```bash
openssl req -x509 -new -nodes \
  -key ca.key \
  -sha256 -days 3650 \
  -out server_ca_chain.crt \
  -subj "/C=SE/O=DataStorageService/OU=CA/CN=DataStorage Root CA"
```

**Результат:**

```
server_ca_chain.crt  — публичный сертификат CA
```

---

### Итог шага 1

```
ca.key   ❗ секрет, не должен хранится на серверах
server_ca_chain.crt   ✅ публичный
```

---

## Шаг 2. Серверный сертификат (uvicorn)

### 2.1 Генерация ключа сервера

```bash
openssl genrsa -out server.key 2048
```

**Результат:**

```
server.key
```

---

### 2.2 Создание CSR (Certificate Signing Request)

```bash
openssl req -new \
  -key server.key \
  -out server.csr \
  -subj "/C=SE/O=DataStorageService/OU=Storage/CN=127.0.0.1"
```

**Результат:**

```
server.csr
```

---

### 2.3 Подпись серверного сертификата Root CA

```bash
openssl x509 -req \
  -in server.csr \
  -CA server_ca_chain.crt \
  -CAkey ca.key \
  -CAcreateserial \
  -out server.crt \
  -days 825 \
  -sha256 \
  -extfile server_openssl.cnf \
  -extensions req_ext
```

**Результат:**

```
server.crt
ca.srl        — служебный файл OpenSSL
```

---

### 2.4 Подготовка PEM-файлов для uvicorn

```bash
cp server.crt server_cert.pem
cp server.key server_shop_key.pem
```

**Результат:**

```
server_cert.pem
server_key.pem
```

---

## Шаг 3. Клиентский сертификат (mTLS)

### 3.1 Генерация ключа клиента

```bash
openssl genrsa -out client.key 2048
```

**Результат:**

```
client.key
```

---

### 3.2 Создание CSR клиента

```bash
openssl req -new \
  -key client.key \
  -out client.csr \
  -subj "/C=SE/O=Shop/OU=Client/CN=shop-1"
```

**Результат:**

```
client.csr
```

---

### 3.3 Подпись клиентского сертификата Root CA

```bash
openssl x509 -req \
  -in client.csr \
  -CA server_ca_chain.crt \
  -CAkey ca.key \
  -CAcreateserial \
  -out client.crt \
  -days 825 \
  -sha256 \
  -extfile client_openssl.cnf \
  -extensions client_cert
```

**Результат:**

```
client.crt
```

---

### 3.4 Подготовка PEM-файлов для клиента

```bash
cp client.crt client_cert.pem
cp client.key client_key.pem
```

**Результат:**

```
client_cert.pem
client_key.pem
```

---

## Очистка временных и одноразовых файлов

(после того как сертификаты успешно выпущены)

```powershell
Remove-Item "*.csr"       # CSR используются только при выпуске
Remove-Item "ca.srl"      # счётчик серийников OpenSSL
Remove-Item "server.key"  # дубликат server_key.pem
Remove-Item "server.crt"  # дубликат server_certserver_cert.pem
Remove-Item "client.crt"  # дубликат client_cert.pem
Remove-Item "client.key"  # дубликат client_key.pem
Remove-Item "*.cnf"       # нужны только на этапе генерации
```

---

## Итоговая структура 

```
certs/
├── ca/
│   ├── server_ca_chain.crt            # необходим для сервера и клиента 
│   └── ca.key                # необходим для подписи сертификатов и не хранится на серверах
├── server/
│   ├── server_cert.pem       # необходим для сервера
│   └── server_key.pem        # необходим для сервера
└── client/
    ├── client_cert.pem  # необходим для клиента
    └── client_key.pem   # необходим для клиента
```

что необходимо для клиента:

```
certs/
├── ca/
│   └── server_ca_chain.crt                
└── client/
    ├── client_cert.pem  
    └── client_key.pem   
```

что необходимо для сервера:
```
certs/
├── ca/
│   └── server_ca_chain.crt
└── server/
    ├── server_cert.pem 
    └── server_key.pem 
```

---

## ВАЖНО

* `ca.key`:
  * ❌ НЕ нужен серверу
  * ❗ хранится оффлайн / в vault
  
* ❗При утечке любого сертификата, необходимо его перевыпустить или заново повторить процедуру создания сертификатов

* Сервер принимает **только клиентские сертификаты** с:

  ```
  Extended Key Usage = clientAuth
  ```

* Сертификат сервера обязан иметь:

  ```
  Extended Key Usage = serverAuth
  Subject Alternative Name (IP / DNS)
  ```

---

