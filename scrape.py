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


def get_mentions(user_id, max_mentions, offset=0):
    """
    Find mentions of specific user

    Arguments:
    ----------
    user_id: int
        User to scrap mentions of

    max_mentions: int
        Maximum amount of posts to scrape

    offset: int
        Offset to start loading

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
    max_mentions = min(max_mentions, answer['count'] - offset)
    if max_mentions <= 0:
        return []

    n_iters = (max_mentions + 49) // 50

    result = list()
    ids = repeat(user_id)

    for i in range(n_iters):
        count = cur_count = min(50, max_mentions - 50 * i)
        answer = vk.newsfeed.getMentions(
            owner_id=user_id, count=50, offset=i * 50 + offset)

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


def get_posts(owner_id, max_posts, offset=0):
    """
    Get list of user's posts

    Arguments:
    ----------
    user_id: int
        ID of user to scrape posts for

    max_posts: int
        Maximal number of posts to scrape

    offset: int
        Offset to start loading

    Returns:
    --------
    list[dict] with results, more specifically, each dict contains 
        'user' -- ID of author
        'date' -- Date and time of post creation (in Unixtime)
        'text' -- Text of the post
        'link' -- Link to the post
    """

    answer = vk.wall.get(owner_id=owner_id, filter='owner')
    max_posts = min(answer['count'] - offset, max_posts)
    if max_posts <= 0:
        return []

    n_iters = (max_posts + 99) // 100

    result = list()

    for i in range(n_iters):
        cur_count = min(100, max_posts - 100 * i)
        answer = vk.wall.get(owner_id=owner_id, count=cur_count,
                             offset=100*i+offset, filter='owner')
        answer = answer['items']
        answer = map(process_post, answer)
        result += list(answer)

    return result


def process_photo(item):
    """
    Process single instance of photo item
    """

    result = dict()

    result['user'] = item['owner_id']
    result['date'] = item['date']

    max_photo = None
    max_photo_width = 0

    for photo in item['sizes']:
        if photo['width'] >= max_photo_width:
            max_photo_width = photo['width']
            max_photo = photo


    result['link'] = max_photo['url']

    return result


def get_photos(owner_id, max_photos, offset=0):
    """
    Pull links to photos posted by user

    Arguments:
    ----------
    owner_id: int
        User to pull images for

    max_photos: int
        Maximal number of images to pull links for

    offset: int
        Offset to start loading

    Returns:
    --------
    list[dict] -- requested information about photos. More specifically, each dict contains:
        'link' -- link to photo
        'user' -- link to user 
        'date' -- date of publication in Unixcode format
    """
    answer = vk.photos.getAll(owner_id=owner_id)
    max_photos = min(max_photos, answer['count'] - offset)

    if max_photos <= 0:
        return []

    n_iters = (max_photos + 199) // 200

    result = list()

    for i in range(n_iters):
        cur_count = min(200, max_photos - 200 * i)
        answer = vk.photos.getAll(
            owner_id=owner_id, count=cur_count, offset=200 * i + offset)
        answer = map(process_photo, answer['items'])
        result += list(answer)

    return result


def get_data(user_id, batch_size=50, offset=0):
    """
    Quick and dirty function that gets at most 200 of each 

    Arguments:
    ----------
    user_id: int
        VK ID of user to pull data for

    offset: int
        Offset to start loading data from

    Returns:
    --------
        dict with results
            'photos' -- array of dicts describing pictures
            'posts' -- array of dicts describing posts
            'mentions' -- array of dicts describing mentions by other users
    """
    photos = get_photos(user_id, batch_size, offset)
    posts = get_posts(user_id, batch_size, offset)
    mentions = get_mentions(user_id, batch_size, offset)

    return {'photos': photos, 'posts': posts, 'mentions': mentions}
