import curses
import textwrap

class StoreUI:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.height, self.width = stdscr.getmaxyx()
        self.input_buffer = ""
        self.status_msg = ""
        self.is_loading = False
        self.scroll_offset = 0

    def draw(self, plugins=[], selected_idx=0, focus='input', confirm_delete=None):
        self.height, self.width = self.stdscr.getmaxyx()
        
        # Dimensões da janela
        win_h = min(25, self.height - 4)
        win_w = min(80, self.width - 4)
        win_y = (self.height - win_h) // 2
        win_x = (self.width - win_w) // 2

        # Cria janela
        win = curses.newwin(win_h, win_w, win_y, win_x)
        win.box()
        
        # Título
        title = " Tasma Store (Plugin Library) "
        win.addstr(0, (win_w - len(title)) // 2, title, curses.A_BOLD)

        # Instruções
        win.addstr(1, 2, "URL do GitHub (Tab alterna foco):", curses.A_DIM)
        
        # Caixa de Input
        input_box_y = 2
        input_box_x = 2
        input_width = win_w - 4
        
        # Desenha fundo da caixa de input
        input_attr = curses.A_REVERSE
        if focus == 'input':
            input_attr |= curses.A_BOLD
            
        win.attron(input_attr)
        win.addstr(input_box_y, input_box_x, " " * input_width)
        
        # Desenha o texto (com scroll simples se for muito longo)
        display_text = self.input_buffer
        if len(display_text) > input_width - 1:
            display_text = "..." + display_text[-(input_width - 4):]
        
        win.addstr(input_box_y, input_box_x, display_text)
        win.attroff(input_attr)

        # Cursor simulado
        if not self.is_loading and focus == 'input':
            cursor_pos = min(len(display_text), input_width - 1)
            win.addch(input_box_y, input_box_x + cursor_pos, ' ', curses.A_REVERSE | curses.A_BLINK)

        # Lista de Plugins
        list_y = 4
        win.addstr(list_y, 2, "Plugins Instalados (Del para remover):", curses.A_BOLD)
        
        list_start_y = list_y + 1
        list_available_h = win_h - list_start_y - 2
        
        # Prepara layout dos itens
        list_items = []
        for p in plugins:
            name = p['name']
            desc = p.get('desc')
            if desc:
                lines = textwrap.wrap(desc, 30)[:3]
            else:
                lines = ["[ ... ]"]
            # Altura = Nome(1) + Desc(len) + Sep(1)
            list_items.append({'name': name, 'lines': lines, 'h': 1 + len(lines) + 1})

        # Scroll logic
        if selected_idx < self.scroll_offset:
            self.scroll_offset = selected_idx
        
        # Garante que o item selecionado esteja visível (rolagem para baixo)
        while True:
            used_height = sum(item['h'] for item in list_items[self.scroll_offset : selected_idx])
            if used_height + list_items[selected_idx]['h'] > list_available_h:
                self.scroll_offset += 1
            else:
                break
            if self.scroll_offset > selected_idx:
                self.scroll_offset = selected_idx
                break
            
        current_y = list_start_y
        for i in range(self.scroll_offset, len(list_items)):
            item = list_items[i]
            if current_y + item['h'] > win_h - 3: break
            
            # Nome
            style = curses.A_BOLD
            if i == selected_idx and focus == 'list':
                style = curses.A_REVERSE | curses.A_BOLD
            
            icon = " "
            win.addstr(current_y, 2, f"{icon} {item['name']}", style)
            current_y += 1
            
            # Descrição
            for line in item['lines']:
                win.addstr(current_y, 4, line, curses.A_DIM)
                current_y += 1
            
            # Linha Separadora
            win.addstr(current_y, 2, "─" * (win_w - 6), curses.A_DIM)
            current_y += 1

        # Status / Loading
        if self.status_msg:
            color = curses.A_BOLD
            if "Erro" in self.status_msg: color = curses.A_BOLD # Poderia usar cor vermelha se disponível no contexto
            win.addstr(win_h - 3, 2, self.status_msg[:win_w-4], color)

        # Confirmação de Deleção (Overlay)
        if confirm_delete:
            display_name = confirm_delete
            if len(display_name) > 20: display_name = display_name[:17] + "..."
            msg = f" Deletar '{display_name}'? (y/n) "
            
            cy = win_h // 2
            cx = (win_w - len(msg)) // 2
            win.attron(curses.A_REVERSE | curses.A_BOLD)
            win.addstr(cy, cx, msg)
            win.attroff(curses.A_REVERSE | curses.A_BOLD)

        win.addstr(win_h - 2, 2, "Enter: Instalar | g: Repo | Esc: Sair", curses.A_DIM)
        win.refresh()