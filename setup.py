from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as f:
    requirements = f.read().splitlines()

setup(
    name="linkedin-job-matcher",
    version="0.1.0",
    author="LinkedIn Job Matcher Team",
    author_email="contact@example.com",
    description="A platform connecting candidates to job opportunities using AI-powered matching",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-username/linkedin-job-matcher",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Framework :: Flask",
        "Intended Audience :: Developers",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.11",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "linkedin-job-matcher=app.cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)