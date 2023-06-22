import socket, threading, json, cv2, time, pickle, struct, imutils
# socket
host = '0.0.0.0'
port = 9191
serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serversocket.bind((host, port))
serversocket.listen(3)

# variables
nclients = 0
data = 0
type = 0
modeserver = ""
# to stream from file => 'videos/'
# vid = cv2.VideoCapture('videos/video_name')
vid = None
def increment_clients():
    global nclients
    nclients += 1

def decrement_clients():
    global  nclients
    nclients -= 1

# messages
def send_message(client_socket, addr):
    msg = start_response() + first()
    client_socket.send(bytes(msg, "utf-8"))

def start_response():
    with open("messages/startresponse.json", 'r') as start:
        firstmsg = json.load(start)
    msg = "\n".join(firstmsg.values()) + "\n"
    return msg

def first():
    with open("messages/response.json", "r") as response:
        firstmsg = json.load(response)
    firstmsg["nclients"] = f'connected: {nclients}'
    msg = "\n".join(firstmsg.values())
    return msg

# receive requests
def request(client_socket, addr):

    req = client_socket.recv(1024)
    req = req.decode('utf-8')

    if req == 'request:streamstart':
        print("\n" + req)
    if req == 'request:streamstop':
        print("\n" + req)

# send frames (stream or video)
def send_frames(client_socket, addr, vid):
    print('welcome')
    print('GOT CONNECTION FROM:', addr)

    if client_socket:
        try:
            while (vid.isOpened()):
                img, frame = vid.read()
                frame = imutils.resize(frame, width=320)
                a = pickle.dumps(frame)
                message = struct.pack("Q", len(a)) + a
                client_socket.sendall(message)
                time.sleep(0.05)

        except Exception:
            print(f"\nstream stop {addr}")
            decrement_clients()

# handle connection
def handle_connection(vid):

    client_socket, addr = serversocket.accept()

    increment_clients()

    thread_msgs = threading.Thread(target=send_message, args=(client_socket, addr))
    thread_msgs.start()

    thread_send = threading.Thread(target=request, args=(client_socket, addr))
    thread_send.start()

    thread_img = threading.Thread(target=send_frames, args=(client_socket, addr, vid,))
    thread_img.start()



# show image
def show_video(vid):
    try:
        while (vid.isOpened()):
            img, frame = vid.read()
            frame = imutils.resize(frame, width=320)
            cv2.imshow(f'{modeserver}', frame)
            time.sleep(0.05)

            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                vid.release()
                exit()
    except Exception:
        print("stop stream")

# main
def main():
    global type, modeserver, vid
    while True:
        print("\n(1) to share camera")
        print("(2) to share video")
        mode = input("Enter number: ")

        if mode == "1":
            vid = cv2.VideoCapture(0)
            modeserver = "live"
            break
        elif mode == "2":
            vid = cv2.VideoCapture('videos/ittihad.mp4')
            modeserver = "video"
            break
        else:
            print("wrong chose, again.")
    print("waiting to listen.. ")


    show = threading.Thread(target=show_video, args=(vid,))
    show.start()
    while True:

        if (nclients <= 3):
            thread_clients = threading.Thread(target=handle_connection, args=(vid,))
            thread_clients.start()


main()

