try:
    from rgbmatrix import RGBMatrix, RGBMatrixOptions
    _HARDWARE = True
except ImportError:
    _HARDWARE = False


class MatrixDisplay:
    def __init__(self, config):
        self._hardware = _HARDWARE
        if self._hardware:
            opts = RGBMatrixOptions()
            opts.rows = config.get("rows", 64)
            opts.cols = config.get("cols", 64)
            opts.chain_length = config.get("chain_length", 1)
            opts.parallel = config.get("parallel", 1)
            opts.hardware_mapping = config.get("hardware_mapping", "adafruit-hat")
            opts.brightness = config.get("brightness", 50)
            self._matrix = RGBMatrix(options=opts)
            self._canvas = self._matrix.CreateFrameCanvas()
        else:
            print("[matrix] No rgbmatrix found — running without display")

    def show(self, image):
        if not self._hardware:
            return
        rgb = image.convert("RGB")
        self._canvas.SetImage(rgb, 0, 0)
        self._canvas = self._matrix.SwapOnVSync(self._canvas)
