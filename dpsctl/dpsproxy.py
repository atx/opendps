#! /usr/bin/env python3

import argparse
import serial
import socket
import uframe


class Proxy:

    def __init__(self, args):
        self.serial = serial.Serial(args.tty, baudrate=args.baud, timeout=1.0)

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((args.bind, args.port))

    def read_uart_frame(self):
        bs = bytearray()
        sof = False
        while True:
            c = self.serial.read(1)
            if not c:
                return None  # Timeout
            c = ord(c)
            if c == uframe._SOF:
                bs = bytearray()
                sof = True
            if sof:
                bs.append(c)
            if c == uframe._EOF:
                sof = False
                break
        return bs

    def run(self):
        while True:
            (data, addr) = self.socket.recvfrom(1024*16)
            self.serial.write(data)
            frame = self.read_uart_frame()
            self.socket.sendto(frame, addr)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--tty", required=True)
    parser.add_argument("-p", "--port", type=int, default=5005)
    parser.add_argument("-i", "--bind", default="0.0.0.0")
    parser.add_argument("-b", "--baud", default=115200)
    args = parser.parse_args()

    proxy = Proxy(args)
    proxy.run()
