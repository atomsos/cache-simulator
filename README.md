# cache-simulator

This simulator is used for testing cache hit/miss, no data is stored actually.

https://github.com/jaminthorns/cpu-cache-simulator for reference

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
  * read data from addr
* write addr data
  * write data to addr
* seqread start_addr size
  * sequential read from start_addr with size 
* seqwrite start_addr size
  * sequential write to start_addr with size
* randread size
  * random read size of data
* randwrite size
  * random write size of data
* stats
  * show stats of cache, hit/miss
* clear
  * clear all cache

