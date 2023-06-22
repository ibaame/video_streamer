import socket, threading, json, cv2, time, pickle, struct, imutils
# create socket

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host_name = socket.gethostname()
host = '127.0.0.1' #host_name # socket.gethostbyname(host_name)
port = 9191
client_socket.connect((host, port))

# variables
data = b""
payload_size = struct.calcsize("Q")

# Stream start request message
def start_request():
    with open("messages/start.json", "r") as startreq:
        msg = json.load(startreq)

        client_socket.send(bytes(msg["request"], "utf-8"))
    receive = client_socket.recv(128)
    receive = receive.decode('utf-8')
    print(receive)


def receive_frame():
    try:
        global data
        while True:
            while len(data) < payload_size:
                packet = client_socket.recv(4 * 1024)  # 4K
                if not packet: break
                data += packet
            packed_msg_size = data[:payload_size]
            data = data[payload_size:]
            msg_size = struct.unpack("Q", packed_msg_size)[0]
            while len(data) < msg_size:
                data += client_socket.recv(4 * 1024)
            frame_data = data[:msg_size]
            data = data[msg_size:]
            frame = pickle.loads(frame_data)
            cv2.imshow(host_name, frame)
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
                # Stream stop request message
    except Exception:
        print('Stop watching the stream')
    finally:
        with open("messages/stop.json", "r") as stopreq:
            stop = json.load(stopreq)
            client_socket.send(bytes(stop["request"], "utf-8"))
        print('Stop watching the stream')
        client_socket.close()

def main():

    start_request()
    receive_frame()

main()

