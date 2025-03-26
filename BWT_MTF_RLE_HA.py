from functools import cmp_to_key
from queue import PriorityQueue

class Node:
    def __init__(self, symbol = None, freq = 0, bit0 = None, bit1 = None):
        if bit0 is not None and bit1 is not None:
            self._bit0 = bit0
            self._bit1 = bit1
            self._freq = bit0.freq + bit1.freq
            self._symbol = None
        else:
            self._symbol = symbol
            self._freq = freq
            self._bit0 = None
            self._bit1 = None

    @property
    def symbol(self):
        return self._symbol

    @property
    def freq(self):
        return self._freq

    @property
    def bit0(self):
        return self._bit0

    @property
    def bit1(self):
        return self._bit1

    def __lt__(self, other):
        return self.freq < other.freq

def compress_file(input_file_path, help_file_path, output_file_path, block_size):
    with open(input_file_path, 'rb') as input_file, open(help_file_path, 'wb') as output_file:
        while True:
            data = input_file.read(block_size)
            if not data:
                break
            last_column_bwt, s_index = bwt_compress(data)
            output_file.write(s_index.to_bytes(2, 'big'))
            mtf_data = mtf_compress(last_column_bwt)

            code_block = rle_compress(mtf_data)

            for count, symbol in code_block:
                write_variable_length_integer(output_file, count)
                output_file.write(bytes([symbol]))
    with open(help_file_path, 'rb') as input_file, open(output_file_path, 'wb') as output_file:
        data = input_file.read()
        arch = ha_compress(data)
        output_file.write(bytes(arch))

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

def mtf_compress(string):
    rezult = []
    T = list(range(256))
    for s in string:
        i = T.index(s)
        rezult.append(i)
        T = [T[i]] + T[:i] + T[i+1:]
    return rezult

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

def ha_compress(data):
    freqs = calculate_freqs(data)
    head = create_header(len(data), freqs)
    root = create_huffman_tree(freqs)
    codes = create_huffman_code(root)
    bits = compress(data, codes)

    return head + bytes(bits)

def calculate_freqs(data):
    freqs = {}
    for byte in data:
        if byte in freqs:
            freqs[byte] += 1
        else: freqs[byte] = 1
    normalize_freqs(freqs)
    return list(freqs.items())

def normalize_freqs(freqs):
    max_freq = max(freqs)
    if max_freq <= 255:
        return

    for j in range(256):
        if freqs[j] > 0:
            freqs[j] = 1 + freqs[j] * 255 // (max_freq + 1)

def create_header(data_length, freqs):
    head = bytearray()

    head.append(data_length & 0xFF)
    head.append((data_length >> 8) & 0xFF)
    head.append((data_length >> 16) & 0xFF)
    head.append((data_length >> 24) & 0xFF)

    count = len(freqs)

    head.append(count & 0xFF)
    head.append((count >> 8) & 0xFF)

    for symbol, frequency in freqs:
        head.append(symbol)
        if frequency <= 255:
            head.append(frequency)
        elif frequency <= 65535:
            head.append(255)
            head.extend(frequency.to_bytes(2, byteorder='little'))
        else:
            head.append(254)
            head.extend(frequency.to_bytes(4, byteorder='little'))

    return head

def create_huffman_tree(freqs):
    pq = PriorityQueue()

    for byte, frequency in freqs:
        pq.put((frequency, Node(symbol=byte, freq=frequency)))

    while pq.qsize() > 1:
        freq0, bit0 = pq.get()
        freq1, bit1 = pq.get()
        parent = Node(bit0=bit0, bit1=bit1)
        pq.put((parent.freq, parent))

    return pq.get()[1]

def create_huffman_code(root):
    codes = {}
    _next(root, codes, "")
    return codes

def _next(node, codes, code):
    if node.bit0 is None and node.bit1 is None:
        codes[node.symbol] = code
    else:
        if node.bit0 is not None:
            _next(node.bit0, codes, code + "0")
        if node.bit1 is not None:
            _next(node.bit1, codes, code + "1")

def compress(data, codes):
    bits = []
    summ = 0
    bit = 0
    for symbol in data:
        for c in codes[symbol]:
            if c == '1':
                summ |= (1 << bit)
            bit += 1
            if bit == 8:
                bits.append(summ)
                summ = 0
                bit = 0

    if bit > 1:
        bits.append(summ)
    return bits



