import socket 

target_host = "www.google.com"
target_port =  80

#Soket Object 
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#Connect the Client here 
client.connect((target_host, target_port))

#Send Some data 
client .send(b"GET / HTTP/1.1\r\nHOST:google.com\r\n\r\n")

response = client.recv(4096)
print(response.decode())
client.close()


