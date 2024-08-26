# 
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
#
import sys
import os.path
import re
from .message_service import MessageService


class MOV(object):
    """The component used to interatc with the Master Of VALAWAI (MOV)
    """
    
    def __init__(self, message_service:MessageService):
        """Initialize the connection to the MOV
        """
        self.message_service = message_service
    
    def __read_file(self, path:str):
        """Read a file and return its content.
        """
        class_file_path = os.path.abspath(os.path.dirname(__file__))
        file_path = os.path.join(class_file_path, path)
        with open(file_path, 'r') as file:
            content = file.read()
        return content
        
    def register_component_msg(self):
        """Register this component into the MOV (https://valawai.github.io/docs/tutorials/mov#register-a-component)
        """
        
        setup = self.__read_file('../setup.py')
        version = re.findall(r"version='(\d+\.\d+\.\d+)'", setup)[0]
        async_api = self.__read_file('../asyncapi.yaml')
             
        msg = {
            "type": "C1",
            "name": "c1_llm_email_replier",
            "version": version,
            "asyncapi_yaml":async_api
            }
        return msg
