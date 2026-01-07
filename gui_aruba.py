import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from aruba_config_net import ArubaCXDevice


def run_vsx():
    try:
        username = entry_user.get()
        password = entry_pass.get()

        vsx_param = [
            {
                "host": p_host.get(),
                "role": "primary",
                "mac": p_mac.get(),
                "src": p_src.get(),
                "peer": p_peer.get(),
                "isl": int(isl_id.get()),
                "ports": p_ports.get().split(","),
            },
            {
                "host": s_host.get(),
                "role": "secondary",
                "mac": s_mac.get(),
                "src": s_src.get(),
                "peer": s_peer.get(),
                "isl": int(isl_id.get()),
                "ports": s_ports.get().split(","),
            },
        ]

        output.delete(1.0, tk.END)

        for sw in vsx_param:
            output.insert(tk.END, f"\n=== Connecting to {sw['host']} ({sw['role']}) ===\n")
            with ArubaCXDevice(sw["host"], username, password) as dev:
                output.insert(tk.END, "Creating ISL LAG...\n")
                dev.create_lag(sw["isl"], sw["ports"], multi_chassis=True)

                output.insert(tk.END, "Configuring VSX...\n")
                dev.build_vsx(
                    role=sw["role"],
                    system_mac=sw["mac"],
                    isl_lag=sw["isl"],
                    keepalive_src=sw["src"],
                    keepalive_peer=sw["peer"],
                )

        messagebox.showinfo("Done", "VSX configuration completed")

    except Exception as e:
        messagebox.showerror("Error", str(e))


root = tk.Tk()
root.title("Aruba CX VSX Configurator")
root.geometry("820x700")

frame = ttk.Frame(root, padding=10)
frame.pack(fill="both", expand=True)

# Credentials
ttk.Label(frame, text="Username").grid(row=0, column=0)
entry_user = ttk.Entry(frame)
entry_user.grid(row=0, column=1)

ttk.Label(frame, text="Password").grid(row=1, column=0)
entry_pass = ttk.Entry(frame, show="*")
entry_pass.grid(row=1, column=1)

# ISL
ttk.Label(frame, text="ISL LAG ID").grid(row=2, column=0)
isl_id = ttk.Entry(frame)
isl_id.insert(0, "254")
isl_id.grid(row=2, column=1)

# PRIMARY
ttk.Label(frame, text="PRIMARY", font=("Arial", 10, "bold")).grid(row=3, column=0)

p_host = ttk.Entry(frame); p_host.insert(0, "192.168.109.10")
p_mac  = ttk.Entry(frame); p_mac.insert(0, "02:01:00:00:01:00")
p_src  = ttk.Entry(frame); p_src.insert(0, "169.254.254.1")
p_peer = ttk.Entry(frame); p_peer.insert(0, "169.254.254.2")
p_ports = ttk.Entry(frame); p_ports.insert(0, "1/1/2,1/1/3")

labels = ["Host", "System MAC", "Keepalive SRC", "Keepalive Peer", "ISL Ports"]
entries = [p_host, p_mac, p_src, p_peer, p_ports]

for i, (l, e) in enumerate(zip(labels, entries), start=4):
    ttk.Label(frame, text=l).grid(row=i, column=0)
    e.grid(row=i, column=1, sticky="ew")

# SECONDARY
ttk.Label(frame, text="SECONDARY", font=("Arial", 10, "bold")).grid(row=9, column=0)

s_host = ttk.Entry(frame); s_host.insert(0, "192.168.109.11")
s_mac  = ttk.Entry(frame); s_mac.insert(0, "02:00:00:00:01:00")
s_src  = ttk.Entry(frame); s_src.insert(0, "169.254.254.2")
s_peer = ttk.Entry(frame); s_peer.insert(0, "169.254.254.1")
s_ports = ttk.Entry(frame); s_ports.insert(0, "1/1/2,1/1/3")

entries = [s_host, s_mac, s_src, s_peer, s_ports]

for i, (l, e) in enumerate(zip(labels, entries), start=10):
    ttk.Label(frame, text=l).grid(row=i, column=0)
    e.grid(row=i, column=1, sticky="ew")

# Run button
ttk.Button(frame, text="Configure VSX", command=run_vsx).grid(row=15, column=0, columnspan=2, pady=10)

# Output
output = scrolledtext.ScrolledText(frame, height=15)
output.grid(row=16, column=0, columnspan=2, sticky="nsew")

frame.columnconfigure(1, weight=1)
frame.rowconfigure(16, weight=1)

root.mainloop()
