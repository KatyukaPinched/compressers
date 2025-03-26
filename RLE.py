def compress_file(input_file_path, output_file_path, block_size):
    with open(input_file_path, 'rb') as input_file, open(output_file_path, 'wb') as output_file:
        while True:
            data = input_file.read(block_size)
            if not data:
                break
            code_block = rle_compress(data)

            for count, symbol in code_block:
                write_variable_length_integer(output_file, count)
                output_file.write(bytes([symbol]))

def write_variable_length_integer(file, value):
    while value > 127:
        file.write(bytes([(value & 127) | 128]))
        value >>= 7
    file.write(bytes([value]))

def rle_compress(data):
    count = 1
    result = []

    for i in range(len(data)):
        if i + 1 == len(data):
            result.append((count, data[i]))
            continue
        elif data[i] == data[i + 1]:
            count += 1
        else:
            result.append((count, data[i]))
            count = 1

    return result



def decompress_file(input_file_path, output_file_path, block_size):
    with open(input_file_path, 'rb') as input_file, open(output_file_path, 'wb') as output_file:
        while True:
            decompressed_block = bytearray()
            bytes_read = 0

            while bytes_read < block_size:
                count, symbol, bytes_consumed = rle_decompress(input_file)

                if count is None:
                    output_file.write(decompressed_block)
                    return

                decompressed_block.extend([symbol] * count)
                bytes_read += bytes_consumed

                if bytes_read > block_size:
                    break

            output_file.write(decompressed_block)

def rle_decompress(input_file):
    count = 0
    shift = 0
    count_bytes = 0
    while True:
        byte = input_file.read(1)
        if not byte:
            return None, None, None

        byte = byte[0]
        count |= (byte & 127) << shift
        count_bytes += 1
        if byte & 128 == 0:
            break
        shift += 7

    symbol = input_file.read(1)
    if not symbol:
        return None, None, None
    symbol = symbol[0]

    return count, symbol, count_bytes + 1



if __name__ == "__main__":
    input_file = 'input.pmd'
    compressed_file = 'compressed.rle'
    decompressed_file = 'decompressed.pmd'
    block_size = 64

    compress_file(input_file, compressed_file, block_size)
    print(f"Файл '{input_file}' сжат в '{compressed_file}'.")

    decompress_file(compressed_file, decompressed_file, block_size)
    print(f"Файл '{compressed_file}' восстановлен в '{decompressed_file}'.")


    ############################ проверка на идентичность
    import filecmp


    def files_are_identical(file1, file2):
        return filecmp.cmp(file1, file2, shallow=False)

    file1 = 'input.pmd'
    file2 = 'decompressed.pmd'

    if files_are_identical(file1, file2):
        print("Файлы идентичны.")
    else:
        print("Файлы различаются.")