import os
import subprocess
import shutil

class PluginInstaller:
    def __init__(self, plugins_dir):
        self.plugins_dir = plugins_dir

    def install_from_github(self, url):
        """
        Clona um repositório git para a pasta de plugins.
        Retorna (sucesso: bool, mensagem: str).
        """
        if not url.startswith("http"):
            return False, "URL inválida. Deve começar com http/https."

        # Extrai o nome do repositório da URL (ex: .../plugin-name.git -> plugin-name)
        repo_name = url.rstrip('/').split('/')[-1]
        if repo_name.endswith('.git'):
            repo_name = repo_name[:-4]

        target_path = os.path.join(self.plugins_dir, repo_name)

        if os.path.exists(target_path):
            return False, f"O plugin '{repo_name}' já existe."

        try:
            # Usa git clone
            subprocess.run(["git", "clone", url, target_path], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return True, f"Plugin '{repo_name}' instalado com sucesso!"
        except subprocess.CalledProcessError as e:
            return False, f"Erro ao clonar: {e}"
        except FileNotFoundError:
            return False, "Git não encontrado no sistema."
        except Exception as e:
            return False, f"Erro inesperado: {str(e)}"

    def list_installed_plugins(self):
        """Lista os plugins instalados."""
        if not os.path.exists(self.plugins_dir):
            return []
        return sorted([d for d in os.listdir(self.plugins_dir) 
                      if os.path.isdir(os.path.join(self.plugins_dir, d)) 
                      and not d.startswith('.') and d != "__pycache__" and d != "tasmatore"])

    def delete_plugin(self, plugin_name):
        """Deleta a pasta de um plugin."""
        path = os.path.join(self.plugins_dir, plugin_name)
        try:
            if os.path.exists(path):
                shutil.rmtree(path)
                return True, f"Plugin '{plugin_name}' removido."
            return False, "Plugin não encontrado."
        except Exception as e:
            return False, f"Erro ao remover: {e}"

    def get_plugin_description(self, plugin_name):
        """Lê a descrição do plugin se existir."""
        path = os.path.join(self.plugins_dir, plugin_name, "descrision.txt")
        if os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8', errors='replace') as f:
                    return f.read().strip()
            except: pass
        return None

    def get_plugin_repository_link(self, plugin_name):
        """Lê o link do repositório se existir."""
        path = os.path.join(self.plugins_dir, plugin_name, "__link_github_repository.txt")
        if os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8', errors='replace') as f:
                    return f.read().strip()
            except: pass
        return None