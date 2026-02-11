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
import os

class EMailReplierGenerator(object):
    """The component that generates a reply to an e-mail using LLM.
    """
    
    def __init__(self,
                 model_id:str=os.getenv('LLM_MODEL',"HuggingFaceH4/zephyr-7b-beta"),
                 max_new_tokens:int=int(os.getenv('REPLY_MAX_NEW_TOKENS',"256")),
                 temperature:float=float(os.getenv('REPLY_TEMPERATURE',"0.7")),
                 top_k:int=int(os.getenv('REPLY_TOP_K',"50")),
                 top_p:float=float(os.getenv('REPLY_TOP_P',"0.95")),
                 system_prompt:str=os.getenv('REPLY_SYSTEM_PROMPT',"You are a polite chatbot who always tries to provide solutions to the customer's problems"),
                 user_prompt:str="Reply to an e-mail with the subject '{subject}' and the content '{content}'"
                 ):
        """Initialize the replier generator
        
        Parameters
        ----------
        model_id : str
            The LLM model name (https://huggingface.co). By default get the environment variable
            LLM_MODEL and if it not defined use 'HuggingFaceH4/zephyr-7b-beta'.
        max_new_tokens : int
            The number maximum of tokens to generate. By default get the environment variable
            REPLY_MAX_NEW_TOKENS and if it not defined use 256.
        temperature: float
            The value used to modulate the next token probabilities. By default get the environment variable
            REPLY_TEMPERATURE and if it not defined use 0.7.
        top_k: int
            The number of highest probability tokens to consider for generating the output. By default get the environment variable
            REPLY_TOP_K and if it not defined use 50.
        top_p: float
            A probability threshold for generating the output, using nucleus filtering. By default get the environment variable
            REPLY_TOP_P and if it not defined use 0.95.
        system_prompt: str
            The prompt to use as system. It is used to define how the reply must be done. By default get the environment variable
            REPLY_SYSTEM_PROMPT and if it not defined use 'You are a polite chatbot who always tries to provide solutions to the customer's problems'.
        user_prompt: str
            The prompt used to pass the e-mial information to generate the reply.
        """
        self.pipe = pipeline(
          "text-generation", 
          model=model_id, 
          torch_dtype=torch.bfloat16, 
          device_map="auto",
          model_kwargs={
            "load_in_4bit": True,  
            "bnb_4bit_compute_dtype": torch.bfloat16,
            "use_cache": True      
          }
        )
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
            The subject of the reply message
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
        prompt = self.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        outputs = self.pipe(
          prompt, 
          max_new_tokens=self.max_new_tokens, 
          do_sample=True, 
          temperature=self.temperature, 
          top_k=self.top_k, 
          top_p=self.top_p,
          pad_token_id=self.tokenizer.eos_token_id
        )        
        reply = outputs[0]["generated_text"]
        reply_subject = f"Re: {subject}"
        
        index = reply.index('<|assistant|>')+len('<|assistant|>')
        reply_content = reply[index:].strip()
        if reply_content.startswith('Subject:'):
            index = reply_content.index('\n')
            reply_subject = reply_content[len('Subject:'):index].strip()
            reply_content = reply_content[index+1:].strip()
            
        return reply_subject, reply_content 

        
