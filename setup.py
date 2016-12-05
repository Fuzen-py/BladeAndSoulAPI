from setuptools import setup

setup(
    name='BladeAndSoul.py',
    version='0.0.2a3',
    packages=['BladeAndSoul'],
    package_data = {
        'BladeAndSoul': ['data/*']},
    license='MIT',
    author='Fuzen.py',
    description='Python3.5 Unofficial BladeAndSoul API',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Software Development :: Libraries :: Python Modules',
        ],
    keywords='Unofficial BladeAndSoul API',
    install_requires=['aiohttp', 'bs4', 'lxml', 'PyYaml'],
    zip_safe=False
)
