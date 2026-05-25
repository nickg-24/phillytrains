# PhillyTrains — Pi Setup Guide

---

## 1. Flash the OS

Use **Raspberry Pi OS Lite (64-bit)** — the headless version without desktop.
Flash it with [Raspberry Pi Imager](https://www.raspberrypi.com/software/).

In the Imager's advanced settings (gear icon) before flashing:
- Set a **hostname** (e.g. `phillytrains`)
- Enable **SSH**
- Set a **username and password**
- Configure **Wi-Fi** if not using ethernet

After flashing, boot the Pi and SSH in:

```bash
ssh <your-username>@phillytrains.local
```

---

## 2. Clone the repo

Git is pre-installed on Pi OS:

```bash
git clone https://github.com/nickg-24/phillytrains.git ~/phillytrains
cd ~/phillytrains
```

---

## 3. Run the setup script

`setup.sh` automates everything from here:

```bash
bash setup.sh
```

It will:
1. Install build dependencies (`python3-dev`, `python3-venv`, `cython3`)
2. Disable the Pi audio driver (required — shared hardware with the matrix)
3. Create a virtual environment and install all Python dependencies
4. Install `rpi-rgb-led-matrix` via pip (compiles C++ — takes a few minutes)
5. Verify the import works
6. Install and enable the `phillytrains` systemd service

At the end it will prompt you to reboot if the audio change requires one.

---

## 4. Verify the hardware

After rebooting, run the smoke test:

```bash
sudo .venv/bin/python3 test_matrix.py
```

The matrix should light up **solid blue**. Press Ctrl+C to stop.

If nothing lights up:
- Check the ribbon cable and the 5V power supply connection to the matrix
- If it lights up but flickers, re-check that audio was disabled (Step 3 handles this, but verify with `grep audio /boot/firmware/config.txt`)
- If the matrix init fails, try changing `hardware_mapping` in `config.yaml` from `"adafruit-hat"` to `"adafruit-hat-pwm"`

---

## 5. Start the display

```bash
sudo systemctl start phillytrains
```

Check status and logs:

```bash
sudo systemctl status phillytrains
sudo journalctl -u phillytrains -f
```

The first run downloads GTFS data (~15 seconds before the first slide appears).

---

## 6. Pushing updates from your laptop

On your laptop:

```bash
git add -A && git commit -m "your message"
git push
```

On the Pi:

```bash
cd ~/phillytrains
git pull
sudo systemctl restart phillytrains
```

---

## Manual setup (reference)

If you prefer not to use `setup.sh`, here are the individual steps:

```bash
# Build deps
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3-dev python3-venv python3-pil cython3

# Disable audio — edit /boot/firmware/config.txt (Bookworm) or /boot/config.txt (Bullseye)
# Change: dtparam=audio=on  →  dtparam=audio=off
# Then reboot.

# Venv + deps
python3 -m venv .venv
.venv/bin/pip install --upgrade pip
.venv/bin/pip install -r requirements.txt
.venv/bin/pip install git+https://github.com/hzeller/rpi-rgb-led-matrix

# Verify
.venv/bin/python3 -c "from rgbmatrix import RGBMatrix; print('OK')"

# Systemd service: see setup.sh for the service file template
```
