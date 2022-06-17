#!/bin/env python

import mmap
import os

patch = {
    'path': '/lib/modules/' + os.uname().release + '/kernel/drivers/bluetooth/',
    'file': 'btusb.ko.xz',
    'offset': 0x0,
    'original': b'\x64',
    'patched': b'\x68',
    'id_search': b'\xd3\x13\x64\x35',
    'id_patch': b'\xd3\x13\x68\x35'
}


def bt_patch():
    os.system('cp ' + patch['path'] + patch['file'] + ' .')
    os.system('xz -d ' + patch['file'])
    with open(patch['file'][:-3], 'r+b') as fis:
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
        os.system('strip -g ' + patch['file'][:-3])
        print('Compressing back...')
        os.system('xz ' + patch['file'][:-3])
        print('Now all you have to do is: ')
        print('  sudo modprobe -r btusb')
        print('  sudo cp ' + patch['file'] + ' ' + patch['path'])
        print('  sudo modprobe btusb')
    return


def main():
    bt_patch()


if __name__ == '__main__':
    main()
