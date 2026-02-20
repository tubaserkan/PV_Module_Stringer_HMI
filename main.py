import customtkinter as ctk
import random
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np


ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class HMI_Final_Master_v12_22(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("PV MODULE STRINGER MONITOR - v12.22 | Full Restoration")
        self.geometry("1600x950")
        self.configure(fg_color="#0a0c12")

     
        self.grid_columnconfigure(0, weight=3) # Ribbon
        self.grid_columnconfigure(1, weight=3) # BOŞ ALAN (Müşteri Rezervi)
        self.grid_columnconfigure(2, weight=2) # 3D Cube & Log
        self.grid_rowconfigure(2, weight=3)
        self.grid_rowconfigure(3, weight=2)

       
        self.ribbon_objects = []
        self.ticker_text = "⚡ DURUM: AKTİF | 3D Hologram Senkronize | Kalite Analizi: CANLI | Lokasyon: Bursa | "
        self.pie_angle = 90
        self.cube_rotation = 45
        
        # Makine Durumları
        self.machine_states = [
            {"text": "🟢 RUNNING", "color": "#00ff88", "log": "Stabil Üretim Devam Ediyor"},
            {"text": "🟡 IDLE / WAIT", "color": "#f1c40f", "log": "Bekleme Moduna Geçildi"},
            {"text": "🔴 FAULT ERROR", "color": "#e74c3c", "log": "SİSTEM HATASI ALGILANDI"}
        ]
        self.current_state_idx = 0

        self.setup_ui()
        self.run_animations()

    def setup_ui(self):
        # 1. HEADER
        self.header = ctk.CTkFrame(self, corner_radius=15, fg_color="#151925", border_width=2, border_color="#2980b9")
        self.header.grid(row=0, column=0, columnspan=3, sticky="ew", padx=15, pady=(15,0))
        ctk.CTkLabel(self.header, text="⚡ PV MODULE STRINGER MONITOR ⚡", 
                     font=ctk.CTkFont(size=26, weight="bold"), text_color="#00d2d3").pack(side="left", padx=30, pady=15)
        self.lbl_clock = ctk.CTkLabel(self.header, text="", font=ctk.CTkFont(size=18), text_color="#ffffff")
        self.lbl_clock.pack(side="right", padx=30)

        # 2. ÜST METRİK KARTLARI
        self.metric_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.metric_frame.grid(row=1, column=0, columnspan=3, sticky="ew", pady=10)
        self.metric_frame.grid_columnconfigure((0,1,2), weight=1)

        # Status
        self.status_card_f = ctk.CTkFrame(self.metric_frame, border_width=2, border_color="#00ff88", fg_color="#1e2738", corner_radius=15)
        self.status_card_f.grid(row=0, column=0, padx=10, sticky="ew")
        self.lbl_status = ctk.CTkLabel(self.status_card_f, text="🟢 RUNNING", font=("Roboto", 24, "bold"), text_color="#00ff88")
        self.lbl_status.pack(pady=20)

        # Flux & Prod
        self.add_bar_metric(self.metric_frame, 1, "💧 FLUX LEVEL", "189.3 ml", "#0984e3", 0.63)
        self.add_bar_metric(self.metric_frame, 2, "🚀 PROD. RATE", "1250 mm/m", "#fdcb6e", 0.85)

        # 3. SOL: % RIBBON BANK
        self.left_panel = ctk.CTkFrame(self, fg_color="#151925", corner_radius=20, border_width=1, border_color="#34495e")
        self.left_panel.grid(row=2, column=0, padx=(15,5), sticky="nsew")
        ctk.CTkLabel(self.left_panel, text="MATERIAL SUPPLY STATUS (%)", font=("Roboto", 16, "bold"), text_color="#00d2ff").pack(pady=15)
        self.create_ribbon_system(self.left_panel)

        # 4. ORTA: BOŞ ALAN
        self.center_empty = ctk.CTkFrame(self, fg_color="transparent")
        self.center_empty.grid(row=2, column=1, padx=5, sticky="nsew")

        # 5. SAĞ: 3D GLASS TANK
        self.right_panel = ctk.CTkFrame(self, fg_color="#151925", corner_radius=20, border_width=0)
        self.right_panel.grid(row=2, column=2, padx=(5,15), sticky="nsew")
        self.create_glass_tank(self.right_panel)

        # 6. ALT: GRAFİKLER (Hover + Rotating Donut)
        self.bottom_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.bottom_frame.grid(row=3, column=0, columnspan=3, padx=15, pady=10, sticky="nsew")
        self.bottom_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        # Tooltip özellikli ilk iki grafik
        self.create_hover_chart(self.bottom_frame, 0, "📈 SPEED TREND", "#00d2d3")
        self.create_hover_chart(self.bottom_frame, 1, "📊 HOURLY PRODUCTION", "#a29bfe")
        # Sağdaki hareketli kalite halkası (Restored)
        self.create_quality_ring(self.bottom_frame, 2)

        # 7. TICKER
        self.ticker_lbl = ctk.CTkLabel(self, text=self.ticker_text, font=("Roboto", 14, "bold"), text_color="white", fg_color="#c0392b")
        self.ticker_lbl.grid(row=4, column=0, columnspan=3, sticky="ew")

    def add_bar_metric(self, parent, col, title, val, color, prog):
        f = ctk.CTkFrame(parent, border_width=2, border_color=color, fg_color="#1e2738", corner_radius=15)
        f.grid(row=0, column=col, padx=10, sticky="ew")
        inner = ctk.CTkFrame(f, fg_color="transparent")
        inner.pack(fill="x", padx=20, pady=20)
        ctk.CTkLabel(inner, text=val, font=("Roboto", 24, "bold")).pack(side="left")
        pb = ctk.CTkProgressBar(inner, height=12, progress_color=color, width=100)
        pb.set(prog); pb.pack(side="right", padx=10)

    def create_glass_tank(self, parent):
        ctk.CTkLabel(parent, text="🎯 VARDİYA HEDEF ANALİZİ", font=("Roboto", 14, "bold"), text_color="#00ff88").pack(pady=(10, 0))
        self.cube_fig = plt.figure(figsize=(3, 3), facecolor='#151925')
        self.cube_ax = self.cube_fig.add_subplot(111, projection='3d')
        self.cube_canvas = FigureCanvasTkAgg(self.cube_fig, master=parent)
        self.cube_canvas.get_tk_widget().pack(fill="both", expand=False)
        self.log_box = ctk.CTkTextbox(parent, fg_color="#000", text_color="#00ff88", font=("Consolas", 11), height=100)
        self.log_box.pack(fill="both", expand=True, padx=15, pady=5)

    def update_glass_tank(self, percentage):
        self.cube_ax.clear()
        self.cube_ax.set_facecolor('#151925')
        fill_h = percentage / 100.0
        v_fill = np.array([[0,0,0], [1,0,0], [1,1,0], [0,1,0], [0,0,fill_h], [1,0,fill_h], [1,1,fill_h], [0,1,fill_h]])
        faces_fill = [[v_fill[0],v_fill[1],v_fill[5],v_fill[4]], [v_fill[1],v_fill[2],v_fill[6],v_fill[5]], 
                      [v_fill[2],v_fill[3],v_fill[7],v_fill[6]], [v_fill[3],v_fill[0],v_fill[4],v_fill[7]], 
                      [v_fill[0],v_fill[1],v_fill[2],v_fill[3]], [v_fill[4],v_fill[5],v_fill[6],v_fill[7]]]
        poly_fill = Poly3DCollection(faces_fill, alpha=0.7, facecolors='#00ff88', edgecolors='#00ff88', linewidths=0.5)
        self.cube_ax.add_collection3d(poly_fill)
        v_empty = np.array([[0,0,fill_h], [1,0,fill_h], [1,1,fill_h], [0,1,fill_h], [0,0,1], [1,0,1], [1,1,1], [0,1,1]])
        faces_empty = [[v_empty[0],v_empty[1],v_empty[5],v_empty[4]], [v_empty[1],v_empty[2],v_empty[6],v_empty[5]], 
                       [v_empty[2],v_empty[3],v_empty[7],v_empty[6]], [v_empty[3],v_empty[0],v_empty[4],v_empty[7]], 
                       [v_empty[4],v_empty[5],v_empty[6],v_empty[7]]]
        poly_empty = Poly3DCollection(faces_empty, alpha=0.1, facecolors='#34495e', edgecolors='#555', linewidths=0.5)
        self.cube_ax.add_collection3d(poly_empty)
        self.cube_ax.view_init(elev=20, azim=self.cube_rotation)
        self.cube_ax.axis('off')
        self.cube_ax.text2D(0.5, 0.05, f"COMPLETED: %{percentage}", transform=self.cube_ax.transAxes, color='#00ff88', ha='center', weight='bold')

    def create_hover_chart(self, parent, col, title, color):
        f = ctk.CTkFrame(parent, fg_color="#1e2738", corner_radius=15)
        f.grid(row=0, column=col, padx=5, sticky="nsew")
        fig, ax = plt.subplots(figsize=(4, 2.5), facecolor='#1e2738')
        ax.set_facecolor('#1e2738')
        x = np.arange(15); y = np.random.randint(1250, 1275, 15)
        line, = ax.plot(x, y, color=color, marker='o', markersize=4, picker=True)
        ax.axis('off')
        annot = ax.annotate("", xy=(0,0), xytext=(10,10), textcoords="offset points",
                            bbox=dict(boxstyle="round", fc="#000", alpha=0.8), color="white", fontsize=9)
        annot.set_visible(False)
        def hover(event):
            if event.inaxes == ax:
                cont, ind = line.contains(event)
                if cont:
                    annot.xy = (x[ind["ind"][0]], y[ind["ind"][0]])
                    annot.set_text(f"Değer: {y[ind['ind'][0]]}")
                    annot.set_visible(True); canvas.draw_idle()
                else:
                    if annot.get_visible(): annot.set_visible(False); canvas.draw_idle()
        canvas = FigureCanvasTkAgg(fig, master=f); canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        canvas.mpl_connect("motion_notify_event", hover)

    def create_quality_ring(self, parent, col):
        f = ctk.CTkFrame(parent, fg_color="#1e2738", corner_radius=15)
        f.grid(row=0, column=col, padx=5, sticky="nsew")
        ctk.CTkLabel(f, text="🎯 SHIFT QUALITY (LIVE)", font=("Roboto", 12, "bold")).pack(pady=5)
        self.q_fig, self.q_ax = plt.subplots(figsize=(4, 2.5), facecolor='#1e2738')
        self.q_canvas = FigureCanvasTkAgg(self.q_fig, master=f); self.q_canvas.get_tk_widget().pack(fill="both", expand=True)

    def create_ribbon_system(self, parent):
        scroll = ctk.CTkScrollableFrame(parent, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=10)
        for i in range(10):
            row = ctk.CTkFrame(scroll, fg_color="#1e2738", corner_radius=8)
            row.pack(fill="x", pady=2)
            ctk.CTkLabel(row, text=f"R{i+1:02}", width=40).pack(side="left", padx=10)
            pb = ctk.CTkProgressBar(row, height=10); val = random.uniform(0.1, 0.95); pb.set(val)
            pb.pack(side="left", fill="x", expand=True, padx=10); self.ribbon_objects.append({"pb":pb, "val":val, "lbl":ctk.CTkLabel(row, text=f"{int(val*100)}%", width=40)})
            self.ribbon_objects[-1]["lbl"].pack(side="right", padx=10)

    def run_animations(self):
        try:
            self.lbl_clock.configure(text=datetime.now().strftime("%H:%M:%S | %d %b 2026"))
            # 1. Kinetic Glass Tank
            self.cube_rotation = (self.cube_rotation + 2) % 360
            self.update_glass_tank(83.2); self.cube_canvas.draw_idle()
            # 2. Machine Status
            if random.random() > 0.992:
                self.current_state_idx = (self.current_state_idx + 1) % len(self.machine_states)
                s = self.machine_states[self.current_state_idx]
                self.lbl_status.configure(text=s["text"], text_color=s["color"]); self.status_card_f.configure(border_color=s["color"])
            # 3. Ribbon System
            for o in self.ribbon_objects:
                o['val'] = max(0, o['val'] - 0.0003); o['pb'].set(o['val']); o['lbl'].configure(text=f"{int(o['val']*100)}%")
                o['pb'].configure(progress_color=("#e74c3c" if o['val'] < 0.3 else "#f1c40f" if o['val'] < 0.6 else "#2ecc71"))
            # 4. Restored Rotating Donut (Shift Quality)
            self.q_ax.clear(); self.pie_angle = (self.pie_angle + 4) % 360
            self.q_ax.pie([98.2, 1.8], colors=["#00ff88", "#ff4757"], startangle=self.pie_angle, wedgeprops={'width':0.4})
            self.q_ax.set_facecolor('#1e2738'); self.q_canvas.draw_idle()
            # 5. Ticker
            self.ticker_lbl.configure(text=self.ticker_text[1:] + self.ticker_text[0])
            self.ticker_text = self.ticker_text[1:] + self.ticker_text[0]
        except Exception: pass
        self.after(400, self.run_animations)

if __name__ == "__main__":
    app = HMI_Final_Master_v12_22()
    app.mainloop()