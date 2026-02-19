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

from typing import Optional, Any, Tuple
import torch
from transformers import pipeline, AutoConfig
import os
import gc
import logging
import warnings

class EMailReplierGenerator:
    """The component that generates a reply to an e-mail using LLM.
    """

    def __init__(
        self,
        model_id: str = os.getenv('LLM_MODEL', "HuggingFaceH4/zephyr-7b-beta"),
        max_new_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        top_k: Optional[int] = None,
        top_p: Optional[float] = None,
        min_new_tokens: Optional[int] = None,
        system_prompt: Optional[str] = None,
        user_prompt: Optional[str] = None
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
        min_new_tokens: int
            The minimum number of tokens to generate. By default get the environment variable
            REPLY_MIN_NEW_TOKENS and if it not defined use 0.
        system_prompt: str
            The prompt to use as system. It is used to define how the reply must be done.
            Supported by environment variable REPLY_SYSTEM_PROMPT.
            Default: 'You are a polite chatbot who always tries to provide solutions to the customer's problems'
        user_prompt: str
            The prompt used to pass the e-mail information to generate the reply.
            Supported by environment variable REPLY_USER_PROMPT.
            Expects placeholders {subject} and {content}.
        """
        self.model_id = model_id
        self.pipe = None  # Lazy loading: pipeline will be initialized on first use

        self.max_new_tokens = max_new_tokens
        self.temperature = temperature
        self.top_k = top_k
        self.top_p = top_p
        self.min_new_tokens = min_new_tokens
        self.system_prompt = system_prompt
        self.user_prompt = user_prompt

        # Initial refresh if parameters weren't explicitly provided
        self.refresh_parameters()

        # Lazy initialization
        if self.pipe is None:
            self._initialize_pipeline()

    def _initialize_pipeline(self) -> None:
        """Initialize the text-generation pipeline with the current model_id."""
        logging.info(f"Starting to load LLM model: {self.model_id}")

        # Cleanup memory before loading new model if one was already loaded
        if hasattr(self, 'pipe') and self.pipe is not None:
            logging.info("Cleaning up memory from previous model...")
            del self.pipe
            self.pipe = None
            gc.collect()
            if torch.cuda.is_available():
                torch.cuda.empty_cache()

        try:
            # Suppress upstream warnings from transformers/tokenizers
            with warnings.catch_warnings():
                # GPT-2/BPE internal deprecation issue
                warnings.filterwarnings("ignore", category=DeprecationWarning, message=".*BPE.__init__ will not create from files anymore.*")
                # OPT/others tied weights warning (occurs even with tie_word_embeddings=False if both weights are in checkpoint)
                warnings.filterwarnings("ignore", category=UserWarning, message=".*tie_word_embeddings=False.*")
                # Explicitly load config to set tie_word_embeddings=False and silence warnings
                config = AutoConfig.from_pretrained(self.model_id, tie_word_embeddings=False)

                self.pipe = pipeline(
                    "text-generation",
                    model=self.model_id,
                    config=config,
                    dtype=torch.bfloat16,
                    device_map="auto",
                    model_kwargs={
                        "use_cache": True
                    }
                )
            logging.info(f"Model {self.model_id} loaded successfully.")
        except Exception as e:
            logging.error(f"Failed to load model {self.model_id}: {e}")
            raise

    def refresh_parameters(self) -> None:
        """Refresh generation parameters from environment variables.

        This allows updating the configuration without restarting the component.
        """
        new_model_id = os.getenv('LLM_MODEL', self.model_id)
        if new_model_id != self.model_id:
            logging.info(f"Model ID change detected: {self.model_id} -> {new_model_id}")
            self.model_id = new_model_id
            # Invalidate the pipeline so it reloads on next generation
            if self.pipe is not None:
                # Immediate cleanup if we are switching models
                self._initialize_pipeline()
            else:
                self.pipe = None

        self.max_new_tokens = int(os.getenv('REPLY_MAX_NEW_TOKENS', self.max_new_tokens or 256))
        self.min_new_tokens = int(os.getenv('REPLY_MIN_NEW_TOKENS', self.min_new_tokens or 0))
        self.temperature = float(os.getenv('REPLY_TEMPERATURE', self.temperature or 0.7))
        self.top_k = int(os.getenv('REPLY_TOP_K', self.top_k or 50))
        self.top_p = float(os.getenv('REPLY_TOP_P', self.top_p or 0.95))
        self.system_prompt = os.getenv('REPLY_SYSTEM_PROMPT', self.system_prompt or "You are a polite chatbot who always tries to provide solutions to the customer's problems")
        self.user_prompt = os.getenv('REPLY_USER_PROMPT', self.user_prompt or "Reply to an e-mail with the subject '{subject}' and the content '{content}'")

    def generate_reply(self, subject: str, content: str) -> Tuple[str, str]:
        """Generate the reply for an email.

        This functions call the LLM  model to obtain a reply for an e-mail.
        It also refreshes parameters from environment variables.

        Parameters
        ----------
        subject : str
            The subject of the e-mail to reply
        content : str
            The content of the e-mail to reply

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
                "content": self.user_prompt.format(subject=subject, content=content)
            }
        ]

        # Use a fallback template if the tokenizer doesn't have one
        chat_template = self.pipe.tokenizer.chat_template
        if not chat_template:
            # Simple ChatML-style template as fallback
            chat_template = (
                "{% for message in messages %}"
                "{{ '<|im_start|>' + message['role'] + '\\n' + message['content'] + '<|im_end|>\\n' }}"
                "{% endfor %}"
                "{% if add_generation_prompt %}"
                "{{ '<|im_start|>assistant\\n' }}"
                "{% endif %}"
            )

        prompt = self.pipe.tokenizer.apply_chat_template(
            messages,
            chat_template=chat_template,
            tokenize=False,
            add_generation_prompt=True
        )

        outputs = self.pipe(
            prompt,
            max_new_tokens=self.max_new_tokens,
            min_new_tokens=self.min_new_tokens,
            max_length=None,  # Silence warning about max_new_tokens vs max_length
            do_sample=True,
            temperature=self.temperature,
            top_k=self.top_k,
            top_p=self.top_p,
            pad_token_id=self.pipe.tokenizer.eos_token_id,
            generation_config=None,  # Silence deprecation warning when passing explicit parameters
            return_full_text=False   # Only return the generated part
        )

        reply_content = outputs[0]["generated_text"].strip()
        
        # Further cleanup: remove any trailing specialized tokens if they leaked
        # or markers that might have been generated by the model itself
        stop_sequences = [
            '<|im_end|>', '<|end|>', '</s>', '<|file_separator|>', 
            '<|assistant|>', 'assistant\n', 'User:'
        ]
        for seq in stop_sequences:
            if seq in reply_content:
                reply_content = reply_content.split(seq)[0].strip()

        # Extract subject if the model prefix it with 'Subject:'
        reply_subject = f"Re: {subject}"
        if reply_content.lower().startswith('subject:'):
            lines = reply_content.split('\n', 1)
            # Remove 'Subject:' prefix case-insensitively
            prefix_len = len('subject:')
            reply_subject = lines[0][prefix_len:].strip()
            reply_content = lines[1].strip() if len(lines) > 1 else ""

        return reply_subject, reply_content

        
