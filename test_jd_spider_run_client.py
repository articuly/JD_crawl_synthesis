from socket import socket, AF_INET, SOCK_STREAM

for goods_id in [100006503184, 100005855828, 100006731124, 100012595602]:
    c_client = socket(AF_INET, SOCK_STREAM)
    c_client.connect(('127.0.0.1', 8801))
    data = str(goods_id).encode()
    c_client.send(data)
    c_client.close()
