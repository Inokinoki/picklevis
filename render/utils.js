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

function change_for_byte(index, color) {
    // Global
    if (index < lookupTable.length && lookupTable[index]) {
        const start = lookupTable[index].start, end = lookupTable[index].end;
        // Change color
        change_bytes_color(start, end, color);
        // Show block
        const block_id = block_prefix + start + "-" + end;
        document.getElementById(block_id).style.display = 
            document.getElementById(block_id).style.display == "none" ? "" : "none";
    }
}
