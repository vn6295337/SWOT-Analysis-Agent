from setuptools import setup, find_packages

setup(
    name="swot-analysis-agent",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="AI-powered strategic SWOT analysis with self-correcting agents",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/swot-analysis-agent",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "fastapi>=0.111.0",
        "uvicorn>=0.30.1",
        "python-dotenv>=1.2.1",
        "pydantic>=2.7.1",
    ],
    extras_require={
        "full": [
            "langgraph>=1.0.4",
            "langchain>=1.1.3",
            "langchain-groq>=1.1.0",
            "langsmith>=0.4.59",
            "tavily-python>=0.7.14",
            "streamlit>=1.36.0",
        ],
        "dev": [
            "pytest>=7.0.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "swot-agent=main:main",
        ],
    },
)
