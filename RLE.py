def compress_file(input_file_path, output_file_path, block_size):
    with open(input_file_path, 'rb') as input_file, open(output_file_path, 'wb') as output_file:
        while True:
            data = input_file.read(block_size)
            if not data:
                break
            code_block = rle_compress(data)

            for flag, count, symbol in code_block:
                output_file.write(bytes([flag]))
                write_variable_length_integer(output_file, count)
                if flag == 1:
                    output_file.write(bytes([symbol]))
                else:
                    output_file.write(symbol)

def write_variable_length_integer(file, value):
    while value > 127:
        file.write(bytes([(value & 127) | 128]))
        value >>= 7
    file.write(bytes([value]))

def rle_compress(data):
    result = []
    i = 0

    while i < len(data):
        if i + 1 < len(data) and data[i] == data[i + 1]:
            count = 1
            while i + 1 < len(data) and data[i] == data[i + 1]:
                count += 1
                i += 1
            result.append((1, count, data[i]))
            i += 1
        else:
            j = i
            while j < len(data) and (j == i or (j + 1 < len(data) and data[j] != data[j + 1])):
                j += 1
            result.append((0, j - i, data[i:j]))
            i = j

    return result



def decompress_file(input_file_path, output_file_path, block_size):
    with open(input_file_path, 'rb') as input_file, open(output_file_path, 'wb') as output_file:
        while True:
            decompressed_block = bytearray()
            bytes_read = 0

            while bytes_read < block_size:
                flag = input_file.read(1)
                if not flag:
                    output_file.write(bytes(decompressed_block))
                    return

                flag = flag[0]
                count = read_variable_length_integer(input_file)

                if flag == 1:
                    symbol_bytes = input_file.read(1)
                    symbol = symbol_bytes[0]
                    decompressed_block.extend([symbol] * count)
                    bytes_read += count
                else:
                    string_bytes = input_file.read(count)
                    if not string_bytes or len(string_bytes) != count:
                        output_file.write(bytes(decompressed_block))
                        return
                    decompressed_block.extend(string_bytes)
                    bytes_read += count

                if bytes_read > block_size:
                    excess_bytes = bytes_read - block_size
                    decompressed_block = decompressed_block[:-excess_bytes]
                    break

            output_file.write(bytes(decompressed_block))

def read_variable_length_integer(file):
    value = 0
    shift = 0
    while True:
        byte = file.read(1)
        if not byte:
            return None
        byte = byte[0]
        value |= (byte & 127) << shift
        shift += 7
        if byte & 128 == 0:
            break
    return value



if __name__ == "__main__":
    input_file = 'russian_text.txt'
    compressed_file = 'compressed.rle'
    decompressed_file = 'decompressed'
    block_size = 4096

    compress_file(input_file, compressed_file, block_size)
    print(f"Файл '{input_file}' сжат в '{compressed_file}'.")

    decompress_file(compressed_file, decompressed_file, block_size)
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
