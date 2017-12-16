from setuptools import setup

import md2slides

setup(
    name=md2slides.__title__,
    version=md2slides.__version__,
    description='Convert MarkDown file to slides (tex or pdf)',
    packages=['md2slides'],
    include_package_data=True,
    zip_safe=False,
    author=md2slides.__author__,
    author_email=md2slides.__author_email__,
    url='http://github.com/lixia/md2slides',
    license=md2slides.__license__,
    platforms=['any'],
    keywords=[
        'markdown',
        'tex',
        'slide'
    ],
    install_requires=['Markdown'],
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Development Status :: testing',
        'Operating System :: linux ',
        'Topic :: Text Processing :: Markup'
    ],
    long_description='''\
md2slides converts markdonw file to tex file or pdf file using pdflatex 
''',
    entry_points={
        'console_scripts': [
            'md2slides = md2slides.main:main',
        ]
    },
)
