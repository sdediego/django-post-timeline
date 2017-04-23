from django.core.cache import cache

# Create your caches here.

CACHE_KEYS = {
    'user_keys': {
        # user primary key (pk = user.pk)
        'posts': 'tml_p-{pk}',
        'timeline': 'tml_t-{pk}',
        'posts_timeline': 'tml_pt-{pk}'
    },
    'post_keys': {
        # post primary key (pk = post.pk)
        'comments': 'tml_c-{pk}',
        'approved_comments': 'tml_ac-{pk}',
        'disapproved_comments': 'tml_dc-{pk}',
    },
}


CACHE_BUST = {
    'posts_timeline': [
        'posts',
        'timeline',
        'posts_timeline',
    ],
    'comments': [
        'comments',
        'approved_comments',
        'disapproved_comments',
    ],
    'approved_comments': [
        'approved_comments',
    ],
    'disapproved_comments': [
        'disapproved_comments',
    ],
}


def cache_bust(cache_types):
    """
    Bust the cache for a given type.
    The 'cache_types' parameters is a list
    of tuples (key_type, pk).
    """
    for key_type, pk in cache_types:
        bust_types = CACHE_BUST.get(key_type, None)
        keys = [make_key(to_bust, pk) for to_bust in bust_types]
        cache.delete_many(keys)


def make_key(key_type, pk):
    """
    Build the cache key for a particular type of cached value.
    """
    key = CACHE_KEYS['user_keys'].get(key_type, None)
    if key is None:
        key = CACHE_KEYS['post_keys'].get(key_type)
    key.format(pk=pk)
    return key


def make_key_many(cache_types):
    """
    Build the cache key for several cache values.
    """
    keys = {}
    for key_type, pk in cache_types:
        key = make_key(key_type, pk)
        keys.update({key_type: key})
    return keys
