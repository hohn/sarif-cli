"""A simple 64-bit snowflake id implementation.

For merging and joining tables externally, the ids must be sufficiently unique.
At the same time, a full 20-byte uuid is excessive and likely slow in a database.
The trade off is using a snowflake id (see References), which is a 64 bit int with
bits allocated between time, a shard/process id, and a counter or random number.

This implementation uses a 42, 8, 15 bit split for (time, process, counter).  The
time is in milliseconds (ms) since unix epoch.

../notes/unique-ids.ipynb illustrates the values used here.


References:
    - https://www.ietf.org/id/draft-peabody-dispatch-new-uuid-format-02.html#name-informative-references
"""
import time

class Snowflake:
    ms_max = (1<<41) * 2
    process_id_max = 1<<8
    counter_max = 1 << 15    

    def __init__(self, process_id):
        assert(process_id < Snowflake.process_id_max)
        self._time_ms = int(time.time_ns() / 1e6)
        self._process_id = process_id
        self._counter = 0
        
    def next(self):
        if self._counter >= Snowflake.counter_max:
            while ((time_ms := int(time.time_ns() / 1e6)) <= self._time_ms):
                pass            # TODO: profile this; should be few loops if any 
            self._time_ms = time_ms
            self._counter = 0

        flake = (self._time_ms << (23) |
                 self._process_id << (15) |
                 self._counter)
        self._counter += 1

        return flake

if __name__ == '__main__':
    # Test lower bits and counter wrapping
    fgen = Snowflake(0)
    for _ in range(0,4):
        fl = fgen.next()
        print(f"counter: {fl & (1<<15)-1:d}  id: {(fl>>15) & (1<<8)-1:d} time_ms: {(fl>>23):d}")
        print(f"{(fl >> 23):_b}")
    print("----")
    for _ in range(0, Snowflake.counter_max):
        fgen.next()
    for _ in range(0,4):
        fl = fgen.next()
        print(f"counter: {fl & (1<<15)-1:d}  id: {(fl>>15) & (1<<8)-1:d} time_ms: {(fl>>23):d}")
        print(f"{(fl >> 23):_b}")
    print("----")
    # simple loop time
    time_start = fgen.next() >> 23
    for _ in range(0, Snowflake.counter_max):
        fgen.next()
    delta = (fgen.next() >> 23) - time_start
    print(f"time delta in ms, one counter cycle: {delta:d}")
