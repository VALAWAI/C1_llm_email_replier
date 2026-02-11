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


from pydantic import BaseModel, Field


class ChangeParametersPayload(BaseModel):
	"""The payload of the message to change the parameters of the component."""

	max_new_tokens: float | None = Field(default=None, ge=100.0, le=1000.0, title="The maximum of tokens to use in the LLM.")
	temperature: float | None = Field(default=None, ge=0.0, le=1.0, title="The temperature of the LLM.")
	top_k: float | None = Field(default=None, ge=1.0, le=100.0, title="The top K to use in the LLM.")
	top_p: float | None = Field(default=None, ge=0.0, le=1.0, title="The top P to use in the LLM.")
	system_prompt: str | None = Field(default=None, title="The prompt to use in the LLM.")
