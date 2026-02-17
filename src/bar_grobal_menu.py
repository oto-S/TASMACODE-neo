import curses

class GlobalMenuBar:
    def __init__(self, ui):
        self.ui = ui
        self.menus = [
            {"label": "Arquivos", "options": ["Novo Arquivo", "Abrir Arquivo", "Abrir Pasta", "Salvar", "Fechar Aba", "Sair"]},
            {"label": "Editar", "options": ["Desfazer", "Refazer", "Copiar", "Colar", "Recortar", "Selecionar Tudo"]},
            {"label": "Exibição", "options": ["Sidebar", "Chat IA", "Estrutura", "Split Vertical", "Split Horizontal"]},
            {"label": "Plugins", "options": ["Loja (F2)", "Gerenciar"]},
            {"label": "Configs", "options": ["Configurações", "Tema"]},
            {"label": "Ajuda", "options": ["Atalhos", "Sobre"]},
            {"label": "Pesquisa", "options": ["Buscar", "Substituir", "Buscar em Arquivos"]},
            {"label": "Novo", "options": ["Novo Arquivo", "Nova Pasta"]}
        ]
        self.active_menu_index = -1
        self.rects = []

    def draw(self, stdscr, width):
        # Draw bar background
        bar_attr = curses.color_pair(5) | curses.A_REVERSE
        try:
            stdscr.attron(bar_attr)
            stdscr.addstr(0, 0, " " * width)
            stdscr.attroff(bar_attr)
        except curses.error: pass

        current_x = 1
        self.rects = []
        
        for i, menu in enumerate(self.menus):
            label = f" {menu['label']} "
            attr = bar_attr
            if i == self.active_menu_index:
                attr = curses.color_pair(4) | curses.A_BOLD | curses.A_REVERSE
            
            try:
                stdscr.addstr(0, current_x, label, attr)
            except curses.error: pass
            
            self.rects.append((current_x, len(label)))
            current_x += len(label)

        # Draw dropdown if active
        if self.active_menu_index != -1:
            self._draw_dropdown(stdscr, self.active_menu_index)

    def _draw_dropdown(self, stdscr, index):
        menu = self.menus[index]
        x = self.rects[index][0]
        y = 1
        options = menu['options']
        max_len = max(len(o) for o in options) + 4
        
        for i, option in enumerate(options):
            try:
                # Shadow/Background
                stdscr.addstr(y + i, x, f" {option} ".ljust(max_len), curses.color_pair(5) | curses.A_REVERSE)
            except curses.error: pass

    def handle_mouse(self, mx, my, event_type):
        # Hover logic (Move)
        if event_type == 'move':
            if my == 0:
                for i, (x, w) in enumerate(self.rects):
                    if x <= mx < x + w:
                        if self.active_menu_index != i:
                            self.active_menu_index = i
                            return True, None # Redraw needed
            return False, None

        # Click logic
        if self.active_menu_index != -1:
            menu = self.menus[self.active_menu_index]
            x = self.rects[self.active_menu_index][0]
            options = menu['options']
            max_len = max(len(o) for o in options) + 4
            
            if 1 <= my <= len(options) and x <= mx < x + max_len:
                return True, options[my - 1]
            
            self.active_menu_index = -1 # Close if clicked outside
            return True, None
            
        return False, None