#!/usr/bin/env python3
"""Sincroniza as mensagens do canal de change-log do Discord com a wiki."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
import sys
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


API_BASE = "https://discord.com/api/v10"
GUILD_ID = os.getenv("DISCORD_GUILD_ID", "1373314901145292932")
CHANNEL_ID = os.getenv("DISCORD_CHANNEL_ID", "1373314902977937451")
CHANNEL_URL = f"https://discord.com/channels/{GUILD_ID}/{CHANNEL_ID}"
OUTPUT_PATH = Path(
    os.getenv(
        "DISCORD_CHANGELOG_OUTPUT",
        Path(__file__).resolve().parents[1] / "discord-changelog.json",
    )
)


def normalize_author(author: dict) -> dict:
    return {
        "id": author.get("id"),
        "username": author.get("username"),
        "display_name": author.get("global_name") or author.get("username"),
    }


def normalize_attachment(attachment: dict) -> dict:
    return {
        "id": attachment.get("id"),
        "filename": attachment.get("filename"),
        "content_type": attachment.get("content_type"),
        "url": attachment.get("url"),
    }


def normalize_embed(embed: dict) -> dict:
    image = embed.get("image") or {}
    thumbnail = embed.get("thumbnail") or {}
    return {
        "title": embed.get("title"),
        "description": embed.get("description"),
        "url": embed.get("url"),
        "image_url": image.get("url") or thumbnail.get("url"),
        "fields": [
            {"name": field.get("name"), "value": field.get("value")}
            for field in embed.get("fields", [])
        ],
    }


def normalize_message(message: dict) -> dict:
    message_id = message.get("id")
    return {
        "id": message_id,
        "url": f"{CHANNEL_URL}/{message_id}",
        "timestamp": message.get("timestamp"),
        "edited_timestamp": message.get("edited_timestamp"),
        "content": message.get("content") or "",
        "author": normalize_author(message.get("author") or {}),
        "attachments": [
            normalize_attachment(attachment)
            for attachment in message.get("attachments", [])
        ],
        "embeds": [normalize_embed(embed) for embed in message.get("embeds", [])],
    }


def fetch_messages(token: str) -> list[dict]:
    query = urlencode({"limit": 100})
    request = Request(
        f"{API_BASE}/channels/{CHANNEL_ID}/messages?{query}",
        headers={
            "Authorization": f"Bot {token}",
            "User-Agent": "DigitalGalaxyWikiChangelog/1.0",
        },
    )
    with urlopen(request, timeout=30) as response:
        messages = json.load(response)

    normalized = [normalize_message(message) for message in messages]
    return sorted(
        normalized,
        key=lambda message: message.get("timestamp") or "",
        reverse=True,
    )


def write_output(messages: list[dict]) -> None:
    payload = {
        "guild_id": GUILD_ID,
        "channel_id": CHANNEL_ID,
        "channel_url": CHANNEL_URL,
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "messages": messages,
    }
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = OUTPUT_PATH.with_suffix(f"{OUTPUT_PATH.suffix}.tmp")
    temporary_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    temporary_path.replace(OUTPUT_PATH)


def main() -> int:
    token = os.getenv("DISCORD_BOT_TOKEN")
    if not token:
        print(
            "Defina DISCORD_BOT_TOKEN com o token de um bot que tenha acesso ao "
            "canal e a permissão Read Message History.",
            file=sys.stderr,
        )
        return 2

    try:
        messages = fetch_messages(token)
        write_output(messages)
    except HTTPError as error:
        details = error.read().decode("utf-8", errors="replace")
        print(f"Discord respondeu HTTP {error.code}: {details}", file=sys.stderr)
        return 1
    except (URLError, TimeoutError, OSError, json.JSONDecodeError) as error:
        print(f"Falha ao sincronizar o Discord: {error}", file=sys.stderr)
        return 1

    print(f"{len(messages)} mensagens sincronizadas em {OUTPUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
