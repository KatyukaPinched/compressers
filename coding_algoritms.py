import heapq
from heapq import heappop, heappush

def isLeaf(root):
    return root.left is None and root.right is None

class Node:
    def __init__(self, ch, freq, left=None, right=None):
        self.ch = ch
        self.freq = freq
        self.left = left
        self.right = right

    def __lt__(self, other):
        return self.freq < other.freq

def encode(root, s, huffman_code):
    if root is None:
        return

    if isLeaf(root):
        huffman_code[root.ch] = s if len(s) > 0 else '1'

    encode(root.left, s + '0', huffman_code)
    encode(root.right, s + '1', huffman_code)

def decode(root, index, s):
    if root is None:
        return index

    if isLeaf(root):
        print(root.ch, end='')
        return index

    index = index + 1
    root = root.left if s[index] == '0' else root.right
    return decode(root, index, s)

def Huffman(text):
    if len(text) == 0:
        return

    freq = {i: text.count(i) for i in set(text)} # создали словарь с символами и их частотами

    pq = [Node(k, v) for k, v in freq.items()] # создание приоритетной очереди для активных узлов дерева
    heapq.heapify(pq) # преобразует очередь в кучу, где каждый родительский узел меньше своих дочерних узлов

    while len(pq) != 1:

        left = heappop(pq)
        right = heappop(pq)

        total = left.freq + right.freq
        heappush(pq, Node(None, total, left, right))

    root = pq[0]

    # проходит по дереву Хаффмана и сохраняет коды Хаффмана в словаре
    huffmanCode = {}
    encode(root, '', huffmanCode)

    for key, value in huffmanCode.items():
        print(f"{key} : {freq[key]} — {value}")

    s = ''
    for c in text:
        s += huffmanCode.get(c)

    print(s)

    if isLeaf(root):
        while root.freq > 0:
            print(root.ch)
            root.freq = root.freq - 1
    else:
        index = -1
        while index < len(s) - 1:
            index = decode(root, index, s)





# реализация преобразования Барроуза-Уилера по последнему столбцу и номеру строке
def BWT(S):
    N = len(S)
    BWM = [S[i:] + S[0:i] for i in range(N)] # получили все строки со сдвигами
    BWM.sort()
    last_column_BWM = "".join([BWM[i][-1] for i in range(N)]) # взяли последний столбец
    S_index = BWM.index(S) # зафиксировали индекс расположения оригинального слова

    return last_column_BWM, S_index

# декодирование с помощью восстановления всех перестановок
def iBWT(last_column_BWM, S_index): # T(n) = O(n^2*logn) S(n) = O(n^2)
    N = len(last_column_BWM)
    BWM = ["" for _ in range(N)]
    for _ in range(N): # прописываем все слова снова и сортируем
        for j in range(N):
            BWM[j] = last_column_BWM[j] + BWM[j]
        BWM.sort()
    S = BWM[S_index]
    return S

# декодирование с помощью вектора обратного преобразования
def better_iBWT(last_column_BWM, S_index):
    N = len(last_column_BWM)
    T = counting_sort_arg(last_column_BWM)
    S = ""
    j = S_index
    for _ in range(N):
        j = T[j]
        S += last_column_BWM[j]
    return S

def counting_sort_arg(S):

    P = [0 for _ in range(128)] # количество вхождений каждого символа
    for s in S:
        P[ord(s)] += 1

    T_sub = [0 for _ in range(128)] # индексы, с которых начинаются последовательности повторяющихся символов
    for j in range(1, 128):
        T_sub[j] = T_sub[j-1] + P[j-1]

    T = [-1 for _ in range(len(S))] # индексы оригинальных символов в отсортированном массиве
    for i in range(len(S)):
        T[T_sub[ord(S[i])]] = i
        T_sub[ord(S[i])] +=1
    return T





def MTF(S):
    T = [chr(i) for i in range(128)]
    T_str = "".join(T)
    L = []
    for s in S:
        i = T_str.index(s)
        L.append(i)
        T_str = T_str[i] + T_str[:i] + T_str[i+1:]
    return L

def iMTF(L):
    T = [chr(i) for i in range(128)]
    T_str = "".join(T)
    S_new = ""
    for i in L:
        S_new += T_str[i]
        T_str = T_str[i] + T_str[:i] + T_str[i + 1:]
    return S_new





def RLE(sequence):
    count = 1
    result = []

    for x, item in enumerate(sequence):
        if x == 0:
            continue
        elif item == sequence[x - 1]:
            count += 1
        else:
            result.append((count, sequence[x - 1]))
            count = 1

    result.append((count, sequence[len(sequence) - 1]))

    return result

def iRLE(sequence):
    result = ""

    for item in sequence:
        result += item[0] * item[1]

    return result





def LZ77(S):
    buffer_size = 5
    coding_list = []
    N = len(S)
    i = 0

    while i < N:

        buffer = S[max(0, i - buffer_size):i]
        max_length = 0
        offset = 0

        for j in range(len(buffer)):
            length = 0
            while (i + length < N and
                   j + length < len(buffer) and
                   buffer[j + length] == S[i + length]):
                length += 1

            if length > max_length:
                max_length = length
                offset = len(buffer) - j

        next_char = S[i + max_length] if (i + max_length < N) else ''

        coding_list.append((offset, max_length, next_char))

        i += max_length + 1 if next_char != '' else max_length

    return coding_list


def iLZ77(coding_list):
    decoded_string = ""

    for offset, length, next_char in coding_list:
        start_index = len(decoded_string) - offset
        decoded_string += decoded_string[start_index:start_index + length]
        if next_char != '':
            decoded_string += next_char

    return decoded_string





def LZ78(S):
    dictionary = ["∅"]
    code = []
    i = 0

    while i < len(S):
        save_word_new = S[i]
        flag_local = False
        save_k = 0

        for j in range(len(dictionary)):
            k = 0
            flag = False

            if S[i] == dictionary[j][0]:
                k = 0
                word_new = ""
                while k < len(dictionary[j]) and i < len(S):
                    if dictionary[j][k] == S[i]:
                        word_new += S[i]
                        flag = True
                    elif dictionary[j][k] != S[i]:
                        flag = False
                        i -= k
                        break
                    k += 1
                    i += 1
            if flag and len(save_word_new) <= len(word_new):
                flag_local = True
                save_word_new = word_new
                save_k = k
                if j - 1 != len(dictionary):
                    i -= k

        if i + save_k < len(S): i += save_k
        else: flag_local = False

        if flag_local:
            dictionary.append(save_word_new + S[i])
            code.append((dictionary.index(save_word_new), S[i]))
        elif len(dictionary) == 0:
            dictionary.append(S[i])
            code.append((0, S[i]))
        else:
            if save_word_new not in dictionary: dictionary.append(save_word_new)
            if i + save_k < len(S): code.append((0, S[i]))
            else: code.append((dictionary.index(save_word_new), ""))

        i += 1
    return dictionary, code

def iLZ78(code):
    dictionary = ["∅"]
    rezult = ""

    for num, val in code:
        if num == 0:
            dictionary.append(val)
            rezult += val
        else:
            dictionary.append(dictionary[num] + val)
            rezult += dictionary[num] + val
    return rezult