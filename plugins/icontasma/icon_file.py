# /home/johnb/tasma-code-absulut/src/icons.py

# Definição de ícones e cores associadas
# As cores devem corresponder às constantes do curses (YELLOW, GREEN, etc.)

DEFAULT_ICON = ""
DIR_ICON = ""

# Extensão -> (Ícone, Cor)
FILE_ICONS = {
    "py": ("", "YELLOW"),
    "txt": ("", "WHITE"),
    "md": ("", "CYAN"),
    "json": ("", "YELLOW"),
    "js": ("", "YELLOW"),
    "ts": ("", "BLUE"),
    "html": ("", "RED"),
    "css": ("", "BLUE"),
    "c": ("", "BLUE"),
    "cpp": ("", "BLUE"),
    "h": ("", "MAGENTA"),
    "java": ("", "RED"),
    "go": ("", "CYAN"),
    "rs": ("", "RED"),
    "php": ("", "MAGENTA"),
    "rb": ("", "RED"),
    "sh": ("", "GREEN"),
    "yml": ("", "MAGENTA"),
    "yaml": ("", "MAGENTA"),
    "toml": ("", "MAGENTA"),
    "ini": ("", "WHITE"),
    "conf": ("", "WHITE"),
    "git": ("", "RED"),
    "gitignore": ("", "RED"),
}

def get_icon_info(name, is_dir):
    """Retorna (icone, nome_cor) para um dado arquivo."""
    if is_dir:
        return DIR_ICON, "BLUE"
    
    ext = name.split('.')[-1].lower() if '.' in name else ""
    return FILE_ICONS.get(ext, (DEFAULT_ICON, "WHITE"))