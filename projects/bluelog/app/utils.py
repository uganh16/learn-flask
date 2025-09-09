import random
from urllib.parse import urlparse, urljoin

from flask import redirect, request


def random_split(n, k):
    if n < 0 or k <= 0:
        return []
    if k == 1:
        return [n]
    indices = [0] + sorted(random.sample(range(n + k), k - 1)) + [n + k]
    return [indices[i+1]-indices[i]-1 for i in range(len(indices) - 1)]


def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc


def redirect_back(default='blog.index', **kwargs):
    for target in request.args.get('next'), request.referrer:
        if not target:
            continue
        if is_safe_url(target):
            return redirect(target)
    return redirect(default, **kwargs)
