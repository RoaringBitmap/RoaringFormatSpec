# test data

These bitmaps were generated from Java : 
https://github.com/RoaringBitmap/RoaringBitmap/blob/master/examples/SerializeToDiskExample.java

They were created by adding the following values:

```Java
        for (int k = 0; k < 100000; k+= 1000) {
            rb.add(k);
        }
        for (int k = 100000; k < 200000; ++k) {
            rb.add(3*k);
        }
        for (int k = 700000; k < 800000; ++k) {
            rb.add(k);
        }
```

That is, they contain all multiplies of 1000 in [0,100000), all multiplies of 3 in [100000,200000) and all values in [700000,800000).

There are two files:
-  bitmapwithoutruns.bin is the result of a serialization without run containers;
-  bitmapwithruns.bin is the result of a serialization with run containers.



