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

import unittest
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from C1_llm_email_replier.email_replier_generator import EMailReplierGenerator

class TestEMailReplierGenerator(unittest.TestCase):
    """Class to test the e-mail replier generator
    """
    
    def setUp(self):
        """Create the generator.
        """
        self.generator = EMailReplierGenerator()
    
    def test_generate_reply(self):
        """Test the reply generation
        """
        subject,reply = self.generator.generate_reply(subject="The buzzerr 316 not work more",content="Hi!\nI buy the buzzerr 316 and after some days it does not work more. The serial number is 123dfr567. Is it any issue with it? Do I need to replace? Is it a refund possible?")
        self.assertGreater(len(subject),3,"Must return the subject")
        self.assertGreater(len(reply),0,"Must return the reply content")
 