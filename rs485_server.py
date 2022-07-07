import time
import serial
from rs485_core import send, receive, cli


if __name__ == "__main__":
    args = cli()
    if args.port != "loopback":
        ser = serial.Serial(
            port=args.port,
            baudrate=args.baudrate,
            parity=args.parity,
            stopbits=args.stopbits,
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
            parity=args.parity,
            stopbits=args.stopbits,
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
