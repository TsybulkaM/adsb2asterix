
all: build

build-bin:
	poetry run pyinstaller --onefile scr/adsb2asterix/main.py