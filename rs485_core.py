import sys
import argparse
import serial


def get_serials():
    serials = []
    for port in serial.tools.list_ports.comports():
        serials.append(port.device)
    return serials


def lrc(byte_data):
    # Sum of bytes without carryover
    summed = 0
    for x in byte_data:
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


def ascii_byte(ascii):
    return int("0x" + ascii, base=16)


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

    client = byte_ascii(ascii_address)
    function = byte_ascii(ascii_function)
    lrc = byte_ascii(ascii_lrc)
    l = lrc(
        client.to_bytes(1, sys.byteorder) + function.to_bytes(1, sys.byteorder) + data
    )
    if l == lrc:
        return {"client": client, "function": function, "data": data}
    else:
        return {}


def send(ser, address, instruction, data):
    ser.write(pack_frame(address, instruction, data))


def receive(ser):
    return unpack_frame(ser.readline().decode("ascii"))


def cli():
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
        args.parity = serial.PARITY_NONE
    elif args.parity == "odd":
        args.parity = serial.PARITY_ODD
    elif args.parity == "even":
        args.parity = serial.PARITY_EVEN
    else:
        print("ERROR: Bad parity")
        exit(1)

    if args.stopbits == 1:
        args.stopbits = serial.STOPBITS_ONE
    elif args.stopbits == 2:
        args.stopbits = serial.STOPBITS_TWO
    else:
        print("ERROR: Bad stopbits")
        exit(1)

    if args.format == 7:
        args.format = serial.SEVENBITS
    elif args.format == 8:
        args.format = serial.EIGHTBITS
    else:
        print("ERROR: Bad format")
        exit(1)

    return args