def decompress_file(input_file_path, output_file_path):
    with open(input_file_path, 'rb') as input_file, open(output_file_path, 'wb') as output_file:
        compressed_data = input_file.read()
        decompressed_ha_data = ha_decompress(compressed_data)

        i = 0
        while i < len(decompressed_ha_data):
            s_index = int.from_bytes(decompressed_ha_data[i:i+2], 'big')
            i += 2

            rle_data = []
            while i < len(decompressed_ha_data):
                count, bytes_read = read_variable_length_integer(decompressed_ha_data[i:])
                i += bytes_read
                if count == 0:
                    break
                symbol = decompressed_ha_data[i]
                i += 1
                rle_data.append((count, symbol))

            decompressed_rle_block = rle_decompress(rle_data)
            decompressed_mtf_data = mtf_decompress(decompressed_rle_block)
            original_block = bwt_decompress(decompressed_mtf_data, s_index)
            output_file.write(original_block)

def ha_decompress(arch):
    data_length, start_index, freqs = parse_header(arch)
    root = create_huffman_tree(freqs)
    data = decompress(arch, start_index, data_length, root)
    return list(data)

def parse_header(arch):
    data_length = (arch[0] |
                   (arch[1] << 8) |
                   (arch[2] << 16) |
                   (arch[3] << 24))

    count = (arch[4] | (arch[5] << 8))
    index = 6
    freqs = {}

    for _ in range(count):
        symbol = arch[index]
        index += 1
        frequency_first_byte = arch[index]
        index += 1

        if frequency_first_byte == 255:
            frequency = int.from_bytes(arch[index:index + 2], byteorder='little')
            index += 2
        elif frequency_first_byte == 254:
            frequency = int.from_bytes(arch[index:index + 4], byteorder='little')
            index += 4
        else:
            frequency = frequency_first_byte

        freqs[symbol] = frequency
    start_index = index
    return data_length, start_index, list(freqs.items())

def decompress(arch, start_index, data_length, root):
    size = 0
    curr = root
    data = bytearray()

    if curr.bit0 is None and curr.bit1 is None:
        data.append(curr.symbol)
        return bytes(data)

    for j in range(start_index, len(arch)):
        for bit in range(8):
            if (arch[j] & (1 << bit)) == 0:
                curr = curr.bit0
            else:
                curr = curr.bit1

            if curr.bit0 is None and curr.bit1 is None:
                data.append(curr.symbol)
                size += 1
                curr = root
                if size == data_length:
                    return bytes(data)

    return bytes(data)

def read_variable_length_integer(data):
    value = 0
    shift = 0
    bytes_read = 0
    for byte in data:
        value |= (byte & 0x7F) << shift
        bytes_read += 1
        if byte & 0x80 == 0:
            break
        shift += 7
    return value, bytes_read

def rle_decompress(data):
    result = []
    for count, symbol in data:
        result.extend([symbol] * count)
    return result

def mtf_decompress(L):
    rezult = []
    T = list(range(256))
    for i in L:
        rezult.append(T[i])
        T = [T[i]] + T[:i] + T[i + 1:]

    return bytes(rezult)

def bwt_decompress(last_column_BWM, S_index):
    T = counting_sort_arg(last_column_BWM)
    j = S_index
    original_S = bytearray()
    for _ in range(len(last_column_BWM)):
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
    input_file = 'input.pmd'
    compressed_file = 'compressed.bwt_mtf_rle_ha'
    help_file = 'help.bwt_mtf_rle_ha'
    decompressed_file = 'decompressed.txt'
    block_size = 64


    compress_file(input_file, help_file, compressed_file, block_size)
    print(f"Файл '{input_file}' сжат в '{compressed_file}'.")

    # decompress_file(compressed_file, decompressed_file)
    # print(f"Файл '{compressed_file}' восстановлен в '{decompressed_file}'.")
    #
    #
    # ############################################ проверка на идентичность
    # import filecmp
    #
    #
    # def files_are_identical(file1, file2):
    #     return filecmp.cmp(file1, file2, shallow=False)
    #
    #
    # # Пример использования
    # file1 = 'input.txt'
    # file2 = 'decompressed.txt'
    #
    # if files_are_identical(file1, file2):
    #     print("Файлы идентичны.")
    # else:
    #     print("Файлы различаются.")