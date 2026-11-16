import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

port = 8080
sock.sendto(b'open_window', ('localhost', port))
data, _ = sock.recvfrom(1024)
print(data.decode('utf-8'))
sock.close()