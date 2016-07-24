import re
import json
import codecs


def handle_mocked_comments(request):
    json_data = json.loads(json_file('single_post_comments.json'))

    path_url = request.path_url
    floor = int(re.search('\?after=(\d+)', path_url).group(1))

    last_floor = floor + 30
    last_floor = len(json_data) if last_floor > len(json_data) else last_floor

    response_data = json_data[floor:last_floor]

    return (200, {}, json.dumps(response_data))


def json_file(path, folder='./tests/data/'):
    return json.load(codecs.open(folder + path, 'r', 'utf-8'))
