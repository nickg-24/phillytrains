# PhillyTrains — Pi Setup Guide

Complete setup instructions for a fresh Raspberry Pi.

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

## 2. System update and build dependencies

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y git python3-dev python3-venv cython3
```

`cython3` is required to compile the LED matrix Python bindings.

---

## 3. Disable the audio driver

The Pi's PWM audio shares hardware with the LED matrix. If audio is enabled, the display will flicker or show garbage. Disable it permanently:

```bash
# On Raspberry Pi OS Bookworm (current):
sudo nano /boot/firmware/config.txt

# On older Bullseye:
sudo nano /boot/config.txt
```

Find the line `dtparam=audio=on` and change it to:

```
dtparam=audio=off
```

Save and reboot:

```bash
sudo reboot
```

---

## 4. Clone the repo

```bash
git clone https://github.com/nickgei123/phillytrains.git ~/phillytrains
cd ~/phillytrains
```

> Replace the URL with your actual GitHub repo URL.

---

## 5. Create a virtual environment and install dependencies

```bash
python3 -m venv .venv
.venv/bin/pip install --upgrade pip
.venv/bin/pip install -r requirements.txt
```

---

## 6. Install the LED matrix library

The rpi-rgb-led-matrix library is pip-installable. It compiles C++ code during install, so it takes a few minutes:

```bash
.venv/bin/pip install git+https://github.com/hzeller/rpi-rgb-led-matrix
```

Verify it installed:

```bash
.venv/bin/python3 -c "from rgbmatrix import RGBMatrix; print('OK')"
```

If you see `OK`, the library is ready.

---

## 7. Verify the matrix hardware

Run the hardware smoke test. This requires `sudo` because the matrix library needs GPIO access:

```bash
sudo .venv/bin/python3 test_matrix.py
```

The matrix should light up **solid blue** for a few seconds. Press Ctrl+C to stop.

If the matrix does not light up:
- Double-check the ribbon cable between the bonnet and the matrix
- Confirm the 5V power supply is plugged into the matrix (not just the Pi)
- Make sure `hardware_mapping: "adafruit-hat"` is correct in `config.yaml`
  - Some Adafruit bonnets need `"adafruit-hat-pwm"` instead — try that if the default doesn't work

---

## 8. Run the display

```bash
sudo .venv/bin/python3 main.py
```

The board will fetch live SEPTA data and begin the slideshow. First run downloads GTFS data (~10–15 seconds before the first slide appears).

To stop: **Ctrl+C**

---

## 9. Auto-start on boot (systemd)

1. Create the service file:

```bash
sudo nano /etc/systemd/system/phillytrains.service
```

2. Paste the following (replace `<your-username>` with your actual username):

```ini
[Unit]
Description=PhillyTrains LED Display
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=root
WorkingDirectory=/home/<your-username>/phillytrains
ExecStart=/home/<your-username>/phillytrains/.venv/bin/python3 -u /home/<your-username>/phillytrains/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

3. Enable and start it:

```bash
sudo systemctl daemon-reload
sudo systemctl enable phillytrains
sudo systemctl start phillytrains
```

4. Check status and live logs:

```bash
sudo systemctl status phillytrains
sudo journalctl -u phillytrains -f
```

---

## 10. Pushing updates from your laptop

On your laptop (WSL):

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

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| Display flickers or shows noise | Audio driver still enabled — revisit Step 3 |
| `OK` prints but test_matrix.py crashes | Try `hardware_mapping: "adafruit-hat-pwm"` in `config.yaml` |
| Display is dim | Increase `brightness` in `config.yaml` (0–100) |
| Slow first start | Normal — GTFS data is downloading. Subsequent starts are fast. |
| `No module named 'rgbmatrix'` | Run install command in Step 6 again; confirm you're using `.venv/bin/python3` |
| `Permission denied` on GPIO | Must run with `sudo .venv/bin/python3`, not plain `python3` |
