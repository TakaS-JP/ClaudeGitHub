"""Tool schema definitions passed to the Claude API."""

AGENT_TOOLS: list[dict] = [
    {
        "name": "list_emails",
        "description": (
            "Fetch a batch of emails from Gmail with lightweight metadata "
            "(subject, sender, date, snippet, has_attachments). "
            "Use this first to get an overview of what needs processing."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "max_results": {
                    "type": "integer",
                    "description": "Maximum number of emails to return (default 20, max 50).",
                    "default": 20,
                },
                "query": {
                    "type": "string",
                    "description": (
                        "Gmail search query, e.g. 'is:unread', 'is:unread in:inbox'. "
                        "Defaults to 'is:unread'."
                    ),
                    "default": "is:unread",
                },
            },
            "required": [],
        },
    },
    {
        "name": "get_email_content",
        "description": (
            "Fetch the full content of a single email: body text and attachment metadata. "
            "Call this when the snippet is insufficient to classify an email."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "email_id": {
                    "type": "string",
                    "description": "The Gmail message ID.",
                },
            },
            "required": ["email_id"],
        },
    },
    {
        "name": "classify_and_act",
        "description": (
            "Record your classification decision for an email. "
            "ALWAYS call this before delete_email or apply_label. "
            "Provide an honest one-sentence reasoning so decisions can be audited."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "email_id": {
                    "type": "string",
                    "description": "The Gmail message ID being classified.",
                },
                "category": {
                    "type": "string",
                    "enum": [
                        "delete",
                        "spam",
                        "save-work",
                        "save-personal",
                        "save-important",
                        "needs-reply",
                        "newsletter-unsubscribe",
                        "skip",
                    ],
                    "description": (
                        "delete: spam/automated notifications/expired promos. "
                        "spam: phishing or unsolicited bulk. "
                        "save-work: professional, client, invoices, work tools. "
                        "save-personal: friends, family, personal services. "
                        "save-important: legal, financial, government, medical. "
                        "needs-reply: explicit questions or action required from you. "
                        "newsletter-unsubscribe: newsletters (will be deleted + noted). "
                        "skip: truly uncertain — leave for human review."
                    ),
                },
                "reasoning": {
                    "type": "string",
                    "description": "One sentence explaining why you chose this category.",
                },
            },
            "required": ["email_id", "category", "reasoning"],
        },
    },
    {
        "name": "delete_email",
        "description": (
            "Move an email to Trash (default) or permanently delete it. "
            "Permanent deletion is irreversible — only use it for confirmed spam/phishing. "
            "You MUST call classify_and_act first."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "email_id": {
                    "type": "string",
                    "description": "The Gmail message ID to delete.",
                },
                "permanent": {
                    "type": "boolean",
                    "description": (
                        "If true, permanently delete instead of moving to Trash. "
                        "Only set true for confirmed spam or phishing."
                    ),
                    "default": False,
                },
            },
            "required": ["email_id"],
        },
    },
    {
        "name": "apply_label",
        "description": (
            "Apply a Gmail label (folder) to an email and optionally archive it. "
            "Use label names: 'Work', 'Personal', 'Important', 'Needs Reply'. "
            "Creates the label automatically if it doesn't exist. "
            "You MUST call classify_and_act first."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "email_id": {
                    "type": "string",
                    "description": "The Gmail message ID.",
                },
                "label_name": {
                    "type": "string",
                    "description": "Label name, e.g. 'Work', 'Personal', 'Important', 'Needs Reply'.",
                },
                "archive": {
                    "type": "boolean",
                    "description": "Remove from INBOX after labelling (default true).",
                    "default": True,
                },
            },
            "required": ["email_id", "label_name"],
        },
    },
    {
        "name": "download_attachments",
        "description": (
            "Download all attachments of an email and save them to a local directory "
            "organised by category. Call this for every email with attachments "
            "that is NOT being deleted."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "email_id": {
                    "type": "string",
                    "description": "The Gmail message ID.",
                },
                "category": {
                    "type": "string",
                    "enum": ["work", "personal", "important", "other"],
                    "description": "Storage sub-directory category.",
                },
            },
            "required": ["email_id", "category"],
        },
    },
    {
        "name": "create_draft_reply",
        "description": (
            "Create a Gmail draft reply to an email. "
            "Call this for every email classified as 'needs-reply'. "
            "Write a complete, polite reply in reply_body."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "email_id": {
                    "type": "string",
                    "description": "The Gmail message ID being replied to.",
                },
                "reply_body": {
                    "type": "string",
                    "description": "Full text of the reply (plain text).",
                },
                "reply_tone": {
                    "type": "string",
                    "enum": ["professional", "friendly", "brief"],
                    "description": "Tone used — for logging and future calibration.",
                    "default": "professional",
                },
            },
            "required": ["email_id", "reply_body"],
        },
    },
    {
        "name": "mark_as_read",
        "description": (
            "Mark an email as read. "
            "Call this after finishing all actions for an email."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "email_id": {
                    "type": "string",
                    "description": "The Gmail message ID.",
                },
            },
            "required": ["email_id"],
        },
    },
    {
        "name": "get_processing_summary",
        "description": (
            "Return a count of all actions taken so far in this session. "
            "Use this to track progress and avoid re-processing emails."
        ),
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    {
        "name": "flag_for_human_review",
        "description": (
            "Mark an email as requiring human attention. "
            "Use this when you are genuinely unsure and 'skip' is not sufficient."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "email_id": {
                    "type": "string",
                    "description": "The Gmail message ID.",
                },
                "reason": {
                    "type": "string",
                    "description": "Why you cannot process this email automatically.",
                },
            },
            "required": ["email_id", "reason"],
        },
    },
]
