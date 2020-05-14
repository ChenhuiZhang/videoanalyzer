"""
Setup
"""
from setuptools import setup, find_packages

setup(
    name="videoanalyzer",
    version="0.0.1",
    author="Hermes Zhang",
    author_email="zhangchenhui2006@gmail.com",
    packages=find_packages(),
    description="Video Analyzer Tool",
    url="https://github.com/ChenhuiZhang/videoanalyzer",
    install_requires=['ffmpeg_python', 'av', 'numpy', 'matplotlib', 'pandas', 'ffmpeg'],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Topic :: Utilities"
    ],
    entry_points={
        'console_scripts': [
            'videoanalyzer = videoanalyzer.videoanalyzer:main',
        ]
    },
    python_requires='>=3.6',
)
