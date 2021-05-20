import argparse
import re
import readline
import random

Cache_replacement_policy = ['LRU', 'LFU', 'FIFO', 'RAND']
Write_policies = ['WB', 'WT']


def get_size(size):
    if isinstance(size, int):
        number = size
    elif isinstance(size, str):
        size = size.upper()
        if size[-1] not in ['B', 'K', 'M', 'G']:
            raise ValueError('Invalid size, should be number + B/K/M/G')
        number = int(size[:-1])
        value = 1024
        for k in ['B', 'K', 'M', 'G']:
            if k == size[-1]:
                break
            number *= value
    return number


class Cache:
    def __init__(self, size, block, mapping, replace, write_policy, memory):
        self.size = get_size(size)          # 8KiB
        self.block_size = get_size(block)   # 64B
        self.block = self.size // self.block_size  # 128 blocks
        if self.size % self.block_size != 0:
            raise ValueError('Cache size must be multiple of block size')
        self.mapping = int(mapping)  # 8-ways associated, so 128/8 = 16 sets
        self.sets = self.block // self.mapping

        self.replace = replace
        self.write_policy = write_policy
        self.memory = memory
        # self.data = [0] * self.size
        self.index = []
        self.dirty = []
        self.usage = []
        for _ in range(self.sets):
            self.index.append(list([None] * self.mapping))
            self.dirty.append(list([0] * self.mapping))
            self.usage.append(list([0] * self.mapping))
        self.hit = 0
        self.miss = 0

    def replace_with(self, _id):
        s = _id % self.sets
        if self.replace == 'LRU':
            usage = self.usage[s]
            empty_id = usage.index(max(usage))
        elif self.replace == 'LFU':
            usage = self.usage[s]
            empty_id = usage.index(min(usage))

        elif self.replace == 'FIFO':
            self.index[s] = self.index[s][1:] + [_id]
            empty_id = self.mapping
        elif self.replace == 'RANDOM':
            empty_id = random.randint(0, self.mapping)
            self.index[s][empty_id] = _id
        # clear dirty
        if self.dirty[s][empty_id] == 1:
            self.memory.write(self.index[s][empty_id], 0)
            self.dirty[s][empty_id] = 0

        return empty_id

    def add_cache(self, _id):
        s = _id % self.sets
        try:
            empty_id = self.index[s].index(None)
        except:  # no None
            # replacement
            empty_id = self.replace_with(_id)
        self.index[s][empty_id] = _id
        return s, empty_id

    def update_usage(self, s, usage_id):
        # s = _id % self.sets
        # idx = self.index[s].index(_id)
        usage = self.usage[s]
        if self.replace == 'LFU':
            # self.
            self.usage[s][usage_id] += 1
        elif self.replace == 'LRU':
            self.usage[s] = list(map(lambda x: x+1, usage))
            self.usage[s][usage_id] = 0

    def write(self, address, data):
        _id = address // self.block_size
        s = _id % self.sets
        if _id in self.index[s]:
            self.hit += 1
            empty_id = self.index[s].index(_id)
        else:
            self.miss += 1
            try:
                empty_id = self.index[s].index(None)
                self.index[s][empty_id] = _id
            except:
                s, empty_id = self.add_cache(_id)
            if self.write_policy == 'WT':
                self.memory.write(address, data)
            elif self.write_policy == 'WB':
                self.dirty[s][empty_id] = 1

        usage_id = empty_id
        self.update_usage(s, usage_id)
        # import pdb; pdb.set_trace()

    def read(self, address):
        _id = address // self.block_size
        s = _id % self.sets
        if _id in self.index[s]:
            # hit
            self.hit += 1
            usage_id = self.index[s].index(_id)
        else:
            # import pdb; pdb.set_trace()
            self.memory.read(_id)
            # print("_id", _id)
            s, usage_id = self.add_cache(_id)
            # miss
            self.miss += 1
            # print("Miss", s, "Use", usage_id)
        self.update_usage(s, usage_id)
        return 0


class Memory:
    def __init__(self, size, block):
        self.size = get_size(size)
        self.block = get_size(block)
        # self.data = [0] * self.size
        self.write_num = 0
        self.read_num = 0

    def write(self, data, address):
        # self.data[address] = data
        self.write_num += 1

    def read(self, address):
        # return self.data[address]
        self.read_num += 1


