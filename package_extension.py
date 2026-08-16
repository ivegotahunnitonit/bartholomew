import zipfile
import os

src_dir = 'chrome_extension'
zip_filename = 'bartholomew_extension_v1.0.0.zip'

with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
    for root, dirs, files in os.walk(src_dir):
        for file in files:
            file_path = os.path.join(root, file)
            arcname = os.path.relpath(file_path, src_dir)
            zipf.write(file_path, arcname)

print(f'Successfully packaged {zip_filename} ({os.path.getsize(zip_filename)} bytes)')
