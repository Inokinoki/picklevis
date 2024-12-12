
from event import PicklevisEventType, PicklevisEventSource
from picklevis_core import OPCODE_INT_NAME_MAPPING

import os
import pickle
import platform
import string

PYTHON_VERSION_TUPLE = platform.python_version_tuple()
if PYTHON_VERSION_TUPLE[0] == '2':
    # Before 3.2
    # Since nobody is actually using prior-3.4/3.5 versions, ignore the major version 3
    import cgi as html
else:
    import html


BYTE_PREFIX = "byte-"
BYTE_ASCII_PREFIX = "byte-ascii-"
BLOCK_PREFIX = "block-"

LINE_MAX_LINE = 32


def _render_hex_table(unpickler, f):
    pkl_file = unpickler.get_file()
    pkl_file.seek(0)

    line_count = 0
    f.write('<table style="border-spacing: 0;"><tr><th></th>')
    for i in range(16):
        f.write("<th><code>{:02X}&nbsp;</code></th>".format(i))
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
        f.write("<tr><th><code>{:08X}</code></th>".format(line_count * 16))

        b_index = 0
        for b in bs:
            f.write('<td id="{}{}" '.format(BYTE_PREFIX, byte_counter + b_index))
            f.write('onmouseover="highlight_for_byte({}, highlight_color)" '.format(byte_counter + b_index))
            f.write('onmouseout="unhighlight_for_byte({}, \'\')" '.format(byte_counter + b_index))
            f.write('onclick="swtich_for_byte({}, highlight_color)">'.format(byte_counter + b_index))
            f.write('<code>{:02X}&nbsp;</code></td>'.format(ord(chr(b))))
            b_index += 1
            if b_index == 8:
                f.write("<td> </td>")

        if len(bs) < 16:
            for i in range(16 - len(bs)):
                f.write("<td> </td> ")

        f.write("<td> </td><td>|</td>")
        b_index = 0
        for b in bs:
            f.write('<td id="{}{}" '.format(BYTE_ASCII_PREFIX, byte_counter + b_index))
            f.write('onmouseover="highlight_for_byte({}, highlight_color)" '.format(byte_counter + b_index))
            f.write('onmouseout="unhighlight_for_byte({}, \'\')" '.format(byte_counter + b_index))
            f.write('onclick="swtich_for_byte({}, highlight_color)"><code>'.format(byte_counter + b_index))
            if chr(ord(chr(b))) in string.printable:
                f.write(html.escape(chr(ord(chr(b)))))
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


def render_to_html(unpickler, name):
    i = 0
    with open(name, "w") as f:
        f.write("<html><head>\n")
        # Add utility functions
        with open(os.path.dirname(os.path.abspath(__file__)) + "/utils.js") as js_file:
            f.write("<script>{}</script>".format(js_file.read()))
        with open(os.path.dirname(os.path.abspath(__file__)) + "/utils.css") as css_file:
            f.write("<style>{}</style>".format(css_file.read()))
        f.write('</head><body onkeydown="keyboard_dispatch(event)">')
        f.write('<div style="display: flex;">\n')
        f.write('<div>\n')
        _render_hex_table(unpickler, f)
        f.write("</div>\n")

        f.write("<script>\n")
        f.write('const lookupTable = new Array({});\n'.format(sum(unpickler.picklevis_byte_count)))
        f.write('const byte_ascii_prefix = "{}";\n'.format(BYTE_ASCII_PREFIX))
        f.write('const byte_prefix = "{}";\n'.format(BYTE_PREFIX))
        f.write('const block_prefix = "{}";\n'.format(BLOCK_PREFIX))
        f.write('const highlight_color = "#D7DBDD";\n')
        f.write('var highlighted = undefined;\n')
        f.write("</script>\n")

        pkl_file = unpickler.get_file()

        frame_event_stack = []
        for event in unpickler.get_events():
            pkl_file.seek(event.offset)
            if pkl_file.tell() == event.offset:
                content = pkl_file.read(event.byte_count)

                start = event.offset
                end = event.offset + event.byte_count

                if PYTHON_VERSION_TUPLE[0] != "2" and event.opcode == pickle.FRAME[0]:
                    # TODO: Handle frame
                    end = event.offset + 9
                    frame_event_stack.insert(0, event)

                f.write("<script>")
                f.write("lookupTable[{}] = ".format(event.offset))
                f.write("{\n")
                f.write('start: {}, end: {}\n'.format(start, end))
                f.write("};\n")
                for index in range(start + 1, end):
                    f.write("lookupTable[{}] = ".format(index))
                    f.write("{\n")
                    f.write('start: {}, end: {}\n'.format(start, end))
                    f.write("};\n")
                f.write("</script>\n")

                f.write('<div class="event-block" id="{}{}-{}" style="display: none;">\n'.format(BLOCK_PREFIX, start, end))

                f.write('<div class="event-block-content">')
                f.write('<div class="event-block-stack">')
                for frame_event in frame_event_stack[::-1]:
                    f.write('In a frame from byte')
                    f.write('{} ({})'.format(frame_event.offset, hex(frame_event.offset)))
                    f.write('to byte')
                    f.write('{} ({})'.format(
                        frame_event.offset + frame_event.byte_count - 1,
                        hex(frame_event.offset + frame_event.byte_count - 1)
                    ))
                    f.write('<br/><br/>\n')
                f.write('</div>')

                render_event_info(f, event, content)
                f.write('</div>')
                f.write("</div>\n")

                # Handle frame event stack
                while len(frame_event_stack) > 0:
                    frame_event = frame_event_stack[0]
                    if end == frame_event.offset + frame_event.byte_count - 1:
                        frame_event_stack.pop()
                    else:
                        break

        f.write('</div><!-- flexible container -->\n')
        f.write("</body></html>")

    return i


