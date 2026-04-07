####### Command for control conveyor #################
#### activate tcp        = activate,tcp
#### power on servo      = pwr_on,conv,0
#### power off servo     = pwr_off,conv,0
#### set velocity x mm/s = set_vel,conv,x   # x = 0 to 200
#### jog forward         = jog_fwd,conv,0
#### jog backward        = jog_bwd,conv,0
#### stop conveyor       = jog_stop,conv,0
#########################################################


import socket, time
from config import *


def connect():
    # Connect to conveyor belt
    global conv
    c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    c.bind((ip_host, port_conv))
    c.listen(1)
    print("socket is listening")

    conv, addr = c.accept()
    c.close()  # Close server socket after accepting connection
    print(f"Connected by {addr}")
    conv.sendall(b'activate,tcp,0.0\n')
    time.sleep(1)

    return conv


def start():
    # Start conveyor belt
    # conv.sendall(b'pwr_on,conv,0\n')
    # time.sleep(1)

    conv.sendall(b'activate,tcp,0.0\n')
    time.sleep(1)

    conv.sendall(b'pwr_on,conv,0\n')
    response = conv.recv(1024)
    print("Server response:", response.decode())
    time.sleep(1)

    conv.sendall(b'set_vel,conv,5\n')
    time.sleep(2)
    # response = conv.recv(1024)
    # print("Server response:", response.decode())

    conv.sendall(b'jog_fwd,conv,0\n')
    response = conv.recv(1024)
    print("Server response:", response.decode())
    time.sleep(5)


def stop():
    # Stop conveyor belt
    conv.sendall(b'jog_stop,conv,0\n')
    time.sleep(1)

def main():
    connect()
    start()
    # time.sleep(10)  # Let the conveyor run for 5 seconds
    stop()

if __name__ == "__main__":
    main()