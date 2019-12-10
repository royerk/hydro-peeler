"""Read binary"""
from datetime import datetime


def header_from_file(filename, header_size=400):
    """Read n first bytes of the file, decode to ASCII and return list of lines."""
    characters_list = []
    with open(filename, 'rb') as f:
        count_bytes = 0
        while count_bytes < header_size:
            characters_list.append(f.read(1).decode("ascii"))  # read one byte at a time and decode it
            count_bytes += 1

    return ''.join(characters_list).split('\n')


def bytes_to_int(b):
    """Read bytes to int (with big endian)."""
    result = int.from_bytes(b, 'big')
    if result > 2**23 - 1:
        result += - 2**24
    return result


def bytes_from_file(filename, chunksize, skip=0, start_read=0, max_read=None):
    """Read binary by chuncksize of bytesm can do partial reading"""

    if start_read > 0 and (start_read - skip) % chunksize != 0:
        print("Start position is not aligned with a multiple of chuncksize.")  # todo raise custom error
        return None

    result = []
    with open(filename, "rb") as f:
        f.seek(skip + start_read)  # skip at least the header
        count = 0
        while True:  # not the most elegant but allows easy partial read
            chunck = f.read(chunksize)
            if chunck:
                result.append(bytes_to_int(chunck))
            else:
                break

            count += 1
            if max_read and count >= max_read:
                break

    return result


def parse_header(header_lines=None, path_file=None, header_size=400):
    """Extract data from header, either from text or from file."""

    if header_lines is None and path_file is None:
        print('Provide either lines or path to file...')
        return None

    if header_lines is None:
        print('Extracting from {}, header size: {}'.format(path_file, header_size))
        header_lines = header_from_file(path_file, header_size)

    header_data = {}

    for line in header_lines:  # todo first 2 lines (+detect revisited/date)
        words = line.strip().split()
        first_word = words[0]
        if first_word == 'Cruise':
            header_data[first_word] = words[1]
        if first_word == 'Site':
            header_data[first_word] = words[1]
        if first_word == 'Header':
            header_data[first_word] = int(words[1])
        if first_word == 'SpleFreq':
            header_data[first_word] = float(words[1])
            header_data['gain'] = float(words[5])
        if first_word == 'SpleFmt':
            header_data[first_word] = int(words[1])
        if first_word == 'Sple/file':
            header_data[first_word] = int(words[1])
        if first_word == 'GPS':
            if words[1] == 'Clkbrd':
                header_data['zero_day'] = int(words[3])
                header_data['zero_date'] = datetime.strptime(' '.join(words[4:]), '%b %d %H:%M:%S %Y')  # Feb 07 03:58:52 2014
            if words[1] == '1st':
                header_data['first_int_index'] = int(words[3])
                header_data['firt_int_day'] = int(words[4])
                header_data['first_int_date'] = datetime.strptime(' '.join(words[5:]), '%b %d %H:%M:%S %Y')  # Feb 07 03:58:52 2014
            if words[1] == 'Filestart':
                header_data['file_start_day'] = int(words[2])
                header_data['file_start_date'] = datetime.strptime(' '.join(words[3:]), '%b %d %H:%M:%S %Y')  # Feb 07 03:58:52 2014
        if first_word == 'Cycle:':
            header_data['Cycle'] = int(words[1])
            header_data['Cycle_sample'] = int(words[3])
            header_data['200days'] = int(words[-1])

    return header_data
 