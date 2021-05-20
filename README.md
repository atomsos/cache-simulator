# cache-simulator

This simulator is used for testing cache hit/miss, no data is stored actually.

## Usage
```bash
$ python ./simulator.py -h
usage: simulator.py [-h] Memory Cache Block Mapping REPLACE Write

Cache Simulator

positional arguments:
  Memory      Memory size, e.g. 16K
  Cache       Cache size, e.g. 16K
  Block       Block size, e.g. 4K
  Mapping     Cache mapping, e.g. 8-ways
  REPLACE     Cache policy, LRU,LFU,FIFO,RAND
  Write       Write policy, WB,WT

optional arguments:
```

## Supported commands

* read addr
* write addr data
* seqread start_addr size
* seqwrite start_addr size
* randread size
* randwrite size
* stats
  * show stats of cache, hit/miss
* clear
  * clear all cache

