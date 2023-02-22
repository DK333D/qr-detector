try:
    from pyzbar import pyzbar
except ImportError:
    print('You need to install zbar')
    print('On Linux: sudo apt install libzbar0')
    print('On Mac: brew install zbar')
    print('On Windows: pip install pyzbar')
    exit(1)


class QrDetector:
    def detect(self, image) -> list[tuple[int, int, int, str]]:
        '''
        Detect QR codes in an image and return a list of targets.
        Each target is a tuple (center_x, center_y, radius, data)
        where data is the decoded data from the QR code.
        '''
        targets = []
        barcodes = pyzbar.decode(image, symbols=[pyzbar.ZBarSymbol.QRCODE])
        for barcode in barcodes:
            x, y, w, h = barcode.rect
            cx, cy = x + w / 2, y + h / 2
            r = max(w, h) / 2
            data = barcode.data.decode('utf-8')
            targets.append((int(cx), int(cy), int(r), data))
        return targets
