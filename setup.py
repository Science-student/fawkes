import os
import re
import sys
from shutil import rmtree

from setuptools import setup, Command

__PATH__ = os.path.abspath(os.path.dirname(__file__))

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

def read_version():
    __PATH__ = os.path.abspath(os.path.dirname(__file__))
    with open(os.path.join(__PATH__, 'fawkes', '__init__.py')) as f:
        version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", f.read(), re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find __version__ string")

__version__ = read_version()

class DeployCommand(Command):
    description = 'Build and deploy the package to PyPI.'
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    @staticmethod
    def status(s):
        print(s)

    def run(self):
        assert 'dev' not in __version__, (
            "Only non-devel versions are allowed. "
            "__version__ == {}".format(__version__))

        with os.popen("git status --short") as fp:
            git_status = fp.read().strip()
            if git_status:
                print("Error: git repository is not clean.\n")
                os.system("git status --short")
                sys.exit(1)

        try:
            self.status('Removing previous builds ...')
            rmtree(os.path.join(__PATH__, 'dist'))
        except OSError:
            pass

        self.status('Building Source and Wheel (universal) distribution ...')
        os.system(f"{sys.executable} setup.py sdist bdist_wheel")

        self.status('Uploading the package to PyPI via Twine ...')
        ret = os.system('twine upload dist/*')
        if ret != 0:
            sys.exit(ret)

        self.status('Creating git tags ...')
        os.system(f"git tag v{__version__}")
        os.system('git tag --list')
        sys.exit()

setup_requires = []

install_requires = [
    'numpy>=1.19.5',
    'tensorflow==2.6.3',
    'keras',
    'mtcnn',
    'pillow>=7.0.0',
    'bleach>=2.1.0'
]

setup(
    name='fawkes',
    version=__version__,
    license='BSD',
    description='An utility to protect user privacy',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url="https://github.com/Shawn-Shan/fawkes",
    author='Shawn Shan',
    author_email='shawnshan@cs.uchicago.edu',
    keywords='fawkes privacy ML',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        "Operating System :: OS Independent",
        'Programming Language :: Python :: 3',
        'Topic :: System :: Monitoring',
    ],
    packages=['fawkes'],
    install_requires=install_requires,
    setup_requires=setup_requires,
    entry_points={
        'console_scripts': ['fawkes=fawkes:main'],
    },
    cmdclass={
        'deploy': DeployCommand,
    },
    include_package_data=True,
    zip_safe=False,
    python_requires='>=3.6',
)