def read(params, memory, cache):
    address = int(params[0])
    data = cache.read(address)
    print("read {}".format(hex(address)))


def write(params, memory, cache):
    address = int(params[0])
    data = int(params[1])
    cache.write(address, data)
    print("write {} to {}".format(data, hex(address)))


def randread(params, memory, cache):
    import random
    num = int(params[0])
    max_address = memory.size - 1
    for _ in range(num):
        addr = random.randint(0, max_address)
        # print(addr, addr // cache.block_size, cache.index, cache.usage)
        cache.read(addr)


def randwrite(params, memory, cache):
    import random
    num = int(params[0])
    max_address = memory.size - 1
    for _ in range(num):
        addr = random.randint(0, max_address)
        cache.write(addr, 0)


def seqread(params, memory, cache):
    start_addr = int(params[0])
    size = int(params[1])
    for _ in range(size):
        cache.read(start_addr + _)


def seqwrite(params, memory, cache):
    # import pdb; pdb.set_trace()
    start_addr = int(params[0])
    size = int(params[1])
    for _ in range(size):
        cache.write(start_addr + _, 0)


def setbreak(cache, memory):
    import pdb
    pdb.set_trace()


def print_stats(memory, cache):
    print("Cache hit: {}, miss: {}, miss rate: {}".format(
        cache.hit, cache.miss, cache.miss / (cache.hit+cache.miss)))


def get_args():
    parser = argparse.ArgumentParser(description='Cache Simulator')
    parser.add_argument('Memory', type=str,
                        help='Memory size, e.g. 16K')
    parser.add_argument('Cache', type=str,
                        help='Cache size, e.g. 16K')
    parser.add_argument('Block', type=str,
                        help='Block size, e.g. 4K')
    parser.add_argument('Mapping', type=int,
                        help='Cache mapping, e.g. 8-ways')
    parser.add_argument('REPLACE', metavar='REPLACE', type=str, choices=Cache_replacement_policy,
                        help='Cache policy, ' + ','.join(Cache_replacement_policy))
    parser.add_argument('Write', type=str, choices=Write_policies,
                        help='Write policy, ' + ','.join(Write_policies))
    args = parser.parse_args()
    return args


def parse_command(command):
    command = command.lower().strip().split()
    command, params = command[0], command[1:]
    if command not in ["read", "write",
                       "randread", "randwrite",
                       "seqread", "seqwrite",
                       #    "printcaches", "printmem",
                       "stats", "clear", "setbreak", "quit"]:
        raise ValueError
    params = list(map(int, params))
    return command, params


def init_cache_memory(args):
    memory = Memory(args.Memory, args.Block)
    cache = Cache(args.Cache, args.Block, args.Mapping,
                  args.REPLACE, args.Write, memory)
    return cache, memory


def start_simulation(args):
    cache, memory = init_cache_memory(args)
    command = None
    history = []
    while command != 'quit':
        # history.append(command)
        # try:
        command = input('> ')
        cmd, params = parse_command(command)
        if cmd == 'read':
            read(params, memory, cache)
        elif cmd == 'write':
            write(params, memory, cache)
        elif cmd == 'randread':
            randread(params, memory, cache)
            print_stats(memory, cache)
        elif cmd == 'randwrite':
            randwrite(params, memory, cache)
            print_stats(memory, cache)
        elif cmd == 'seqread':
            seqread(params, memory, cache)
            print_stats(memory, cache)
        elif cmd == 'seqwrite':
            seqwrite(params, memory, cache)
            print_stats(memory, cache)
        elif cmd == 'setbreak':
            setbreak(cache, memory)
        elif cmd == 'stats':
            print_stats(memory, cache)
        elif cmd == 'clear':
            cache, memory = init_cache_memory(args)
            print("Clear")
        elif cmd == 'quit':
            break
        # except IndexError:
        #     print('Error: out of bounds')
        # except Exception as e:
        #     print('Syntax error')


def main():
    args = get_args()
    start_simulation(args)


if __name__ == '__main__':
    main()
