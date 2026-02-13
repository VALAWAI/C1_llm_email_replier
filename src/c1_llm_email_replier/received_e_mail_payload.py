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
from received_e_mail_address_payload import ReceivedEMailAddressPayload

class ReceivedEMailPayload(BaseModel):
	"""The payload containing metadata and content of a received e-mail."""

	addresses: list[ReceivedEMailAddressPayload] = Field(default_factory=list, title="List of all participants (sender and recipients) associated with the email.")
	subject: str | None = Field(default=None, title="The subject line of the email.")
	mime_type: str | None = Field(default=None, title="The MIME type of the content (e.g., text/html, text/plain).")
	content: str | None = Field(default=None, title="The actual body content of the email.")
	received_at: int | None = Field(default=None, title="The Unix epoch timestamp (seconds) when the email was received.")
