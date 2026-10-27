import os
import re
import json
import tkinter as tk
from tkinter import ttk, messagebox

# Determina o diretório base de forma inteligente (procura onde está o site.html)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def find_paths():
    """Identifica corretamente os caminhos independentemente de onde o script seja executado."""
    # Cenário A: Executando dentro da pasta 'ukazxda'
    site_in_current = os.path.join(BASE_DIR, "site.html")
    dev_in_current = os.path.join(BASE_DIR, "dev")
    
    if os.path.exists(site_in_current):
        return dev_in_current, site_in_current

    # Cenário B: Executando na raiz do repositório
    site_in_sub = os.path.join(BASE_DIR, "site.html")
    dev_in_sub = os.path.join(BASE_DIR, "dev")
    
    if os.path.exists(site_in_sub):
        return dev_in_sub, site_in_sub
        
    # Fallback padrão caso não ache (cria apontando para subpasta)
    return dev_in_sub, site_in_sub

DEV_DIR, SITE_HTML_FILE = find_paths()

def extract_title(file_path):
    """Extrai o título da tag <title> ou usa o nome do arquivo."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read(4096)
            match = re.search(r'<title>(.*?)</title>', content, re.IGNORECASE | re.DOTALL)
            if match:
                title = re.sub(r'<[^>]+>', '', match.group(1)).strip()
                if title:
                    return title
    except Exception:
        pass
    return os.path.splitext(os.path.basename(file_path))[0]

def scan_dev_folder():
    """Varre a pasta dev em busca de arquivos HTML."""
    projects = []
    if not os.path.exists(DEV_DIR):
        return projects

    output_dir = os.path.dirname(SITE_HTML_FILE)
    for root, dirs, files in os.walk(DEV_DIR):
        for file in files:
            if file.lower().endswith(".html"):
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, output_dir).replace(os.sep, "/")
                title = extract_title(full_path)
                projects.append({"path": rel_path, "title": title})
    return projects

def get_existing_active_paths():
    """Lê o site.html atual para manter marcados os projetos que já estão ativos."""
    active_paths = set()
    if not os.path.exists(SITE_HTML_FILE):
        return active_paths
    try:
        with open(SITE_HTML_FILE, "r", encoding="utf-8") as f:
            content = f.read()
            match = re.search(r'// PROJETOS_START\s*const devProjects = (\[.*?\]);\s*// PROJETOS_END', content, re.DOTALL)
            if match:
                data = json.loads(match.group(1))
                for item in data:
                    if "path" in item:
                        active_paths.add(item["path"])
    except Exception:
        pass
    return active_paths

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Gerenciador de Projetos - UKAzXDA")
        self.root.geometry("720x480")
        self.root.minsize(550, 350)

        style = ttk.Style()
        style.theme_use('clam')

        header_frame = ttk.Frame(root, padding=10)
        header_frame.pack(fill=tk.X)

        title_label = ttk.Label(
            header_frame, 
            text=f"Projetos em: {os.path.relpath(DEV_DIR, BASE_DIR)}", 
            font=("Segoe UI", 12, "bold")
        )
        title_label.pack(anchor=tk.W)

        subtitle_label = ttk.Label(
            header_frame, 
            text="Marque os HTMLs que deseja exibir no site.html.", 
            font=("Segoe UI", 9)
        )
        subtitle_label.pack(anchor=tk.W, pady=(2, 0))

        tree_frame = ttk.Frame(root, padding=(10, 0, 10, 10))
        tree_frame.pack(fill=tk.BOTH, expand=True)

        self.tree = ttk.Treeview(tree_frame, columns=("status", "title", "path"), show="headings", selectmode="browse")
        self.tree.heading("status", text="Exibir?")
        self.tree.heading("title", text="Título do Projeto")
        self.tree.heading("path", text="Caminho do Arquivo")

        self.tree.column("status", width=70, anchor=tk.CENTER)
        self.tree.column("title", width=240, anchor=tk.W)
        self.tree.column("path", width=360, anchor=tk.W)

        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree.bind("<ButtonRelease-1>", self.toggle_item)

        btn_frame = ttk.Frame(root, padding=10)
        btn_frame.pack(fill=tk.X)

        self.btn_select_all = ttk.Button(btn_frame, text="Marcar Todos", command=self.select_all)
        self.btn_select_all.pack(side=tk.LEFT, padx=5)

        self.btn_deselect_all = ttk.Button(btn_frame, text="Desmarcar Todos", command=self.deselect_all)
        self.btn_deselect_all.pack(side=tk.LEFT, padx=5)

        self.btn_save = ttk.Button(btn_frame, text="Salvar e Injetar no site.html", command=self.update_site_html)
        self.btn_save.pack(side=tk.RIGHT, padx=5)

        self.projects_data = []
        self.load_projects()

    def load_projects(self):
        scanned = scan_dev_folder()
        active_paths = get_existing_active_paths()
        
        self.projects_data = []
        for item in scanned:
            # Se for a primeira execução ou o arquivo já estava ativo no site, marca como True por padrão
            is_active = item["path"] in active_paths if active_paths else True
            self.projects_data.append({
                "path": item["path"],
                "title": item["title"],
                "active": is_active
            })
        self.refresh_tree()

    def refresh_tree(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        for idx, item in enumerate(self.projects_data):
            status_symbol = "[ X ]" if item["active"] else "[   ]"
            self.tree.insert("", tk.END, iid=str(idx), values=(status_symbol, item["title"], item["path"]))

    def toggle_item(self, event):
        selected_id = self.tree.focus()
        if selected_id:
            try:
                idx = int(selected_id)
                self.projects_data[idx]["active"] = not self.projects_data[idx]["active"]
                self.refresh_tree()
            except Exception:
                pass

    def select_all(self):
        for item in self.projects_data:
            item["active"] = True
        self.refresh_tree()

    def deselect_all(self):
        for item in self.projects_data:
            item["active"] = False
        self.refresh_tree()

    def update_site_html(self):
        if not os.path.exists(SITE_HTML_FILE):
            messagebox.showerror("Erro", f"Arquivo '{SITE_HTML_FILE}' não foi encontrado!")
            return

        active_projects = [
            {"path": item["path"], "title": item["title"]}
            for item in self.projects_data if item["active"]
        ]

        js_data = json.dumps(active_projects, ensure_ascii=False, indent=4)
        new_script_content = f"// PROJETOS_START\nconst devProjects = {js_data};\n// PROJETOS_END"

        try:
            with open(SITE_HTML_FILE, "r", encoding="utf-8") as f:
                html_content = f.read()

            pattern = r'// PROJETOS_START[\s\S]*?// PROJETOS_END'
            if re.search(pattern, html_content):
                updated_html = re.sub(pattern, new_script_content, html_content)
            else:
                messagebox.showerror("Erro", "Não foi encontrada a marcação '// PROJETOS_START' no site.html!")
                return

            with open(SITE_HTML_FILE, "w", encoding="utf-8") as f:
                f.write(updated_html)

            messagebox.showinfo(
                "Sucesso", 
                f"{len(active_projects)} projeto(s) aplicados diretamente no 'site.html' com sucesso!"
            )
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao atualizar o site.html:\n{e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()