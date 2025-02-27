## Imagineering_golomb.py
## Source code by koda
## release 03/02/2025 --version 0.1

import sys
import re
from collections import Counter

###EXTRACT
def read_rom(romFile, addr, size):
    """
    Reads a portion of a ROM file.

    Parameters:
        romFile (str): The path to the ROM file.
        addr (int): The address in the ROM to start reading from.
        size (int): The number of bytes to read from the ROM.

    Returns:
        bytes: A byte object containing the data read from the ROM.
    """
    with open(romFile, "rb") as f:
        f.seek(addr)
        data = f.read(size)
    return data

def readTbl(tblFile):
    """
    Reads a .tbl file to create a character mapping table.
    
    Parameters:
        tblFile (str): The path to the .tbl file.
    
    Returns:
        dict: A dictionary where the keys are byte values (int) and the values are strings.
    """
    charTable = {}   
    with open(tblFile, "r", encoding='UTF-8') as f:
        for line in f:
            if line.startswith(";") or line.startswith("/"):
                continue 
            if "=" in line:
                hexValue, chars = line.split("=", 1)
                if "~" in chars:
                    continue 
                try:
                    hexValue = int(hexValue, 16)
                    chars = chars.rstrip("\n")
                    charTable[hexValue] = chars  
                except ValueError:
                    continue 
    return charTable

def get_translated_char(byte_value):
    """
    Retrieves the translated character for a given byte value based on the character table.

    Parameters:
        byte_value (int): The byte value to look up in the character table.

    Returns:
        str: The translated character or a placeholder string if not found.
    """
    char_table = readTbl(tbl_file)
    if byte_value in char_table:
        return char_table[byte_value]
    else:
        return f"~{byte_value:02X}~"

def get_charmaps(romFile, addr, size):
    """
    Retrieves the character maps from the ROM file, dividing it into three sections: 
    charmap0, charmap1, and charmap2.

    Parameters:
        romFile (str): The path to the ROM file.
        addr (int): The starting address of the character maps in the ROM.
        size (int): The size of the character maps section.

    Returns:
        list: A list containing three sublists of translated characters (alpha0, alpha1, alpha2).
    """
    data = read_rom(romFile, addr, size)

    charmap0_max_size = charmap1_max_size = charmap2_max_size = charmap3_max_size = 0

    if size <= 0xF:
        charmap0_max_size = 16
        nybbles_division = [0xF,0xFF,0xFF,0xFF]
    elif 0xF < size <= 0x1F:
        charmap0_max_size = 15
        charmap1_max_size = 16
        nybbles_division = [0xE,0xF,0xFF,0xFF]
    elif 0x1F < size <= 0x2E:
        charmap0_max_size = 14
        charmap1_max_size = 16
        charmap2_max_size = 16
        nybbles_division = [0xD,0xE,0xF,0xFF]
    elif 0x2E < size <= 0x3D:
        charmap0_max_size = 13
        charmap1_max_size = 16
        charmap2_max_size = 16
        charmap3_max_size = 16
        nybbles_division = [0xC,0xD,0xE,0xF]
    else:
        print("Charmap max size exceeded")
        exit()

    # Divide chars
    charmap0 = data[:charmap0_max_size]
    remaining_data = data[charmap0_max_size:]

    charmap1 = remaining_data[:charmap1_max_size]
    remaining_data = remaining_data[charmap1_max_size:]

    charmap2 = remaining_data[:charmap2_max_size]
    remaining_data = remaining_data[charmap2_max_size:]

    charmap3 = remaining_data[:charmap3_max_size]

    # Decode chars to using tbl
    alpha0 = [get_translated_char(byte) for byte in charmap0]
    alpha1 = [get_translated_char(byte) for byte in charmap1]
    alpha2 = [get_translated_char(byte) for byte in charmap2]
    alpha3 = [get_translated_char(byte) for byte in charmap3]

    alphabets = [alpha0, alpha1, alpha2, alpha3]
    return alphabets, nybbles_division

