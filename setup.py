import setuptools

with open("README.md") as f:
	long_description = f.read()

setuptools.setup(
	name = "pyradium",
	packages = setuptools.find_packages(),
	version = "0.0.15",
	license = "gpl-3.0",
	description = "Creating HTML presentations with LaTeX-ish features from XML source",
	long_description = long_description,
	long_description_content_type = "text/markdown",
	author = "Johannes Bauer",
	author_email = "joe@johannes-bauer.com",
	url = "https://github.com/johndoe31415/pyradium",
	download_url = "https://github.com/johndoe31415/pyradium/archive/0.0.15.tar.gz",
	keywords = [ "latex", "presentation", "template", "html" ],
	install_requires = [
		"mako",
		"pygments",
		"requests",
		"lzstr>=0.0.3",
	],
	entry_points = {
		"console_scripts": [
			"pyradium = pyradium.__main__:main"
		]
	},
	include_package_data = True,
	classifiers = [
		"Development Status :: 5 - Production/Stable",
		"Intended Audience :: Developers",
		"License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
		"Programming Language :: Python :: 3",
		"Programming Language :: Python :: 3 :: Only",
		"Programming Language :: Python :: 3.5",
		"Programming Language :: Python :: 3.6",
		"Programming Language :: Python :: 3.7",
		"Programming Language :: Python :: 3.8",
		"Programming Language :: Python :: 3.9",
	],
)
