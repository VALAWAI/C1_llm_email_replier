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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
import unittest
import os
import sys
from unittest.mock import patch, MagicMock

from c1_llm_email_replier.email_replier_generator import EMailReplierGenerator

class TestEMailReplierGenerator(unittest.TestCase):
    """Class to test the e-mail replier generator with mocking.
    """
    
    def setUp(self):
        """Clear environment variables before each test to ensure isolation.
        """
        for key in ['LLM_MODEL', 'REPLY_MAX_NEW_TOKENS', 'REPLY_MIN_NEW_TOKENS', 'REPLY_TEMPERATURE', 
                    'REPLY_TOP_K', 'REPLY_TOP_P', 'REPLY_SYSTEM_PROMPT', 'REPLY_USER_PROMPT']:
            if key in os.environ:
                del os.environ[key]

    def tearDown(self):
        """Restore the environment variables to their default values.
        """
        os.environ['LLM_MODEL'] = "HuggingFaceH4/zephyr-7b-beta"
        os.environ['REPLY_MAX_NEW_TOKENS'] = "256"
        os.environ['REPLY_MIN_NEW_TOKENS'] = "0"
        os.environ['REPLY_TEMPERATURE'] = "0.7"

    @patch('c1_llm_email_replier.email_replier_generator.pipeline')
    @patch('c1_llm_email_replier.email_replier_generator.AutoConfig')
    def test_dynamic_parameter_updates(self, mock_config, mock_pipeline):
        """Test that parameters are correctly updated from environment variables."""
        generator = EMailReplierGenerator(model_id="test-model")
        
        # Default values
        self.assertEqual(generator.max_new_tokens, 256)
        self.assertEqual(generator.temperature, 0.7)
        
        # Update env
        os.environ['REPLY_MAX_NEW_TOKENS'] = '512'
        os.environ['REPLY_MIN_NEW_TOKENS'] = '50'
        os.environ['REPLY_TEMPERATURE'] = '0.9'
        
        generator.refresh_parameters()
        
        self.assertEqual(generator.max_new_tokens, 512)
        self.assertEqual(generator.min_new_tokens, 50)
        self.assertEqual(generator.temperature, 0.9)

    @patch('c1_llm_email_replier.email_replier_generator.pipeline')
    @patch('c1_llm_email_replier.email_replier_generator.AutoConfig')
    def test_model_id_switch_reloads_pipeline(self, mock_config, mock_pipeline):
        """Test that changing LLM_MODEL env var triggers a pipeline re-initialization."""
        generator = EMailReplierGenerator(model_id="model-1")
        generator.pipe = MagicMock() # Simulate loaded pipe
        
        os.environ['LLM_MODEL'] = 'model-2'
        generator.refresh_parameters()
        
        self.assertEqual(generator.model_id, 'model-2')
        # Pipeline should have been called again (once in __init__/lazy check, once here)
        self.assertEqual(mock_pipeline.call_count, 2)

    @patch('c1_llm_email_replier.email_replier_generator.pipeline')
    @patch('c1_llm_email_replier.email_replier_generator.AutoConfig')
    def test_generate_reply_with_mock(self, mock_config, mock_pipeline):
        """Test the logic of generate_reply with a mocked pipeline."""
        mock_pipe = MagicMock()
        mock_pipeline.return_value = mock_pipe
        
        # Mocking the output of the pipeline
        mock_pipe.return_value = [{"generated_text": "Hello <|assistant|> Subject: Test\nContent of the reply"}]
        mock_pipe.tokenizer.apply_chat_template.return_value = "Mocked prompt"
        
        generator = EMailReplierGenerator(model_id="test-model")
        subject, content = generator.generate_reply(subject="Query", content="Help me")
        
        self.assertEqual(subject, "Test")
        self.assertEqual(content, "Content of the reply")
        mock_pipe.assert_called()