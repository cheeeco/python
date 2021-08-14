import argparse
import threading
import socket
import sys
import re

import taskqueue


class ClientThread(threading.Thread):
    def __init__(self, conn, addr, server):
        super().__init__(daemon=True)
        self.conn = conn
        self.addr = addr
        self.server = server
        self.data = b''
        self.commands = [
            (re.compile(r'ADD (?P<q_name>\S+) (?P<length>\d+) (?P<t_data>.+)', re.DOTALL), self.server.add_task),
            (re.compile(r'GET (?P<q_name>\S+)'), self.server.get_task),
            (re.compile(r'ACK (?P<q_name>\S+) (?P<t_id>\S+)'), self.server.ack_task),
            (re.compile(r'IN (?P<q_name>\S+) (?P<t_id>\S+)'), self.server.check_task)
        ]

    def run(self):
        while True:
            try:
                self.data = self.data + self.conn.recv(1024)
            except OSError:
                break

            if self.data.endswith(b'\n'):
                try:
                    self.exec_command(self.data)
                except OSError:
                    break

    def exec_command(self, data : bytes):
        data_str = data.decode('utf-8').strip()
        res = b''
        for command in self.commands:
            m = command[0].fullmatch(data_str)
            if m is not None:
                try:
                    res = command[1](*tuple(m.groupdict().values()))
                except ValueError:
                    res = b'INVALID COMMAND ARGUMENTS'
                break
            else:
                res = b'INVALID COMMAND'
        self.conn.send(res.strip() + b'\n')
        self.data = b''


class TaskQueueServer(threading.Thread):
    def __init__(self, port, ip, path, timeout):
        super().__init__(daemon=True)
        # socket moment)
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.bind((ip, port))
            self.sock.listen(10)
        except OSError:
            print('FAILED TO CREATE SOCKET')
            sys.exit()

        self.clients = []
        self.queues = {}

    def run(self):
        while True:
            conn, addr = self.sock.accept()
            new_client = ClientThread(conn, addr, self)
            self.clients.append(new_client)
            new_client.start()

    def add_task(self, q_name, length, t_data):
        length = int(length)
        t_data = t_data.encode('utf-8')
        if len(t_data) != length:
            raise ValueError
        if q_name not in self.queues:
            self.queues[q_name] = taskqueue.TaskQueue(q_name)
        return self.queues[q_name].add_task(length, t_data)

    def get_task(self, q_name):
        if q_name not in self.queues:
            return b'NONE'
        else:
            return self.queues[q_name].get_task()
    
    def ack_task(self, q_name, id):
        if len(id) > 128:
            raise ValueError
        if q_name not in self.queues:
            return b'QUEUE NOT EXISTS'
        else:
            return self.queues[q_name].ack_task(id)

    def check_task(self, q_name, id):
        if q_name not in self.queues:
            return b'QUEUE NOT EXISTS'
        else:
            return self.queues[q_name].check_task(id)

    def dump(self):
        pass


def parse_args():
    parser = argparse.ArgumentParser(description='This is a simple task queue server with custom protocol')
    parser.add_argument(
        '-p',
        action="store",
        dest="port",
        type=int,
        default=5556,
        help='Server port')
    parser.add_argument(
        '-i',
        action="store",
        dest="ip",
        type=str,
        default='0.0.0.0',
        help='Server ip address')
    parser.add_argument(
        '-c',
        action="store",
        dest="path",
        type=str,
        default='./',
        help='Server checkpoints dir')
    parser.add_argument(
        '-t',
        action="store",
        dest="timeout",
        type=int,
        default=300,
        help='Task maximum GET timeout in seconds')
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    server = TaskQueueServer(**args.__dict__)
    server.run()
    sys.exit()