from setuptools import setup, find_packages

setup(
    name = "django-testmaker",
    version = "0.2a3",
    packages = find_packages(),
    author = "Eric Holscher",
    author_email = "eric@ericholscher.com",
    description = "A package to help automate creation of testing in Django",
    url = "http://code.google.com/p/django-testmaker/",
    include_package_data = True
)
