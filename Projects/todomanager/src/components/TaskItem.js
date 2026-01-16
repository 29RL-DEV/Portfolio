// TaskItem Component - Individual task display and interaction
// Shows task details with status, timestamps, and action buttons
// Features: Checkbox toggle, edit/delete actions, status badges, timestamps

import React, { useState } from 'react';

/**
 * TaskItem - Single task component
 * 
 * Features:
 * - Checkbox to toggle task status
 * - Visual styling based on status (todo, in-progress, done)
 * - Display title and description
 * - Show creation timestamp
 * - Edit and delete buttons
 * - Responsive layout
 * 
 * Props:
 * - task: Task object with id, title, description, status, created_at
 * - onToggle: Callback to change task status
 * - onDelete: Callback to delete task
 * - onEdit: Callback to edit task
 */
const TaskItem = ({ task, onToggle, onDelete, onEdit }) => {
  const [isExpanded, setIsExpanded] = useState(false);
  
  // Color styles for different task statuses
  const statusStyles = {
    todo: "bg-white/5 border-white/10 text-muted",
    "in-progress": "bg-green-500/15 border-green-500/30 text-green-400",
    in_progress: "bg-green-500/15 border-green-500/30 text-green-400",
    done: "bg-green-500/25 border-green-500/40 text-green-300",
  };


  // Status display labels
  const statusLabels = {
    todo: '📝 To Do',
    'in-progress': '⏳ In Progress',
    in_progress: '⏳ In Progress',
    done: '✅ Completed',
  };

  // Format date and time for display
  const formatDateTime = (dateString) => {
    const date = new Date(dateString);
    const dateStr = date.toLocaleDateString('en-US', { 
      month: 'short', 
      day: 'numeric', 
      year: 'numeric' 
    });
    const timeStr = date.toLocaleTimeString('en-US', { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
    return `${dateStr} at ${timeStr}`;
  };

  const isDone = task.status === 'done';

  return (
    <div className="bg-card backdrop-blur-xl rounded-2xl p-6 border border-border min-w-0 overflow-hidden break-words">
      <div className="flex items-start justify-between gap-4">
        {/* Checkbox and Content */}
        <div className="flex items-start gap-4 flex-1 min-w-0">
          {/* Checkbox - Toggle Task Status */}
          <input
            type="checkbox"
            checked={isDone}
            onChange={() => onToggle(task.id)}
            className="w-6 h-6 mt-1 cursor-pointer accent-green-400 flex-shrink-0 hover:accent-green-300"
            title={isDone ? "Mark as pending" : "Mark as completed"}
          />

          {/* Task Details */}
          <div className="flex-1 min-w-0">
            {/* Title */}
            <h3
              className={`text-lg font-semibold break-words transition ${
                isDone ? "line-through text-muted" : "text-strong"
              }`}
            >
              {task.title}
            </h3>

            {/* Description - if present */}
            {task.description && (
              <div>
                <p
                  className={`text-sm mt-2 break-words leading-relaxed ${
                    isExpanded ? "" : "line-clamp-3"
                  } ${isDone ? "text-muted" : "text-muted"}`}
                >
                  {task.description}
                </p>
                {task.description.length > 150 && (
                  <button
                    onClick={() => setIsExpanded(!isExpanded)}
                    className="text-xs mt-2 text-green-400 hover:text-green-300 font-semibold transition"
                  >
                    {isExpanded ? "↑ Read less" : "↓ Read more"}
                  </button>
                )}
              </div>
            )}

            {/* Status Badge and Timestamp */}
            <div className="flex flex-wrap items-center gap-3 mt-4">
              {/* Status Badge */}
              <span
                className={`text-xs font-semibold px-3 py-1 rounded-full border ${
                  statusStyles[task.status]
                }`}
              >
                {statusLabels[task.status]}
              </span>

              {/* Timestamp */}
              <span className="text-xs text-muted flex items-center gap-1">
                <i className="fas fa-clock"></i>
                {formatDateTime(task.created_at)}
              </span>
            </div>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex gap-2 flex-shrink-0">
          {/* Edit Button */}
          <button
            onClick={() => onEdit()}
            className="px-4 py-2 bg-green-500 hover:bg-green-600 text-green-950 rounded-lg transition font-medium text-sm flex items-center gap-2 shadow-md hover:shadow-lg whitespace-nowrap"
            title="Edit this task"
          >
            <i className="fas fa-edit"></i>
            <span className="hidden sm:inline">Edit</span>
          </button>

          {/* Delete Button */}
          <button
            onClick={() => onDelete(task.id)}
            className="px-4 py-2 bg-green-700 hover:bg-green-800 text-green-100 rounded-lg transition font-medium text-sm flex items-center gap-2 shadow-md hover:shadow-lg whitespace-nowrap"
            title="Delete this task"
          >
            <i className="fas fa-trash"></i>
            <span className="hidden sm:inline">Delete</span>
          </button>
        </div>
      </div>
    </div>
  );
};

export default TaskItem;