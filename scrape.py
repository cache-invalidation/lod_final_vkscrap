from .credentials import ANTICAPTCHA_KEY, VK_LOGIN, VK_PASSWORD, VK_TOKEN
from vk_api import VkApi
from vk_api.utils import get_random_id
from time import sleep
from itertools import repeat


vk_session = VkApi(token=VK_TOKEN)
vk = vk_session.get_api()

def get_group_screen_name_by_id(id):
    response = vk.groups.getById(group_id=id)
    return response[0]['screen_name']

def get_link(item):
    """
    Turns an item into a link
    """

    link = "https://vk.com/"

    if item['to_id'] > 0:
        link += 'id' + str(item['to_id'])
    else:
        screen_name = get_group_screen_name_by_id(-item['to_id'])
        link += screen_name

    link += "?w=wall" + str(item['to_id']) + '_' + str(item['id'])

    return link

def process_mention(item):
    """
    Process single mention item
    """
    if item['from_id'] < 0:
        return None

    result = dict()
    result['text'] = item['text']
    result['date'] = item['date']
    result['link'] = get_link(item)
    result['mentioned_by'] = item['from_id']

    return result

def get_mentions(user_id, max_mentions):
    """
    Find mentions of specific user

    Arguments:
    ----------
    user_id: int
        User to scrap mentions of

    max_mentions: int
        Maximum amount of posts to scrape

    Returns:
    --------
    list[dict] -- results of parsing, where
        'text' -- Text of the post
        'date' -- time of post creation in unixtime
        'link' -- link to the post
        'user' -- id of user that was mentioned
        'mentioned_by' -- id of user that has mentioned requested one
    """

    answer = vk.newsfeed.getMentions(owner_id=user_id, count=20)
    max_mentions = min(max_mentions, answer['count'])
    n_iters = (max_mentions + 49) // 50

    result = list()
    ids = repeat(user_id)

    for i in range(n_iters):
        answer = vk.newsfeed.getMentions(owner_id=user_id, count=50, offset = i * 50)

        answer = map(process_mention, answer['items'])
        answer = filter(lambda x: x is not None, answer)
        answer = zip(ids, answer)
        answer = map(lambda xs: xs[1].update({'user': xs[0]}) or xs[1], answer)

        result += list(answer)

    return result

def get_link_wall_post(item):
    if 'owner_id' not in item:
        print(item)

    id = str(item['owner_id'])
    return 'https://vk.com/id{}?w=wall{}_{}'.format(id, id, str(item['id']))

def process_post(item):
    """
    Process single item from get_posts
    """

    result = dict()
    result['date'] = item['date']
    result['user'] = item['from_id']
    result['text'] = item['text']
    result['link'] = get_link_wall_post(item)

    return result

def get_posts(owner_id, max_posts):
    """
    Get list of user's posts

    Arguments:
    ----------
    user_id: int
        ID of user to scrape posts for

    max_posts: int
        Maximal number of posts to scrape

    Returns:
    --------
    list[dict] with results, more specifically, each dict contains 
        'user' -- ID of author
        'date' -- Date and time of post creation (in Unixtime)
        'text' -- Text of the post
        'link' -- Link to the post
    """

    answer = vk.wall.get(owner_id=owner_id, filter='owner')
    max_posts = min(answer['count'], max_posts)
    n_iters = (max_posts + 99) // 100

    result = list()

    for i in range(n_iters):
        answer = vk.wall.get(owner_id=owner_id, count=100, offset=100*i, filter='owner')
        answer = answer['items']
        answer = map(process_post, answer)
        result += list(answer)

    return result 


