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
from reply_e_mail_address_payload import ReplyEMailAddressPayload

class ReplyEMailPayload(BaseModel):
	"""The payload with the information of a reply e-mail."""

	addresses: list[ReplyEMailAddressPayload] | None = Field(default_factory=list,title="The addresses of the people to receive the reply.")
	subject: str | None = Field(default=None, title="The e-mail subject.")
	is_html: bool | None = Field(default=None, title="True if the e-mail content is HTML.")
	content: str | None = Field(default=None, title="The content of the e-mail.")
