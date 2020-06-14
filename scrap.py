#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import re
import requests
from os import mkdir, path
from sys import argv


def getChapterURLFormat(volumeURL, volume, seen=[]):
	if 'Volume' in chapter:
		urlFormats = [
		    '{}/p000.jpg'.format(volumeURL, manga, volume),
		    '{}/{} {} - p000.jpg'.format(volumeURL, manga.replace('-', ' '),
		                                 volume),
		    '{}/{} Tome {} - 000.jpg'.format(volumeURL,
		                                     manga.replace('-', ' '), volume),
		    '{}/{}-T{:02}-000.jpg'.format(volumeURL, manga.replace('-', ''),
		                                  volume),
		    '{}/00.jpg'.format(volumeURL, manga, volume),
		    '{}/{} - T{} - 00.jpg'.format(volumeURL, manga, volume),
		    '{}/00.png'.format(volumeURL, manga, volume),
		    '{}/{} - T{} - 00.png'.format(volumeURL, manga, volume),
		    '{}/000.jpg'.format(volumeURL, manga, volume),
		    '{}/{} - T{} - 000.jpg'.format(volumeURL, manga, volume),
		    '{}/{} - T{} - 000.png'.format(volumeURL, manga, volume),
		]
	else:
		urlFormats = [
		    '{}/00.jpg'.format(volumeURL, chapter),
		    '{}/000.jpg'.format(volumeURL, chapter),
		    '{}/00.png'.format(volumeURL, chapter),
		    '{}/000.png'.format(volumeURL, chapter)
		]

	for url in urlFormats:
		if url not in seen:
			for i in range(0, 5):
				response = requests.get(url.replace('00.', '0{}.'.format(i)),
				                        headers=headers)

				if response.ok:
					return url


def scrapPage(urlFormat, offset, volume, page, double=False, index=0):

	if not double:
		url = urlFormat.replace('#PAGE',
		                        '{{:0{}}}'.format(offset).format(page))
	else:
		url = urlFormat.replace(
		    '#PAGE', '{{:0{}}}-{{:0{}}}'.format(offset,
		                                        offset).format(page, page + 1))

	extension = url.split('.')[-1]

	file = 'Scans/{}/{}{}/{}.{}'.format(
	    manga, 'Volume ' if 'Volume' in chapter else 'Chapitre ', volume,
	    page if index == 0 else page + index, extension)

	response = requests.get(url, headers=headers, stream=True)
	if not response.ok and not double:
		return scrapPage(urlFormat, offset, volume, page, True, index)
	elif not response.ok:
		return False

	print(url, file)

	with open(file, 'wb') as fd:
		for block in response.iter_content(1024):
			if not block:
				break
			fd.write(block)

	return True


def scrapVolume(volume, retry=False, index=0, seen=[]):
	volumeURL = 'https://c.japscan.to/lel/{}/{}{}'.format(
	    manga, chapter, volume)
	urlFormat = getChapterURLFormat(volumeURL, volume, seen)

	if not urlFormat:
		return False

	dirName = 'Scans/{}/{}{}'.format(
	    manga, 'Volume ' if 'Volume' in chapter else 'Chapitre ', volume)

	mkdir(dirName) if not path.exists(dirName) else None

	offset = urlFormat.split('/')[-1].split('_')[-1].split('-')[-1].split(
	    'p')[-2].split(' ')[-1].split('.')[0]
	offsetLen = len(offset)

	urlFormat = urlFormat.replace(offset + '.jpg', '#PAGE.jpg')

	page = errors = 0
	while errors != 4:
		errors = 0 if scrapPage(urlFormat, offsetLen, volume, page, False,
		                        index) else errors + 1
		page += 1

	if errors == page:
		return False
	return True


if __name__ == '__main__':
	chapter = 'Volume-' if '-v' in argv else ''
	argv.remove('-v') if '-v' in argv else None

	headers = {
	    'User-Agent':
	    'Mozilla/5.0 (X11; Linux x86_64; rv:68.0) Gecko/20100101 Firefox/68.0',
	    'Accept':
	    'text/html',
	    'Cookie':
	    '__cfduid=dabf03e9250f0a606cd73250ec75de44d1545398829; cf_clearance={}'
	    .format(argv[1])
	}

	manga = argv[2]
	index = int(argv[3]) if len(argv) > 3 else 1

	mkdir('Scans/{}'.format(manga)) if not path.exists(
	    'Scans/{}'.format(manga)) else None

	while scrapVolume(index):

		if scrapVolume(index + 0.5):
			print('{} {} {} : OK'.format(
			    manga, 'Volume' if 'Volume' in chapter else 'Chapitre',
			    index + 0.5))

		print('{} {} {} : OK'.format(
		    manga, 'Volume' if 'Volume' in chapter else 'Chapitre', index))
		index += 1

	print('{} {} {} : KO'.format(
	    manga, 'Volume' if 'Volume' in chapter else 'Chapitre', index))
