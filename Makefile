all: main

clean:
	rm voice
	rm *.pyc

main: voice.c
	export PKG_CONFIG_PATH=/users/ssalbiz/dev/sphinxbase/usr/local/lib/pkgconfig
	echo pkg-config --cflags --libs pocketspinx sphinxbase
	gcc -o voice voice.c \
      -DMODELDIR=\"`pkg-config --variable=modeldir pocketsphinx`\" \
      `pkg-config --cflags --libs pocketsphinx sphinxbase`
