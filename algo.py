import tkinter as tk
from tkinter import ttk, messagebox, filedialog, colorchooser, simpledialog
import math
import copy
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Task class with dependencies
class Task:
    def __init__(self, task_id, release_time, deadline, workload, dependencies=None):
        self.task_id = task_id
        self.release_time = release_time
        self.deadline = deadline
        self.workload = workload
        self.dependencies = dependencies or []

# ScheduleEntry class
class ScheduleEntry:
    def __init__(self, task_id, start_time, end_time, frequency):
        self.task_id = task_id
        self.start_time = start_time
        self.end_time = end_time
        self.frequency = frequency

    def __str__(self):
        return f"Task {self.task_id}: [{self.start_time:.1f}, {self.end_time:.1f}] at f={self.frequency:.2f}"

# SimulationController with delay
class SimulationController:
    def __init__(self):
        self.playing = False
        self.position = 0
        self.delay = 500  # Initial delay in milliseconds

    def play(self):
        self.playing = True

    def pause(self):
        self.playing = False

    def reset(self):
        self.playing = False
        self.position = 0

# Tooltip class for UI enhancement
class Tooltip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.widget.bind("<Enter>", self.show)
        self.widget.bind("<Leave>", self.hide)

    def show(self, event):
        self.tip = tk.Toplevel(self.widget)
        self.tip.wm_overrideredirect(True)
        self.tip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
        label = ttk.Label(self.tip, text=self.text, background="yellow", relief="solid")
        label.pack()

    def hide(self, event):
        if hasattr(self, "tip"):
            self.tip.destroy()

