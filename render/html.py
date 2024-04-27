
from event import PicklevisEventType, PicklevisEventSource, PicklevisEventGroup, PicklevisEvent
from picklevis_core import Unpickler, OPCODE_INT_NAME_MAPPING

import os
import pickle
import string


BYTE_PREFIX = "byte-"
BYTE_ASCII_PREFIX = "byte-ascii-"
BLOCK_PREFIX = "block-"


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
            f.write(f'<td id="{BYTE_PREFIX}{byte_counter + b_index}" ')
            f.write(f'onmouseover="change_for_byte({byte_counter + b_index}, \'red\')" ')
            f.write(f'onmouseout="change_for_byte({byte_counter + b_index}, \'\')">')
            f.write(f'{b:02X}&nbsp;</td>')
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
        f.write("<html><head>\n")
        # Add utility functions
        with open(os.path.dirname(os.path.abspath(__file__)) + "/utils.js") as js_file:
            f.write(f"<script>{js_file.read()}</script>")
        with open(os.path.dirname(os.path.abspath(__file__)) + "/utils.css") as css_file:
            f.write(f"<style>{css_file.read()}</style>")
        f.write("</head><body>")
        f.write('<div style="display: flex;">\n')
        f.write('<div>\n')
        _render_hex_table(unpickler, f)
        f.write("</div>\n")

        f.write("<script>\n")
        f.write(f'const lookupTable = new Array({sum(unpickler.picklevis_byte_count)});\n')
        f.write(f'const byte_ascii_prefix = "{BYTE_ASCII_PREFIX}";\n')
        f.write(f'const byte_prefix = "{BYTE_PREFIX}";\n')
        f.write(f'const block_prefix = "{BLOCK_PREFIX}";\n')
        f.write("</script>\n")

        pkl_file = unpickler.get_file()
        for event in unpickler.get_events():
            if pkl_file.seek(event.offset) == event.offset:
                content = pkl_file.read(event.byte_count)

                start = event.offset
                end = event.offset + event.byte_count
                if event.opcode != pickle.FRAME[0]:
                    f.write("<script>")
                    f.write(f"lookupTable[{event.offset}] = ")
                    f.write("{\n")
                    f.write(f'start: {start}, end: {end}\n')
                    f.write("};\n")
                    for i in range(start + 1, end):
                        f.write(f"lookupTable[{i}] = ")
                        f.write("{\n")
                        f.write(f'start: {start}, end: {end}\n')
                        f.write("};\n")
                    f.write("</script>\n")

                f.write(f'<div class="event-block" id="{BLOCK_PREFIX}{start}-{end}" style="display: none;"><div class="event-block-content">[OP-{OPCODE_INT_NAME_MAPPING[event.opcode]}] {event.opcode}, {event.byte_count} bytes - {event.offset}: {content} </div></div>')
        f.write('</div><!-- flexible container -->\n')
        f.write("</body></html>")
        print(i)
    return i
