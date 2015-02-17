from setuptools import setup, find_packages
import os
import onlinejudge


CLASSIFIERS = [
    'Development Status :: 3 - Alpha',
    'Environment :: Web Environment',
    'Framework :: Django',
    'Intended Audience :: Developers',
    'Intended Audience :: Education',
    'License :: OSI Approved :: BSD License',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Topic :: Education :: Computer Aided Instruction (CAI)'
    'Topic :: Education :: Testing',
    'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    'Topic :: Software Development',
    'Topic :: Software Development :: Libraries :: Application Frameworks',
    "Programming Language :: Python :: 2.7",
]

setup(
    author="Damir Arbula",
    author_email="damir.arbula@gmail.com",
    name='django-onlinejudge',
    version=onlinejudge.__version__,
    description='Django Online Judge',
    long_description=open(os.path.join(os.path.dirname(__file__), 'README.md')).read(),
    #url='',
    license='BSD License',
    platforms=['OS Independent'],
    classifiers=CLASSIFIERS,
    packages=find_packages(),
    exclude_package_data={'': ['README.rst']},
    install_requires=[
        'Django>=1.6,<1.7',
        'Django-Select2>=4.2.2',
        'Markdown>=2.5.1',
        'django-contrib-comments>=1.5',
        'django-crispy-forms>=1.4.0',
        'django-markup>=0.4',
        'django-sekizai>=0.7',
        'django-taggit>=0.12.2',
        'South>=1.0.1',
        'celery==3.1.16',
        'django_ace>=1.0.2-dev',
    ],
    dependency_links=['https://github.com/bradleyayers/django-ace/tarball/master/74a9cd9d51#egg=django_ace-1.0.2-dev']
    #tests_require=[
    #],
    #
    #include_package_data=True,
    #zip_safe=False,
    #test_suite='runtests.main',
)
