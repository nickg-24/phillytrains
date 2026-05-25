# PhillyTrains — Pi Setup Guide

---

## 1. Flash the OS

Use **Raspberry Pi OS Lite (64-bit)** — the headless version without a desktop.
Flash it with [Raspberry Pi Imager](https://www.raspberrypi.com/software/).

PhillyTrains requires internet access at runtime to fetch live SEPTA data. Configure your network **during imaging** — it's the easiest point to do it and avoids needing a monitor or keyboard later.

In the Imager's advanced settings (click the gear icon) before flashing:
- Set a **hostname** (e.g. `phillytrains`)
- Enable **SSH**
- Set a **username and password**
- Set your **Wi-Fi SSID and password** (or use ethernet — either works)

Boot the Pi and SSH in:

```bash
ssh <your-username>@phillytrains.local
```

---

## 2. Clone the repo

```bash
git clone https://github.com/nickg-24/phillytrains.git ~/phillytrains
cd ~/phillytrains
```

---

## 3. Configure your stops

Edit `config.yaml` before running setup. At minimum, update `rail_lines` and `subway` for your commute.

**Rail lines** — one entry per origin/destination pair you want to track:

```yaml
rail_lines:
  - name: "Suburban"
    origin: "Suburban Station"
    destination: "Conshohocken"
    route_id: "NOR"
    n: 2
```

`origin` and `destination` must exactly match SEPTA stop names. To look one up, run:

```bash
python3 -c "
import requests, zipfile, io, csv
z = zipfile.ZipFile(io.BytesIO(requests.get('https://www3.septa.org/developer/gtfs_public.zip').content))
r = zipfile.ZipFile(io.BytesIO(z.read('google_rail.zip')))
for row in csv.DictReader(io.TextIOWrapper(r.open('stops.txt'), 'utf-8')):
    print(row['stop_name'])
"
```

`route_id` is the SEPTA route code (e.g. `NOR` for Norristown/Manayunk, `LAN` for Lansdale/Doylestown). `n` is how many upcoming trains to show.

**Subway** — BSL stop IDs for your station. To find your stop IDs, run:

```bash
python3 -c "
import requests, zipfile, io, csv
z = zipfile.ZipFile(io.BytesIO(requests.get('https://www3.septa.org/developer/gtfs_public.zip').content))
b = zipfile.ZipFile(io.BytesIO(z.read('google_bus.zip')))
for row in csv.DictReader(io.TextIOWrapper(b.open('stops.txt'), 'utf-8')):
    if 'your station' in row['stop_name'].lower():
        print(row['stop_id'], ':', row['stop_name'])
"
```

Replace `'your station'` with your station name. Set `route_id` to `B1` for BSL, `MFL` for Market-Frankford, or your trolley route.

**Alerts** — list the route IDs you want service alerts for:

```yaml
alerts:
  route_ids:
    - "NOR"
    - "B1"
```

---

## 4. Run the setup script

```bash
bash setup.sh
```

It will:
1. Install build dependencies
2. Disable the Pi audio driver (required — shares hardware with the matrix)
3. Create a Python virtual environment and install all dependencies
4. Build and install `rpi-rgb-led-matrix` (compiles C++ — takes a few minutes)
5. Install and enable the `phillytrains` systemd service

Reboot if prompted.

---

## 5. Verify the hardware

```bash
sudo .venv/bin/python3 test_matrix.py
```

The matrix should light up **solid blue**. Press Ctrl+C to stop.

If nothing lights up:
- Check the ribbon cable and 5V power supply to the matrix
- If it flickers, confirm audio is disabled: `grep audio /boot/firmware/config.txt`
- If matrix init fails, try changing `hardware_mapping` in `config.yaml` from `"adafruit-hat"` to `"adafruit-hat-pwm"`

---

## 6. Start the display

```bash
sudo systemctl start phillytrains
```

Check status and logs:

```bash
sudo systemctl status phillytrains
sudo journalctl -u phillytrains -f
```

The first run downloads GTFS data from SEPTA — on a Pi 3 this takes **60–90 seconds** before anything appears on the matrix. Subsequent boots are the same since the data isn't cached. This is normal.

On every boot the service starts automatically. If the network isn't ready yet, the service retries every 15 seconds until it connects.

---

## Pushing updates

On your laptop:

```bash
git add -A && git commit -m "your message"
git push
```

On the Pi:

```bash
cd ~/phillytrains && git pull && sudo systemctl restart phillytrains
```
