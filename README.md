# ConfigManager

## Install

```sh
pip install git+https://github.com/yamause/configmanager.git
```

## Use

### Create basic.yml


Before you can use ConfigManager, you must define the configuration values.

- `name` : item name.
- `description` : description for item.
- `type` : item type. used to validate types. (string, int, float, bool)
- `default` : default value.

```yml
---
# basic.yml
- name: item
  description: your item
  type: string
  default: foo
- name: item2
  description: your item2
  type: int
  default: 100
```

### Code

```python
from configmanager import ConfigManager
from configmanager.source import DictConfigSource, EnvConfigSource

# Create an instance of ConfigManager
manager = ConfigManager(basic_config_path="basic.yml")

# Load the configuration
dict_source = DictConfigSource({"item": "bar"})  # Config source at dictionary
env_source = EnvConfigSource()  # Config source at environment

# Add a new source.
# If the same settings exist, the source added later will take precedence.
manager.add_source(dict_source)
manager.add_source(env_source)

# Load config
manager.load()

# Get config value
value = manager.get("item")
print(f"Value for 'item': {value}")
```

## Available configuration sources

### DictConfigSource

```python
from configmanager import ConfigManager
from configmanager.source import DictConfigSource

source = DictConfigSource({"item": "bar"})  # Config source at dictionary
manager.add_source(source)
```

### EnvConfigSource

```sh
export ITEM="bar"
```

```python
from configmanager import ConfigManager
from configmanager.source import EnvConfigSource

source = EnvConfigSource()  # Config source at environment
manager.add_source(source)
```

### CliConfigSource

```sh
python your_script.py --item bar
```

```python
from configmanager import ConfigManager

ConfigManager.get_cli_args()  # Config source at command args
```

### FileConfigSource

```yaml
# config.yml
item: bar
```

```python
from configmanager import ConfigManager
from configmanager import FileConfigSource

source = FileConfigSource("config.yml")  # Config source at yaml file
manager.add_source(source)
```