def render_stack_cell(f, content):
    c = content if len(content) < LINE_MAX_LINE else "{}...".format(content[:LINE_MAX_LINE])
    f.write('<td style="border: 1px solid black; padding: 10px;">')
    f.write("<code>{}</code>".format(html.escape(c)))
    f.write('</td>')


def render_stack_num(f, number):
    f.write('<td style="text-align: right; padding: 10px;">')
    f.write("<code>{}</code>".format(html.escape(str(number))))
    f.write('</td>')


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
    f.write('<table style="text-align: center; border-collapse: collapse;">')
    for ele in elements:
        render_stack_row(f, str(ele))
    # TODO: Add a column for description?
    f.write('<tr style="text-align: center"><td></td><td>&DownArrow;</td></tr>')

    render_stack(f, stack, count)
    f.write('</table>')


def render_pop_stack(f, stack, elements, count=5):
    f.write('<table style="text-align: center; border-collapse: collapse;">')
    for ele in elements:
        render_stack_row(f, str(ele))
    # TODO: Add a column for description?
    f.write('<tr style="text-align: center"><td></td><td>&UpArrow;</td></tr>')

    render_stack(f, stack, count)
    f.write('</table>')


def render_push_meta_stack(f, stack, meta_stack, count=5):
    f.write('<table style="text-align: center; border-collapse: collapse;">')
    render_stack(f, meta_stack, count)
    # TODO: Add a column for description?
    f.write('<tr style="text-align: center"><td></td><td>&DownArrow;</td></tr>')

    render_stack(f, stack, count)
    f.write('</table>')


def render_pop_meta_stack(f, stack, meta_stack, count=5):
    f.write('<table style="text-align: center; border-collapse: collapse;">')
    render_stack(f, meta_stack, count)
    # TODO: Add a column for description?
    f.write('<tr style="text-align: center"><td></td><td>&DownArrow;</td></tr>')

    render_stack(f, stack, count)
    f.write('</table>')


def render_event_type(type):
    if type == PicklevisEventType.MEMO:
        return "MEMO"
    elif type == PicklevisEventType.STACK:
        return "STACK"
    elif type == PicklevisEventType.METASTACK:
        return "METASTACK"
    elif type == PicklevisEventType.INFO:
        return "INFO"
    elif type == PicklevisEventType.GROUP:
        return "GROUP"
    return "Unknown"


def render_event_info(f, event, content):
    f.write('<div>')
    f.write('Operation: {} ({}, {})<br/>\n'.format(
        html.escape(OPCODE_INT_NAME_MAPPING[ord(chr(event.opcode))]), event.opcode, hex(ord(chr(event.opcode))),
    ))
    f.write('From byte {} ({})'.format(event.offset, hex(event.offset)))
    f.write('to byte {} '.format(event.offset + event.byte_count - 1))
    f.write('({})<br/>\n'.format(hex(event.offset + event.byte_count - 1)))
    f.write('Total: {} byte{}<br/>\n'.format(event.byte_count, "s" if event.byte_count > 1 else ""))
    for e in event.events:
        if e.type == PicklevisEventType.MEMO:
            f.write('<b>{}:</b><br/> \n'.format(render_event_type(e.type)))
            if e.datasource == PicklevisEventSource.STACK:
                render_pop_stack(
                    f,
                    stack=e.stack if e.stack else [],
                    elements=list(map(lambda name: 'MEMO "{}"'.format(name), e.elements))
                )
            elif e.datasource == PicklevisEventSource.MEMO:
                render_push_stack(
                    f,
                    stack=e.stack if e.stack else [],
                    elements=list(map(lambda name: 'MEMO "{}"'.format(name), e.elements))
                )
        elif e.type == PicklevisEventType.STACK:
            f.write('<b>{}:</b><br/>\n'.format(render_event_type(e.type)))
            if e.datasource == PicklevisEventSource.MEMO:
                render_push_stack(
                    f,
                    stack=e.stack if e.stack else [],
                    elements=list(map(lambda name: 'MEMO "{}"'.format(name), e.elements))
                )
            elif e.datasource == PicklevisEventSource.STACK:
                render_pop_stack(f, stack=e.stack if e.stack else [], elements=e.elements)
            else:
                render_push_stack(f, stack=e.stack if e.stack else [], elements=e.elements)
        elif e.type == PicklevisEventType.METASTACK:
            f.write('<b>{}:</b><br/>\n'.format(render_event_type(e.type)))
            if e.datasource == PicklevisEventSource.METASTACK:
                render_push_meta_stack(f, stack=e.stack if e.stack else [], meta_stack=e.meta_stack if e.meta_stack else [])
            else:
                render_pop_meta_stack(f, stack=e.stack if e.stack else [], meta_stack=e.meta_stack if e.meta_stack else [])
        else:
            f.write('{}: {} - {}<br/>'.format(render_event_type(e.type), e.detail, content[e.offset: e.offset + e.byte_count]))

    f.write("</div>")
