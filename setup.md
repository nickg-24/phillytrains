# Train Board Setup

Steps to prepare a Raspberry Pi for running the train board project.
The Pi is treated as a single-purpose system, so everything is installed system-wide.

---

## 1. Install system packages

Update apt and install the required build tools:

```bash
sudo apt update
sudo apt upgrade
sudo apt install -y git python3-dev python3-pip python3-pillow make g++
```

---

## 2. Install Python packages

Raspberry Pi OS blocks system-wide pip installs by default.
Use the `--break-system-packages` flag:

```bash
pip3 install --upgrade pip setuptools wheel --break-system-packages
pip3 install -r requirements.txt --break-system-packages
```

`requirements.txt` includes:

```
requests
protobuf
gtfs-realtime-bindings
pyyaml
Pillow
```

---

## 3. Install the LED matrix library

Clone the hzeller repo and build the Python bindings:

```bash
git clone https://github.com/hzeller/rpi-rgb-led-matrix
cd rpi-rgb-led-matrix/bindings/python
make build-python
sudo make install-python
```

Verify installation:

```bash
python3 -c "from rgbmatrix import RGBMatrix; print('OK')"
```

If `OK` is printed, the bindings installed correctly.

---

## 4. Project setup

Clone or copy the train board project to your Pi, then edit `config.yaml` with your station and display settings:

```yaml
origin: "Conshohocken"
destination: "Suburban Station"
n: 2
debug: 1
refresh_interval: 120   # seconds between data refreshes

matrix:
  rows: 64
  cols: 64
  chain_length: 1
  parallel: 1
  hardware_mapping: "adafruit-hat"
  brightness: 60

display:
  logo: 5
  train: 10
  alert: 10
```

**Notes:**

* `origin` and `destination` are the station names as listed in SEPTA’s GTFS data.
* `refresh_interval` controls how often new data is pulled from SEPTA’s APIs.
* `matrix` and `display` blocks control hardware and timing behavior for the LED slideshow.

---

## 5. Run the scripts

Fetch data manually (for testing):

```bash
python3 fetch_data.py
```

Run the slideshow on the LED matrix:

```bash
sudo python3 matrix_control.py
```

(`sudo` is required for GPIO access on most Pi setups.)

---

## 6. Optional: Auto-start on boot

If you want the board to start automatically:

1. Edit your crontab:

   ```bash
   sudo crontab -e
   ```
2. Add this line:

   ```bash
   @reboot sleep 20 && cd /path/to/phillytrains && : > logs/matrix.log && python3 matrix_control.py > logs/matrix.log 2>&1 &
   ```

---

## 7. Troubleshooting

* **No LEDs lighting up:**
  Check power wiring, brightness setting, and GPIO mapping.
* **Slow startup:**
  The first launch downloads and parses SEPTA’s full GTFS dataset (~10–15s).
  After that, refreshes are fast.
* **Wrong stations:**
  Make sure `origin` and `destination` match SEPTA stop names exactly.
* **Dim or harsh display:**
  Adjust `matrix.brightness` in `config.yaml` (0–100).