# Main SchedulerUI class
class SchedulerUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Green Energy-Efficient Scheduler")
        self.tasks = []
        self.schedule = []
        self.task_counter = 1

        # Set up GUI theme
        style = ttk.Style()
        style.theme_use('clam')

        # Menu bar
        menubar = tk.Menu(root)
        helpmenu = tk.Menu(menubar, tearoff=0)
        helpmenu.add_command(label="How to Use", command=self.show_help)
        helpmenu.add_command(label="About", command=self.show_about)
        menubar.add_cascade(label="Help", menu=helpmenu)
        root.config(menu=menubar)

        # Add Task frame
        add_frame = ttk.LabelFrame(root, text="Add Task")
        add_frame.pack(padx=10, pady=5, fill="x")
        ttk.Label(add_frame, text="Release Time:").grid(row=0, column=0)
        self.release_entry = ttk.Entry(add_frame)
        self.release_entry.grid(row=0, column=1)
        Tooltip(self.release_entry, "Time when the task becomes available")
        ttk.Label(add_frame, text="Deadline:").grid(row=1, column=0)
        self.deadline_entry = ttk.Entry(add_frame)
        self.deadline_entry.grid(row=1, column=1)
        Tooltip(self.deadline_entry, "Time by which the task must be completed")
        ttk.Label(add_frame, text="Workload:").grid(row=2, column=0)
        self.workload_entry = ttk.Entry(add_frame)
        self.workload_entry.grid(row=2, column=1)
        Tooltip(self.workload_entry, "Amount of work required (in units)")
        ttk.Button(add_frame, text="Add Task", command=self.add_task).grid(row=3, column=0, columnspan=2, pady=5)
        ttk.Button(add_frame, text="Load Tasks", command=self.load_tasks).grid(row=4, column=0, columnspan=2, pady=5)

        # Tasks List frame
        tasks_frame = ttk.LabelFrame(root, text="Tasks List")
        tasks_frame.pack(padx=10, pady=5, fill="both", expand=True)
        self.tasks_listbox = tk.Listbox(tasks_frame, height=6)
        self.tasks_listbox.pack(side="left", fill="both", expand=True)
        scrollbar = ttk.Scrollbar(tasks_frame, command=self.tasks_listbox.yview)
        scrollbar.pack(side="right", fill="y")
        self.tasks_listbox.config(yscrollcommand=scrollbar.set)
        ttk.Button(tasks_frame, text="Delete Selected Task", command=self.delete_task).pack(pady=5)

        # Buttons frame
        button_frame = ttk.Frame(root)
        button_frame.pack(pady=5)
        ttk.Button(button_frame, text="Schedule Tasks", command=self.schedule_tasks).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text="Export Schedule", command=self.export_schedule).grid(row=0, column=1, padx=5)
        ttk.Button(button_frame, text="Show Gantt Chart", command=self.show_gantt_chart).grid(row=0, column=2, padx=5)
        ttk.Button(button_frame, text="Simulate", command=self.run_simulation).grid(row=0, column=3, padx=5)

        # Result frame
        result_frame = ttk.LabelFrame(root, text="Scheduling Result")
        result_frame.pack(padx=10, pady=5, fill="both", expand=True)
        self.result_text = tk.Text(result_frame, height=10)
        self.result_text.pack(fill="both", expand=True)

    def add_task(self):
        """Add a new task with validation."""
        try:
            release_time = float(self.release_entry.get())
            deadline = float(self.deadline_entry.get())
            workload = float(self.workload_entry.get())
            if release_time < 0 or deadline <= release_time or workload <= 0:
                raise ValueError("Invalid input values.")
            f_required = workload / (deadline - release_time)
            if f_required > 4.0:
                raise ValueError(f"Workload too high. Minimum frequency needed: {f_required:.2f} > 4.0")
            elif f_required < 1.0:
                raise ValueError(f"Workload too low for deadline. Minimum frequency: {f_required:.2f} < 1.0")
        except ValueError as e:
            messagebox.showerror("Input Error", str(e))
            return

        task = Task(self.task_counter, release_time, deadline, workload)
        self.tasks.append(task)
        self.tasks_listbox.insert(tk.END, f"Task {self.task_counter}: r={release_time}, d={deadline}, w={workload}")
        self.task_counter += 1
        self.release_entry.delete(0, tk.END)
        self.deadline_entry.delete(0, tk.END)
        self.workload_entry.delete(0, tk.END)

    def load_tasks(self):
        """Load tasks from a file."""
        file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
        if file_path:
            with open(file_path, "r") as file:
                for line in file:
                    try:
                        release_time, deadline, workload = map(float, line.strip().split(","))
                        task = Task(self.task_counter, release_time, deadline, workload)
                        self.tasks.append(task)
                        self.tasks_listbox.insert(tk.END, f"Task {self.task_counter}: r={release_time}, d={deadline}, w={workload}")
                        self.task_counter += 1
                    except ValueError:
                        messagebox.showerror("File Error", f"Invalid format in {file_path}")
                        return

    def delete_task(self):
        """Delete the selected task."""
        selection = self.tasks_listbox.curselection()
        if not selection:
            return
        index = selection[0]
        del self.tasks[index]
        self.tasks_listbox.delete(index)

    def schedule_tasks(self):
        """Schedule tasks with dependency support."""
        if not self.tasks:
            messagebox.showwarning("No Tasks", "Add tasks first.")
            return

        f_min, f_max, alpha, dt = 1.0, 4.0, 2.0, 1.0
        t, E, self.schedule = 0.0, 0.0, []
        tasks_copy = copy.deepcopy(self.tasks)

        while t < 1000:
            ready_tasks = [task for task in tasks_copy if t >= task.release_time and task.workload > 0 and
                           all(dep.workload <= 1e-6 for dep in tasks_copy if dep.task_id in task.dependencies)]
            if ready_tasks:
                selected_task = min(ready_tasks, key=lambda task: task.deadline)
                slack = selected_task.deadline - t
                f_current = min(max(selected_task.workload / slack, f_min), f_max) if slack > 0 else f_max
                work_done = f_current * dt
                actual_dt = dt if work_done <= selected_task.workload else selected_task.workload / f_current
                work_done = min(work_done, selected_task.workload)
                selected_task.workload -= work_done
                E += (f_current ** alpha) * actual_dt
                self.schedule.append(ScheduleEntry(selected_task.task_id, t, t + actual_dt, f_current))
                t += actual_dt
            else:
                future = [task.release_time for task in tasks_copy if task.workload > 0 and task.release_time > t]
                if future:
                    t = min(future)
                else:
                    break

        result = "All tasks completed.\n" if all(task.workload <= 1e-6 for task in tasks_copy) else "Some tasks missed deadlines.\n"
        result += f"Total energy consumed: {E:.1f}\nSchedule:\n" + "\n".join(str(entry) for entry in self.schedule)
        self.result_text.delete("1.0", tk.END)
        self.result_text.insert(tk.END, result)

    def export_schedule(self):
        """Export the schedule to a text file."""
        if not self.schedule:
            messagebox.showwarning("No Schedule", "Run scheduling first.")
            return
        file_path = filedialog.asksaveasfilename(defaultextension=".txt")
        if file_path:
            with open(file_path, "w") as file:
                for entry in self.schedule:
                    file.write(str(entry) + "\n")
            messagebox.showinfo("Export Successful", f"Schedule saved to {file_path}")

    def show_gantt_chart(self):
        """Display an editable Gantt chart."""
        if not self.schedule:
            messagebox.showwarning("No Schedule", "Run scheduling first.")
            return

        # Create a new window for the Gantt chart
        chart_window = tk.Toplevel(self.root)
        chart_window.title("Gantt Chart")

        # Determine maximum time and unique task IDs
        max_time = max(entry.end_time for entry in self.schedule)
        task_ids = set(entry.task_id for entry in self.schedule)

        # Use default colors for tasks
        custom_colors = {task_id: f"#{(task_id * 1234567) % 0xFFFFFF:06x}" for task_id in task_ids}

        # Create the Matplotlib figure and axis
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.set_xlabel("Time")
        ax.set_ylabel("Task ID")
        ax.set_xlim(0, max_time)
        ax.set_ylim(0, max(task_ids) + 1)
        ax.grid(True)

        # Create and pack the canvas BEFORE defining the update function.
        canvas = FigureCanvasTkAgg(fig, master=chart_window)
        canvas.get_tk_widget().pack(fill="both", expand=True)

        # Define the function to update the Gantt chart with current custom_colors.
        def update_gantt_chart():
            ax.clear()
            ax.set_xlabel("Time")
            ax.set_ylabel("Task ID")
            ax.set_xlim(0, max_time)
            ax.set_ylim(0, max(task_ids) + 1)
            ax.grid(True)
            for entry in self.schedule:
                color = custom_colors.get(entry.task_id, "#000000")
                ax.barh(entry.task_id, entry.end_time - entry.start_time,
                        left=entry.start_time, height=0.4, color=color, edgecolor="black")
                ax.text((entry.start_time + entry.end_time) / 2, entry.task_id,
                        f"T{entry.task_id}", va="center", ha="center", color="white", fontsize=8)
            canvas.draw()

        # Initialize the chart with default colors
        update_gantt_chart()

        # Function to edit colors for a specific task
        def edit_colors():
            task_id = simpledialog.askinteger("Edit Color", "Enter Task ID to change its color:", parent=chart_window)
            if task_id is None:
                return
            if task_id not in custom_colors:
                messagebox.showerror("Error", f"Task ID {task_id} not found in schedule.", parent=chart_window)
                return
            new_color = colorchooser.askcolor(title=f"Choose new color for Task {task_id}")[1]
            if new_color:
                custom_colors[task_id] = new_color
                update_gantt_chart()

        # Function to save the current chart as a PNG file
        def save_chart():
            save_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG Files", "*.png")])
            if save_path:
                fig.savefig(save_path)
                messagebox.showinfo("Saved", f"Gantt chart saved to {save_path}", parent=chart_window)

        # Create a control frame at the bottom of the chart window
        control_frame = ttk.Frame(chart_window)
        control_frame.pack(pady=5)
        ttk.Button(control_frame, text="Edit Colors", command=edit_colors).pack(side="left", padx=5)
        ttk.Button(control_frame, text="Save Chart", command=save_chart).pack(side="left", padx=5)

    def run_simulation(self):
        """Run a real-time simulation with energy visualization and controls."""
        if not self.schedule:
            messagebox.showwarning("No Schedule", "Run scheduling first.")
            return

        # Create simulation window
        sim_window = tk.Toplevel(self.root)
        sim_window.title("Simulation")

        # Calculate maximum time and task ID
        max_time = max(entry.end_time for entry in self.schedule)
        max_task_id = max(entry.task_id for entry in self.schedule)

        # Set up Matplotlib figure with two subplots
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 6), gridspec_kw={'height_ratios': [3, 1]})
        ax1.set_ylim(0, max_task_id + 1)
        ax1.set_xlim(0, max_time)
        ax1.set_ylabel("Task ID")
        ax2.set_xlim(0, max_time)
        ax2.set_xlabel("Time")
        ax2.set_ylabel("Energy")

        # Embed the figure in Tkinter
        canvas = FigureCanvasTkAgg(fig, master=sim_window)
        canvas.get_tk_widget().pack(fill="both", expand=True)

        # Define colors for tasks
        colors = {entry.task_id: f"#{hash(entry.task_id) & 0xFFFFFF:06x}" for entry in self.schedule}

        # Initialize controller
        controller = SimulationController()

        # Energy data
        energy_data = [(entry.end_time, (entry.frequency ** 2.0) * (entry.end_time - entry.start_time))
                       for entry in self.schedule]
        cumulative_energy = [sum(e[1] for e in energy_data[:i + 1]) for i in range(len(energy_data))]

        # Progress bar
        progress_bar = ttk.Progressbar(sim_window, maximum=len(self.schedule), mode="determinate")
        progress_bar.pack(pady=5)

        # Function to update the plot
        def update_plot():
            if controller.position < len(self.schedule):
                if controller.playing:
                    entry = self.schedule[controller.position]
                    ax1.barh(entry.task_id, entry.end_time - entry.start_time, left=entry.start_time,
                             height=0.4, color=colors[entry.task_id])
                    if controller.position > 0:
                        ax2.plot([self.schedule[controller.position - 1].end_time, entry.end_time],
                                 [cumulative_energy[controller.position - 1], cumulative_energy[controller.position]], "b-")
                    progress_bar["value"] = controller.position
                    controller.position += 1
                    canvas.draw()
            sim_window.after(controller.delay, update_plot)

        # Step forward and backward functions
        def step_forward():
            if controller.position < len(self.schedule):
                entry = self.schedule[controller.position]
                ax1.barh(entry.task_id, entry.end_time - entry.start_time, left=entry.start_time,
                         height=0.4, color=colors[entry.task_id])
                if controller.position > 0:
                    ax2.plot([self.schedule[controller.position - 1].end_time, entry.end_time],
                             [cumulative_energy[controller.position - 1], cumulative_energy[controller.position]], "b-")
                progress_bar["value"] = controller.position
                controller.position += 1
                canvas.draw()

        def step_backward():
            if controller.position > 0:
                controller.position -= 1
                ax1.clear()
                ax1.set_ylim(0, max_task_id + 1)
                ax1.set_xlim(0, max_time)
                ax1.set_ylabel("Task ID")
                for i in range(controller.position):
                    entry = self.schedule[i]
                    ax1.barh(entry.task_id, entry.end_time - entry.start_time, left=entry.start_time,
                             height=0.4, color=colors[entry.task_id])
                ax2.clear()
                ax2.set_xlim(0, max_time)
                ax2.set_xlabel("Time")
                ax2.set_ylabel("Energy")
                if controller.position > 0:
                    ax2.plot([0] + [e.end_time for e in self.schedule[:controller.position]],
                             [0] + cumulative_energy[:controller.position], "b-")
                progress_bar["value"] = controller.position
                canvas.draw()

        # Toggle play/pause
        def toggle_play_pause():
            if controller.playing:
                controller.pause()
                toggle_button.config(text="Play")
            else:
                controller.play()
                toggle_button.config(text="Pause")

        # Speed controls
        def faster():
            controller.delay = max(100, controller.delay - 100)

        def slower():
            controller.delay = min(2000, controller.delay + 100)

        # Reset simulation
        def reset():
            ax1.clear()
            ax1.set_ylim(0, max_task_id + 1)
            ax1.set_xlim(0, max_time)
            ax1.set_ylabel("Task ID")
            ax2.clear()
            ax2.set_xlim(0, max_time)
            ax2.set_xlabel("Time")
            ax2.set_ylabel("Energy")
            controller.position = 0
            controller.playing = False
            toggle_button.config(text="Play")
            progress_bar["value"] = 0
            canvas.draw()

        # Save animation
        def save_animation():
            save_fig, (save_ax1, save_ax2) = plt.subplots(2, 1, figsize=(8, 6), gridspec_kw={'height_ratios': [3, 1]})
            save_ax1.set_ylim(0, max_task_id + 1)
            save_ax1.set_xlim(0, max_time)
            save_ax1.set_ylabel("Task ID")
            save_ax2.set_xlim(0, max_time)
            save_ax2.set_xlabel("Time")
            save_ax2.set_ylabel("Energy")

            def init():
                return []

            def update(frame):
                entry = self.schedule[frame]
                bar = save_ax1.barh(entry.task_id, entry.end_time - entry.start_time, left=entry.start_time,
                                     height=0.4, color=colors[entry.task_id])
                if frame > 0:
                    line = save_ax2.plot([self.schedule[frame - 1].end_time, entry.end_time],
                                         [cumulative_energy[frame - 1], cumulative_energy[frame]], "b-")
                else:
                    line = []
                return bar, line

            anim = animation.FuncAnimation(save_fig, update, frames=len(self.schedule), init_func=init, blit=False)

            save_path = filedialog.asksaveasfilename(defaultextension=".mp4",
                                                     filetypes=[("MP4 Files", "*.mp4"), ("GIF Files", "*.gif")])
            if save_path:
                try:
                    if save_path.endswith(".mp4"):
                        anim.save(save_path, writer="ffmpeg", fps=2)
                    elif save_path.endswith(".gif"):
                        anim.save(save_path, writer="pillow", fps=2)
                    messagebox.showinfo("Saved", f"Animation saved to {save_path}")
                except Exception as e:
                    messagebox.showerror("Save Error", f"Failed to save animation: {e}")

        # Control frame for simulation
        control_frame = ttk.Frame(sim_window)
        control_frame.pack(pady=5)

        toggle_button = ttk.Button(control_frame, text="Play", command=toggle_play_pause)
        toggle_button.pack(side="left", padx=5)
        ttk.Button(control_frame, text="Step Forward", command=step_forward).pack(side="left", padx=5)
        ttk.Button(control_frame, text="Step Backward", command=step_backward).pack(side="left", padx=5)
        ttk.Button(control_frame, text="Faster", command=faster).pack(side="left", padx=5)
        ttk.Button(control_frame, text="Slower", command=slower).pack(side="left", padx=5)
        ttk.Button(control_frame, text="Reset", command=reset).pack(side="left", padx=5)
        ttk.Button(control_frame, text="Save Animation", command=save_animation).pack(side="left", padx=5)

        # Start simulation
        update_plot()

    def show_help(self):
        """Display help information."""
        message = (
            "1. Enter the Release Time, Deadline, and Workload for a task, then click 'Add Task'.\n"
            "2. Click 'Schedule Tasks' to run the green scheduling algorithm.\n"
            "3. Use 'Export Schedule' to save the result to a file.\n"
            "4. Click 'Show Gantt Chart' to visualize the schedule.\n"
            "5. Click 'Simulate' to see task execution in real time.\n"
            "6. Use 'Delete Selected Task' to remove tasks before scheduling."
        )
        messagebox.showinfo("How to Use", message)

    def show_about(self):
        """Display about information."""
        messagebox.showinfo("About", "Green Energy-Efficient Scheduler\nCreated with Tkinter and Python")

def main():
    root = tk.Tk()
    app = SchedulerUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
