import pytest


@pytest.fixture(autouse=True)
def use_unhashed_static_storage(settings):
    # Tests don't run `npm run build` / `collectstatic`, so the manifest
    # CompressedManifestStaticFilesStorage needs (staticfiles.json) never
    # gets created. Fall back to the plain storage, which resolves
    # {% static %} tags without requiring a manifest entry to exist.
    settings.STORAGES["staticfiles"]["BACKEND"] = (
        "django.contrib.staticfiles.storage.StaticFilesStorage"
    )
