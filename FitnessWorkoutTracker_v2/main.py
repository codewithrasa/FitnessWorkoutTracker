# main.py

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from workout import WorkoutManager
from exercise import Exercise

class App(tk.Tk):
    def __init__(self):
        super().__init__()

        # Setting up main window (Readable / Usability)
        self.title('Fitness Workout Tracker — v2')
        self.geometry('1000x600')

        # Apply a clean theme for better UI experience (Usability)
        self.style = ttk.Style(self)
        try:
            self.style.theme_use('clam')
        except Exception:
            pass

        # Workout manager handles all exercise data (Modularity)
        self.manager = WorkoutManager()

        # Load starter exercises so the UI isn't empty (Usability)
        self._seed_sample_exercises()

        # Build the whole interface (Modularity / Readability)
        self._build_ui()

        # Make sure the list updates as soon as the app loads
        self._refresh_exercise_list()

        # Confirm close properly (Stability)
        self.protocol('WM_DELETE_WINDOW', self._on_close)

    def _seed_sample_exercises(self):
        # Default example exercises to make the app usable right away
        samples = [
            ('Push-Up','Chest',3,12,10,3,'Strength'),
            ('Squat','Legs',4,15,15,4,'Strength'),
            ('Jumping Jacks','Full Body',2,30,5,2,'Cardio'),
            ('Plank','Core',3,1,3,5,'Core')
        ]
        for s in samples:
            try:
                self.manager.add_exercise(*s)
            except Exception:
                # Ignore any duplicate or invalid seeds (Stability)
                pass

    def _build_ui(self):
        # Main layout organization (Readable)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        # Sidebar holds filters and routine controls
        sidebar = ttk.Frame(self, padding=(10,10))
        sidebar.grid(row=0, column=0, sticky='ns')
        self._build_sidebar(sidebar)

        # Content area shows exercise list and routine preview
        content = ttk.Frame(self, padding=(10,10))
        content.grid(row=0, column=1, sticky='nsew')
        content.columnconfigure(0, weight=1)
        content.rowconfigure(1, weight=1)
        self._build_content(content)

        # Detail panel displays selected exercise information
        detail = ttk.Frame(self, padding=(10,10), width=300)
        detail.grid(row=0, column=2, sticky='ns')
        self._build_detail_panel(detail)

    def _build_sidebar(self, parent):
        # Category filter section
        ttk.Label(parent, text='Categories', font=('Helvetica',12,'bold')).pack(anchor='w')
        self.category_var = tk.StringVar(value='All')
        categories = ['All','Strength','Cardio','Core','Flexibility','General']

        # Radio buttons let the user switch exercise views
        for c in categories:
            ttk.Radiobutton(parent, text=c, value=c, variable=self.category_var,
                            command=self._on_filter_change).pack(anchor='w', pady=2)

        ttk.Separator(parent, orient='horizontal').pack(fill='x', pady=8)

        # Buttons for common actions
        ttk.Button(parent, text='Add Exercise', command=self._open_add_dialog).pack(fill='x', pady=4)
        ttk.Button(parent, text='Clear Routine', command=self._clear_routine).pack(fill='x', pady=4)
        ttk.Button(parent, text='Complete Next', command=self._complete_next).pack(fill='x', pady=4)

        # Dropdown to add selected exercise into routine
        ttk.Label(parent, text='Add to Routine:', font=('Helvetica',10,'bold')).pack(anchor='w', pady=(10,0))
        self.add_routine_var = tk.StringVar()
        self.add_routine_combo = ttk.Combobox(parent, textvariable=self.add_routine_var, width=20, state='readonly')
        self.add_routine_combo.pack(anchor='w', pady=2)
        ttk.Button(parent, text='Add Selected', command=self._add_selected_to_routine).pack(fill='x', pady=4)

        # Keep routine dropdown updated
        self._update_routine_dropdown()

    def _update_routine_dropdown(self):
        # Fill dropdown with all exercise names
        all_ex_names = [ex.name for ex in self.manager.get_all_exercises()]
        self.add_routine_combo['values'] = all_ex_names
        if all_ex_names:
            self.add_routine_combo.current(0)

    def _add_selected_to_routine(self):
        # Add chosen exercise into the daily routine
        name = self.add_routine_var.get()
        if not name:
            messagebox.showwarning('Select Exercise', 'Please select an exercise first.')
            return

        ex = self.manager.exercise_bst.find_by_name(name)
        if ex:
            self.manager.add_to_daily_routine(ex)
            self._refresh_routine_label()
            messagebox.showinfo('Added', f'{ex.name} added to daily routine.')
        else:
            messagebox.showerror('Error', 'Selected exercise not found.')

    def _build_content(self, parent):
        # Top toolbar for searching and sorting
        toolbar = ttk.Frame(parent)
        toolbar.grid(row=0, column=0, sticky='ew', pady=(0,8))
        toolbar.columnconfigure(1, weight=1)

        # Search bar to filter the list (Usability)
        ttk.Label(toolbar, text='Search:').grid(row=0, column=0, sticky='w')
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(toolbar, textvariable=self.search_var)
        search_entry.grid(row=0, column=1, sticky='ew', padx=6)
        search_entry.bind('<KeyRelease>', lambda e: self._refresh_exercise_list())

        # Sorting options
        ttk.Label(toolbar, text='Sort by:').grid(row=0, column=2, padx=(10,2))
        self.sort_var = tk.StringVar(value='name')
        ttk.Combobox(toolbar, textvariable=self.sort_var,
                     values=['name','duration','difficulty'], width=12).grid(row=0, column=3)
        ttk.Button(toolbar, text='Apply', command=self._refresh_exercise_list).grid(row=0, column=4, padx=6)

        # Treeview that shows all exercises (Readable)
        self.tree = ttk.Treeview(parent,
                                 columns=('muscle','sets','reps','duration','difficulty','category'),
                                 show='headings', selectmode='browse', height=20)
        self.tree.grid(row=1, column=0, sticky='nsew')

        # Define table columns
        for col, text in [('muscle','Muscle'),('sets','Sets'),('reps','Reps'),
                          ('duration','Duration'),('difficulty','Diff'),('category','Category')]:
            self.tree.heading(col, text=text)
            self.tree.column(col, width=80, anchor='center')

        # When user selects an exercise, show details on the right
        self.tree.bind('<<TreeviewSelect>>', self._on_select_exercise)

        # Right-click menu for quick actions
        self.menu = tk.Menu(self, tearoff=0)
        self.menu.add_command(label='Add to Routine', command=self._menu_add_to_routine)
        self.menu.add_command(label='Edit', command=self._menu_edit)
        self.menu.add_command(label='Delete', command=self._menu_delete)
        self.tree.bind('<Button-3>', self._show_context_menu)

        # Routine label at bottom
        routine_frame = ttk.Frame(parent)
        routine_frame.grid(row=2, column=0, sticky='ew', pady=(8,0))
        ttk.Label(routine_frame, text='Daily Routine:', font=('Helvetica',10,'bold')).pack(anchor='w')
        self.routine_var = tk.StringVar(value='(empty)')
        ttk.Label(routine_frame, textvariable=self.routine_var).pack(anchor='w')

    def _build_detail_panel(self, parent):
        # Panel that displays selected exercise details
        ttk.Label(parent, text='Exercise Details', font=('Helvetica',12,'bold')).pack(anchor='w')

        # Read-only text box for details
        self.detail_text = tk.Text(parent, width=36, height=20, wrap='word', state='disabled')
        self.detail_text.pack(pady=6)

        ttk.Separator(parent, orient='horizontal').pack(fill='x', pady=6)

        # Routine progress section
        ttk.Label(parent, text='Routine Controls', font=('Helvetica',12,'bold')).pack(anchor='w')
        self.progress = ttk.Progressbar(parent, length=0, mode='determinate')
        self.progress.pack(pady=6)

        # Buttons for starting routine + save/load system functionality
        ttk.Button(parent, text='Start Routine', command=self._start_routine).pack(fill='x', pady=4)
        ttk.Button(parent, text='Save Exercises ', command=self._save_to_file).pack(fill='x', pady=4)
        ttk.Button(parent, text='Load Exercises ', command=self._load_from_file).pack(fill='x', pady=4)

    def _refresh_exercise_list(self):
        # Clear the tree before repopulating
        for i in self.tree.get_children():
            self.tree.delete(i)

        # Apply filters and sorting
        cat = self.category_var.get()
        if cat == 'All':
            cat = None
        search = self.search_var.get().strip() or None
        sort_key = self.sort_var.get() or None

        # Get filtered results
        items = self.manager.get_all_exercises(sort_key=sort_key, category_filter=cat, search=search)

        # Insert updated items into the table
        for ex in items:
            self.tree.insert('', 'end', iid=ex.name,
                             values=(ex.muscle_group, ex.sets, ex.reps, ex.duration,
                                     ex.difficulty, ex.category))

        # Update routine label and dropdown
        self._refresh_routine_label()
        self._update_routine_dropdown()

    def _on_select_exercise(self, event):
        # Show full details for selected exercise
        sel = self.tree.selection()
        if not sel:
            return
        name = sel[0]
        ex = self.manager.exercise_bst.find_by_name(name)
        if not ex:
            return
        self._show_details(ex)

    def _show_details(self, ex):
        # Display exercise details in the right panel
        self.detail_text.config(state='normal')
        self.detail_text.delete('1.0','end')

        self.detail_text.insert('end', f"Name: {ex.name}\n")
        self.detail_text.insert('end', f"Muscle Group: {ex.muscle_group}\n")
        self.detail_text.insert('end', f"Sets x Reps: {ex.sets} x {ex.reps}\n")
        self.detail_text.insert('end', f"Duration: {ex.duration} minutes\n")
        self.detail_text.insert('end', f"Difficulty: {ex.difficulty}\n")
        self.detail_text.insert('end', f"Category: {ex.category}\n")

        self.detail_text.config(state='disabled')

    def _open_add_dialog(self):
        # Opens dialog window for adding/editing an exercise
        dialog = AddExerciseDialog(self)
        self.wait_window(dialog.top)

        if dialog.result:
            try:
                self.manager.add_exercise(**dialog.result)
                self._refresh_exercise_list()
                messagebox.showinfo('Added','Exercise added successfully.')
            except Exception as e:
                # Let user know when invalid data breaks saving (Stability)
                messagebox.showerror('Error', f'Failed to add exercise: {e}')

    def _menu_add_to_routine(self):
        # Add selected exercise via context menu
        sel = self.tree.selection()
        if not sel:
            return
        name = sel[0]
        ex = self.manager.exercise_bst.find_by_name(name)
        if ex:
            self.manager.add_to_daily_routine(ex)
            self._refresh_routine_label()

    def _menu_edit(self):
        # Edit selected exercise from context menu
        sel = self.tree.selection()
        if not sel:
            return
        name = sel[0]
        ex = self.manager.exercise_bst.find_by_name(name)
        if not ex:
            return

        dialog = AddExerciseDialog(self, exercise=ex)
        self.wait_window(dialog.top)

        if dialog.result:
            try:
                self.manager.edit_exercise(name, **dialog.result)
                self._refresh_exercise_list()
                messagebox.showinfo('Updated','Exercise updated.')
            except Exception as e:
                messagebox.showerror('Error', f'Failed to edit: {e}')

    def _menu_delete(self):
        # Deletes selected exercise safely
        sel = self.tree.selection()
        if not sel:
            return
        name = sel[0]

        confirm = messagebox.askyesno('Confirm', f'Delete exercise "{name}"?')
        if confirm:
            self.manager.delete_exercise(name)
            self._refresh_exercise_list()

    def _show_context_menu(self, event):
        # Display right-click menu at cursor position
        iid = self.tree.identify_row(event.y)
        if iid:
            self.tree.selection_set(iid)
            self.menu.post(event.x_root, event.y_root)

    def _refresh_routine_label(self):
        # Show routine exercises in a single line
        items = self.manager.get_routine_list()
        if not items:
            self.routine_var.set('(empty)')
        else:
            self.routine_var.set(' -> '.join(x.name for x in items))

        # Update progress bar limits
        total = len(items)
        if total:
            self.progress['maximum'] = total
            self.progress['value'] = 0
        else:
            self.progress['maximum'] = 1
            self.progress['value'] = 0

    def _clear_routine(self):
        # Remove every exercise from routine (simple reset)
        self.manager.clear_routine()
        self._refresh_routine_label()

    def _complete_next(self):
        # Mark next routine exercise as completed
        ex = self.manager.complete_next_exercise()
        if ex:
            messagebox.showinfo('Completed', f'Completed: {ex.name}')
            cur = self.progress['value'] + 1
            self.progress['value'] = cur
            self._refresh_routine_label()
        else:
            messagebox.showinfo('Routine', 'No exercises in routine.')

    def _start_routine(self):
        # Step through each exercise and let user confirm completion
        items = self.manager.get_routine_list()
        if not items:
            messagebox.showinfo('Routine', 'Routine is empty. Add exercises to routine first.')
            return

        for i, ex in enumerate(list(items), start=1):
            resp = messagebox.askyesno('Next Exercise',
                                       f'[{i}/{len(items)}] Do this: {ex.name} — {ex.sets}x{ex.reps} ({ex.duration}min)?\nClick Yes when done, No to stop.')

            if resp:
                self.manager.complete_next_exercise()
                self.progress['value'] = i
                self._refresh_routine_label()
            else:
                break

        messagebox.showinfo('Routine', 'Routine session ended.')

    def _save_to_file(self):
        # Save all exercises to a JSON file for persistence
        import json, tkinter.filedialog as fd
        path = fd.asksaveasfilename(defaultextension='.json', filetypes=[('JSON', '*.json')])
        if not path:
            return

        data = [ex.to_dict() for ex in self.manager.get_all_exercises()]
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)

        messagebox.showinfo('Saved', f'Saved {len(data)} exercises.')

    def _load_from_file(self):
        # Load exercises from JSON file (Stability)
        import json, tkinter.filedialog as fd
        path = fd.askopenfilename(filetypes=[('JSON', '*.json')])
        if not path:
            return

        with open(path, 'r') as f:
            data = json.load(f)

        # Reset manager and rebuild from loaded file
        self.manager = WorkoutManager()
        for d in data:
            try:
                self.manager.add_exercise(
                    d.get('name'),
                    d.get('muscle_group','General'),
                    d.get('sets',1),
                    d.get('reps',1),
                    int(d.get('duration',0)),
                    int(d.get('difficulty',1)),
                    d.get('category','General')
                )
            except Exception:
                # Ignore invalid entries while loading
                pass

        self._refresh_exercise_list()
        messagebox.showinfo('Loaded','Exercises loaded from file.')

    def _on_filter_change(self):
        # When switching categories, refresh the list
        self._refresh_exercise_list()

    def _on_close(self):
        # Exit cleanly instead of force closing
        self.destroy()


