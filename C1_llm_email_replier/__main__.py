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


from message_service import MessageService
from mov import MOV
from received_email_handler import ReceivedEMailHandler
from change_parameters_handler import ChangeParametersHandler
import logging
import os
from logging.handlers import RotatingFileHandler


def configure_log():
    """Configure the logging system
    """

    console_level = logging.INFO
    try:
        
        console_level = logging.getLevelName(os.getenv("LOG_CONSOLE_LEVEL","INFO"))
        
    except Exception:
        
        logging.exception("Could not obtain the log console level")

    console_handler = logging.StreamHandler()
    console_handler.setLevel(console_level)
    root_logger = logging.getLogger()
    root_logger.addHandler(console_handler)

    file_level = logging.INFO
    file_level = logging.INFO
    file_max_bytes = 1000000    
    file_backup_count = 5
    try:
        
        file_level = logging.getLevelName(os.getenv("LOG_FILE_LEVEL","INFO"))
        
    except Exception:
        
        logging.exception("Could not obtain the log file level")
        
    try:
        
        file_max_bytes = int(os.getenv("LOG_FILE_MAX_BYTES","1000000"))
        
    except Exception:
        
        logging.exception("Could not obtain the log file max bytes")
        
    try:
        
        file_backup_count = int(os.getenv("LOG_FILE_BACKUP_COUNT","5"))
        
    except Exception:
        
        logging.exception("Could not obtain the log file backup count")

    file_handler = RotatingFileHandler('log/c1_llm_email_replier.txt', maxBytes=file_max_bytes, backupCount=file_backup_count)
    file_handler.setLevel(file_level)
    root_logger.addHandler(file_handler)


def main():
    """The function to launch the C1 LLM E-mail replier component
    """
    
    try:
        # Create connection to RabbitMQ
        message_service = MessageService()
        mov = MOV(message_service)
    
        # Create the handlers for the events 
        ReceivedEMailHandler(message_service, mov)
        ChangeParametersHandler(message_service, mov)
    
        # Register the component
        mov.register_component()
    
        # Start to process the received events
        logging.info("Started C1 LLM E-Mail Replier")
        message_service.start_consuming()
        message_service.close()
        
    except Exception:
        
        logging.exception("Could not start the component")
        

if __name__ == "__main__":
    
    configure_log()
    main()
