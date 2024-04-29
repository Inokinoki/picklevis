function change_bytes_color(start, end, color) {
    // Highlight opcode
    document.getElementById(byte_ascii_prefix + start).style.color = color;
    document.getElementById(byte_prefix + start).style.color = color;
    // Highlight body
    for (let i = start + 1; i < end; i++) {
        document.getElementById(byte_ascii_prefix + i).style.backgroundColor = color;
        document.getElementById(byte_prefix + i).style.backgroundColor = color;
    }
}

function highlight_for_byte(index, color) {
    // Global
    if (index < lookupTable.length && lookupTable[index]) {
        if (highlighted) {
            // Early return due to selected block
            return;
        }

        const start = lookupTable[index].start, end = lookupTable[index].end;
        // Change color
        change_bytes_color(start, end, color);
        // Show block
        const block_id = block_prefix + start + "-" + end;
        document.getElementById(block_id).style.display = "";
    }
}

function unhighlight_for_byte(index, color) {
    // Global
    if (index < lookupTable.length && lookupTable[index]) {
        if (highlighted) {
            // Early return due to selected block
            return;
        }

        const start = lookupTable[index].start, end = lookupTable[index].end;
        // Change color
        change_bytes_color(start, end, color);
        // Show block
        const block_id = block_prefix + start + "-" + end;
        document.getElementById(block_id).style.display = "none";
    }
}

function swtich_for_byte(index, color) {
    // Global
    if (index < lookupTable.length && lookupTable[index]) {
        if (highlighted) {
            const highlight_start = lookupTable[highlighted].start, highlight_end = lookupTable[highlighted].end;
            const block_id = block_prefix + highlight_start + "-" + highlight_end;
            if (index >= highlight_start && index < highlight_end) {
                // Already highlighted, cancel the highlight
                change_bytes_color(highlight_start, highlight_end, '');
                document.getElementById(block_id).style.display = "none";

                highlighted = undefined;
                return;
            }

            // Cancel the current highlight because clicked on another one
            change_bytes_color(highlight_start, highlight_end, '');
            document.getElementById(block_id).style.display = "none";
        }

        // Activate the highlight
        const start = lookupTable[index].start, end = lookupTable[index].end;
        const block_id = block_prefix + start + "-" + end;
        change_bytes_color(start, end, color);
        document.getElementById(block_id).style.display = "";

        highlighted = index;
    }
}
