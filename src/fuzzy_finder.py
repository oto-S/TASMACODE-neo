import curses
import os

class FuzzyFinderWindow:
    def __init__(self, ui, project_root, tab_manager, show_hidden=False):
        self.ui = ui
        self.project_root = project_root
        self.tab_manager = tab_manager
        self.show_hidden = show_hidden
        self.stdscr = ui.stdscr
        self.active = True
        
        self.query = ""
        self.selected_idx = 0
        self.scroll_offset = 0
        
        self.all_files = self._get_file_list()
        self.filtered_files = self.all_files

    def _get_file_list(self):
        """Recursively gets all files in the project root."""
        file_list = []
        for root, dirs, files in os.walk(self.project_root):
            if not self.show_hidden:
                # Exclude hidden directories and files
                dirs[:] = [d for d in dirs if not d.startswith('.')]
                files = [f for f in files if not f.startswith('.')]
            
            for file in files:
                # Store path relative to project root
                full_path = os.path.join(root, file)
                relative_path = os.path.relpath(full_path, self.project_root)
                file_list.append(relative_path)
        return sorted(file_list)

    def _fuzzy_match(self):
        """Filters and sorts files based on the query."""
        if not self.query:
            self.filtered_files = self.all_files
            return

        query_chars = list(self.query.lower())
        matches = []
        
        for filepath in self.all_files:
            lower_path = filepath.lower()
            it = iter(lower_path)
            if all(c in it for c in query_chars):
                matches.append(filepath)
        
        self.filtered_files = matches
        self.selected_idx = 0
        self.scroll_offset = 0

    def run(self):
        """Main loop for the fuzzy finder window."""
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
        win_h = min(20, h - 4)
        win_w = min(80, w - 6)
        win_y = 3
        win_x = (w - win_w) // 2

        win = curses.newwin(win_h, win_w, win_y, win_x)
        win.bkgd(' ', curses.color_pair(5))
        win.box()
        
        win.addstr(1, 2, f"Find File: {self.query}")
        win.addstr(2, 1, "─" * (win_w - 2))

        list_y = 3
        max_items = win_h - 4
        
        if self.selected_idx < self.scroll_offset: self.scroll_offset = self.selected_idx
        if self.selected_idx >= self.scroll_offset + max_items: self.scroll_offset = self.selected_idx - max_items + 1

        for i in range(max_items):
            data_idx = self.scroll_offset + i
            if data_idx >= len(self.filtered_files): break
            
            filepath = self.filtered_files[data_idx]
            style = curses.A_REVERSE if data_idx == self.selected_idx else curses.A_NORMAL
            win.addstr(list_y + i, 2, filepath.ljust(win_w - 4), style)

        win.refresh()

    def handle_input(self, key):
        key_code = key if isinstance(key, int) else ord(key)

        if key_code == 27: self.active = False
        elif key_code == curses.KEY_UP: self.selected_idx = max(0, self.selected_idx - 1)
        elif key_code == curses.KEY_DOWN: self.selected_idx = min(len(self.filtered_files) - 1, self.selected_idx + 1)
        elif key_code in (10, 13):
            if self.filtered_files:
                relative_path = self.filtered_files[self.selected_idx]
                full_path = os.path.join(self.project_root, relative_path)
                self.tab_manager.open_file(full_path)
            self.active = False
        elif key_code in (curses.KEY_BACKSPACE, 127, 8):
            self.query = self.query[:-1]
            self._fuzzy_match()
        elif isinstance(key, str) and key.isprintable():
            self.query += key
            self._fuzzy_match()