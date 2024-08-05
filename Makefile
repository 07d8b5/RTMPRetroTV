# Makefile for various ffmpeg and mpv commands

# Default variables for input and output files
INPUT ?= input.mp4
OUTPUT ?= output.mp4
PLAYLIST ?= playlist.txt
STREAM_URL ?= rtmp://172.17.0.3/live/test

VENV_DIR := venv
PYTHON := python3
PIP := $(VENV_DIR)/bin/pip

venv:
	@$(PYTHON) -m venv $(VENV_DIR)
	@echo "Virtual environment created in $(VENV_DIR)"

install: venv
	@$(PIP) install --upgrade pip
	@$(PIP) install -r requirements.txt
	@echo "Dependencies installed"

clean:
	@rm -rf $(VENV_DIR)
	@echo "Virtual environment removed"

run:
	python src/main.py

lint:
	ruff check src/
	ruff format src/

# NVIDIA hardware-accelerated conversion
convert_hw:
	ffmpeg -i $(INPUT) \
		-vf "scale=-1:480, pad=854:480:(ow-iw)/2:(oh-ih)/2, fps=30, format=nv12" \
		-c:v h264_nvenc -preset slow -rc:v vbr -cq:v 23 -b:v 2000k -maxrate 2500k -bufsize 5000k \
		-profile:v high -level:v 4.1 -movflags +faststart -pix_fmt yuv420p \
		-colorspace bt709 -color_primaries bt709 -color_trc bt709 \
		-c:a aac -b:a 128k -ar 48000 -ac 2 -af "volume=1.0" \
		-metadata title="Converted Video" -metadata author="Your Name" -metadata comment="This is a converted video." \
		-gpu 0 -f mp4 $(OUTPUT)

# Software-based conversion
convert_sw:
	ffmpeg -i $(INPUT) \
		-vf "scale=-1:480, pad=854:480:(ow-iw)/2:(oh-ih)/2, fps=30, format=nv12" \
		-c:v libx264 -preset slow -crf 23 -b:v 2000k -maxrate 2500k -bufsize 5000k \
		-profile:v high -level:v 4.1 -movflags +faststart -pix_fmt yuv420p \
		-colorspace bt709 -color_primaries bt709 -color_trc bt709 \
		-c:a aac -b:a 128k -ar 48000 -ac 2 -af "volume=1.0" \
		-metadata title="Converted Video" -metadata author="Your Name" -metadata comment="This is a converted video." \
		-f mp4 $(OUTPUT)

# Play stream with MPV
play_stream:
	mpv $(STREAM_URL) --video-sync=display-resample

# Stream to server
stream_to_server:
	ffmpeg -v verbose -re -f concat -safe 0 -i $(PLAYLIST) \
		-c:v libx264 -preset veryfast -maxrate 3000k -bufsize 10000k -pix_fmt yuv420p -g 60 \
		-c:a aac -b:a 256k -ar 48000 -f flv $(STREAM_URL) 2>&1 | grep --line-buffered 'Auto' >> log_file.log

.PHONY: venv install clean convert_hw convert_sw play_stream stream_to_server
