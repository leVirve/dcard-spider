API_ROOT = 'http://dcard.tw/_api'
FORUMS = 'forums'
POSTS = 'posts'


forums_url = '{api_root}/{api_forums}'.format(
    api_root=API_ROOT,
    api_forums=FORUMS
)

posts_meta_url_pattern = '{api_root}/{api_forums}/{{forum}}/{api_posts}'.format(
    api_root=API_ROOT,
    api_forums=FORUMS,
    api_posts=POSTS,
)

post_url_pattern = '{api_root}/{api_posts}/{{post_id}}'.format(
    api_root=API_ROOT,
    api_posts=POSTS,
)

post_links_url_pattern = '{post_url}/links'.format(
    post_url=post_url_pattern
)

post_comments_url_pattern = '{post_url}/comments'.format(
    post_url=post_url_pattern
)
