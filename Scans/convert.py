#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from subprocess import run
from glob import glob
from sys import argv

manga = argv[1]

volumes = glob(f'{manga}/*')

for volume in volumes:
	jpg = glob(f'{volume}/*.jpg')
	jpg.sort(key=lambda x: int(x.split('/')[-1].replace('.jpg', '')))

	run(['convert'] + jpg + [f"{manga}/{volume.split('/')[-1]}.pdf"])
