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

import torch
from transformers import pipeline


class EMailReplierGenerator(object):
    """The component that generates a reply to an e-mail using LLM.
    """
    
    
    def __init__(self,
                 model:str="HuggingFaceH4/zephyr-7b-beta",
                 max_new_tokens:int=256,
                 temperature:float=0.7,
                 top_k:float=50,
                 top_p:float=0.95,
                 system_prompt:str="You are a polite chatbot who always try to provide solutions to the customers problems",
                 user_prompt:str="Reply to an e-mail with the subject '{subject}' and the content '{content}'"
                 ):
        """Initialize the replier generator
        
        Parameters
        ----------
        model : str
            The LLM model name (https://huggingface.co)
        max_new_tokens : int
            The number maximum of tokens to generate
        temperature: float
            The value used to modulate the next token probabilities.
        top_k: float
            The number of highest probability tokens to consider for generating the output.
        top_p: float
            A probability threshold for generating the output, using nucleus filtering.
        system_prompt: str
            The prompt to use as system. It is used to define how the reply must be done.
        user_prompt: str
            The prompt used to pass the e-mial information to generate the reply.
        """
        self.pipe = pipeline("text-generation", model=model, torch_dtype=torch.bfloat16, device_map="auto")
        self.max_new_tokens = max_new_tokens
        self.temperature = temperature
        self.top_k = top_k
        self.top_p = top_p
        self.system_prompt = system_prompt
        self.user_prompt = user_prompt
    
    def generate_reply(self,subject:str,content:str):
        """Generate the reply for an email.
        
        This functions call the LLM  model to obtain a reply for an e-mail.
        
        Parameters
        ----------
        subject : str
            The subject of the emial to reply
        content : str
            The content of the email to reply
            
        Returns
        -------
        str
            The content of the reply message
        """
        messages = [
            {
                 "role": "system",
                 "content": self.system_prompt
            },
            {
                 "role": "user", 
                 "content": self.user_prompt.format(subject=subject,content=content)
            }
        ]
        prompt = self.pipe.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        outputs = self.pipe(prompt, max_new_tokens=self.max_new_tokens, do_sample=True, temperature=self.temperature, top_k=self.top_k, top_p=self.top_p)
        
        return outputs[0]["generated_text"]

        
