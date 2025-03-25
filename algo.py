import math

class Task:
    def __init__(self, task_id, release_time, deadline, workload):
        self.task_id = task_id
        self.release_time = release_time
        self.deadline = deadline
        self.workload = workload

class ScheduleEntry:
    def __init__(self, task_id, start_time, end_time, frequency):
        self.task_id = task_id
        self.start_time = start_time
        self.end_time = end_time
        self.frequency = frequency

    def __str__(self):
        return f"Task {self.task_id}: [{self.start_time:.1f}, {self.end_time:.1f}] at f={self.frequency:.2f}"

def get_positive_float(prompt):
    while True:
        try:
            value = float(input(prompt))
            if value > 0:
                return value
            else:
                print("Value must be positive.")
        except ValueError:
            print("Invalid input. Please enter a number.")

def main():
    print("Welcome to the Green Energy-Efficient Scheduler!")
    print("Processor parameters: f_min=1.0, f_max=4.0, alpha=2.0, dt=1.0\n")
    
    while True:
        # Get number of tasks
        while True:
            try:
                num_tasks = int(input("Enter the number of tasks to schedule (non-negative integer): "))
                if num_tasks >= 0:
                    break
                print("Please enter a non-negative integer.")
            except ValueError:
                print("Invalid input. Please enter an integer.")

        tasks = []
        for i in range(num_tasks):
            print(f"Enter details for task {i+1}:")
            r = get_positive_float("Release time (r >= 0): ")
            while True:
                d = get_positive_float("Deadline (d > r): ")
                if d > r:
                    break
                print("Deadline must be greater than release time.")
            w = get_positive_float("Workload (w > 0): ")
            tasks.append(Task(i+1, r, d, w))
        
        # Processor parameters
        f_min, f_max, alpha, dt = 1.0, 4.0, 2.0, 1.0
        t, E, schedule = 0.0, 0.0, []
        
        while t < 1000:
            ready_tasks = [task for task in tasks if t >= task.release_time and task.workload > 0]
            if ready_tasks:
                selected_task = min(ready_tasks, key=lambda task: task.deadline)
                slack = selected_task.deadline - t
                f_current = min(max(selected_task.workload / slack, f_min), f_max) if slack > 0 else f_max
                work_done = f_current * dt
                actual_dt = dt if work_done <= selected_task.workload else selected_task.workload / f_current
                work_done = min(work_done, selected_task.workload)
                selected_task.workload -= work_done
                E += (f_current ** alpha) * actual_dt
                schedule.append(ScheduleEntry(selected_task.task_id, t, t + actual_dt, f_current))
                t += actual_dt
            else:
                next_time = min((task.release_time for task in tasks if task.workload > 0 and task.release_time > t), default=None)
                if next_time is None:
                    break
                t = next_time

        all_completed = all(task.workload == 0 for task in tasks)
        if all_completed:
            print("All tasks completed.")
            print(f"Total energy consumed: {E:.1f}")
            print("Schedule:")
            for entry in schedule:
                print(entry)
        else:
            print("Some tasks missed their deadlines.")
            for task in tasks:
                if task.workload > 0:
                    print(f"Task {task.task_id} not completed, remaining work: {task.workload}")
        
        if input("Do you want to schedule another set of tasks? (yes/no): ").strip().lower() != "yes":
            break
    
    print("Thank you for using the Green Energy-Efficient Scheduler!")

if __name__ == "__main__":
    main()
