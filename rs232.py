import argparse
import serial, time
import io, threading


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

last_recv = time.time()


def send(text):
    ser.write((text + args.terminator).encode("utf-8"))


def recieve_loop():
    global last_recv
    while True:
        recv = ser.read_until(args.terminator.encode("utf-8")).decode("utf-8")
        if recv:
            print("\t\tRecieved:", recv)
            last_recv = time.time()


def measure_time():
    previous_last_recv = last_recv
    send("ping")
    while last_recv <= previous_last_recv:
        roundtrip = last_recv - previous_last_recv
        if time.time() - previous_last_recv > args.timeout:
            print("ERROR: Timeout while trying to calculate roundtrip.")
            return
    send("pong")
    time.sleep(0.2)
    print("Roundtrip is:", roundtrip, "seconds")


t = threading.Thread(target=recieve_loop)
t.daemon = True
t.start()

while True:

    inp = input("Command: ")
    if inp == "ping":
        measure_time()
    elif inp == "exit":
        exit(0)
    else:
        send(inp)
        time.sleep(0.2)
