import socket
import time

TCP = "10.10.0.104"
TCP_PORT = 2025

ROBOT = "10.10.0.61"
MOVE_PORT = 30003
GRIP_PORT = 63352

s_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s_tcp.connect((TCP, TCP_PORT))

s_robotArm = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s_robotArm.connect((ROBOT, MOVE_PORT))

s_robotGrip = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s_robotGrip.connect((ROBOT, GRIP_PORT))


s_robotGrip.send(b'GET ACT\n')
g_recv = str(s_robotGrip.recv(10), 'UTF-8')
if '1' in g_recv:
    print('Gripper Activated')
s_robotGrip.send(b'SET FOR 1\n')
s_robotGrip.send(b'SET POS 0\n')

down = False
GRABDOWN = -0.135
while True:
    p = s_tcp.recv(1024).decode()
    if p != "#,#\n":
        try:
            coord = list(map(lambda x: round(float(x), 2) /
                         1000, p.replace("#", "").split(",")))
            coord = [coord[0] - 0.00596, coord[1] - 0.08338]
            print(coord)

            s_robotArm.send(
                f'movej(pose_add(get_actual_tcp_pose(),p[{-coord[1]},{-coord[0]},0,0,0,0]),2,10,0,0)\n'.encode('utf-8'))
            time.sleep(0.1)

            if (((coord[0]**2+coord[1]**2)**(1/2)) < 0.005) and not down:
                # s_robotArm.send(f'movel(pose_add(get_actual_tcp_pose(),p[{-coord[1]},{-coord[0]},0,0,0,0]),2,10,0,0)\n'.encode('utf-8'))
                s_robotArm.send(
                    f'movej(pose_add(get_actual_tcp_pose(),p[0,0,{GRABDOWN},0,0,0]),2,10,0,0)\n'.encode('utf-8'))
                down = True
                time.sleep(3)

                s_robotGrip.send(b'SET POS 255\n')
                time.sleep(1)
                s_robotArm.send(
                    f'movej(pose_add(get_actual_tcp_pose(),p[0,0,{-GRABDOWN},0,0,0]),2,10,0,0)\n'.encode('utf-8'))
                while True:
                    pass
            # print ('get ACT  == ' + g_recv)
            # s_robotGrip.send(b'GET POS\n')
            # g_recv = str(s_robotGrip.recv(10), 'UTF-8')
            # print(g_recv)

            # s_robotArm.send(b'movel(p[-0.29561,0.15120,0.40782,1.798,-2.565,0],0.5,2,0,0)\n')
        except Exception as e:
            pass
