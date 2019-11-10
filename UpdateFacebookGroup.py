import facebook
from dotenv import load_dotenv
import os

def UpdateMessageToFacebook(UpdateMessage: str):
    """
    Post the status update on Facebook Group.
    :param UpdateMessage:
    :return:
    """
    load_dotenv()
    Token = os.getenv("FacebookAccessToken")
    GroupID = os.getenv("BadmintonGroupID")

    # Instantiate GraphAPI with the proper token.
    graph = facebook.GraphAPI(Token)
    # Old code used to retrieve gorup ID
    #groups = graph.get_object("me/groups")
    #group_id = groups['data'][0]['id'] # we take the ID of the first group
    # Post message to the Group Feed.
    graph.put_object(GroupID, "feed", message=UpdateMessage)