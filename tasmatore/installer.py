import os
import subprocess
import shutil

class PluginInstaller:
    def __init__(self, plugins_dir):
        self.plugins_dir = plugins_dir
        # Define o diretório temporário para downloads, localizado em 'tasmatore/tpm'.
        self.tpm_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tpm")
        # Garante que o diretório temporário exista.
        if not os.path.exists(self.tpm_dir):
            os.makedirs(self.tpm_dir, exist_ok=True)

    def install_from_github(self, url, on_progress=None):
        """
        Clona um repositório git para uma pasta temporária ('tpm') e depois o move
        para o diretório final de plugins.
        Retorna (sucesso: bool, mensagem: str).
        """
        if not url.startswith("http"):
            return False, "URL inválida. Deve começar com http/https."

        # Extrai o nome do repositório da URL (ex: .../plugin-name.git -> plugin-name)
        repo_name = url.rstrip('/').split('/')[-1]
        if repo_name.endswith('.git'):
            repo_name = repo_name[:-4]

        # Caminho final onde o plugin será instalado.
        final_plugin_path = os.path.join(self.plugins_dir, repo_name)

        if os.path.exists(final_plugin_path):
            return False, f"O plugin '{repo_name}' já existe."

        # Define um caminho de download temporário para evitar corromper a pasta de plugins.
        temp_download_path = os.path.join(self.tpm_dir, repo_name)
        
        # Limpa qualquer resquício de uma tentativa anterior que falhou.
        if os.path.exists(temp_download_path):
            shutil.rmtree(temp_download_path)

        try:
            # 1. Clona o repositório na pasta temporária 'tpm'.
            process = subprocess.Popen(
                ["git", "clone", "--progress", url, temp_download_path],
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE,
                universal_newlines=True,
                encoding='utf-8',
                errors='replace'
            )
            
            # Lê o progresso do stderr (onde o git escreve o status)
            while True:
                char = process.stderr.read(1)
                if char == '' and process.poll() is not None:
                    break
                if char != '' and on_progress:
                    on_progress(char)
            
            if process.returncode != 0:
                raise subprocess.CalledProcessError(process.returncode, process.args)
            
            # 2. Move o plugin da pasta temporária para a pasta final de plugins.
            shutil.move(temp_download_path, final_plugin_path)
            
            return True, f"Plugin '{repo_name}' instalado com sucesso!"
        except subprocess.CalledProcessError as e:
            # Se o git clone falhar, limpa a pasta temporária se ela foi criada.
            if os.path.exists(temp_download_path):
                shutil.rmtree(temp_download_path)
            # Retorna a mensagem de erro do git para o usuário.
            error_message = e.stderr.decode('utf-8', 'ignore').strip()
            return False, f"Erro ao clonar: {error_message or e}"
        except FileNotFoundError:
            return False, "Git não encontrado no sistema."
        except Exception as e:
            # Limpa em caso de qualquer outro erro.
            if os.path.exists(temp_download_path):
                shutil.rmtree(temp_download_path)
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

    def update_plugin(self, plugin_name):
        """Tenta atualizar o plugin via git pull."""
        path = os.path.join(self.plugins_dir, plugin_name)
        if not os.path.exists(os.path.join(path, ".git")):
            return False, "Plugin não é um repositório Git (não pode atualizar)."
        
        try:
            subprocess.run(
                ["git", "-C", path, "pull"],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            return True, f"Plugin '{plugin_name}' atualizado com sucesso."
        except Exception as e:
            return False, f"Erro ao atualizar: {e}"