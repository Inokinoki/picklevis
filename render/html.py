
from event import PicklevisEventType, PicklevisEventSource, PicklevisEventGroup, PicklevisEvent
from picklevis_core import Unpickler, OPCODE_INT_NAME_MAPPING

import html
import os
import pickle
import string


BYTE_PREFIX = "byte-"
BYTE_ASCII_PREFIX = "byte-ascii-"
BLOCK_PREFIX = "block-"

LINE_MAX_LINE = 32


def _render_hex_table(unpickler: Unpickler, f):
    pkl_file = unpickler.get_file()
    pkl_file.seek(0)

    line_count = 0
    f.write('<table style="border-spacing: 0;"><tr><th></th>')
    for i in range(16):
        f.write(f"<th><code>{i:02X}&nbsp;</code></th>")
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
        f.write(f"<tr><th><code>{(line_count * 16):08X}</code></th>")

        b_index = 0
        for b in bs:
            f.write(f'<td id="{BYTE_PREFIX}{byte_counter + b_index}" ')
            f.write(f'onmouseover="highlight_for_byte({byte_counter + b_index}, highlight_color)" ')
            f.write(f'onmouseout="unhighlight_for_byte({byte_counter + b_index}, \'\')" ')
            f.write(f'onclick="swtich_for_byte({byte_counter + b_index}, highlight_color)">')
            f.write(f'<code>{b:02X}&nbsp;</code></td>')
            b_index += 1
            if b_index == 8:
                f.write("<td> </td>")

        if len(bs) < 16:
            for i in range(16 - len(bs)):
                f.write("<td> </td> ")

        f.write("<td> </td><td>|</td>")
        b_index = 0
        for b in bs:
            f.write(f'<td id="{BYTE_ASCII_PREFIX}{byte_counter + b_index}" ')
            f.write(f'onmouseover="highlight_for_byte({byte_counter + b_index}, highlight_color)" ')
            f.write(f'onmouseout="unhighlight_for_byte({byte_counter + b_index}, \'\')" ')
            f.write(f'onclick="swtich_for_byte({byte_counter + b_index}, highlight_color)"><code>')
            if chr(b) in string.printable:
                f.write(f'{html.escape(chr(b))}')
            else:
                f.write(".")
            f.write("</code></td>\n")
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
        f.write('const highlight_color = "#D7DBDD";\n')
        f.write('var highlighted = undefined;\n')
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
                    for index in range(start + 1, end):
                        f.write(f"lookupTable[{index}] = ")
                        f.write("{\n")
                        f.write(f'start: {start}, end: {end}\n')
                        f.write("};\n")
                    f.write("</script>\n")
                f.write(f'<div class="event-block" id="{BLOCK_PREFIX}{start}-{end}" style="display: none;">\n')
                render_event_info(f, event, content)
                f.write("</div>\n")

        f.write('</div><!-- flexible container -->\n')
        f.write("</body></html>")

    return i


def render_stack_cell(f, content):
    c = content if len(content) < LINE_MAX_LINE else f"{content[:LINE_MAX_LINE]}..."
    f.write(f'<td style="border: 1px solid black; padding: 10px;"><code>{html.escape(c)}</code></td>')


def render_stack_num(f, number):
    f.write(f'<td style="text-align: right; padding: 10px;"><code>{html.escape(str(number))}</code></td>')


def render_stack_row(f, content, number=None):
    f.write('<tr>')
    render_stack_num(f, number if number is not None else '')
    render_stack_cell(f, content)
    f.write('</tr>')


def render_stack(f, stack, count=5):
    stack_size = len(stack)
    for e in stack[:min(count, stack_size)]:
        render_stack_row(f, str(e), stack_size - 1)
        stack_size -= 1

    if stack_size > 0:
        render_stack_row(f, "...")

    f.write('<tr>')
    render_stack_num(f, '')
    f.write('<td style="padding: 10px;">Stack</td>')
    f.write('</tr>')


def render_push_stack(f, stack, elements, count=5):
    f.write(f'<table style="text-align: center; border-collapse: collapse;">')
    for ele in elements:
        render_stack_row(f, str(ele))
    # TODO: Add a column for description?
    f.write('<tr style="text-align: center"><td></td><td>&DownArrow;</td></tr>')

    render_stack(f, stack, count)
    f.write(f'</table>')


def render_pop_stack(f, stack, elements, count=5):
    f.write(f'<table style="text-align: center; border-collapse: collapse;">')
    for ele in elements:
        render_stack_row(f, str(ele))
    # TODO: Add a column for description?
    f.write('<tr style="text-align: center"><td></td><td>&UpArrow;</td></tr>')

    render_stack(f, stack, count)
    f.write(f'</table>')


def render_push_meta_stack(f, stack, meta_stack, count=5):
    f.write(f'<table style="text-align: center; border-collapse: collapse;">')
    render_stack(f, meta_stack, count)
    # TODO: Add a column for description?
    f.write('<tr style="text-align: center"><td></td><td>&DownArrow;</td></tr>')

    render_stack(f, stack, count)
    f.write(f'</table>')


def render_pop_meta_stack(f, stack, meta_stack, count=5):
    f.write(f'<table style="text-align: center; border-collapse: collapse;">')
    render_stack(f, meta_stack, count)
    # TODO: Add a column for description?
    f.write('<tr style="text-align: center"><td></td><td>&DownArrow;</td></tr>')

    render_stack(f, stack, count)
    f.write(f'</table>')


def render_event_info(f, event, content):
    f.write('<div class="event-block-content">')
    f.write(f'Operation: {html.escape(OPCODE_INT_NAME_MAPPING[event.opcode])} ({event.opcode}, {hex(event.opcode)})<br/>\n')
    f.write(f'From byte {event.offset} ({hex(event.offset)}) to byte {event.offset + event.byte_count - 1} ({hex(event.offset + event.byte_count - 1)})<br/>\n')
    f.write(f'Total: {event.byte_count} byte{"s" if event.byte_count > 1 else ""}<br/>\n')
    for e in event.events:
        if e.type == PicklevisEventType.MEMO:
            if e.datasource == PicklevisEventSource.STACK:
                render_pop_stack(f, stack=e.stack if e.stack else [], elements=list(map(lambda name: f'MEMO "{name}"', e.elements)))
            elif e.datasource == PicklevisEventSource.MEMO:
                render_push_stack(f, stack=e.stack if e.stack else [], elements=list(map(lambda name: f'MEMO "{name}"', e.elements)))
        elif e.type == PicklevisEventType.STACK:
            if e.datasource == PicklevisEventSource.MEMO:
                render_push_stack(f, stack=e.stack if e.stack else [], elements=list(map(lambda name: f'MEMO "{name}"', e.elements)))
            elif e.datasource == PicklevisEventSource.STACK:
                render_pop_stack(f, stack=e.stack if e.stack else [], elements=e.elements)
            else:
                render_push_stack(f, stack=e.stack if e.stack else [], elements=e.elements)
        elif e.type == PicklevisEventType.METASTACK:
            if e.datasource == PicklevisEventSource.METASTACK:
                render_push_meta_stack(f, stack=e.stack if e.stack else [], meta_stack=e.meta_stack if e.meta_stack else [])
            else:
                render_pop_meta_stack(f, stack=e.stack if e.stack else [], meta_stack=e.meta_stack if e.meta_stack else [])

    f.write("</div>")
