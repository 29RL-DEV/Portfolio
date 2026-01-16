// TaskList Component - Main task management container
// Handles fetching, creating, updating, and deleting tasks
// Features: Real-time sync with backend, optimistic updates, error handling

import React, { useState, useEffect } from "react";
import { taskAPI } from "../api/tasks";
import TaskItem from "./TaskItem";
import TaskForm from "./TaskForm";
import { useNavigate } from "react-router-dom";

/**
 * TaskList - Main task management component
 *
 * State Management:
 * - tasks: Array of task objects
 * - loading: Loading state during API calls
 * - error: Error message string
 * - editingTask: Currently edited task object or null
 *
 * API Operations:
 * - fetchTasks(): GET /api/tasks/ - Retrieve all user tasks
 * - handleCreate(): POST /api/tasks/ - Create new task
 * - handleUpdate(): PUT /api/tasks/{id}/ - Update existing task
 * - handleDelete(): DELETE /api/tasks/{id}/ - Delete task
 * - handleToggleStatus(): PATCH task status
 */
const TaskList = () => {
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [, setError] = useState(null);
  const [editingTask, setEditingTask] = useState(null);

  // Fetch tasks on component mount
  // Only runs once due to empty dependency array
  useEffect(() => {
    fetchTasks();
  }, []);

  /**
   * Fetch all tasks for the current authenticated user
   * Backend filters tasks by user automatically via JWT token
   */
  const fetchTasks = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await taskAPI.getAll();
      // Handle both array and paginated responses
      setTasks(Array.isArray(data) ? data : data.results || []);
    } catch (error) {
      setError("Failed to load tasks. Please try again.");
      console.error("Error fetching tasks:", error);
      setTasks([]);
    } finally {
      setLoading(false);
    }
  };

  /**
   * Create new task - optimistic update pattern
   * Shows new task immediately, then verifies with server
   * If server request fails, error is shown but UI already updated
   */
  const handleCreate = async (taskData) => {
    try {
      setError(null);
      const newTask = await taskAPI.create(taskData);
      setTasks((prev) => [newTask, ...prev]);
    } catch (error) {
      setError("Failed to create task. Please try again.");
      console.error("Error creating task:", error);
    }
  };

  /**
   * Update existing task
   * Finds task by ID and updates it in the list
   * Closes editing form after successful update
   */
  const handleUpdate = async (taskData) => {
    try {
      setError(null);
      const updatedTask = await taskAPI.update(editingTask.id, taskData);
      setTasks((prev) =>
        prev.map((task) => (task.id === updatedTask.id ? updatedTask : task)),
      );
      setEditingTask(null);
    } catch (error) {
      setError("Failed to update task. Please try again.");
      console.error("Error updating task:", error);
    }
  };

  /**
   * Delete task with confirmation
   * Asks user before removing task from list
   * Removes task from local state after server confirms deletion
   */
  const handleDelete = async (id) => {
    if (!window.confirm("Are you sure you want to delete this task?")) return;
    try {
      setError(null);
      await taskAPI.delete(id);
      setTasks((prev) => prev.filter((task) => task.id !== id));
    } catch (error) {
      setError("Failed to delete task. Please try again.");
      console.error("Error deleting task:", error);
    }
  };

  /**
   * Toggle task status between 'todo' and 'done'
   * Quick status update for task completion workflow
   * Shows visual feedback of completion percentage
   */
  const handleToggleStatus = async (id) => {
    const task = tasks.find((t) => t.id === id);
    if (!task) return;

    const newStatus = task.status === "done" ? "todo" : "done";

    try {
      setError(null);
      const updatedTask = await taskAPI.update(id, { status: newStatus });
      setTasks((prev) =>
        prev.map((t) => (t.id === updatedTask.id ? updatedTask : t)),
      );
    } catch (error) {
      setError("Failed to update task status. Please try again.");
      console.error("Error updating status:", error);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-900 to-blue-700 flex justify-center">
      <div className="w-full max-w-7xl px-6 pt-32">
        <div className="grid grid-cols-1 lg:grid-cols-[460px_minmax(0,650px)] gap-6 lg:gap-20 items-start">
          {" "}
          {/* ADD TASK – CARD CA LOGIN */}
          <div className="bg-blue-900 bg-opacity-40 backdrop-blur-xl rounded-2xl p-5 shadow-xl border border-blue-700">
            <TaskForm
              onSubmit={editingTask ? handleUpdate : handleCreate}
              initialData={editingTask || {}}
              onCancel={() => setEditingTask(null)}
              isEditing={!!editingTask}
            />
          </div>
          {/* TASK LIST */}
          <div className="space-y-4">
            {loading && (
              <div className="text-center py-16 text-blue-300">Loading…</div>
            )}

            {!loading && tasks.length === 0 && (
              <div className="bg-blue-900 bg-opacity-40 backdrop-blur-xl rounded-2xl p-10 border border-blue-700 text-center text-blue-200">
                No tasks yet. Create one to get started!
              </div>
            )}

            {tasks.map((task) => (
              <TaskItem
                key={task.id}
                task={task}
                onToggle={handleToggleStatus}
                onDelete={handleDelete}
                onEdit={() => setEditingTask(task)}
              />
            ))}

            {/* PROGRESS */}
            {tasks.length > 0 && (
              <div className="mt-8 bg-blue-900 bg-opacity-40 backdrop-blur-xl rounded-2xl p-6 border border-blue-700">
                <div className="flex items-center gap-4 min-w-0">
                  <p className="text-blue-200 break-words">
                    {tasks.filter((t) => t.status === "done").length} /{" "}
                    {tasks.length}
                  </p>
                  <div className="flex-1 min-w-0 h-2 bg-blue-800 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-gradient-to-r from-green-400 to-green-500"
                      style={{
                        width: `${
                          (tasks.filter((t) => t.status === "done").length /
                            tasks.length) *
                          100
                        }%`,
                      }}
                    />
                  </div>
                </div>
              </div>
            )}

            {/* Back to Portfolio Button - 2cm spacing (75px) */}
            <div style={{ marginTop: "75px" }} className="flex justify-center">
              <a
                href="https://29rl.dev/?from=portfolio&return=/"
                className="bg-black/60 backdrop-blur-md border border-white/10 text-green-400 px-6 py-2 rounded-lg text-sm font-semibold shadow-lg hover:bg-black/80 transition inline-flex items-center gap-2 whitespace-nowrap"
              >
                ← Back to Portfolio
              </a>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TaskList;
