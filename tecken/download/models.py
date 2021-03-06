# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, you can obtain one at http://mozilla.org/MPL/2.0/.

import hashlib
import random

from django.db import models
from django.core.cache import cache
from django.utils.encoding import force_bytes


class TotalCountMixin:
    @classmethod
    def total_count(cls, refresh=False):
        cache_key = f"total_count:{cls.__name__}"
        value = cache.get(cache_key)
        if refresh or value is None:
            value = cls.objects.all().count()
            # The slight-random on the expiry time is to avoid a stampeding
            # herd if they all expire at the same time.
            expires = int(60 * 60 * 24 * 31 + 10000 * random.random())
            cache.set(cache_key, value, expires)
        return value

    @classmethod
    def incr_total_count(cls, amount=1):
        cache_key = f"total_count:{cls.__name__}"
        try:
            cache.incr(cache_key, amount)
        except ValueError:
            cls.total_count()


class MissingSymbol(models.Model, TotalCountMixin):
    # Use this to quickly identify symbols when you need to look them up
    hash = models.CharField(max_length=32, unique=True)
    # Looking through 70,000 old symbol uploads, the longest
    # symbol was 39 char, debug ID 34 char, filename 44 char.
    # However, the missing symbols might be weird and wonderful so
    # allow for larger ones.
    symbol = models.CharField(max_length=150)
    debugid = models.CharField(max_length=150)
    filename = models.CharField(max_length=150)
    # These are optional because they only really apply when
    # symbol downloads are queried from stackwalker.
    code_file = models.CharField(max_length=150, null=True)
    code_id = models.CharField(max_length=150, null=True)
    # This is to keep track of every time we re-encounter this as missing.
    count = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True, db_index=True)

    def __repr__(self):
        return (
            f"<{self.__class__.__name__} id={self.id} "
            f"{self.symbol!r} / "
            f"{self.debugid!r} / "
            f"{self.filename!r}>"
        )

    @classmethod
    def make_md5_hash(cls, *strings):
        return hashlib.md5(
            force_bytes(":".join(x for x in strings if x is not None))
        ).hexdigest()
