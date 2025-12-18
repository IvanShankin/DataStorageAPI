## PKI модель

CA:
- Один корневой CA
- Используется для:
  - server_storage
  - client_shop

Server (storage):
- Проверяет client cert (mTLS)
- Принимает ТОЛЬКО клиентов, подписанных нашим CA

Client (shop):
- Идентифицируется по client cert
- Не имеет доступа без сертификата
