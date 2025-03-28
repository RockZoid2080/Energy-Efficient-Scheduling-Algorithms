import tkinter as tk
from tkinter import ttk, messagebox
import math
import copy

class Task:
    def __init__(self, task_id, release_time, deadline, workload):
        """
        Initializes a Task with its identifier, release time, deadline, and required workload.
        """
        self.task_id = task_id
        self.release_time = release_time
        self.deadline = deadline
        self.workload = workload

class ScheduleEntry:
    def __init__(self, task_id, start_time, end_time, frequency):
        """
        Records a scheduling decision with task identifier, start/end times, and CPU frequency used.
        """
        self.task_id = task_id
        self.start_time = start_time
        self.end_time = end_time
        self.frequency = frequency

    def __str__(self):
        return f"Task {self.task_id}: [{self.start_time:.1f}, {self.end_time:.1f}] at f={self.frequency:.2f}"

class SchedulerUI:
    def __init__(self, root):
        """
        Initializes the GUI components, task list, and counters.
        """
        self.root = root
        self.root.title("Green Energy-Efficient Scheduler")
        self.tasks = []
        self.task_counter = 1

        # Frame for adding tasks
        add_frame = ttk.LabelFrame(root, text="Add Task")
        add_frame.pack(padx=10, pady=10, fill="x")

        ttk.Label(add_frame, text="Release Time:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.release_entry = ttk.Entry(add_frame)
        self.release_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(add_frame, text="Deadline:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.deadline_entry = ttk.Entry(add_frame)
        self.deadline_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(add_frame, text="Workload:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        self.workload_entry = ttk.Entry(add_frame)
        self.workload_entry.grid(row=2, column=1, padx=5, pady=5)

        add_button = ttk.Button(add_frame, text="Add Task", command=self.add_task)
        add_button.grid(row=3, column=0, columnspan=2, pady=5)

        # Listbox to show tasks
        tasks_frame = ttk.LabelFrame(root, text="Tasks List")
        tasks_frame.pack(padx=10, pady=10, fill="both", expand=True)

        self.tasks_listbox = tk.Listbox(tasks_frame, height=10)
        self.tasks_listbox.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        scrollbar = ttk.Scrollbar(tasks_frame, orient="vertical", command=self.tasks_listbox.yview)
        scrollbar.pack(side="right", fill="y")
        self.tasks_listbox.config(yscrollcommand=scrollbar.set)

        # Button to schedule tasks
        schedule_button = ttk.Button(root, text="Schedule Tasks", command=self.schedule_tasks)
        schedule_button.pack(pady=5)

        # Text widget to show scheduling result
        result_frame = ttk.LabelFrame(root, text="Scheduling Result")
        result_frame.pack(padx=10, pady=10, fill="both", expand=True)
        self.result_text = tk.Text(result_frame, height=15)
        self.result_text.pack(fill="both", expand=True, padx=5, pady=5)

    def add_task(self):
        """
        Reads and validates task parameters from the input fields and adds the task.
        """
        try:
            release_time = float(self.release_entry.get())
            deadline = float(self.deadline_entry.get())
            workload = float(self.workload_entry.get())
            if release_time < 0:
                messagebox.showerror("Input Error", "Release time must be non-negative.")
                return
            if deadline <= release_time:
                messagebox.showerror("Input Error", "Deadline must be greater than release time.")
                return
            if workload <= 0:
                messagebox.showerror("Input Error", "Workload must be positive.")
                return
        except ValueError:
            messagebox.showerror("Input Error", "Please enter valid numbers.")
            return

        # Create and add new task to the list
        task = Task(self.task_counter, release_time, deadline, workload)
        self.tasks.append(task)
        self.tasks_listbox.insert(tk.END, f"Task {self.task_counter}: r={release_time}, d={deadline}, w={workload}")
        self.task_counter += 1

        # Clear input fields for next task
        self.release_entry.delete(0, tk.END)
        self.deadline_entry.delete(0, tk.END)
        self.workload_entry.delete(0, tk.END)

    def schedule_tasks(self):
        """
        Executes the scheduling simulation, computes energy consumption, and displays the results.
        """
        if not self.tasks:
            messagebox.showwarning("No Tasks", "Please add at least one task before scheduling.")
            return

        # Processor parameters: minimum frequency, maximum frequency, energy exponent (alpha), and time slice dt.
        f_min, f_max, alpha, dt = 1.0, 4.0, 2.0, 1.0
        t, total_energy, schedule = 0.0, 0.0, []

        # Create a copy of tasks since we modify the workload during scheduling.
        tasks_copy = copy.deepcopy(self.tasks)

        # Simulation loop
        while t < 1000:
            # Filter tasks that are ready to execute and have remaining workload.
            ready_tasks = [task for task in tasks_copy if t >= task.release_time and task.workload > 0]
            if ready_tasks:
                # Choose the task with the earliest deadline.
                selected_task = min(ready_tasks, key=lambda task: task.deadline)
                slack = selected_task.deadline - t
                # Compute current frequency based on remaining workload and slack time.
                if slack > 0:
                    f_current = min(max(selected_task.workload / slack, f_min), f_max)
                else:
                    f_current = f_max

                work_possible = f_current * dt
                # Adjust the execution time if the remaining workload is less than work_possible.
                actual_dt = dt if work_possible <= selected_task.workload else selected_task.workload / f_current
                work_done = min(work_possible, selected_task.workload)
                
                selected_task.workload -= work_done
                total_energy += (f_current ** alpha) * actual_dt
                schedule.append(ScheduleEntry(selected_task.task_id, t, t + actual_dt, f_current))
                t += actual_dt
            else:
                # No tasks are ready; jump to the next release time.
                future_times = [task.release_time for task in tasks_copy if task.workload > 0 and task.release_time > t]
                if future_times:
                    t = min(future_times)
                else:
                    break

        # Prepare result summary.
        result = ""
        all_completed = all(task.workload <= 1e-6 for task in tasks_copy)
        if all_completed:
            result += "All tasks completed.\n"
            result += f"Total energy consumed: {total_energy:.1f}\n"
            result += "Schedule:\n"
            for entry in schedule:
                result += str(entry) + "\n"
        else:
            result += "Some tasks missed their deadlines.\n"
            for task in tasks_copy:
                if task.workload > 0:
                    result += f"Task {task.task_id} not completed, remaining work: {task.workload}\n"

        # Display the result in the text widget.
        self.result_text.delete("1.0", tk.END)
        self.result_text.insert(tk.END, result)

def main():
    root = tk.Tk()
    app = SchedulerUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
