from typing import Optional

from src.config import settings


def get_langfuse_handler(session_id: Optional[str] = None):
	"""Return a Langfuse CallbackHandler, or None if not configured."""
	if not settings.langfuse_public_key:
		return None
	# Imported lazily so the app runs even without langfuse installed/configured.
	from langfuse.callback import CallbackHandler

	return CallbackHandler(
		public_key=settings.langfuse_public_key,
		secret_key=settings.langfuse_secret_key,
		host=settings.langfuse_host,
		session_id=session_id,
	)
