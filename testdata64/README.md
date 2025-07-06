# test data for 64-bit Roaring Bitmap files

There is no standard 64-bit Roaring format. There are 
several implementations with different trade-offs.

However, we offer a possible implementation that is simply a 
series of standard Roaring bitmapss.


On a little-endian system, we generated `bitmap64.bin` with the following
C++ program.
```Cpp
    Roaring64Map bitmap;

    // Step 1: Set one out of every two values in [0, 2^16)
    for (uint64_t i = 0; i < 65536; i += 2) {
        bitmap.add(i);
    }

    // Step 2: Set all values in [2^32, 2^32 + 1,000,000)
    uint64_t start = 1ULL << 32;
    uint64_t end = start + 1000000;
    bitmap.addRange(start, end);

    // Step 3: Set the value 2^48
    bitmap.add(1ULL << 48);

    // Serialize the bitmap
    size_t buffer_size = bitmap.getSizeInBytes(true);
    std::vector<char> buffer(buffer_size);
    bitmap.write(buffer.data(), true);

    // Save to file
    std::ofstream out_file("bitmap64.bin", std::ios::binary);
```

This should create the following data structure:

- A roaring bitmap with key 0 having a single container (bitset). The key is written at byte index 8.
- A roaring bitmap with key 1 having 16 containers, all run containers.  The key is written at byte index 8220.
- A roaring bitmap with key 65536 having a single container, an array container. The key is written at byte index 8454