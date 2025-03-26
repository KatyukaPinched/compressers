def encode_varint(value):
    result = bytearray()
    while value >= 128:
        result.append((value & 127) | 128)
        value >>= 7
    result.append(value)
    return result

def decode_varint(data):
    value = 0
    shift = 0
    i = 0
    while True:
        byte = data[i]
        value |= (byte & 127) << shift
        i += 1
        if byte < 128:
            break
        shift += 7
    return value, i

def compress_file(input_file_path, output_file_path):
    with open(input_file_path, 'rb') as input_file, open(output_file_path, 'wb') as output_file:
        dictionary = {b"": 0}
        buffer = bytearray()
        for chunk in iter(lambda: input_file.read(4096), b""):
            for char in chunk:
                byte_char = bytes([char])
                current_prefix = bytes(buffer + byte_char)

                if current_prefix in dictionary:
                    buffer += byte_char
                else:
                    index = dictionary.get(bytes(buffer), 0)
                    output_file.write(encode_varint(index))
                    output_file.write(byte_char)
                    dictionary[current_prefix] = len(dictionary)
                    buffer = bytearray()

        if buffer:
            index = dictionary.get(bytes(buffer), 0)
            output_file.write(encode_varint(index))
            output_file.write(b"")

def decompress_file(input_file_path, output_file_path):
    with open(input_file_path, 'rb') as input_file, open(output_file_path, 'wb') as output_file:
        dictionary = [b""]
        i = 0
        input_data = input_file.read()
        while i < len(input_data):
            index, offset = decode_varint(input_data[i:])
            i+=offset
            value = input_data[i:i+1]
            i+=1

            if index == 0:
                entry = value
            else:
                entry = dictionary[index] + value

            output_file.write(entry)
            dictionary.append(entry)



if __name__ == "__main__":
    input_file = 'input.pmd'
    compressed_file = 'compressed.lz78'
    decompressed_file = 'decompressed.pmd'

    compress_file(input_file, compressed_file)
    print(f"Файл '{input_file}' сжат в '{compressed_file}'.")

    decompress_file(compressed_file, decompressed_file)
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

