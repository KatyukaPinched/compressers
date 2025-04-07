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


def ha_compress_file(data_filename, arch_filename):
    with open(data_filename, 'rb') as data_file:
        data = data_file.read()
    if len(data) == 0: return 1
    arch = compress_bytes(data)
    with open(arch_filename, 'wb') as arch_file:
        arch_file.write(arch)

def compress_bytes(data):
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



def ha_decompress_file(arch_filename, output_filename):
    with open(arch_filename, 'rb') as arch_file:
        arch_data = arch_file.read()
    data = decompress_bytes(arch_data)
    with open(output_filename, 'wb') as output_file:
        output_file.write(data)

def decompress_bytes(arch):
    data_length, start_index, freqs = parse_header(arch)
    root = create_huffman_tree(freqs)
    data = decompress(arch, start_index, data_length, root)
    return data

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



if __name__ == "__main__":
    input_file = 'russian_text.txt'
    compressed_file = 'compressed.huf'
    decompressed_file = 'decompressed'

    ha_compress_file(input_file, compressed_file)
    print(f"Файл '{input_file}' сжат в '{compressed_file}'.")

    ha_decompress_file(compressed_file, decompressed_file)
    print(f"Файл '{compressed_file}' восстановлен в '{decompressed_file}'.")


    ################################################################ проверка на идентичность
    import filecmp


    def files_are_identical(file1, file2):
        return filecmp.cmp(file1, file2, shallow=False)

    file1 = 'russian_text.txt'
    file2 = 'decompressed'

    if files_are_identical(file1, file2):
        print("Файлы идентичны.")
    else:
        print("Файлы различаются.")
