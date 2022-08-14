#!/usr/bin python

import mmap
import os
from tempfile import TemporaryDirectory
from pathlib import Path

patch = {
    'path': Path('/lib/modules/') / os.uname().release / 'kernel/drivers/bluetooth',
    'file': 'btusb.ko.xz',
    'offset': 0x0,
    'original': b'\x64',
    'patched': b'\x68',
    'id_search': b'\xd3\x13\x64\x35',
    'id_patch': b'\xd3\x13\x68\x35'
}

write_patch = os.geteuid() == 0


def bt_patch():
    source_path = Path(patch["path"]) / patch["file"]
    with TemporaryDirectory() as tmp_dir:
        cp_path = Path(tmp_dir) / patch["file"]
        os.system(f'cp {source_path} {cp_path}')
        os.system(f'xz -d {cp_path}')
        extracted_ko_path = Path(str(cp_path)[:-3])
        with open(extracted_ko_path, 'r+b') as fis:
            haystack = mmap.mmap(fis.fileno(), length=0, access=mmap.ACCESS_READ)
            patch['offset'] = haystack.find(patch['id_search'])
            if patch['offset'] == -1:
                print('Did not find a match, exiting...')
                return
            print('Found offset: 0x%x' % patch['offset'])
            fis.seek(patch['offset'])
            data = fis.read(4)
            print(data)
            if data == patch['id_search']:
                print('Ok! Patching...')
            else:
                print('Search bytes dont match, exiting!')
                return
            fis.seek(patch['offset'])
            fis.write(patch['id_patch'])
            fis.close()
            print("Striping signing keys from module...")
            os.system(f'strip -g {extracted_ko_path}')
            print('Compressing back...')
            os.system(f'xz {extracted_ko_path}')
            if not write_patch:
                print('Now all you have to do is: ')
                print(f'  sudo modprobe -r btusb')
                print(f'  sudo cp {cp_path} {source_path}')
                print(f'  sudo modprobe btusb')
            else:
                os.system(f'modprobe -r btusb')
                os.system(f'cp {cp_path} {source_path}')
                os.system(f'modprobe btusb')
        return


def main():
    bt_patch()


if __name__ == '__main__':
    main()