def hex_to_nybbles(hex_data):
    """
    Converts a list of bytes (hex data) into a list of nybbles (4-bit nibbles).
    
    Parameters:
        hex_data (list): A list of bytes (each byte is 8 bits).

    Returns:
        list: A list of nybbles (4-bit values).
    """
    compressed_nybbles = []
    for byte in hex_data:
        compressed_nybbles.append(byte >> 4)
        compressed_nybbles.append(byte & 0x0F)
    return compressed_nybbles

def decompress_golomb(compressed_data, charmap, charmapsize, line_breaker):
    """
    Decompresses the data using Golomb coding, translating the nybbles into characters 
    based on the character maps.

    Parameters:
        compressed_data (list): A list of nybbles representing the compressed data.
        charmap (list): A list of character maps (each containing a sublist of characters).
        line_breaker (int): The byte value used to signify a line break.

    Returns:
        list: A list of decompressed strings, where each string is a line of text.
    """
    line_breaker = get_translated_char(line_breaker)  
    decompressed_text = []
    line = []
    i = 0
    while i < len(compressed_data):
        nybble = compressed_data[i]
         
        # 4 bits characters
        if nybble <= charmapsize[0]:
            if nybble > len(charmap[0]) - 1:
                break
            char = charmap[0][nybble]
            if char == line_breaker:
                line.append(line_breaker)            
                decompressed_text.append(''.join(line))
                line = []  
            else:
                line.append(char)
            i += 1
        
        # 8 bits characters #1
        elif nybble == charmapsize[1]:
            if i + 1 < len(compressed_data):
                expanded_index = compressed_data[i + 1]
                if expanded_index > len(charmap[1]) - 1:
                    break
                char = charmap[1][expanded_index]
                if char == line_breaker:
                    line.append(line_breaker)
                    decompressed_text.append(''.join(line))
                    line = []
                else:
                    line.append(char)
                i += 2
            else:
                break
        
        # 8 bits characters #2
        elif nybble == charmapsize[2]:
            if i + 1 < len(compressed_data):
                expanded_index = compressed_data[i + 1]
                if expanded_index > len(charmap[2]) - 1:
                    break
                char = charmap[2][expanded_index]
                if char == line_breaker:
                    line.append(line_breaker)
                    decompressed_text.append(''.join(line))
                    line = []
                else:
                    line.append(char)
                i += 2
            else:
                break
            
        # 8 bits characters #3
        elif nybble == charmapsize[3]:
            if i + 1 < len(compressed_data):
                expanded_index = compressed_data[i + 1]
                if expanded_index > len(charmap[3]) - 1:
                    break
                char = charmap[3][expanded_index]
                if char == line_breaker:
                    line.append(line_breaker)
                    decompressed_text.append(''.join(line))
                    line = []
                else:
                    line.append(char)
                i += 2
            else:
                break
        else:
            last_nybble = compressed_data[i - 1]
            post_nybble = compressed_data[i + 1]
            raise ValueError(f"Invalid nybble value: {nybble}, debbug secuence: {last_nybble} {nybble} {post_nybble}")
            break
        
    return decompressed_text

def writeOutFile(file, scriptText):
    """
    Writes decompressed text to an output file, with each line formatted with a semicolon 
    and newline.

    Parameters:
        file (str): The path to the output file.
        scriptText (list): A list of strings representing the script content.
    """
    with open(file, "w", encoding='UTF-8') as f:
        i = 0
        for line in scriptText:
            f.write(f"@{i+1}\n")
            f.write(f";{line}\n")
            f.write(f"{line}\n")
            f.write("|\n")
            i += 1
            
###INSERT
def readScriptFile(file):
    """
    Reads a file with a game's text.
    
    Parameters:
        file (str): The path to the file to read.
    
    Returns:
        tuple: Containing:
            - textData (list of str): A list of strings, each representing a line of text from the file.
    """
    with open(file, "r", encoding='utf-8') as f:
        script = []
        for line in f.readlines():
            line = line.rstrip("\n")  
            if line.startswith(";") or line.startswith("@") or line.startswith("|"):
                continue
            script.append(line)
    return script

