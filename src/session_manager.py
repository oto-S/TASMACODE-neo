# /home/johnb/tasma-code-absulut/src/session_manager.py
import json
import os

class SessionManager:
    """
    Responsabilidade: Gerenciar a persistência de estado da sessão (ex: última pasta aberta).
    Isola a lógica de I/O de configuração de sessão do fluxo principal.
    """
    def __init__(self, session_file="session.json"):
        # Define o caminho do arquivo de sessão relativo à raiz do projeto
        # __file__ é src/session_manager.py -> dirname é src/ -> dirname é root/
        base_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(base_dir)
        self.session_path = os.path.join(project_root, session_file)

    def _load_data(self):
        """Carrega todos os dados do arquivo de sessão."""
        if not os.path.exists(self.session_path):
            return {}
        try:
            with open(self.session_path, 'r') as f:
                return json.load(f)
        except (IOError, json.JSONDecodeError):
            return {}

    def _save_data(self, data):
        """Salva todos os dados no arquivo de sessão."""
        try:
            with open(self.session_path, 'w') as f:
                json.dump(data, f, indent=4)
        except IOError:
            pass # Falha silenciosa

    def save_sidebar_path(self, path):
        """Salva o caminho atual da sidebar no arquivo de sessão."""
        data = self._load_data()
        data["last_path"] = os.path.abspath(path)
        self._save_data(data)

    def load_sidebar_path(self):
        """Carrega o último caminho da sidebar ou retorna a home do usuário."""
        data = self._load_data()
        last_path = data.get("last_path")
        if last_path and os.path.isdir(last_path):
            return last_path
        return os.path.expanduser("~")

    def load_recent_files(self):
        """Carrega a lista de arquivos recentes do arquivo de sessão."""
        return self._load_data().get("recent_files", [])

    def save_recent_files(self, recent_files_list):
        """Salva a lista de arquivos recentes no arquivo de sessão."""
        data = self._load_data()
        data["recent_files"] = recent_files_list
        self._save_data(data)