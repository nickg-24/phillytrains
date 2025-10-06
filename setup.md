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

## 6. Auto-start on boot (recommended)

To have the board start automatically when the Pi boots, use **systemd**.

1. Create a new service file:

   ```bash
   sudo vim /etc/systemd/system/phillytrains.service
   ```

2. Paste the following:

   ```ini
   [Unit]
   Description=SEPTA LED Matrix Display
   After=network-online.target
   Wants=network-online.target

   [Service]
   Type=simple
   User=root
   WorkingDirectory=/path/to/phillytrains
   ExecStart=/usr/bin/python3 -u /path/to/phillytrains/matrix_control.py
   Restart=always
   RestartSec=10

   [Install]
   WantedBy=multi-user.target
   ```

   > **Note:**
   > The script must run as `root` because the LED matrix library requires GPIO access.

3. Reload systemd and enable the service:

   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable phillytrains
   sudo systemctl start phillytrains
   ```

4. To check the status or logs:

   ```bash
   sudo systemctl status phillytrains
   sudo journalctl -u phillytrains -f
   ```

   * `status` shows whether it’s running.
   * `journalctl -f` streams live output (like `tail -f`).

5. The service will now start automatically on every boot.


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