def encode_chars_and_give_frecuency(script, tbl_file):
    """
    Converts a list of text into hexadecimal values using the tbl dictionary,
    and also creates a frequency histogram of the characters.
    
    Parameters:
        script (list): List of strings.
        tbl_file (str): .tbl file containing the character table.
    
    Returns:
        tuple: 
            - A list of list.
            - A dictionary with the frequencies of the characters.
    """
    char_table = readTbl(tbl_file)
    lines = []
    freq_counter = Counter()
    hex_format = r'~([0-9A-Fa-f]{2})~'
    
    for line in script:
        byte_values = []
        matches = re.findall(hex_format, line)     
        for match in matches:
            hex_value = int(match, 16)
            line = line.replace(f"~{match}~", chr(hex_value))

        for char in line:
            if char in char_table.values():
                hex_value = [k for k, v in char_table.items() if v == char][0]
                byte_values.append(hex_value)
                freq_counter[hex_value] += 1
            else:
                byte_value = ord(char)
                byte_values.append(byte_value)
                freq_counter[byte_value] += 1

        lines.append(byte_values)

    sorted_histogram = dict(sorted(freq_counter.items(), key=lambda x: (-x[1], x[0])))

    return lines, sorted_histogram

def create_charmap(frequency_chars):
    """
    Converts a list of text into hexadecimal values using the tbl dictionary,
    and also creates a frequency histogram of the characters.
    
    Parameters:
        frequency_chars (dict): A dictionary with the frequencies of the characters.
    
    Returns:
        tuple: 
            - A list of hexadecimal values (as integers).
            - A dictionary with the frequencies of the characters.
    """  
    charmap0_size = 0
    
    if len(frequency_chars) <= 0xF:
        charmap0_size = 16
    elif 0xF < len(frequency_chars) <= 0x1F:
        charmap0_size = 15
    elif 0x1F < len(frequency_chars) <= 0x2E:
        charmap0_size = 14
    elif 0x2E < len(frequency_chars) <= 0x3D:
        charmap0_size = 13
    else:
        print("Charmap max size exceeded")
        exit()

    charmap1_size = 16
    charmap2_size = 16
    charmap3_size = 16
    
    alphabet0 = list(frequency_chars.keys())[:charmap0_size]
    alphabet1 = list(frequency_chars.keys())[charmap0_size:charmap0_size + charmap1_size]
    alphabet2 = list(frequency_chars.keys())[charmap0_size + charmap1_size:charmap0_size + charmap1_size + charmap2_size]
    alphabet3 = list(frequency_chars.keys())[charmap0_size + charmap1_size + charmap2_size:charmap0_size + charmap1_size + charmap2_size + charmap3_size]
    alphabets = [alphabet0, alphabet1, alphabet2, alphabet3]
    
    new_charmap = bytearray()
    for hex_value in frequency_chars.keys():
        new_charmap.append(hex_value)

    new_charmap_size = len(new_charmap)

    return alphabets, new_charmap, new_charmap_size

