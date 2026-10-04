import numpy as np
from collections import Counter
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from quantum_simulator import QuantumSimulator  # type: ignore


# ─────────────────────────────────────────────
#  Colors & Fonts  (IBM Quantum-inspired)
# ─────────────────────────────────────────────
BG        = "#0f1729"
PANEL     = "#1a2540"
ACCENT    = "#0062ff"
ACCENT2   = "#4589ff"
TEXT      = "#dde1ff"
MUTED     = "#8b9ccc"
SUCCESS   = "#42be65"
FONT_MONO = ("Courier New", 10)
FONT_UI   = ("Segoe UI", 10)
FONT_BOLD = ("Segoe UI", 10, "bold")
FONT_HEAD = ("Segoe UI", 13, "bold")


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Spring 26 Quantum Simulator")
        self.configure(bg=BG)
        self.resizable(False, False)

        self.file_path = tk.StringVar(value="")
        self.shots_var = tk.StringVar(value="1024")

        self._build_ui()
        self._center()

    def _center(self):
        self.update_idletasks()
        w, h = self.winfo_width(), self.winfo_height()
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f"+{(sw-w)//2}+{(sh-h)//2}")

    def _build_ui(self):
        # ── Header ──────────────────────────────
        hdr = tk.Frame(self, bg=PANEL, padx=20, pady=14)
        hdr.pack(fill="x")
        tk.Label(hdr, text="⬡  Quantum Circuit Simulator",
                 font=FONT_HEAD, bg=PANEL, fg=ACCENT2).pack(side="left")
        tk.Label(hdr, text="QASM  ·  statevector",
                 font=("Segoe UI", 9), bg=PANEL, fg=MUTED).pack(side="right", pady=4)

        tk.Frame(self, bg=ACCENT, height=2).pack(fill="x")

        # ── Inputs ──────────────────────────────
        inp = tk.Frame(self, bg=BG, padx=20, pady=16)
        inp.pack(fill="x")

        tk.Label(inp, text="QASM File", font=FONT_BOLD,
                 bg=BG, fg=TEXT).grid(row=0, column=0, sticky="w", pady=(0, 4))

        file_row = tk.Frame(inp, bg=BG)
        file_row.grid(row=1, column=0, sticky="ew", pady=(0, 12))

        tk.Entry(
            file_row, textvariable=self.file_path,
            font=FONT_MONO, width=44,
            bg=PANEL, fg=TEXT, insertbackground=TEXT,
            relief="flat", bd=0, highlightthickness=1,
            highlightbackground=ACCENT, highlightcolor=ACCENT2
        ).pack(side="left", ipady=6, padx=(0, 8))

        tk.Button(
            file_row, text="Browse…", command=self._browse,
            font=FONT_UI, bg=ACCENT, fg="white",
            activebackground=ACCENT2, activeforeground="white",
            relief="flat", bd=0, padx=12, pady=5, cursor="hand2"
        ).pack(side="left")

        shots_row = tk.Frame(inp, bg=BG)
        shots_row.grid(row=2, column=0, sticky="w", pady=(0, 4))
        tk.Label(shots_row, text="Shots", font=FONT_BOLD,
                 bg=BG, fg=TEXT).pack(side="left")
        tk.Label(shots_row, text="  (number of measurements)",
                 font=("Segoe UI", 9), bg=BG, fg=MUTED).pack(side="left")

        tk.Entry(
            inp, textvariable=self.shots_var,
            font=FONT_MONO, width=10,
            bg=PANEL, fg=TEXT, insertbackground=TEXT,
            relief="flat", bd=0, highlightthickness=1,
            highlightbackground=ACCENT, highlightcolor=ACCENT2
        ).grid(row=3, column=0, sticky="w", ipady=6, pady=(4, 0))

        # ── Run button ──────────────────────────
        btn_row = tk.Frame(self, bg=BG, padx=20, pady=4)
        btn_row.pack(fill="x")
        tk.Button(
            btn_row, text="▶  Run Simulation", command=self._run,
            font=("Segoe UI", 11, "bold"), bg=ACCENT, fg="white",
            activebackground=ACCENT2, activeforeground="white",
            relief="flat", bd=0, padx=20, pady=9, cursor="hand2"
        ).pack(side="left")

        self.status_lbl = tk.Label(btn_row, text="", font=("Segoe UI", 9),
                                   bg=BG, fg=MUTED)
        self.status_lbl.pack(side="left", padx=14)

        tk.Frame(self, bg=PANEL, height=1).pack(fill="x", pady=(8, 0))

        # ── Output ──────────────────────────────
        out = tk.Frame(self, bg=BG, padx=20, pady=12)
        out.pack(fill="both", expand=True)

        tk.Label(out, text="Results", font=FONT_BOLD,
                 bg=BG, fg=TEXT).pack(anchor="w", pady=(0, 6))

        self.output = scrolledtext.ScrolledText(
            out, width=72, height=22,
            font=FONT_MONO, bg=PANEL, fg=TEXT,
            insertbackground=TEXT, relief="flat", bd=0,
            highlightthickness=1, highlightbackground=PANEL,
            state="disabled", wrap="none"
        )
        self.output.pack(fill="both", expand=True)

        self.output.tag_config("header",  foreground=ACCENT2, font=("Segoe UI", 9, "bold"))
        self.output.tag_config("state",   foreground=TEXT)
        self.output.tag_config("bar",     foreground=ACCENT)
        self.output.tag_config("muted",   foreground=MUTED)
        self.output.tag_config("success", foreground=SUCCESS)
        self.output.tag_config("label",   foreground=ACCENT2)

        tk.Label(self, text="IBM QASM 2.0  ·  statevector simulation  ·  numpy backend",
                 font=("Segoe UI", 8), bg=BG, fg=MUTED).pack(pady=(4, 10))

    # ── Helpers ─────────────────────────────────
    def _browse(self):
        path = filedialog.askopenfilename(
            title="Select QASM file",
            filetypes=[("QASM files", "*.qasm"), ("All files", "*.*")]
        )
        if path:
            self.file_path.set(path)

    def _write(self, text, tag=None):
        self.output.configure(state="normal")
        self.output.insert("end", text, tag or "state")
        self.output.configure(state="disabled")

    def _clear(self):
        self.output.configure(state="normal")
        self.output.delete("1.0", "end")
        self.output.configure(state="disabled")

    # ── Run ─────────────────────────────────────
    def _run(self):
        path = self.file_path.get().strip()
        if not path:
            messagebox.showwarning("No file", "Please select a QASM file first.")
            return
        try:
            shots = int(self.shots_var.get())
            if shots < 1:
                raise ValueError
        except ValueError:
            messagebox.showerror("Bad input", "Shots must be a positive integer.")
            return

        self._clear()
        self.status_lbl.config(text="Running…", fg=MUTED)
        self.update()

        try:
            sim = QuantumSimulator()
            sim.initialize_simulator(path)
            sim.run_simulator(path, shots)  # calls your original method
        except Exception as e:
            self.status_lbl.config(text="Error", fg="#ff7eb6")
            self._write(f"ERROR: {e}\n", "header")
            return

        self.status_lbl.config(text="Done ✓", fg=SUCCESS)
        self._render_results(sim, shots)

    # ── Render results into the output box ──────
    def _render_results(self, sim, shots):
        n  = sim.num_qubits
        sv = sim.statevector

        # Statevector
        self._write("  STATEVECTOR  (non-zero amplitudes)\n", "header")
        self._write("─" * 60 + "\n", "muted")
        for i, amp in enumerate(sv):
            if abs(amp) < 1e-9:
                continue
            label = format(i, f"0{n}b")
            prob  = abs(amp) ** 2
            sign  = "+" if amp.imag >= 0 else "-"
            self._write(f"  |{label}⟩  ", "label")
            self._write(f"{amp.real:+.5f} {sign} {abs(amp.imag):.5f}i", "state")
            self._write(f"    prob = {prob:.5f}\n", "muted")

        # Counts  (re-sample from the statevector your simulator built)
        probs   = np.abs(sv) ** 2
        indices = np.random.choice(len(probs), size=shots, p=probs)
        counts  = Counter(format(i, f"0{n}b") for i in indices)

        self._write(f"\n  COUNTS  ({shots} shots)\n", "header")
        self._write("─" * 60 + "\n", "muted")
        max_c = max(counts.values())
        for bs, c in sorted(counts.items()):
            filled = int(28 * c / max_c)
            bar    = "█" * filled + "░" * (28 - filled)
            self._write(f"  |{bs}⟩  ", "label")
            self._write(bar, "bar")
            self._write(f"  {c:>5}  ({100 * c / shots:5.1f}%)\n", "muted")

        self._write(f"\n  {n} qubit(s)  ·  {2**n} basis states  ·  {shots} shots\n", "success")


# ─────────────────────────────────────────────
if __name__ == "__main__":
    App().mainloop()
