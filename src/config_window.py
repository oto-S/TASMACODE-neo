# /home/johnb/tasma-code-absulut/src/config_window.py
import curses
from config import Config

class ConfigWindow:
    def __init__(self, ui, config):
        self.ui = ui
        self.config = config
        self.stdscr = ui.stdscr
        self.active = True
        self.default_config = Config("DEFAULTS_DUMMY")

        self.categories = ["Keys", "Colors", "Snippets", "Themes", "Settings"]
        self.current_category_idx = 0
        
        self.items = []
        self.current_item_idx = 0
        self.scroll_offset = 0
        
        self.filter_query = ""
        self.filtering = False

        self.load_items_for_category()

    def load_items_for_category(self):
        self.current_item_idx = 0
        self.scroll_offset = 0
        category = self.categories[self.current_category_idx]
        
        raw_items = []
        if category == "Keys":
            raw_items = sorted(self.config.keys.items())
        elif category == "Colors":
            raw_items = sorted(self.config.colors.items())
        elif category == "Snippets":
            raw_items = sorted(self.config.snippets.items())
        elif category == "Themes":
            themes = self.config.get_available_themes()
            raw_items = [(t, "Apply") for t in themes]
            if not raw_items:
                raw_items = [("No themes found", "in themes/ folder")]
        elif category == "Settings":
            raw_items = sorted(self.config.settings.items())

        # Aplica Filtro
        if self.filter_query:
            self.items = [i for i in raw_items if self.filter_query.lower() in str(i[0]).lower()]
        else:
            self.items = raw_items

    def run(self):
        original_timeout = self.stdscr.gettimeout()
        self.stdscr.timeout(-1) # Ensure blocking input
        try:
            while self.active:
                self.draw()
                key = self.ui.get_input()
                self.handle_input(key)
        finally:
            self.stdscr.timeout(original_timeout)

    def draw(self):
        h, w = self.ui.height, self.ui.width
        win_h = h - 4
        win_w = w - 6
        win_y = 2
        win_x = 3

        win = curses.newwin(win_h, win_w, win_y, win_x)
        win.bkgd(' ', curses.color_pair(5))
        win.box()
        win.addstr(0, 2, " Settings (F6) ", curses.A_BOLD)
        
        # Mostra status do filtro
        if self.filter_query or self.filtering:
            filter_txt = f" Filter: {self.filter_query} "
            win.addstr(0, win_w - len(filter_txt) - 2, filter_txt, curses.A_REVERSE)

        cat_x = 2
        for i, cat in enumerate(self.categories):
            style = curses.A_REVERSE if i == self.current_category_idx else curses.A_NORMAL
            win.addstr(2, cat_x, f" {cat} ", style)
            cat_x += len(cat) + 3

        item_y = 4
        max_items = win_h - 6
        
        if self.current_item_idx >= self.scroll_offset + max_items:
            self.scroll_offset = self.current_item_idx - max_items + 1
        if self.current_item_idx < self.scroll_offset:
            self.scroll_offset = self.current_item_idx

        for i in range(max_items):
            data_idx = self.scroll_offset + i
            if data_idx >= len(self.items): break
            
            key, value = self.items[data_idx]
            display_str = f"{key}: {value}"
            
            style = curses.A_NORMAL
            if data_idx == self.current_item_idx: style = curses.A_REVERSE
            
            win.addstr(item_y + i, 4, display_str.ljust(win_w - 6), style)

        help_str = "Tab:Category|Enter:Edit|/:Filter|s:Save|Esc:Close"
        if self.categories[self.current_category_idx] == "Themes":
            help_str += "|x:Export"
        win.addstr(win_h - 2, 2, help_str)
        win.refresh()

    def handle_input(self, key):
        # Modo de Filtro
        if self.filtering:
            if key == 27: # Esc cancela
                self.filtering = False
                self.filter_query = ""
                self.load_items_for_category()
            elif key in (10, 13): # Enter confirma
                self.filtering = False
            elif key in (curses.KEY_BACKSPACE, 127, 8):
                self.filter_query = self.filter_query[:-1]
                self.load_items_for_category()
            elif isinstance(key, str) and key.isprintable():
                self.filter_query += key
                self.load_items_for_category()
            return

        # Modo Normal
        key_code = key if isinstance(key, int) else ord(key)

        if key_code == 27: self.active = False
        elif key_code == curses.KEY_UP: self.current_item_idx = max(0, self.current_item_idx - 1)
        elif key_code == curses.KEY_DOWN: self.current_item_idx = min(len(self.items) - 1, self.current_item_idx + 1)
        elif key_code == 9: # Tab
            self.current_category_idx = (self.current_category_idx + 1) % len(self.categories)
            self.load_items_for_category()
        elif key_code in (10, 13): self.edit_current_item()
        elif key_code in (ord('s'), ord('S')):
            self.config.save_to_user_config()
            self.ui.prompt("Config saved. Color changes are applied immediately.")
            self.active = False
        elif key_code == ord('/'):
            self.filtering = True
        elif key_code == ord('r'):
            self.reset_current_item()
        elif key_code == ord('R'):
            self.reset_current_category()
        elif key_code == ord('x'):
            if self.categories[self.current_category_idx] == "Themes":
                self.export_current_theme()

    def edit_current_item(self):
        if not self.items: return
            
        key, old_value = self.items[self.current_item_idx]
        category = self.categories[self.current_category_idx]
        
        if category == "Themes":
            if key == "No themes found": return
            if self.config.apply_theme(key):
                self.ui._initialize_colors()
                self.ui.prompt(f"Theme '{key}' applied.")
            return
        
        if category == "Settings":
            if isinstance(old_value, bool):
                self.config.settings[key] = not old_value
            self.load_items_for_category()
            return

        # Para snippets, o valor pode ser longo. Mostramos uma versão curta.
        display_old_value = str(old_value).replace('\n', '\\n')[:40]
        new_value_str = self.ui.prompt(f"New value for '{key}' ({display_old_value}): ")
        
        if new_value_str is not None:
            if category == "Keys":
                try:
                    self.config.keys[key] = int(new_value_str)
                except ValueError:
                    self.ui.prompt("Invalid key value. Only integers are supported for now.")
                    return
            elif category == "Colors":
                if new_value_str.upper() in self.ui.color_map:
                    self.config.colors[key] = new_value_str.upper()
                    self.ui._initialize_colors() # Aplica cores dinamicamente
                else:
                    self.ui.prompt("Invalid color name.")
                    return
            elif category == "Snippets":
                # Usuário pode usar \n para novas linhas no prompt
                self.config.snippets[key] = new_value_str.replace('\\n', '\n')
            self.load_items_for_category()

    def reset_current_item(self):
        if not self.items: return
        
        key, _ = self.items[self.current_item_idx]
        category = self.categories[self.current_category_idx]
        
        if category == "Themes":
            self.ui.prompt("Cannot reset themes directly.")
            return

        confirm = self.ui.prompt(f"Reset '{key}' to default? (y/n): ")
        if not confirm or confirm.lower() != 'y':
            self.ui.prompt("Reset cancelled.")
            return

        new_value = None
        if category == "Keys":
            new_value = self.default_config.keys.get(key)
        elif category == "Colors":
            new_value = self.default_config.colors.get(key)
        elif category == "Snippets":
            new_value = self.default_config.snippets.get(key)
        elif category == "Settings":
            new_value = self.default_config.settings.get(key)
            
        if new_value is not None:
            if category == "Keys": self.config.keys[key] = new_value
            elif category == "Colors": 
                self.config.colors[key] = new_value
                self.ui._initialize_colors()
            elif category == "Snippets": self.config.snippets[key] = new_value
            elif category == "Settings": self.config.settings[key] = new_value
            self.ui.prompt(f"Reset '{key}' to default.")
            self.load_items_for_category()
        else:
            self.ui.prompt(f"No default value found for '{key}'.")

    def reset_current_category(self):
        """Resets all settings in the current category to their defaults."""
        category = self.categories[self.current_category_idx]
        if category == "Themes":
            self.ui.prompt("Cannot reset the Themes category.")
            return

        confirm = self.ui.prompt(f"Reset ALL settings in '{category}' to default? (y/n): ")
        if not confirm or confirm.lower() != 'y':
            self.ui.prompt("Reset cancelled.")
            return

        if category == "Keys":
            self.config.keys = self.default_config.keys.copy()
        elif category == "Colors":
            self.config.colors = self.default_config.colors.copy()
            self.ui._initialize_colors() # Apply changes immediately
        elif category == "Snippets":
            self.config.snippets = self.default_config.snippets.copy()
        elif category == "Settings":
            self.config.settings = self.default_config.settings.copy()

        self.ui.prompt(f"All settings in '{category}' have been reset.")
        self.load_items_for_category()

    def export_current_theme(self):
        name = self.ui.prompt("Export theme as (name): ")
        if name:
            if self.config.export_theme(name):
                self.ui.prompt(f"Theme '{name}' exported successfully.")
                self.load_items_for_category()
            else:
                self.ui.prompt("Failed to export theme.")