# Dialog window used for both editing and adding exercises
class AddExerciseDialog:
    def __init__(self, parent, exercise=None):
        top = self.top = tk.Toplevel(parent)
        top.title('Add Exercise' if exercise is None else 'Edit Exercise')
        top.grab_set()
        self.result = None
        self.exercise = exercise

        # Layout container
        frm = ttk.Frame(top, padding=10)
        frm.pack(fill='both', expand=True)

        # Entry fields for exercise information
        ttk.Label(frm, text='Name:').grid(row=0, column=0, sticky='w')
        self.name = tk.StringVar(value=getattr(exercise,'name','') if exercise else '')
        ttk.Entry(frm, textvariable=self.name, width=30).grid(row=0, column=1, sticky='w')

        ttk.Label(frm, text='Muscle Group:').grid(row=1, column=0, sticky='w')
        self.group = tk.StringVar(value=getattr(exercise,'muscle_group','') if exercise else '')
        ttk.Entry(frm, textvariable=self.group, width=30).grid(row=1, column=1, sticky='w')

        ttk.Label(frm, text='Sets:').grid(row=2, column=0, sticky='w')
        self.sets = tk.StringVar(value=str(getattr(exercise,'sets','3') if exercise else '3'))
        ttk.Entry(frm, textvariable=self.sets, width=10).grid(row=2, column=1, sticky='w')

        ttk.Label(frm, text='Reps:').grid(row=3, column=0, sticky='w')
        self.reps = tk.StringVar(value=str(getattr(exercise,'reps','10') if exercise else '10'))
        ttk.Entry(frm, textvariable=self.reps, width=10).grid(row=3, column=1, sticky='w')

        ttk.Label(frm, text='Duration (min):').grid(row=4, column=0, sticky='w')
        self.duration = tk.StringVar(value=str(getattr(exercise,'duration','5') if exercise else '5'))
        ttk.Entry(frm, textvariable=self.duration, width=10).grid(row=4, column=1, sticky='w')

        ttk.Label(frm, text='Difficulty (1-10):').grid(row=5, column=0, sticky='w')
        self.difficulty = tk.StringVar(value=str(getattr(exercise,'difficulty','3') if exercise else '3'))
        ttk.Entry(frm, textvariable=self.difficulty, width=10).grid(row=5, column=1, sticky='w')

        ttk.Label(frm, text='Category:').grid(row=6, column=0, sticky='w')
        self.category = tk.StringVar(value=getattr(exercise,'category','General') if exercise else 'General')
        ttk.Combobox(frm, textvariable=self.category,
                     values=['General','Strength','Cardio','Core','Flexibility'], width=18).grid(row=6, column=1, sticky='w')

        # Save and cancel buttons
        btn = ttk.Frame(frm)
        btn.grid(row=10, column=0, columnspan=2, pady=(10,0))
        ttk.Button(btn, text='Cancel', command=self._cancel).pack(side='right', padx=4)
        ttk.Button(btn, text='Save', command=self._save).pack(side='right', padx=4)

    def _cancel(self):
        # User backed out without saving
        self.top.destroy()

    def _save(self):
        # Collect and validate user-provided input
        try:
            name = self.name.get().strip()
            group = self.group.get().strip()
            sets = int(self.sets.get())
            reps = int(self.reps.get())
            duration = int(self.duration.get())
            difficulty = int(self.difficulty.get())
            category = self.category.get()

            if not name:
                raise ValueError('Name required')

            # Send data back to app
            self.result = dict(name=name, muscle_group=group, sets=sets, reps=reps,
                               duration=duration, difficulty=difficulty, category=category)
            self.top.destroy()

        except Exception as e:
            # Let the user know if something is wrong
            messagebox.showerror('Invalid', f'Please correct fields: {e}')


if __name__ == '__main__':
    # Start the actual application
    app = App()
    app.mainloop()
