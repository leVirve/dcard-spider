from dcard import Dcard
from pprint import pprint as print

if __name__ == '__main__':
    dcard = Dcard()

    #a = dcard.get_forums(no_school=True)
    b = dcard.get_post_ids('graduate', pages=2)
    print(len(b))
