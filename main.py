import socketIO_client
import time
import threading
import os
import pty
import subprocess

io = socketIO_client.SocketIO('witcoin.ru', 4000)
io.emit('auth', 'test3')

master, slave = pty.openpty()
if not os.path.exists('tmp'):
    os.mkdir('tmp')
videoPipeName = 'tmp/video.avi'
if not os.path.exists(videoPipeName):
    os.mkfifo(videoPipeName)


def send_video():
    video_in = os.open(videoPipeName, os.O_RDONLY)
    while True:
        data = os.read(video_in, 10000)
        if len(data):
            io.emit('video.data', bytearray(data))
threading.Thread(target=send_video).start()


def send_console():
    while True:
        data = os.read(master, 10000)
        if len(data):
            io.emit('console', data.decode('utf-8'))
threading.Thread(target=send_console).start()


def receive_console(data):
    os.write(master, data.encode('utf-8'))
io.on('console', receive_console)


def receive_source_code(data):
    io.emit('console.clear')
    f = open('tmp/source.cpp', 'w')
    f.write(data)
    f.close()
    io.emit('console', 'Source code received, generate object file\r\n')

    completed_process = subprocess.run(
        'g++ -c source.cpp -o object.o --std=c++11',
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, cwd='./tmp'
    )
    io.emit('console', completed_process.stdout.decode('utf-8') + completed_process.stderr.decode('utf-8'))
    if completed_process.returncode == 0:
        io.emit('console', 'Object file generated, linking\r\n')
    else:
        io.emit('console', 'Errors have occurred, stop\r\n')
        exit()

    completed_process = subprocess.run(
        'g++ -o executable object.o -lopencv_core -lopencv_highgui',
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, cwd='./tmp'
    )
    io.emit('console', completed_process.stdout.decode('utf-8') + completed_process.stderr.decode('utf-8'))
    if completed_process.returncode == 0:
        io.emit('console', 'Linked successful\r\n')
    else:
        io.emit('console', 'Errors have occurred, stop\r\n')
        exit()

    io.emit('video.init')
    io.emit('console', '\r\n')
    completed_process = subprocess.run('./executable', stdin=slave, stdout=slave, stderr=slave, cwd='./tmp')
    io.emit('console', '\r\n\r\nProgram exit with code {}\r\n'.format(completed_process.returncode))
    time.sleep(5)
    io.emit('video.end')
io.on('source-code', receive_source_code)

io.wait()
