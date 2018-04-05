from operator import itemgetter

def get_channel_id(youtube):
    response = youtube.clientchannels().list(
        part="id,snippet",
        mine=True,
        maxResults=1
    ).execute()
    channel = response.get("items", [])[0]
    return channel["id"]

def get_live_broadcast(youtube):
    broadcast = {
        'id': "",
        'title': "",
        'liveChatId': ""
    }
    response = youtube.liveBroadcasts().list(
        part="id,snippet",
        mine=True,
        broadcastType="persistent",
        maxResults=10
    ).execute()

    items = response.get("items", []);
    item = itemgetter(0)(items)
    if (item):
        broadcast['id'] = item["id"]
        broadcast['title'] = item["snippet"]["title"]
        broadcast['liveChatId'] = item["snippet"]["liveChatId"]

    return broadcast

def get_live_chat_messages(youtube, liveChatId, pageToken=None):
    if (pageToken):
        request = youtube.liveChatMessages().list(
            liveChatId=liveChatId,
            part="id,snippet,authorDetails",
            pageToken=pageToken
        )
    else:
        request = youtube.liveChatMessages().list(
            liveChatId=liveChatId,
            part="id,snippet,authorDetails"
        )

    response = request.execute()
    return {
        'chat_messages': response.get("items", []),
        'next_page_token': response['nextPageToken'],
        'polling_interval_seconds': response['pollingIntervalMillis'] / 1000
    }

def get_live_chat_message(items):
    for item in items:
        yield {
            'id': item["id"],
            'message': item["snippet"]["displayMessage"],
            'user': item["authorDetails"]["displayName"]
        }

def post_message(youtube, live_chat_id, message):
    return youtube.liveChatMessages().insert(
        part="snippet",
        body=dict(
            snippet=dict(
                liveChatId=live_chat_id,
                type="textMessageEvent",
                textMessageDetails=dict(
                    messageText=message
                )
            ),
        )
    ).execute()
