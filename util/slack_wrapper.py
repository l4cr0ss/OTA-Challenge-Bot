import json
from typing import Any

from slack_sdk import WebClient
from slack_sdk.web import SlackResponse

from util.util import load_json


def validate_response(func):
    def wrapper():
        resp: SlackResponse = func()
        if resp:
            resp.validate()
        return resp

    return wrapper


class SlackWrapper:
    """
    Slack API wrapper
    """

    def __init__(self, slack_token):
        """
        SlackWrapper constructor.
        Connect to the real-time messaging API and
        load the bot's login data.
        """
        self.client = WebClient(slack_token)

        identity = self.client.users_identity()
        identity.validate()

        self.username = identity['user']['name']
        self.user_id = identity['user']['id']

    @validate_response
    def invite_user(self, user: str, channel: str) -> SlackResponse:
        """
        Invite a user to a given channel.
        """

        return self.client.conversations_invite(channel=channel, users=user)

    @validate_response
    def set_purpose(self, channel: str, purpose: str) -> SlackResponse:
        """
        Set the purpose of a given channel.
        """

        return self.client.conversations_setPurpose(channel=channel, purpose=purpose)

    @validate_response
    def set_topic(self, channel: str, topic: str) -> SlackResponse:
        """Set the topic of a given channel."""

        return self.client.conversations_setTopic(channel=channel, topic=topic)

    @validate_response
    def get_members(self) -> SlackResponse:
        """
        Return a list of all members.
        """

        return self.client.users_list()

    @validate_response
    def get_member(self, user_id: str) -> SlackResponse:
        """
        Return a member for a given user_id.
        """

        return self.client.users_info(user=user_id)

    @validate_response
    def create_channel(self, name: str, is_private=False) -> SlackResponse:
        """
        Create a channel with a given name.
        """

        return self.client.conversations_create(name=name, is_private=is_private)

    @validate_response
    def rename_channel(self, channel_id: str, new_name: str) -> SlackResponse:
        """
        Rename an existing channel.
        """

        return self.client.conversations_rename(channel=channel_id, name=new_name)

    @validate_response
    def get_channel_info(self, channel_id: str) -> SlackResponse:
        """
        Return the channel info of a given channel ID.
        """

        return self.client.conversations_info(channel=channel_id)

    @validate_response
    def get_channel_members(self, channel_id: str) -> Any:
        """ Return list of member ids in a given channel ID. """

        return self.get_channel_info(channel_id).data['channel']['members']

    @validate_response
    def update_channel_purpose_name(self, channel_id: str, new_name: str) -> SlackResponse:
        """
        Updates the channel purpose 'name' field for a given channel ID.
        """

        channel_info = self.get_channel_info(channel_id)

        purpose = load_json(channel_info['channel']['purpose']['value'])
        purpose['name'] = new_name

        return self.set_purpose(channel_id, json.dumps(purpose))

    @validate_response
    def post_message(self, channel_id: str, text: str, timestamp="", parse="full") -> SlackResponse:
        """
        Post a message in a given channel.
        channel_id can also be a user_id for private messages.
        Add timestamp for replying to a specific message.
        """

        return self.client.chat_postMessage(channel=channel_id, text=text, as_user=True, parse=parse,
                                            thread_ts=timestamp)

    @validate_response
    def post_message_with_react(self, channel_id: str, text: str, reaction: str, parse="full"):
        """Post a message in a given channel and add the specified reaction to it."""

        result = self.post_message(channel_id, text, "", parse)

        self.client.reactions_add(channel=channel_id, name=reaction, timestamp=result["ts"])

    @validate_response
    def get_message(self, channel_id: str, timestamp: str) -> SlackResponse:
        """Retrieve a message from the channel with the specified timestamp."""

        return self.client.conversations_history(channel=channel_id, latest=timestamp, limit=1, inclusive=True)

    @validate_response
    def update_message(self, channel_id: str, msg_timestamp: str, text: str, parse="full") -> SlackResponse:
        """Update a message, identified by the specified timestamp with a new text."""

        return self.client.chat_update(channel=channel_id, ts=msg_timestamp, text=text, as_user=True, parse=parse)

    @validate_response
    def get_public_channels(self) -> SlackResponse:
        """Fetch all public channels."""

        return self.client.conversations_list(types="public_channel")

    @validate_response
    def get_private_channels(self) -> SlackResponse:
        """Fetch all private channels in which the user participates."""

        return self.client.conversations_list(types="private_channel")

    @validate_response
    def archive_private_channel(self, channel_id: str) -> SlackResponse:
        """Archive a private channel"""

        return self.client.conversations_archive(channel=channel_id)

    @validate_response
    def archive_public_channel(self, channel_id: str) -> SlackResponse:
        """Archive a public channel"""

        return self.client.conversations_archive(channel=channel_id)

    @validate_response
    def add_reminder_hours(self, user: str, msg: str, offset: str) -> SlackResponse:
        """Add a reminder with a given text for the specified user."""

        return self.client.reminders_add(text=msg, time=f"in {offset} hours", user=user)

    @validate_response
    def get_reminders(self) -> SlackResponse:
        """Retrieve all reminders created by the bot."""

        return self.client.reminders_list()

    @validate_response
    def remove_reminder(self, reminder_id: str) -> SlackResponse:

        return self.client.reminders_delete(reminder=reminder_id)

    def remove_reminders_by_text(self, text: str):
        """Remove all reminders that contain the specified text."""
        reminders = self.get_reminders()

        for reminder in reminders.get("reminders", []):
            if text in reminder["text"]:
                self.remove_reminder(reminder["id"])
