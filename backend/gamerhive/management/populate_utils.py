from gamerhive.models import Platform, Game, Company

def get_platform_ids(families):
    ids = list(Platform.objects.filter(name__icontains=families[0]).values_list("igdb_platform_id", flat=True))
    for family in families[1:]:
        ids += list(Platform.objects.filter(name__icontains=family).values_list("igdb_platform_id", flat=True))
    return ids

def create_unique_slug(name):
    from django.utils.text import slugify
    base_slug = slugify(name)
    slug = base_slug
    counter = 1
    while Game.objects.filter(slug=slug).exists():
        slug = f"{base_slug}-{counter}"
        counter += 1
    return slug
