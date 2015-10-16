# coding=utf-8

import os
import io
import subprocess


def unpack(directory, content):
    filename = directory + '/temp.rar'
    temp_dir = directory + '/temp'
    output = io.FileIO(filename, mode='w')
    output.write(content)
    output.flush()
    output.close()
    command = '/usr/local/bin/7z e -y -o' + temp_dir + ' ' + filename
    subprocess.check_output(command, shell=True)
    os.remove(filename)
    files = os.listdir(temp_dir)
    for item in files:
        if not item.endswith('.srt'):
            files.remove(item)
            os.remove(temp_dir+'/'+item)
    return temp_dir, files
