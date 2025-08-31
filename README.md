## achie's replay namer

this wasn't really ever meant for anyone but me to use, so it hard codes some stuff and assumes that you have some tools that i use:
### tools
i recommend [astral uv](https://docs.astral.sh/uv/) since it will do all the package management for you, but you can also use pip to install the dependencies in [pyproject.toml](/pyproject.toml) if you really dont care for uv
### fix hard code
before using you need to point the script to your replay directories in [renaming.py](/renaming.py). it assumes that we play on eu and na, but it would be easy to change it to include kr if you want