# -*- coding: utf-8 -*-

"""Extractors for https://www.freepik.com/"""

from .common import Extractor, Message
from .. import text, util

BASE_PATTERN = r"(?:https?://)?www\.freepik\.com"


class FreepikExtractor(Extractor):
    """Base class for Freepik extractors"""
    category = "freepik"
    directory_fmt = ("{category}",)
    filename_fmt = "{id}.{extension}"
    archive_fmt = "{id}"
    root = "https://www.freepik.com"
    page_start = 1
    per_page = 20

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.item = match.group(1)

    def items(self):
        fmt = self.config("format") or "raw"
        metadata = self.metadata()

        for item in self.items_to_extract():
            util.delete_items(
                item, ("unnecessary_fields", "to_remove"))
            url = item["urls"][fmt]
            text.nameext_from_url(url, item)

            if metadata:
                item.update(metadata)
            item["extension"] = "jpg"  # or the appropriate file extension
            item["date"] = text.parse_datetime(item["created_at"])  # if available

            yield Message.Directory, item
            yield Message.Url, url, item

    @staticmethod
    def metadata():
        return None

    def skip(self, num):
        pages = num // self.per_page
        self.page_start += pages
        return pages * self.per_page

    def _pagination(self, url, params, results=False):
        params["per_page"] = self.per_page
        params["page"] = self.page_start

        while True:
            items = self.request(url, params=params).json()
            if results:
                items = items["results"]
            yield from items

            if len(items) < self.per_page:
                return
            params["page"] += 1


class FreepikImageExtractor(FreepikExtractor):
    """Extractor for a single image from Freepik"""
    subcategory = "image"
    pattern = BASE_PATTERN + r"/download-file/([^/?#]+)"
    example = "https://www.freepik.com/download-file/ID"

    def items_to_extract(self):
        url = "{}/api/v1/download".format(self.root)
        return (self.request(url, params={"id": self.item}).json(),)


# Define other extractors for user, collection, search, etc.
