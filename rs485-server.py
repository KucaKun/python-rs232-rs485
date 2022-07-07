import argparse
import time
import serial
import sys


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


def lrc(data):
    # Sum of bytes without carryover
    summed = 0
    for x in data:
        summed += int(x)
        if summed > 255:
            summed -= 255

    # Two's compliment
    if (summed & (1 << 7)) != 0:  # if sign bit is set
        summed -= 255
    return (summed & 0xFF).to_bytes(1, sys.byteorder)


def byte_ascii(byte):
    v = hex(int(byte)).split("x")[1].upper()
    return "0" + v if len(v) == 1 else v


def pack_frame(address, function, data):
    data = data.encode("ascii")
    # Calculate lrc before converting bytes to ascii
    l = lrc(
        address.to_bytes(1, sys.byteorder) + function.to_bytes(1, sys.byteorder) + data
    )
    address = byte_ascii(address)
    function = byte_ascii(function)
    l = byte_ascii(l)
    return f":{address}{function}{data}{l}\r\n".encode("ascii")


def unpack_frame(frame):
    ascii_address = frame[1:3]
    ascii_function = frame[3:5]
    data = frame[5:-5]
    ascii_lrc = frame[-5:-3]


def send(address, instruction, data):
    ser.write(pack_frame(address, instruction, data))


def receive():
    return unpack_frame(ser.readline().decode("ascii"))


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
            send(address, function, data)
        elif inp.startswith("2"):
            address = inp.split(" ")[1]
            receive(address)
        elif inp == "exit":
            exit(0)
        else:
            print("Usage (without square brackets):")
            print("Send:")
            print("1 [address] [function] [data]")
            print("Receive:")
            print("2 [address]")
        time.sleep(0.2)
