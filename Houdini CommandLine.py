import glob
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import subprocess
import os
import time
import json
from ttkthemes import ThemedTk
import threading

class ModernHoudiniRenderUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Houdini Command Line Cache/Renderer")
        self.render_process = None
        self.latest_path = ""
        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)
        self.root.set_theme("equilux")
        self.hip_path = tk.StringVar()
        self.hcmd_path = self.detect_houdini_version()
        if not self.hcmd_path:
            messagebox.showerror("Error", "No Houdini installation detected.")
            self.root.destroy()
            return
        self.progress_var = tk.DoubleVar()
        
        # Define supported node types and their render commands
        self.supported_nodes = {
            "filecache::2.0": lambda path: f'render -V {path}/render',
            "usdrender_rop": lambda path: f'render -V {path}'
        }


        self.style = ttk.Style()
        self.style.configure("Title.TLabel", font=("Helvetica", 24, "bold"))
        self.style.configure("Subtitle.TLabel", font=("Helvetica", 12))
        self.style.configure("Custom.TButton", font=("Helvetica", 12, "bold"))
        self.style.configure("Path.TEntry", font=("Consolas", 10))


        self.main_container = ttk.Frame(root, padding="10")
        self.main_container.pack(fill=tk.BOTH, expand=True)
        

        self.main_container.columnconfigure(0, weight=2) 
        self.main_container.columnconfigure(1, weight=3)  

        self.left_frame = ttk.Frame(self.main_container)
        self.right_frame = ttk.Frame(self.main_container)
        
        self.left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        self.right_frame.grid(row=0, column=1, sticky="nsew")


        self.create_widgets()

    def create_widgets(self):
        # Title Section
        title_frame = ttk.Frame(self.left_frame)
        title_frame.pack(fill=tk.X, pady=(0, 20))

        ttk.Label(title_frame, text="Houdini Command Line Cache/Renderer", 
                 style="Title.TLabel", wraplength=400).pack()
        ttk.Label(title_frame, text="Streamline your rendering workflow", 
                 style="Subtitle.TLabel").pack()


        input_frame = ttk.LabelFrame(self.left_frame, text="Configuration", padding="10")
        input_frame.pack(fill=tk.X, pady=10)

        # Hip File Path
        path_frame = ttk.Frame(input_frame)
        path_frame.pack(fill=tk.X, pady=5)

        ttk.Label(path_frame, text="Hip File Path:").pack(side=tk.LEFT, padx=5)
        path_entry = ttk.Entry(path_frame, textvariable=self.hip_path, style="Path.TEntry")
        path_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        browse_btn = ttk.Button(path_frame, text="Browse", 
                              command=self.browse_hip, style="Custom.TButton")
        browse_btn.pack(side=tk.LEFT, padx=5)

        # Node Selection Section
        node_selection_frame = ttk.LabelFrame(self.left_frame, text="Available Nodes", padding="10")
        node_selection_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        scan_button_frame = ttk.Frame(node_selection_frame)
        scan_button_frame.pack(fill=tk.X, pady=5)

        scan_nodes_btn = ttk.Button(scan_button_frame, text="Scan Nodes", 
                                  command=self.scan_nodes, style="Custom.TButton")
        scan_nodes_btn.pack(side=tk.RIGHT, padx=5)

        # Create Treeview for nodes
        self.nodes_tree = ttk.Treeview(node_selection_frame, 
                                     columns=("Node Type", "Node Path"), 
                                     show="headings", 
                                     selectmode="browse")
        
        self.nodes_tree.heading("Node Type", text="Node Type")
        self.nodes_tree.heading("Node Path", text="Node Path")
        
        # Configure column widths
        self.nodes_tree.column("Node Type", width=150, minwidth=100)
        self.nodes_tree.column("Node Path", width=250, minwidth=150)
        
        # Add scrollbars
        tree_scroll_y = ttk.Scrollbar(node_selection_frame, 
                                    orient="vertical", 
                                    command=self.nodes_tree.yview)
        tree_scroll_x = ttk.Scrollbar(node_selection_frame, 
                                    orient="horizontal", 
                                    command=self.nodes_tree.xview)
        
        self.nodes_tree.configure(yscrollcommand=tree_scroll_y.set, 
                                xscrollcommand=tree_scroll_x.set)
        
        # Pack the Treeview and scrollbars
        self.nodes_tree.pack(fill=tk.BOTH, expand=True, pady=5)
        tree_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        tree_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)

        # Progress bar
        self.progress_bar = ttk.Progressbar(self.left_frame, 
                                          variable=self.progress_var, 
                                          mode='determinate')
        self.progress_bar.pack(fill=tk.X, pady=10)

        # Status message
        self.status_label = ttk.Label(self.left_frame, 
                                    text="Ready to render", 
                                    wraplength=400, 
                                    justify=tk.LEFT)
        self.status_label.pack(fill=tk.X, pady=5)

        # Control buttons
        control_frame = ttk.Frame(self.left_frame)
        control_frame.pack(fill=tk.X, pady=10)

        render_btn = ttk.Button(control_frame, 
                              text="Start Render", 
                              command=self.start_render, 
                              style="Custom.TButton")
        render_btn.pack(side=tk.RIGHT, padx=5)

        cancel_btn = ttk.Button(control_frame, 
                              text="Cancel Render", 
                              command=self.cancel_render, 
                              style="Custom.TButton")
        cancel_btn.pack(side=tk.RIGHT, padx=5)


        log_frame = ttk.LabelFrame(self.right_frame, text="Render Log", padding="10")
        log_frame.pack(fill=tk.BOTH, expand=True)


        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)


        self.log_text = tk.Text(log_frame, wrap=tk.WORD, font=("Consolas", 10))
        self.log_text.grid(row=0, column=0, sticky="nsew")


        scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=self.log_text.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.log_text.configure(yscrollcommand=scrollbar.set)

        self.log_text.insert(tk.END, "Logs will appear here...\n")

    def detect_houdini_version(self):
        """Automatically detect the installed Houdini version."""
        houdini_paths = glob.glob(r"C:\Program Files\Side Effects Software\Houdini*\bin\hcmd.exe")
        if houdini_paths:
            return max(houdini_paths)
        return ""

    def add_log(self, message):
        """Add message to log window and auto-scroll"""
        self.log_text.insert(tk.END, message)
        self.log_text.see(tk.END)
        self.root.update_idletasks()

    def update_progress(self, value, message):
        """Update progress bar and status message"""
        self.progress_var.set(value)
        self.status_label.config(text=message)
        self.root.update_idletasks()

    def browse_hip(self):
        """Open file dialog to select Houdini file"""
        filename = filedialog.askopenfilename(
            filetypes=[("Houdini Files", "*.hip *.hipnc"), ("All Files", "*.*")]
        )
        if filename:
            self.hip_path.set(filename)
            self.add_log(f"File selected: {filename}\n")

    def cleanup_temp_files(self):
        temp_files = [self.nodes_file, os.path.join(self.temp_dir, "detect_nodes.py")]
        for file in temp_files:
            if os.path.exists(file):
                os.remove(file)
                self.add_log(f"Cleaned up: {file}\n")

    def create_detection_script(self):
        """Create a Python script that will run inside Houdini to detect specific nodes"""        
        script_content = '''
import hou
import json
import os

def find_nodes_by_type(node_types):
    """Find and return all nodes matching the specified types in the current Houdini session."""
    matching_nodes = []
    all_nodes = hou.node("/").allSubChildren()
    for node in all_nodes:
        if node.type().name() in node_types:
            matching_nodes.append({
                "type": node.type().name(),  # This is the node type
                "path": node.path()
            })
    return matching_nodes

# Node types to look for
node_types = ["filecache::2.0", "usdrender_rop"]

# Get the nodes
nodes = find_nodes_by_type(node_types)

# Save to temp file
nodes_file = r"''' + self.nodes_file.replace('\\', '\\\\') + '''"
with open(nodes_file, "w") as f:
    json.dump(nodes, f)

# Print results
print(f"Found {len(nodes)} nodes")
for node in nodes:
    print(f"- {node['type']}: {node['path']}")
'''
        
        script_path = os.path.join(self.temp_dir, "detect_nodes.py")
        with open(script_path, "w") as f:
            f.write(script_content)
        return script_path

    def scan_nodes(self):

        if not self.hip_path.get():
            messagebox.showerror("Error", "Please provide a Hip file path")
            return

        if not os.path.exists(self.hcmd_path):
            messagebox.showerror("Error", "Houdini command line tool (hcmd.exe) not found")
            return

        self.nodes_file = os.path.join(os.getenv("TEMP"), "detected_nodes.json")
        self.temp_dir = os.getenv("TEMP")

        def run_scan():
            try:
                self.update_progress(20, "Opening Houdini Command Line...")

                script_path = self.create_detection_script()

                process = subprocess.Popen(
                    [self.hcmd_path],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )

                self.update_progress(40, "Initializing Houdini session...")

                # Send the hbatch command and wait
                hbatch_cmd = f'hbatch -i -j 48 "{self.hip_path.get()}"\n'
                process.stdin.write(hbatch_cmd)
                process.stdin.flush()
                time.sleep(3) 

                self.update_progress(60, "Running detection script...")

                detect_cmd = f'python "{script_path}"\n'
                process.stdin.write(detect_cmd)
                process.stdin.flush()

                self.update_progress(80, "Processing detected nodes...")

                def monitor_output(pipe, is_error=False):
                    while process and process.poll() is None:
                        line = pipe.readline()
                        if not line:
                            break
                        prefix = "ERROR: " if is_error else ""
                        self.add_log(f"{prefix}{line}")
                    if process:
                        pipe.close()

                log_thread = threading.Thread(target=monitor_output, 
                                           args=(process.stdout,), 
                                           daemon=True)
                error_thread = threading.Thread(target=monitor_output, 
                                             args=(process.stderr, True), 
                                             daemon=True)
                
                log_thread.start()
                error_thread.start()

                # Wait for the JSON file
                max_attempts = 10
                attempts = 0
                nodes_processed = False
                
                while attempts < max_attempts:
                    if os.path.exists(self.nodes_file):
                        try:
                            with open(self.nodes_file, "r") as f:
                                nodes = json.load(f)
                                
                                # Clear existing items
                                for item in self.nodes_tree.get_children():
                                    self.nodes_tree.delete(item)
                                
                                for node in nodes:
                                    self.nodes_tree.insert("", "end", 
                                                         values=(node['type'], 
                                                                node['path']))

                                if nodes:
                                    self.update_progress(100, f"Found {len(nodes)} nodes!")
                                else:
                                    self.update_progress(100, "No nodes found.")
                                nodes_processed = True
                                break
                        except json.JSONDecodeError:
                            self.add_log("Waiting for complete node data...\n")
                        except Exception as e:
                            self.add_log(f"Error reading nodes file: {str(e)}\n")
                    
                    attempts += 1
                    time.sleep(1)
                
                if not nodes_processed:
                    self.update_progress(100, "No nodes detected or detection timed out.")

                process.terminate()
                time.sleep(2)
                
                try:
                    self.cleanup_temp_files()
                    self.add_log("Temporary files cleaned up successfully.\n")
                except Exception as e:
                    self.add_log(f"Warning: Could not clean up temporary files: {str(e)}\n")

            except Exception as e:
                self.update_progress(0, f"Error: {str(e)}")
                self.add_log(f"Exception occurred: {str(e)}\n")
                messagebox.showerror("Error", f"An error occurred: {str(e)}")

        threading.Thread(target=run_scan, daemon=True).start()

    def start_render(self):
        selected_items = self.nodes_tree.selection()
        if not selected_items:
            messagebox.showerror("Error", "Please select a node to render")
            return

        if not self.hip_path.get():
            messagebox.showerror("Error", "Please provide a Hip file path")
            return

        if not os.path.exists(self.hcmd_path):
            messagebox.showerror("Error", "Houdini command line tool (hcmd.exe) not found")
            return

        try:
            item = selected_items[0]
            node_type, node_path = self.nodes_tree.item(item, "values")
            self.add_log(f"Selected node type: {node_type} at path: {node_path}\n")

            if node_type not in self.supported_nodes:
                error_msg = (
                    f"Node type '{node_type}' is not supported.\n"
                    f"Supported types are:\n"
                    f"• filecache::2.0\n"
                    f"• usdrender_rop"
                )
                self.add_log(f"Error: {error_msg}\n")
                messagebox.showerror("Unsupported Node Type", error_msg)
                return

            def render_process():
                try:
                    self.update_progress(20, "Starting Houdini Command Line...")
                    self.add_log("Starting render process...\n")

                    self.render_process = subprocess.Popen(
                        [self.hcmd_path],
                        stdin=subprocess.PIPE,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                        creationflags=subprocess.CREATE_NO_WINDOW
                    )

                    self.update_progress(40, "Initializing Houdini session...")
                    hbatch_cmd = f'hbatch -i -j 48 "{self.hip_path.get()}"\n'
                    self.add_log(f"Sending hbatch command: {hbatch_cmd}\n")
                    self.render_process.stdin.write(hbatch_cmd)
                    self.render_process.stdin.flush()
                    time.sleep(3)

                    self.update_progress(60, f"Starting render for {node_type} node...")

                    render_cmd = self.supported_nodes[node_type](node_path) + '\n'
                    self.add_log(f"Executing render command: {render_cmd}\n")
                    self.render_process.stdin.write(render_cmd)
                    self.render_process.stdin.flush()

                    self.update_progress(80, "Monitoring render progress...")

                    def monitor_output(pipe, is_error=False):
                        while self.render_process and self.render_process.poll() is None:
                            line = pipe.readline()
                            if not line:
                                break
                            prefix = "ERROR: " if is_error else ""
                            self.add_log(f"{prefix}{line}")
                        if self.render_process:
                            pipe.close()

                    log_thread = threading.Thread(target=monitor_output, 
                                               args=(self.render_process.stdout,), 
                                               daemon=True)
                    error_thread = threading.Thread(target=monitor_output, 
                                                 args=(self.render_process.stderr, True), 
                                                 daemon=True)
                    
                    log_thread.start()
                    error_thread.start()

                    self.update_progress(100, "Render process started successfully!")

                except Exception as e:
                    self.update_progress(0, f"Error: {str(e)}")
                    self.add_log(f"Exception occurred: {str(e)}\n")
                    messagebox.showerror("Error", f"An error occurred during rendering: {str(e)}")
                    if self.render_process:
                        self.render_process.terminate()
                        self.render_process = None

            threading.Thread(target=render_process, daemon=True).start()

        except ValueError as e:
            error_msg = f"Invalid node selection format: {str(e)}"
            self.add_log(f"Error: {error_msg}\n")
            messagebox.showerror("Error", error_msg)
        except Exception as e:
            error_msg = f"An unexpected error occurred: {str(e)}"
            self.add_log(f"Error: {error_msg}\n")
            messagebox.showerror("Error", error_msg)

    import subprocess

    def cancel_render(self):
        """Cancel the current render process and also terminate the Husk and karma_cc processes if running."""
        if self.render_process and self.render_process.poll() is None:
            self.render_process.terminate()
            self.render_process = None
            self.update_progress(0, "Render cancelled.")
            self.add_log("Render process terminated.\n")

        try:
            husk_process = subprocess.Popen(
                'tasklist /FI "IMAGENAME eq husk.exe" /NH', 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE, 
                text=True
            )
            output, error = husk_process.communicate()
            
            if "husk.exe" in output:
                subprocess.run('taskkill /F /IM husk.exe', check=True)
                self.add_log("Husk process terminated.\n")
            else:
                self.add_log("No Husk process found.\n")
            
            karma_process = subprocess.Popen(
                'tasklist /FI "IMAGENAME eq karma_cc.exe" /NH', 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE, 
                text=True
            )
            output, error = karma_process.communicate()
            
            if "karma_cc.exe" in output:
                subprocess.run('taskkill /F /IM karma_cc.exe', check=True)
                self.add_log("Karma_CC process terminated.\n")
            else:
                self.add_log("No Karma_CC process found.\n")

        except Exception as e:
            self.add_log(f"Error while terminating processes: {str(e)}\n")



    def on_closing(self):
        if self.render_process and self.render_process.poll() is None:
            self.cancel_render()
        self.root.destroy()

def main():
    root = ThemedTk(theme="equilux")
    app = ModernHoudiniRenderUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()