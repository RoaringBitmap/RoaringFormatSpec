all: roaringbitmap64.png roaringbitmap.png

roaringbitmap64.dot: roaringbitmap64.ksy roaringbitmap.ksy
	# Generate the Graphviz representation of the KSY file
	kaitai-struct-compiler --target graphviz --outdir .  roaringbitmap64.ksy

roaringbitmap64.png: roaringbitmap64.dot
	# Generate the PNG image from the Graphviz DOT file
	dot -Tpng -o roaringbitmap64.png roaringbitmap64.dot

roaringbitmap.png: roaringbitmap.dot
	# Generate the PNG image from the Graphviz DOT file
	dot -Tpng -o roaringbitmap.png roaringbitmap.dot

roaringbitmap.dot: roaringbitmap.ksy
	# Generate the Graphviz representation of the KSY file
	kaitai-struct-compiler --target graphviz --outdir .  roaringbitmap.ksy