# TODO: is this dead code ?
import re

from django.contrib.postgres.search import (
    SearchQuery,
    SearchRank,
    SearchVector,
    TrigramSimilarity,
)
from django.db import connection
from django.db.models import Count, F

from catalog.models import Course


def search_course(string):

    slug_matches = re.findall(r"([A-Za-z]+)[- ]{0,1}([A-Za-z])[- ]{0,1}(\d+)", string)

    if slug_matches:
        fac, middle, digits = slug_matches[0]
        slug = f"{fac}-{middle}-{digits}"
        slug = slug.lower()
        exact_slug = Course.objects.filter(slug__iexact=slug).annotate(
            Count("document")
        )
        if len(exact_slug) > 0:
            return exact_slug

    if connection.vendor != "postgresql":
        return Course.objects.filter(name__contains=string)

    if len(string) < 6:
        similarity = 0.05
    else:
        similarity = 0.2

    vector = SearchVector("slug", config="french") + SearchVector(
        "name", config="french"
    )
    query = SearchQuery(string, config="french")

    return (
        Course.objects.annotate(
            rank=SearchRank(vector, query),
            name_similarity=TrigramSimilarity("name", string),
            slug_similarity=TrigramSimilarity("slug", string),
            document__count=Count("document"),
            similarity=F("name_similarity") + F("slug_similarity"),
        )
        .filter(similarity__gt=similarity)
        .order_by("-rank", "-similarity", "-document__count")
    )
