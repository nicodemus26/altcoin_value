import os
import os.path
from setuptools import setup

author = "Nicodemus Allen-Tonar"
author_email = "nicodemus26@gmail.com"
version = "0.0.0"
package_name = "altcoin_value"
with open(os.path.join(package_name, "__init__.py")) as f:
    for line in f:
        fragments = [l.strip() for l in line.split()]
	if (len(fragments) > 2 and
            fragments[0] == "__version__" and fragments[1] == "="):
            version_expr = " ".join(fragments[2:])
            version = eval(version_expr)
            continue

setup(
    name = package_name,
    version = version,
    author = author,
    author_email = author_email,
    description = "A tool for evaluating total value of diserate altcoins",
    license = "GPL3",
    keywords = "altcoint cryptocurrency",
    url = "https://github.com/nicodemus26/altcoin_value",
    packages=[package_name],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: GPL3 License",
    ],
    entry_points = {
        "console_scripts": [
            "%s = %s.main:main" % (package_name, package_name),
        ],
    },
)
