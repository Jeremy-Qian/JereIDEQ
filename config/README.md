# Configuration System

This directory contains the configuration files for JereIDEQ. The IDE has been refactored to use JSON configuration files instead of hardcoded values.

## Configuration Files

### theme.json
Contains all theme-related configuration including:
- Editor appearance (background, font family and size)
- Line number colors
- Status bar styling
- Syntax highlighting colors
- Tab appearance and colors
- Welcome screen colors

### editor.json
Contains editor behavior configuration including:
- Auto-pairing settings (enabled/disabled and character pairs)
- Auto-indent settings (enabled/disabled and character pairs)
- Line number visibility settings
- Syntax highlighting settings (keywords and built-ins)
- Font tab size

## Configuration Structure

The configuration system uses a hierarchical JSON structure with dot notation access. For example, to access the editor background color:

```python
from src.config.config_manager import config_manager
background_color = config_manager.get_config_value('theme', 'editor.background', '#FFFFFF')
```

## Modifying Configuration

You can modify the configuration by editing the JSON files directly. The changes will be loaded the next time the application starts.

## Adding New Configuration

To add new configuration values:

1. Add the appropriate key/value pair to the relevant JSON file
2. Access the value in code using `config_manager.get_config_value()` with dot notation
3. Provide a sensible default value as the third parameter for backward compatibility

## Default Values

The configuration system provides default values for all settings, ensuring the application will work even if configuration files are missing or incomplete.
