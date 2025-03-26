from functools import cmp_to_key

def compress_file(input_file_path, output_file_path, block_size):
    with open(input_file_path, 'rb') as input_file, open(output_file_path, 'wb') as output_file:
        while True:
            data = input_file.read(block_size)
            if not data:
                break
            last_column_bwt, s_index = bwt_compress(data)
            code_block = rle_compress(last_column_bwt)

            output_file.write(s_index.to_bytes(4, byteorder='little'))
            for count, symbol in code_block:
                write_variable_length_integer(output_file, count)
                output_file.write(bytes([symbol]))

def write_variable_length_integer(file, value):
    while value > 127:
        file.write(bytes([(value & 127) | 128]))
        value >>= 7
    file.write(bytes([value]))

def bwt_compress(S):
    n = len(S)
    indices = list(range(n))

    def compare_cyclic_shifts(i, j):
        for k in range(n):
            char_i = S[(i + k) % n]
            char_j = S[(j + k) % n]
            if char_i < char_j:
                return -1
            elif char_i > char_j:
                return 1
        return 0


    indices.sort(key=cmp_to_key(compare_cyclic_shifts))


    last_column_bwt = bytes([S[indices[i]-1] if indices[i] > 0 else S[-1] for i in range(n)])
    s_index = indices.index(0)
    return last_column_bwt, s_index

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
            s_index_bytes = input_file.read(4)
            if not s_index_bytes:
                break

            s_index = int.from_bytes(s_index_bytes, byteorder='little')
            decompressed_block = bytearray()
            bytes_read = 0

            while bytes_read < block_size:
                count, symbol, bytes_consumed = rle_decompress(input_file)

                if count is None:
                    decompressed_block = bwt_decompress(decompressed_block, s_index)
                    output_file.write(decompressed_block)
                    return

                decompressed_block.extend([symbol] * count)
                bytes_read += count

                if bytes_read > block_size:
                    break

            decompressed_block = bwt_decompress(decompressed_block, s_index)
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

def bwt_decompress(last_column_BWM, S_index):
    N = len(last_column_BWM)
    T = counting_sort_arg(last_column_BWM)
    j = S_index
    original_S = bytearray()
    for _ in range(N):
        j = T[j]
        original_S.append(last_column_BWM[j])
    return bytes(original_S)

def counting_sort_arg(S):
    P = [0] * 256
    for s in S:
        P[s] += 1

    T_sub = [0] * 256
    for j in range(1, 256):
        T_sub[j] = T_sub[j - 1] + P[j - 1]

    T = [-1] * len(S)
    for i in range(len(S)):
        T[T_sub[S[i]]] = i
        T_sub[S[i]] += 1
    return T



if __name__ == "__main__":
    input_file = 'input.raw'
    compressed_file = 'compressed.bwt_pmd'
    decompressed_file = 'decompressed.raw'
    block_size = 64

    compress_file(input_file, compressed_file, block_size)
    print(f"Файл '{input_file}' сжат в '{compressed_file}'.")

    decompress_file(compressed_file, decompressed_file, block_size)
    print(f"Файл '{compressed_file}' восстановлен в '{decompressed_file}'.")


    ########################### проверка на идентичность
    import filecmp


    def files_are_identical(file1, file2):
        return filecmp.cmp(file1, file2, shallow=False)

    file1 = 'input.raw'
    file2 = 'decompressed.raw'

    if files_are_identical(file1, file2):
        print("Файлы идентичны.")
    else:
        print("Файлы различаются.")