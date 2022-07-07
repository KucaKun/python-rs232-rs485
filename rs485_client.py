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
            bytesize=args.format,
        )
    while True:
        recv = receive(ser)
        if recv and recv["client"] == args.address:
            print(
                "Received:",
                recv["data"],
                "\nfrom address:",
                recv["client"],
                "\nfunction:",
                recv["function"],
            )
            if recv["data"] == "ping" and recv["function"] == 0:
                send(ser, recv["client"], 99, "pong")
        else:
            print("ERROR: Wrong LRC")
