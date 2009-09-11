from setuptools import setup, find_packages

setup(
    name = "django-test-utils",
    version = "0.3",
    packages = find_packages(),
    author = "Eric Holscher",
    author_email = "eric@ericholscher.com",
    description = "A package to help testing in Django",
    url = "http://github.com/ericholscher/django-test-utils/tree/master",
    download_url='http://www.github.com/ericholscher/django-test-utils/tarball/0.3.0',
    test_suite = "test_project.runtests.runtests",
    include_package_data = True,
    install_requires=[
        'BeautifulSoup',
    ]
    )
