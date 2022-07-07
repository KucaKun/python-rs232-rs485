import argparse
import serial, time
import threading
from pymodbus.client.sync import ModbusSerialClient
from pymodbus.server.sync import ModbusSerialServer


def get_serials():
    serials = []
    for port in serial.tools.list_ports.comports():
        serials.append(port.device)
    return serials


parser = argparse.ArgumentParser()
parser.add_argument("port", type=str, default="loopback")
parser.add_argument("--baudrate", type=int, default="9600")
parser.add_argument("--parity", type=str, help="none, odd or even", default="none")
parser.add_argument("--stopbits", type=int, help="1 or 2 bits", default=1)
parser.add_argument("--format", type=int, help="7 or 8 bits", default=8)
parser.add_argument("--terminator", type=str, help="terminator character", default="\n")
parser.add_argument("--xonxoff", type=bool, help="flow control XON XOFF", default=False)
parser.add_argument("--dsrdtr", type=bool, help="flow control DSR DTR", default=False)
parser.add_argument("--rtscts", type=bool, help="flow control RTS CTS", default=False)
parser.add_argument(
    "--timeout", type=int, help="seconds of response timeout", default=3
)
args = parser.parse_args()


ModbusSerialClient()
