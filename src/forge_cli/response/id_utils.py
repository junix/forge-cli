from __future__ import annotations


def reason_id_of(old_chat_id: str) -> str:
    """
    Generates a reasoning item ID from a chat completion ID.

    This function takes an OpenAI-style chat completion ID (e.g., 'chatcmpl-76cc5d4a-fd51-94e9-94e2-9a2ba4b0c1d7')
    and converts it to a standardized reasoning item ID format by removing the 'chatcmpl-' prefix
    and adding a 'reason-' prefix.

    Args:
        old_chat_id (str): The original chat completion ID, typically in the format
            'chatcmpl-<uuid>' or just '<uuid>'. If the ID already has the 'chatcmpl-'
            prefix, it will be removed before adding the new prefix.

    Returns:
        str: A new ID string in the format 'reason-<uuid>' that can be used to identify
            a reasoning item associated with the original chat completion.

    Examples:
        >>> reason_id_of('chatcmpl-76cc5d4a-fd51-94e9-94e2-9a2ba4b0c1d7')
        'reason-76cc5d4a-fd51-94e9-94e2-9a2ba4b0c1d7'
        >>> reason_id_of('76cc5d4a-fd51-94e9-94e2-9a2ba4b0c1d7')
        'reason-76cc5d4a-fd51-94e9-94e2-9a2ba4b0c1d7'
    """
    if old_chat_id.startswith("chatcmpl-"):
        old_chat_id = old_chat_id[len("chatcmpl-") :]
    return f"reason-{old_chat_id}"


def message_id_of(old_chat_id: str) -> str:
    """
    Generates a message ID from a chat completion ID.

    This function takes an OpenAI-style chat completion ID (e.g., 'chatcmpl-76cc5d4a-fd51-94e9-94e2-9a2ba4b0c1d7')
    and converts it to a standardized message ID format by removing the 'chatcmpl-' prefix
    and adding a 'msg-' prefix.

    Args:
        old_chat_id (str): The original chat completion ID, typically in the format
            'chatcmpl-<uuid>' or just '<uuid>'. If the ID already has the 'chatcmpl-'
            prefix, it will be removed before adding the new prefix.

    Returns:
        str: A new ID string in the format 'msg-<uuid>' that can be used to identify
            a message associated with the original chat completion.

    Examples:
        >>> message_id_of('chatcmpl-76cc5d4a-fd51-94e9-94e2-9a2ba4b0c1d7')
        'msg-76cc5d4a-fd51-94e9-94e2-9a2ba4b0c1d7'
        >>> message_id_of('76cc5d4a-fd51-94e9-94e2-9a2ba4b0c1d7')
        'msg-76cc5d4a-fd51-94e9-94e2-9a2ba4b0c1d7'
    """
    if old_chat_id.startswith("chatcmpl-"):
        old_chat_id = old_chat_id[len("chatcmpl-") :]
    return f"msg-{old_chat_id}"
