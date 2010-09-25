#!/usr/bin/env python

from setuptools import setup, find_packages, Extension

setup(
	name='bootalk',
	version='1.1.0',
	description='Japanese text reader daemon',
	author='kenboo',
	author_email='kenbooing@gmail.com',
	url='http://com.nicovideo.jp/community/co475423/',
	packages=find_packages(),
	long_description = """\
	Japnese text reader daemon with AquesTalk2 synthesizer
	backend.
	""",
	classifiers = [
		"License :: OSI Approved :: GNU General Public License",
		"Programming Language :: Python",
		"Development Status :: 4 - Beta",
		"Intended Audience :: Developers",
		"Topic :: dropship",
	],
	keywords='japanese text reader voice sythesizer',
	license='GPL',
	scripts = ['bootalk.py'],
	install_requires = [
		'setuptools', 'pyalsaaudio',
		# these two are required but not in the repository
		# 'pyaquestalk2', 'mecab-python'
	],
	test_suite = 'nose.collector',
)
