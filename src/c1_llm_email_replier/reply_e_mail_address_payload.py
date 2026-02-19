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

from enum import Enum
from pydantic import BaseModel, Field, ConfigDict

class ReplyEMailAddressType(str, Enum):
    """The type of address associated with an e-mail to reply.
    """
    TO = "TO"
    CC = "CC"
    BCC = "BCC"

class ReplyEMailAddressPayload(BaseModel):
	"""Describe the address associated with an e-mail to reply."""

	address_type: ReplyEMailAddressType | None = Field(default=None, alias="type", title="The type of address.")
	name: str | None = Field(default=None, title="The name of the user.")
	address: str | None = Field(default=None, title="The e-mail address.")

	model_config = ConfigDict(serialize_by_alias=True, populate_by_name=True)