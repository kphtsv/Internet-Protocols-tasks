import struct

HEADER_FORMAT = '! 6H '


def get_bits(source: int, pointer: int, length=1):
    return (source >> ((pointer - length) + 1)) & ((1 << length) - 1)


def join_bytes(arr: bytearray):
    result = 0
    for i in range(len(arr)):
        result = (result << 8) + arr[i]
    return result


def read_mark(packet: bytearray, position: int):
    current_byte_pointer = position - 1
    first = packet[current_byte_pointer]
    indicator = get_bits(first, 7, 2)
    tail = get_bits(first, 5, 6)

    if indicator == 0:
        mark_length = tail
        next_pointer = current_byte_pointer + 1 + mark_length
        mark = packet[current_byte_pointer + 1:next_pointer]
        return mark, next_pointer + 1  # в С.О. с 1
    elif indicator == 3:
        second = packet[current_byte_pointer + 1]
        mark_position = (tail << 8) + second  # в отсчёте с единицы
        mark, _ = read_mark(packet, mark_position)
        return mark, current_byte_pointer + 2 + 1  # в С.О. с 1


def decode_marks(packet: bytearray, start_position: int):  # в С.О. с единицы
    current_pointer = start_position - 1
    marks = []
    while packet[current_pointer] != 0:  # последовательность марок кончается байтом с нулём
        mark, next_position = read_mark(packet, current_pointer + 1)
        marks.append(mark.decode('ascii'))
        current_pointer = next_position - 1
    return marks, current_pointer + 1


def decode_resource_record(packet: bytearray, start_position: int):
    marks, next_position = decode_marks(packet, start_position)
    current_pointer = next_position - 1
    r_type = join_bytes(packet[current_pointer:current_pointer + 2])
    current_pointer += 2
    r_class = join_bytes(packet[current_pointer:current_pointer + 2])
    current_pointer += 2
    r_ttl = join_bytes(packet[current_pointer:current_pointer + 4])
    current_pointer += 4
    r_data_length = join_bytes(packet[current_pointer:current_pointer + 2])
    current_pointer += 2
    r_data = packet[current_pointer:current_pointer + r_data_length]
    current_pointer += r_data_length

    data = {
        'type': r_type,
        'class': r_class,
        'ttl': r_ttl,
        'rd_length': r_data_length,
        'r_data': r_data
    }

    return data, current_pointer + 1


class Packet:
    def __init__(self, data):
        # ---- HEADER ----
        self.id = 0
        self.qr = 0  # question or response
        self.opcode = 0  # тип запроса
        self.aa = 0  # autoritative answer
        self.tc = 0  # trimmed content
        self.rd = 0  # recursion desired
        self.ra = 0  # recursion allowed
        self.z = 0  # Zарезервировано
        self.rcode = 0  # response code

        self.qd_count = 0  # кол-во question записей
        self.an_count = 0  # кол-во записей ответов
        self.ns_count = 0  # количество записей в Authority Section
        self.ar_count = 0  # количество записей в Additional Record Section

        self.questions = []
        self.answers = []
        self.authority_records = []
        self.additional_records = []

        if data:
            self.rewrite_from_data(data)

    def rewrite_header_from_data(self, header_data: bytes):
        try:
            unpacked = struct.unpack(HEADER_FORMAT, header_data[0:struct.calcsize(HEADER_FORMAT)])
        except struct.error:
            raise Exception('Unable to unpack data.')

        self.id = unpacked[0]
        self.qr = get_bits(unpacked[1], 15, 1)
        self.opcode = get_bits(unpacked[1], 14, 4)
        self.aa = get_bits(unpacked[1], 10, 1)
        self.tc = get_bits(unpacked[1], 9, 1)
        self.rd = get_bits(unpacked[1], 8, 1)
        self.ra = get_bits(unpacked[1], 7, 1)
        self.z = get_bits(unpacked[1], 6, 3)
        self.rcode = get_bits(unpacked[1], 3, 4)
        self.qd_count = unpacked[2]
        self.an_count = unpacked[3]
        self.ns_count = unpacked[4]
        self.ar_count = unpacked[5]

    def rewrite_from_data(self, data: bytes):
        if len(data) < 12:
            raise Exception('Data not long enough to unpack.')

        # header
        packet = bytearray(data)  # TODO возможно, преобразования в массив не нужно для обр. по инд.
        self.rewrite_header_from_data(bytes(packet[0:12]))
        next_pointer = 12

        questions = []
        for i in range(self.qd_count):
            q_marks, next_pointer = decode_marks(packet, next_pointer)
            next_pointer -= 1

            q_type = join_bytes(packet[next_pointer:next_pointer + 2])
            q_class = join_bytes(packet[next_pointer + 2:next_pointer + 4])
            next_pointer += 4

            question = {
                'q_marks': q_marks,
                'q_type': q_type,
                'q_class': q_class
            }
            questions.append(question)
        self.questions = questions

        answers = []
        for i in range(self.an_count):
            answer, next_pointer = decode_resource_record(packet, next_pointer + 1)
            next_pointer -= 1
            answers.append(answer)
        self.answers = answers

        authority_records = []
        for i in range(self.an_count):
            auth_rec, next_pointer = decode_resource_record(packet, next_pointer + 1)
            next_pointer -= 1
            authority_records.append(auth_rec)
        self.authority_records = authority_records

        additional_records = []
        for i in range(self.an_count):
            add_rec, next_pointer = decode_resource_record(packet, next_pointer + 1)
            next_pointer -= 1
            additional_records.append(add_rec)
        self.additional_records = additional_records

    def collect_to_data(self):
        count_bytes_written = 0

        second_row = self.qr << 15 + self.opcode << 11 + self.aa << 10 + self.tc << 9 + self.rd << 8 + self.ra << 7 + \
                     self.rcode
        try:
            header = struct.pack(HEADER_FORMAT,
                                 self.id,
                                 second_row,
                                 self.qd_count,
                                 self.an_count,
                                 self.ns_count,
                                 self.ar_count)
        except struct.error:
            raise Exception('Invalid data for DNS header packet fields.')
        count_bytes_written += 12

        marks_used = {}  # словарь bytes -> position

        for i in range(len(self.questions)):
            question = self.questions[i]
            q_marks = question['q_marks']  # список bytearray-ев
            q_type = question['q_type']  # int
            q_class = question['q_class']  # int

            for mark in q_marks:
                bytes_mark = b''
                if mark in marks_used:
                    position = marks_used[mark]
                    # TODO надо их как-то записать 
                    indicator = 3
                    tail = get_bits(position, 13, 6)

                    second_half = get_bits(position, 7, 8)
                else:


