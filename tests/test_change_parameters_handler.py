# 
# This file is part of the C1_llm_email_replier distribution (https://github.com/VALAWAI/C1_llm_email_replier).
# Copyright (c) 2022-2026 VALAWAI (https://valawai.eu/).
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#

import os
import random
import re
import unittest
import uuid

from mov_api import mov_get_log_message_with
from unittest_parametrize import ParametrizedTestCase, param, parametrize

from c1_llm_email_replier.change_parameters_handler import ChangeParametersHandler
from c1_llm_email_replier.message_service import MessageService
from c1_llm_email_replier.mov import MOV


class TestChangeParametersHandler(unittest.TestCase):
  """Class to test the handler of the messages to change the component parameters.
  """

  @classmethod
  def setUpClass(cls):
    """Create the handler.
    """

    cls.message_service = MessageService()
    cls.mov = MOV(cls.message_service)
    cls.handler = ChangeParametersHandler(cls.message_service, cls.mov)
    cls.message_service.start_consuming_and_forget()

  @classmethod
  def tearDownClass(cls):
    """Stops the message service.
    """

    cls.mov.unregister_component()
    cls.message_service.close()

  def test_capture_bad_json_message_body(self):
    """Check that the handler can manage when the body is not a valid json
    """
    
    with self.assertLogs() as cm:
      
      self.handler.handle_message(None, None, None, "{")
      
    assert len(cm.output) == 1
    assert re.search("Unexpected message \\{", cm.output[0])

  def __assert_process_change_parameters(self, level:str, parameters:dict):
    """Check that

      Parameters
      ----------
      level: str
      The expected level of the message when the parameters are changed
      parameters: object
      The parameters that can not be set
    """

    self.message_service.publish_to('valawai/c1/llm_email_replier/control/parameters', parameters)
    mov_get_log_message_with(level,parameters)

  def test_change_parameters(self):
    """Check that the handler change the parameters
    """

    random.random()
    parameters = {
      'max_new_tokens': 256.0 + random.randrange(11, 111, 1),
      'temperature': 0.7 + 0.001 * random.randrange(1, 100, 1),
      'top_k': 40.0 + random.randrange(1, 21, 1),
      'top_p': 0.9 + 0.001 * random.randrange(1, 99, 1),
      'system_prompt': 'You are a polite email replier who used as contact info the e-mail ' + str(uuid.uuid4()) + '@valawai.eu'
    }
    self.__assert_process_change_parameters('INFO', parameters)
    for param_name in parameters:

      expected = str(parameters[param_name])
      env_property_name = param_name.upper()
      env_property = os.getenv(env_property_name)
      assert expected == env_property


  def test_not_change_max_new_tokens_with_a_bad_value(self):
    """Check that the handler not change the 'max_new_tokens' when it is not valid
    """
    
    parameters = {
      'max_new_tokens':str(uuid.uuid4())
    }
    self.__assert_process_change_parameters('ERROR', parameters)

  def test_not_change_max_new_tokens_with_a_low_value(self):
    """Check that the handler not change the 'max_new_tokens' if the value is too low
    """
    
    parameters = {
      'max_new_tokens': 1.0*random.randrange(0, 99, 1)
    }
    self.__assert_process_change_parameters('ERROR', parameters)

  def test_not_change_max_new_tokens_with_a_hight_value(self):
    """Check that the handler not change the 'max_new_tokens' if the value is too hight
    """
    
    parameters = {
      'max_new_tokens': 1.0*random.randrange(1001, 2000, 1)
    }
    self.__assert_process_change_parameters('ERROR', parameters)

  def test_change_max_new_tokens(self):
    """Check that the handler change the 'max_new_tokens'
    """
    
    max_new_tokens = 256.0 + random.randrange(11, 111, 1)
    parameters = {
      'max_new_tokens':max_new_tokens
    }
    self.__assert_process_change_parameters('INFO', parameters)
    self.assertEqual(str(max_new_tokens), os.getenv("REPLY_MAX_NEW_TOKENS"))

  def test_not_change_temperature_with_a_bad_value(self):
    """Check that the handler not change the 'temperature' when it is not valid
    """
    
    parameters = {
      'temperature': str(uuid.uuid4())
    }
    self.__assert_process_change_parameters('ERROR', parameters)

  def test_not_change_temperature_with_a_value_less_than_0(self):
    """Check that the handler not change the 'temperature' if the value is less than 0
    """
    
    parameters = {
      'temperature': -1.0 * random.random()
    }
    self.__assert_process_change_parameters('ERROR', parameters)

  def test_not_change_temperature_with_a_value_more_than_1(self):
    """Check that the handler not change the 'temperature' if the value is more than 1
    """
    
    parameters = {
      'temperature': 1.0000001 + random.random()
    }
    self.__assert_process_change_parameters('ERROR', parameters)

  def test_change_temperture(self):
    """Check that the handler change the 'temperature'
    """
    
    temperature = 0.7 + 0.001 * random.randrange(1, 99, 1)
    parameters = {
      'temperature':temperature
    }
    self.__assert_process_change_parameters('INFO', parameters)
    self.assertEqual(str(temperature), os.getenv("REPLY_TEMPERATURE"))

  def test_not_change_top_k_with_a_bad_value(self):
    """Check that the handler not change the 'top_k' when it is not valid
    """
    
    parameters = {
      'top_k':str(uuid.uuid4())
    }
    self.__assert_process_change_parameters('ERROR', parameters)

  def test_not_change_top_k_with_a_value_less_than_1(self):
    """Check that the handler not change the 'top_k' if the value is less than 1
    """
    
    parameters = {
      'top_k': -1.0 * random.randrange(0, 100, 1)
    }
    self.__assert_process_change_parameters('ERROR', parameters)

  def test_not_change_top_k_with_a_value_more_than_100(self):
    """Check that the handler not change the 'top_k' if the value is more than 100
    """
    
    parameters = {
      'top_k': 1.0 * random.randrange(101, 200, 1)
    }
    self.__assert_process_change_parameters('ERROR', parameters)

  def test_change_top_k(self):
    """Check that the handler change the 'top_k'
    """
    
    top_k = 40.0 + random.randrange(1, 21, 1)
    parameters = {
      'top_k':top_k
    }
    self.__assert_process_change_parameters('INFO', parameters)
    self.assertEqual(str(top_k), os.getenv("REPLY_TOP_K"))

  def test_not_change_top_p_with_a_bad_value(self):
    """Check that the handler not change the 'top_p' when it is not valid
    """
    
    parameters = {
      'top_p':str(uuid.uuid4())
    }
    self.__assert_process_change_parameters('ERROR', parameters)

  def test_not_change_top_p_with_a_value_less_than_0(self):
    """Check that the handler not change the 'top_p' if the value is less than 0
    """
    
    parameters = {
      'top_p': -10 * random.random()
    }
    self.__assert_process_change_parameters('ERROR', parameters)

  def test_not_change_top_p_with_a_value_more_than_1(self):
    """Check that the handler not change the 'top_p' if the value is more than 1
    """
    
    parameters = {
      'top_p': 1.0000001 + random.random()
    }
    self.__assert_process_change_parameters('ERROR', parameters)

  def test_change_top_p(self):
    """Check that the handler change the 'top_p'
    """
    
    top_p = 0.9 + 0.001 * random.randrange(1, 99, 1)
    parameters = {
      'top_p':top_p
    }
    self.__assert_process_change_parameters('INFO', parameters)
    self.assertEqual(str(top_p), os.getenv("REPLY_TOP_P"))

  def test_not_change_system_prompt_with_a_prompt_length_too_short(self):
    """Check that the handler not change the 'system_prompt' if the value is less than 10 characters
    """
    
    parameters = {
      'system_prompt':"".join(map(chr, (ord('a')+(y%26) for y in range(9))))
    }
    self.__assert_process_change_parameters('ERROR', parameters)

  def test_not_change_system_prompt_with_a_prompt_length_too_long(self):
    """Check that the handler not change the 'system_prompt' if the value is more than 10000 characters
    """
    
    parameters = {
      'system_prompt':"".join(map(chr, (ord('a')+(y%26) for y in range(100001))))
    }
    self.__assert_process_change_parameters('ERROR', parameters)

  def test_change_system_prompt(self):
    """Check that the handler change the 'system_prompt'
    """
    
    system_prompt = 'You are a polite email replier who used as contact info the e-mail ' + str(uuid.uuid4()) + '@valawai.eu'
    parameters = {
      'system_prompt':system_prompt
    }
    self.__assert_process_change_parameters('INFO', parameters)
    self.assertEqual(system_prompt, os.getenv("REPLY_SYSTEM_PROMPT"))
    
  def test_change_parameters(self):
    """Check that the handler change the parameters
    """
    
    max_new_tokens = 256.0 + random.randrange(11, 111, 1)
    temperature = 0.7 + 0.001 * random.randrange(1, 100, 1)
    top_k = 40.0 + random.randrange(1, 21, 1)
    top_p = 0.9 + 0.001 * random.randrange(1, 99, 1)
    system_prompt = 'You are a polite email replier who used as contact info the e-mail ' + str(uuid.uuid4()) + '@valawai.eu'
    parameters = {
      'max_new_tokens':max_new_tokens,
      'temperature':temperature,
      'top_k':top_k,
      'top_p':top_p,
      'system_prompt':system_prompt
    }
    self.__assert_process_change_parameters('INFO', parameters)
    self.assertEqual(str(max_new_tokens), os.getenv("REPLY_MAX_NEW_TOKENS"))
    self.assertEqual(str(temperature), os.getenv("REPLY_TEMPERATURE"))
    self.assertEqual(str(top_k), os.getenv("REPLY_TOP_K"))
    self.assertEqual(str(top_p), os.getenv("REPLY_TOP_P"))
    self.assertEqual(system_prompt, os.getenv("REPLY_SYSTEM_PROMPT"))
