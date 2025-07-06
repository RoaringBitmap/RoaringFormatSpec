# test data for 64-bit Roaring Bitmap files

There is no standard 64-bit Roaring format. There are 
several implementations with different trade-offs.

However, we offer a possible implementation that is simply a 
series of standard Roaring bitmapss.

## `bitmap64.bin`

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

## `portable_bitmap64.bin`

In a similar spirit, we created `portable_bitmap64.bin` from the following C program.
It should be made of three buckets with indexes 0, 1, 2. Within each 'bucket', we should
have the same content, a Roaring bitmap with run containers, bitset containers and array containers.

```c
#include <assert.h>
#include <roaring.h>
#include <stdint.h>
#include <stdio.h>

void write_file(const char *path, const char *contents, size_t len) {
    FILE *f = fopen(path, "wb");
    assert(f != NULL);
    size_t n = fwrite(contents, 1, len, f);
    assert(n == len);
    fclose(f);
}

void write_frozen(const roaring_bitmap_t *b) {
    size_t size = roaring_bitmap_frozen_size_in_bytes(b);
    char *data = roaring_malloc(size);
    roaring_bitmap_frozen_serialize(b, data);
    write_file("frozen_bitmap.bin", data, size);
    roaring_free(data);
}

void write_portable(const roaring_bitmap_t *b) {
    size_t size = roaring_bitmap_portable_size_in_bytes(b);
    char *data = roaring_malloc(size);
    roaring_bitmap_portable_serialize(b, data);
    write_file("portable_bitmap.bin", data, size);
    roaring_free(data);
}

void write_native(const roaring_bitmap_t *b) {
    size_t size = roaring_bitmap_size_in_bytes(b);
    char *data = roaring_malloc(size);
    roaring_bitmap_serialize(b, data);
    write_file("native_bitmap.bin", data, size);
    roaring_free(data);
}

void write_portable64(const roaring64_bitmap_t *b) {
    size_t size = roaring64_bitmap_portable_size_in_bytes(b);
    char *data = roaring_malloc(size);
    roaring64_bitmap_portable_serialize(b, data);
    write_file("portable_bitmap64.bin", data, size);
    roaring_free(data);
}

roaring_bitmap_t *make_bitmap(void) {
    int i;

    roaring_bitmap_t *b = roaring_bitmap_create();
    // Range container
    roaring_bitmap_add_range(b, 0x00000, 0x09000);
    roaring_bitmap_add_range(b, 0x0A000, 0x10000);
    // Array container
    roaring_bitmap_add(b, 0x20000);
    roaring_bitmap_add(b, 0x20005);
    // Bitmap container
    for (i = 0; i < 0x10000; i += 2) {
      roaring_bitmap_add(b, 0x80000 + i);
    }

    roaring_bitmap_run_optimize(b);

    return b;
}

roaring64_bitmap_t *make_bitmap64(void) {
    int i;
    int j;
    uint64_t base;

    roaring64_bitmap_t *b = roaring64_bitmap_create();

    for (i = 0; i < 2; ++i) {
        base = (uint64_t)i << 32;
        // Range container
        roaring64_bitmap_add_range_closed(b, base | 0x00000, base | 0x09000);
        roaring64_bitmap_add_range_closed(b, base | 0x0A000, base | 0x10000);
        // Array container
        roaring64_bitmap_add(b, base | 0x20000);
        roaring64_bitmap_add(b, base | 0x20005);
        // Bitmap container
        for (j = 0; j < 0x10000; j += 2) {
          roaring64_bitmap_add(b, base | 0x80000 + j);
        }
    }

    roaring64_bitmap_run_optimize(b);

    return b;
}

int main(void) {
    roaring_bitmap_t *b = make_bitmap();
    write_frozen(b);
    write_portable(b);
    write_native(b);
    roaring_bitmap_free(b);

    roaring64_bitmap_t *b64 = make_bitmap64();
    write_portable64(b64);
    roaring64_bitmap_free(b64);
}
```