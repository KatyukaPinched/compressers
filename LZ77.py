
def compress_file(input_file_path, output_file_path, window_size, lookahead_buffer_size):
    with open(input_file_path, 'rb') as input_file, open(output_file_path, 'wb') as output_file:
        data = input_file.read()
        compressed_data = lz77_compress(data, window_size, lookahead_buffer_size)
        packed_data = pack_compressed_data(compressed_data)
        output_file.write(packed_data)

def pack_compressed_data(compressed_data):
    packed_data = bytearray()
    for distance, length, next_char in compressed_data:
        packed_data.extend(distance.to_bytes(2, 'little'))
        packed_data.extend(length.to_bytes(2, 'little'))
        packed_data.append(next_char)
    return packed_data

def lz77_compress(data, window_size, lookahead_buffer_size):
    compressed_data = []
    i = 0
    n = len(data)

    while i < n:
        match_length = 0
        match_distance = 0

        start = max(0, i - window_size)

        for j in range(start, i):
            length = 0
            while (j + length < n and
                   i + length < n and
                   length < lookahead_buffer_size and
                   data[j + length] == data[i + length]):
                length += 1

            if length > match_length:
                match_length = length
                match_distance = i - j

        if match_length > 0:
            next_char_index = i + match_length
            next_char = data[next_char_index] if next_char_index < n else 0
            compressed_data.append((match_distance, match_length, next_char))
            i += match_length + 1
        else:
            compressed_data.append((0, 0, data[i]))
            i += 1

    return compressed_data



def decompress_file(input_file_path, output_file_path):
    with open(input_file_path, 'rb') as input_file, open(output_file_path, 'wb') as output_file:

        data = input_file.read()
        compressed_data = parse_compressed_data(data)
        decompressed_data = lz77_decompress(compressed_data)
        output_file.write(decompressed_data)

def parse_compressed_data(compressed_data):
    packed_data = []
    i = 0
    n = len(compressed_data)

    while i < n:
        if i + 4 >= n:
            break

        match_distance = compressed_data[i] | (compressed_data[i + 1] << 8)
        match_length = compressed_data[i + 2] | (compressed_data[i + 3] << 8)
        next_char = compressed_data[i + 4]

        packed_data.append((match_distance, match_length, next_char))
        i += 5
    return packed_data

def lz77_decompress(compressed_data):
    decompressed_data = bytearray()

    for distance, length, next_char in compressed_data:
        if distance == 0 and length == 0:
            decompressed_data.append(next_char)
        else:
            start_index = len(decompressed_data) - distance
            for j in range(length):
                decompressed_data.append(decompressed_data[start_index + j])
            if next_char == 0: break
            decompressed_data.append(next_char)

    return bytes(decompressed_data)



if __name__ == "__main__":
    input_file = 'russian_text.txt'
    compressed_file = 'compressed.lz77'
    decompressed_file = 'decompressed'

    compress_file(input_file, compressed_file, 500, 400)
    print(f"Файл '{input_file}' сжат в '{compressed_file}'.")

    decompress_file(compressed_file, decompressed_file)
    print(f"Файл '{compressed_file}' восстановлен в '{decompressed_file}'.")


    ############################ проверка на идентичность
    import filecmp


    def files_are_identical(file1, file2):
        return filecmp.cmp(file1, file2, shallow=False)

    file1 = 'russian_text.txt'
    file2 = 'decompressed'

    if files_are_identical(file1, file2):
        print("Файлы идентичны.")
    else:
        print("Файлы различаются.")

