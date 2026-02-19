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
import logging
from c1_llm_email_replier.email_replier_generator import EMailReplierGenerator

class TestEMailReplierGeneratorIntegration(unittest.TestCase):
    """Integration tests for EMailReplierGenerator using a real model (no mocks).
    
    WARNING: This test will attempt to download/load a real LLM. 
    It is recommended to use a small model like 'facebook/opt-125m' for testing.
    """
    
    @classmethod
    def setUpClass(cls):
        """Set up the generator once for all tests in this class.
        """
        # Set a small model for integration testing to save time and memory
        os.environ['LLM_MODEL'] = os.getenv('INTEGRATION_TEST_MODEL', "facebook/opt-125m")
        cls.generator = EMailReplierGenerator()

    @classmethod
    def tearDownClass(cls):
        """Restore the environment variables to their default values.
        """
        os.environ['LLM_MODEL'] = "HuggingFaceH4/zephyr-7b-beta"
        os.environ['REPLY_MAX_NEW_TOKENS'] = "256"
        os.environ['REPLY_MIN_NEW_TOKENS'] = "0"
        os.environ['REPLY_TEMPERATURE'] = "0.7"

    def test_real_generation(self):
        """Verify that the generator can produce a reply with a real model.
        """
        subject = "Meeting Request"
        content = "Hi, are you available for a meeting tomorrow at 10 AM?"
        
        reply_subject, reply_content = self.generator.generate_reply(subject, content)
        
        logging.info(f"Generated Subject: {reply_subject}")
        logging.info(f"Generated Content: {reply_content}")
        
        self.assertIsInstance(reply_subject, str)
        self.assertIsInstance(reply_content, str)
        self.assertTrue(len(reply_content) > 0)
        self.assertTrue(reply_subject.startswith("Re:"))

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    unittest.main()
