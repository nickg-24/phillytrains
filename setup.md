# Train Board Setup

Steps to prepare a Raspberry Pi for running the train board project. The Pi is treated as a single-purpose system, so everything is installed system-wide.

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

Raspberry Pi OS blocks system-wide pip installs by default. Use the `--break-system-packages` flag:

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

Clone the train board repo and edit `config.yaml` with station settings:

```yaml
origin: "Conshohocken"
destination: "Suburban Station"
n: 2
debug: 1
refresh_interval: 60
```

---

## 5. Run the scripts

* Fetch data only:

  ```bash
  python3 fetch_data.py
  ```

* Run the slideshow on the LED matrix:

  ```bash
  python3 matrix_control.py
  ```
