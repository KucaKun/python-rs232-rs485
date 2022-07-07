import argparse
import time
import serial
from rs485_core import send, receive


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
parser.add_argument(
    "--timeout", type=int, help="seconds of response timeout", default=3
)
args = parser.parse_args()

if args.port != "loopback":
    if args.port not in get_serials():
        print("ERROR: No such port")
        exit(1)

if args.parity == "none":
    parity = serial.PARITY_NONE
elif args.parity == "odd":
    parity = serial.PARITY_ODD
elif args.parity == "even":
    parity = serial.PARITY_EVEN
else:
    print("ERROR: Bad parity")
    exit(1)

if args.stopbits == 1:
    stopbits = serial.STOPBITS_ONE
elif args.stopbits == 2:
    stopbits = serial.STOPBITS_TWO
else:
    print("ERROR: Bad stopbits")
    exit(1)

if args.format == 7:
    format = serial.SEVENBITS
elif args.format == 8:
    format = serial.EIGHTBITS
else:
    print("ERROR: Bad format")
    exit(1)


if __name__ == "__main__":

    if args.port != "loopback":
        ser = serial.Serial(
            port=args.port,
            baudrate=args.baudrate,
            parity=parity,
            stopbits=stopbits,
            bytesize=format,
            timeout=args.timeout,
            xonxoff=args.xonxoff,
            rtscts=args.rtscts,
            dsrdtr=args.dsrdtr,
        )
    else:
        ser = serial.serial_for_url(
            "loop://",
            baudrate=args.baudrate,
            parity=parity,
            stopbits=stopbits,
            bytesize=format,
            timeout=args.timeout,
            xonxoff=args.xonxoff,
            rtscts=args.rtscts,
            dsrdtr=args.dsrdtr,
        )

    while True:

        inp = input("Command: ")
        if inp.startswith("1"):
            address = inp.split(" ")[1]
            function = inp.split(" ")[2]
            data = " ".join(inp.split(" ")[3:-1])
            send(ser, address, function, data)
            print()
        elif inp.startswith("2"):
            address = inp.split(" ")[1]
            recv = receive(ser, address)
            if recv:
                print(
                    "Received:",
                    recv["data"],
                    "\nfrom address:",
                    recv["client"],
                    "\nfunction:",
                    recv["function"],
                )
            else:
                print("ERROR: Wrong LRC")
        elif inp == "exit":
            exit(0)
        else:
            print("Usage (without square brackets):")
            print("Send:")
            print("1 [address] [function] [data]")
            print("Receive:")
            print("2 [address]")
        time.sleep(0.2)
