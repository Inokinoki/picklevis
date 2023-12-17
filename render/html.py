
from event import PicklevisEventType, PicklevisEventSource, PicklevisEventGroup, PicklevisEvent
from picklevis_core import Unpickler, OPCODE_INT_NAME_MAPPING

import pickle
import string


BYTE_PREFIX = "byte-"
BYTE_ASCII_PREFIX = "byte-ascii-"


def _render_hex_table(unpickler: Unpickler, f):
    pkl_file = unpickler.get_file()
    pkl_file.seek(0)

    line_count = 0
    f.write('<table style="border-spacing: 0;"><tr><th></th>')
    for i in range(16):
        f.write(f"<th>{i:02X}&nbsp;</th>")
        if i == 7:
            f.write("<th> </th>")
    f.write("</tr>")

    byte_counter = 0
    while True:
        bs = pkl_file.read(16)
        if len(bs) == 0:
            # EOF
            break

        byte_counter = line_count * 16
        f.write(f"<tr><th>{(line_count * 16):08X}</th>")

        b_index = 0
        for b in bs:
            f.write(f'<td id="{BYTE_PREFIX}{byte_counter + b_index}">{b:02X}&nbsp;</td> ')
            b_index += 1
            if b_index == 8:
                f.write("<td> </td>")

        if len(bs) < 16:
            for i in range(16 - len(bs)):
                f.write("<td> </td> ")

        f.write("<td> </td><td>|</td>")
        b_index = 0
        for b in bs:
            if chr(b) in string.printable:
                f.write(f'<td id="{BYTE_ASCII_PREFIX}{byte_counter + b_index}">{chr(b)}</td>')
            else:
                f.write(f'<td id="{BYTE_ASCII_PREFIX}{byte_counter + b_index}">.</td>')
            b_index += 1

        if len(bs) < 16:
            for i in range(16 - len(bs)):
                f.write("<td> </td> ")

        f.write("<td>|</td>")
        f.write("</tr>\n")
        line_count += 1
    f.write("</table>\n")


def render_to_html(unpickler: Unpickler, name):
    i = 0
    with open(name, "w") as f:
        f.write("<html><body>\n")
        _render_hex_table(unpickler, f)

        pkl_file = unpickler.get_file()
        for event in unpickler.get_events():
            if pkl_file.seek(event.offset) == event.offset:
                content = pkl_file.read(event.byte_count)
                f.write("<style>")
                f.write(f"td#{BYTE_ASCII_PREFIX}{event.offset}, td#{BYTE_PREFIX}{event.offset}" " { color: " + "blue" + ";} ")
                if event.opcode != pickle.FRAME[0]:
                    for index in range(event.offset + 1, event.offset + event.byte_count):
                        f.write(f"td#{BYTE_ASCII_PREFIX}{index}, td#{BYTE_PREFIX}{index}" " { background-color: " + "red" + ";} ")
                else:
                    for index in range(event.offset + 1, event.offset + event.byte_count):
                        f.write(f"td#{BYTE_ASCII_PREFIX}{index}, td#{BYTE_PREFIX}{index}" " { background-color: " + "rgba(128, 128, 128, 128)" + ";} ")

                f.write("</style>")
                f.write(f"[OP-{OPCODE_INT_NAME_MAPPING[event.opcode]}] {event.opcode}, {event.byte_count} bytes - {event.offset}: {content} <br/>")
        f.write("</body></html>")
        print(i)
    return i
