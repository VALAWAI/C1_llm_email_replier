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

import os
import pika
import time
import logging

class MessageService(object):
    """The service to send and receive messages from the RabbitMQ
    """
    
    def __init__(self,
                 host:str=os.getenv('RABBITMQ_HOST','mov-mq'),
                 port:int=int(os.getenv('RABBITMQ_PORT',"5672")),
                 username:str=os.getenv('RABBITMQ_USERNAME','mov'),
                 password:str=os.getenv('RABBITMQ_PASSWORD','password'),
                 max_retries:int=int(os.getenv('RABBITMQ_MAX_RETRIES',"100")),
                 retry_sleep_seconds:int=int(os.getenv('RABBITMQ_RETRY_SLEEP',"3")),
                 ):
        """Initialize the connection to the RabbitMQ
        
        Parameters
        ----------
        host : str
            The RabbitMQ server host name. By default uses the environment variable RABBITMQ_HOST
            and if it is not defined uses 'mov-mq'.
        port : int
            The RabbitMQ server port. By default uses the environment variable RABBITMQ_PORT
            and if it is not defined uses '5672'.
        username : str
            The user name of the credential to connect to the RabbitMQ serve. By default uses the environment
            variable RABBITMQ_USERNAME and if it is not defined uses 'mov'.
        password : str
            The password of the credential to connect to the RabbitMQ serve. By default uses the environment
            variable RABBITMQ_PASSWORD and if it is not defined uses 'password'.
        max_retries : int
            The number maximum of tries to create a connection with the RabbitMQ server. By default uses
            the environment variable RABBITMQ_MAX_RETRIES and if it is not defined uses '100'.
        retry_sleep_seconds : int
            The seconds to wait between the tries for create a connection with the RabbitMQ server.
            By default uses the environment variable RABBITMQ_RETRY_SLEEP and if it is not defined uses '3'.
        """
        
        tries=0
        while tries < max_retries:
            
            try:
            
                credentials = pika.PlainCredentials(username=username,password=password)
                self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=host,port=port,credentials=credentials))
                self.channel = self.connection.channel()
                return
            
            except Exception:
                print("Connection was closed, retrying...")
                logging.exception("Connection was closed, retrying...")
                time.sleep(retry_sleep_seconds)
                
            tries+=1
            
        raise Exception("Cannot connect with the RabbitMQ")