# This file is part of the C1_llm_emial_replier distribution (https://github.com/VALAWAI/C1_llm_email_replier).
# Copyright (c) 2022-2026 VALAWAI (https://valawai.eu/).
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from setuptools import setup, find_packages
setup(
    name='C1 LLM E-Mail replier',
    version='1.0.0',
    packages=find_packages(include=['C1_llm_email_replier', 'C1_llm_email_replier.*']),
    install_requires=[
        'torch>=2.4.0',
        'transformers>=4.44.2',
        'accelerate>=0.33.0'
    ],
    setup_requires=['pytest-runner'],
    tests_require=['pytest']
)

   