def compress_to_nybbles(text_list, alphabets):
    """
    Converts a bytearray of text (in hexadecimal values) into nybbles using a character map.
    
    Parameters:
        text_list (list): A list of list.
        alphabets (list): A list containing three sublists, each representing a charmap.
    
    Returns:
        list: A list of nybbles representing the compressed text.
    """

    if len(alphabets[0]) == 13:
        flag_0 = 0xD
        flag_1 = 0xE
        flag_2 = 0xF
    elif len(alphabets[0]) == 14:
        flag_0 = 0xE
        flag_1 = 0xF
        flag_2 = 0xF
    elif len(alphabets[0]) == 15:
        flag_0 = 0xF
        flag_1 = 0xF
        flag_2 = 0xF
    elif len(alphabets[0]) == 16:
        flag_0 = 0xF
        flag_1 = 0xF
        flag_2 = 0xF

    nybbles = []
    buffer = []
    cumulative_lenghts = []
    distance = 0
    
    all_chars = {}
    for i, alphabet in enumerate(alphabets):
        for j, char in enumerate(alphabet):
            all_chars[char] = (i, j)

    for line in text_list:
        for byte in line:
            i, j = all_chars[byte]
            if i == 0:
                buffer.append(j)
                distance += 4
            elif i == 1:
                buffer.append(flag_0)
                buffer.append(j)
                distance += 8
            elif i == 2:
                buffer.append(flag_1)
                buffer.append(j)
                distance +=8
            elif i == 3:
                buffer.append(flag_2)
                buffer.append(j)
                distance +=8
        if len(buffer) % 2 != 0:
            buffer.append(0)
            nybbles.extend(buffer)
            buffer = []
            distance += 4
        else:
            nybbles.extend(buffer)
            buffer = []      
        cumulative_lenghts.append(distance)

    cumulative_lenghts = [length // 8 for length in cumulative_lenghts]
        
    return nybbles, cumulative_lenghts

def nybbles_to_hex(nybbles):
    """
    Converts a list of nybbles into a bytearray and returns the bytearray size.

    Parameters:
        nybbles (list): List of nybbles (4-bit values).
    
    Returns:
        tuple: 
            - bytearray: The corresponding bytearray of the nybbles.
            - int: The size of the bytearray.
    """
    byte_values = bytearray()

    for i in range(0, len(nybbles), 2):
        nybble_pair = (nybbles[i] << 4) | nybbles[i + 1]
        byte_values.append(nybble_pair)

    return byte_values, len(byte_values)

def create_ptr_table(line_lenghts, messages_counts):
    """
    Creates the pointer table from line lengths and the blocks defined by messages_counts.
    Each value is converted to hexadecimal and represented in little-endian format.

    Parameters:
        line_lengths (list): List of line lengths.
        messages_counts (list): List of the number of lines per block.

    Returns:
        list: List of pointers (in little-endian format) separating the blocks.
    """
    table_pointers = bytearray()
    index = 0
    
    for block_size_index, block_size in enumerate(messages_counts):
        for i in range(block_size):
            length = line_lenghts[index]
            low_byte = length & 0xFF
            high_byte = (length >> 8) & 0xFF
            table_pointers.append(low_byte)
            table_pointers.append(high_byte)
            index += 1
        
        if block_size_index < len(messages_counts):
            table_pointers.append(0x00)
            table_pointers.append(0x00)
    
    while index < len(line_lenghts):
        length = line_lenghts[index]
        low_byte = length & 0xFF
        high_byte = (length >> 8) & 0xFF
        table_pointers.append(low_byte)
        table_pointers.append(high_byte)
        index += 1
        
    #DEBBUG LIST
##    for byte in table_pointers:
##        print(hex(byte))
##    print(len(table_pointers)//2)
    
    return table_pointers, len(table_pointers)

def writeROM(romFile, startOffset, originalSize, data):
    """
    Writes data to the ROM at the specified offset.

    Parameters:
        romFile (str): The path to the ROM file.
        startOffset (int): The offset in the ROM file where data should be written.
        originalSize (int): The original size of the data to ensure there is enough space for the write operation.
        data (bytes or bytearray): The data to write to the ROM.
    
    Returns:
        int: The amount of free space left after writing the data.
    """
    # Check free space
    freeSpace = int(originalSize) - len(data)

    # Fill free space
    filledData = data + b'\x00' * freeSpace
        
    with open(romFile, "r+b") as f: 
        f.seek(startOffset)
        f.write(filledData)
    return freeSpace
    
if __name__ == "__main__":
    if len(sys.argv) < 5:
        sys.stdout.write("Usage: -d <romFile> <outFile> <tblFile>\n")
        sys.stdout.write("       -c <outFile> <romFile> <tblFile>\n")
        sys.stdout.write("       -h show help.\n")
        sys.stdout.write("       -v show version.\n")
        sys.exit(1)
    
    # Option
    option = sys.argv[1]
    ##CONFIG############################################
    ##EDIT HERE#########################################
    script_offset = 0x1185
    script_size = 0xC01
    charmap_offset = 0x114F
    charmap_size = 0x36
    ptr_table_offset = 0x1D88
    ptr_table_size = 0x68
    ptr_table_sections = [24,25]
    line_breaker = 0x00
    ####################################################
    
    # Decompress
    if option == '-d' and len(sys.argv) == 5:
        rom_file = sys.argv[2]
        out_file = sys.argv[3]
        tbl_file = sys.argv[4]
        
        # Read rom file script
        compressed_data = read_rom(rom_file, script_offset, script_size)
        # Read rom file charmap
        charmap, charmaps_size = get_charmaps(rom_file, charmap_offset, charmap_size)
        # Convert hex data to nybbles
        compressed_nybbles = hex_to_nybbles(compressed_data)
        # Convert nybbles to raw text
        decompressed_text = decompress_golomb(compressed_nybbles, charmap, charmaps_size, line_breaker)
        # Export to bin file
        writeOutFile(out_file, decompressed_text)
        print("------- CHAR MAPS -------\n")
        print(charmap)
        print(f"CHARMAP BLOCK SIZE: {charmap_size} / {hex(charmap_size)} bytes.")
        print(f"TEXT BLOCK SIZE: {script_size} / {hex(script_size)} bytes.")
        print(f"PTR_TABLE BLOCK SIZE: {ptr_table_size} / {hex(ptr_table_size)} bytes.")
        print(f"Text extracted to {out_file}")
        print("Decoding complete.\n")
        
    # Compress
    elif option == '-c' and len(sys.argv) == 5:        
        out_file = sys.argv[2]
        rom_file = sys.argv[3]
        tbl_file = sys.argv[4]

        # Read decompressed script
        script = readScriptFile(out_file)
        # Encode with tbl
        encoded_script, frecuency_table = encode_chars_and_give_frecuency(script, tbl_file)
        # Create new charmaps
        charmap, new_charmap_raw, new_charmap_size = create_charmap(frecuency_table)
        # Create nybbles
        compressed_text, lines_lenghts = compress_to_nybbles(encoded_script, charmap)
        # Convert nybbles to hex data
        new_script, new_script_size = nybbles_to_hex(compressed_text)
        # Create pointers table
        new_ptr_table, new_ptr_table_size = create_ptr_table(lines_lenghts, ptr_table_sections)
        # Write data to ROM if pass len checks
        if new_charmap_size > charmap_size:
            print(f"ERROR: char map size has exceeded its maximum size. Remove {new_charmap_size - charmap_size} character type.")
            char_values = [[chr(byte) for byte in alphabet] for alphabet in charmap]
            print(char_values)
            exit()
        if new_script_size > script_size:
            print(f"ERROR: script size has exceeded its maximum size. Remove {new_script_size - script_size} bytes.")
            exit()
        if new_ptr_table_size > ptr_table_size:
            print(f"ERROR: table pointer size has exceeded its maximum size. Remove {(new_ptr_table_size - ptr_table_size)//2} lines in script.")
            exit()
        charmap_freespace = writeROM(rom_file, charmap_offset, charmap_size, new_charmap_raw)
        print(f"CharMap write to address {hex(charmap_offset)}, {charmap_freespace} chars free.")
        script_freespace = writeROM(rom_file, script_offset, script_size, new_script)
        print(f"Script text write to address {hex(script_offset)}, {script_freespace} bytes free.")
        ptr_table_freespace = writeROM(rom_file, ptr_table_offset, ptr_table_size, new_ptr_table)
        print(f"Pointer table write to address {hex(ptr_table_offset)}, {ptr_table_freespace//2} lines/pointers left.")
##        #FIX FOR BARBIE, 1 POINTER REPEATED (uncomment for Barbie)
##        save_ptr = read_rom(rom_file, 0x1DB6, 0x02)
##        writeROM(rom_file, 0x1DB8, 0x02, save_ptr)
        
    elif option == '-v' or option == '?':
        print("Golomb Text Decompressor/Compressor by koda v0.1")
        
    else:
        sys.stdout.write("Usage: -d <romFile> <outFile> <tblFile>\n")
        sys.stdout.write("       -c <outFile> <romFile> <tblFile>\n")
        sys.stdout.write("       -h show help.\n")
        sys.stdout.write("       -v show version.\n")
        sys.exit(1)
