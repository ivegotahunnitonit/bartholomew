import os
import base64

os.makedirs('chrome_extension/icons', exist_ok=True)

# Standard cyan 16x16, 48x48, 128x128 valid PNG data
try:
    from PIL import Image, ImageDraw
    for size in [16, 48, 128]:
        img = Image.new('RGBA', (size, size), (9, 13, 22, 255))
        draw = ImageDraw.Draw(img)
        draw.rounded_rectangle([1, 1, size-2, size-2], radius=max(2, int(size*0.2)), outline=(0, 242, 254, 255), width=max(1, int(size/32)))
        scale = size / 128.0
        pts = [(72*scale, 16*scale), (32*scale, 72*scale), (64*scale, 72*scale), (56*scale, 112*scale), (96*scale, 56*scale), (64*scale, 56*scale)]
        draw.polygon(pts, fill=(0, 242, 254, 255))
        img.save(f'chrome_extension/icons/icon{size}.png')
    print('Generated PNG icons with PIL')
except Exception as e:
    # 1x1 cyan PNG fallback
    cyan_png = base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==')
    for size in [16, 48, 128]:
        with open(f'chrome_extension/icons/icon{size}.png', 'wb') as f:
            f.write(cyan_png)
    print('Fallback PNG icons created')
