import json

from django.core.management.base import BaseCommand
from django.db import transaction

from catalog.models import Category, Course
from catalog.slug import normalize_slug


def get_category(slug, name=None, parent=None, type=None):
    cat, created = Category.objects.get_or_create(
        slug=slug, defaults={"name": name, "slug": slug, "type": type}
    )
    if created and parent:
        cat.parents.add(parent)
    return cat


class Command(BaseCommand):
    def handle(self, *args, **options):

        with open("catalog/management/parser/data/courses.json") as f:
            programs = json.load(f)

        with transaction.atomic():
            for course in Course.objects.all():
                course.categories.clear()
            for program_slug, courses in programs.items():
                category = get_category(program_slug)
                for course in courses.values():
                    bloc = course["bloc"]
                    p = get_category(
                        f"{program_slug}-{bloc}",
                        name=f"Bloc {bloc}",
                        parent=category,
                        type=Category.CategoryType.BLOC,
                    )
                    c = Course.objects.get_or_create(
                        slug=normalize_slug(course["id"]),
                        defaults={
                            "slug": normalize_slug(course["id"]),
                            "name": course["title"],
                        },
                    )[0]
                    c.categories.add(p)
