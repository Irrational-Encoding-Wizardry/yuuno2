#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Yuuno - IPython + VapourSynth
# Copyright (C) 2017-2019 StuxCrystal (Roland Netzsch <stuxcrystal@encode.moe>)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
from setuptools import setup, find_packages

# with open('README.rst', encoding="utf-8") as readme_file:
#     readme = readme_file.read()
#
# with open('HISTORY.rst', encoding="utf-8") as history_file:
#     history = history_file.read()
readme = history = ""

requirements = [
    "notebook", "IPython",                                      # IPython is technically part of notebook.
    "yuuno2-core",
    "blessed"
]

test_requirements = [
    "aiounittest"
]
extras_requires = {
    "vapoursynth": ["vapoursynth"]
}
setup_requires = [

]

setup(
    name='yuuno2-notebook',
    version='2.0',
    description="Yuuno-Server - Remote encoding server.",
    long_description=readme + '\n\n' + history,
    author="stuxcrystal",
    author_email='stuxcrystal@encode.moe',
    url='https://github.com/stuxcrystal/yuuno-core',
    packages=find_packages(exclude=("tests", )),
    package_dir={'yuuno': 'yuuno'},
    include_package_data=True,
    install_requires=requirements,
    extras_require=extras_requires,
    setup_requires=setup_requires,
    license="GNU Lesser General Public License v3 (LGPLv3)",
    zip_safe=False,
    keywords='yuuno',
    classifiers=[
        'Natural Language :: English',

        'Development Status :: 5 - Production/Stable',

        'Intended Audience :: Developers',
        'Intended Audience :: Other Audience',

        'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',

        'Programming Language :: Python :: 3.7',

        'Topic :: Multimedia :: Video',
        'Topic :: Multimedia :: Video :: Display',
        'Topic :: Multimedia :: Video :: Non-Linear Editor',
    ],
    test_suite='tests',
    tests_require=test_requirements
)

