try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

exec(open('gtts_token/version.py').read())

setup(
    name='gTTS-token',
    version=__version__,
    author='Guy Dipietro',
    author_email='Guy_Dipietro@bose.com',
    url='https://github.com/BoseCorp/gTTS-token',
    download_url="https://ingress-platform.live-aws-useast1.bose.io/dev/svc-core-devops-nexus/prod/core-devops-nexus-core/repository/gTTS-token-Bose/",
    packages=['gtts_token'],
    license='MIT',
    description='Calculates a token to run the Google Translate text to speech',
    long_description=open('README.md').read(),
    install_requires=[
        "requests"
    ],
    classifiers=[
          'Environment :: Console',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: MIT License',
          'Operating System :: MacOS :: MacOS X',
          'Operating System :: Unix',
          'Operating System :: POSIX',
          'Operating System :: POSIX :: Linux',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3.3',
          'Programming Language :: Python :: 3.4',
          'Topic :: Software Development :: Libraries',
          'Topic :: Multimedia :: Sound/Audio :: Speech'
    ],
)
