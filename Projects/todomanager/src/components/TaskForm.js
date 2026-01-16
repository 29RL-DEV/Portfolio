// TaskForm Component - Create and edit tasks
// Handles task creation and editing with validation
// Features: Form validation, error display, optimistic updates, clear on submit

import React, { useState, useEffect } from 'react';

/**
 * TaskForm - Task creation and editing form
 * 
 * Features:
 * - Create new tasks
 * - Edit existing tasks
 * - Form validation (required fields, length limits)
 * - Status selection (todo, in-progress, done)
 * - Error handling and display
 * - Auto-clear on successful create (not on edit)
 * 
 * Props:
 * - onSubmit: Callback function when form is submitted
 * - initialData: Task data for editing (empty for create)
 * - onCancel: Callback to close edit mode
 * - isEditing: Boolean indicating if in edit mode
 */
const TaskForm = ({ onSubmit, initialData = {}, onCancel, isEditing = false }) => {
  const [formData, setFormData] = useState({
    title: initialData.title || '',
    description: initialData.description || '',
    status: initialData.status || 'todo',
  });
  const [error, setError] = useState('');

  // Update form when initialData changes (e.g., when editing different task)
  useEffect(() => {
    setFormData({
      title: initialData.title || '',
      description: initialData.description || '',
      status: initialData.status || 'todo',
    });
    setError('');
  }, [initialData]);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
    setError('');
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    
    // Validation: Title is required
    if (!formData.title.trim()) {
      setError('Task title is required');
      return;
    }
    
    // Validation: Title length (reasonable limit)
    if (formData.title.trim().length > 200) {
      setError('Title must be less than 200 characters');
      return;
    }
    
    // Validation: Description length (if provided)
    if (formData.description && formData.description.length > 1000) {
      setError('Description must be less than 1000 characters');
      return;
    }
    
    // Submit form data to parent component
    onSubmit(formData);
    
    // Clear form only in create mode (not edit mode)
    if (!isEditing) {
      setFormData({ title: '', description: '', status: 'todo' });
    }
  };

  return (
    <form onSubmit={handleSubmit} className="bg-blue-900 bg-opacity-30 backdrop-blur-sm border border-blue-700 rounded-xl shadow-lg p-4 mb-6 hover:border-blue-600 transition">
      <h3 className="text-lg font-semibold mb-3 text-blue-100 flex items-center gap-2">
        {isEditing ? (
          <>
            <i className="fas fa-edit"></i>
            Edit Task
          </>
        ) : (
          <>
            <i className="fas fa-plus-circle"></i>
            Add New Task
          </>
        )}
      </h3>
      
      {/* Error Message */}
      {error && (
        <div className="bg-red-500 bg-opacity-20 border border-red-500 text-red-200 px-3 py-2 rounded-lg mb-4 text-sm flex items-center gap-2">
          <i className="fas fa-exclamation-triangle"></i>
          {error}
        </div>
      )}

      <div className="space-y-3">
        {/* Title Input */}
        <div>
          <label htmlFor="title" className="block text-sm font-medium text-blue-200 mb-2">
            <i className="fas fa-heading mr-2"></i>Task Title
          </label>
          <input
            type="text"
            id="title"
            name="title"
            value={formData.title}
            onChange={handleChange}
            placeholder="What needs to be done?"
            maxLength="200"
            className="w-full px-4 py-2 bg-blue-900 border border-blue-600 rounded-lg text-white placeholder-blue-400 focus:outline-none focus:ring-2 focus:ring-blue-400 transition"
            required
          />
          <p className="text-xs text-blue-400 mt-1">{formData.title.length}/200</p>
        </div>

        {/* Description Input */}
        <div>
          <label htmlFor="description" className="block text-sm font-medium text-blue-200 mb-2">
            <i className="fas fa-align-left mr-2"></i>Description (Optional)
          </label>
          <textarea
            id="description"
            name="description"
            value={formData.description}
            onChange={handleChange}
            placeholder="Add more details..."
            maxLength="1000"
            rows="2"
            className="w-full px-4 py-2 bg-blue-900 border border-blue-600 rounded-lg text-white placeholder-blue-400 focus:outline-none focus:ring-2 focus:ring-blue-400 transition resize-none"
          ></textarea>
          <p className="text-xs text-blue-400 mt-1">{formData.description.length}/1000</p>
        </div>

        {/* Status Selection */}
        <div>
          <label htmlFor="status" className="block text-sm font-medium text-blue-200 mb-2">
            <i className="fas fa-check-square mr-2"></i>Status
          </label>
          <select
            id="status"
            name="status"
            value={formData.status}
            onChange={handleChange}
            className="w-full px-4 py-2 bg-blue-900 border border-blue-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-400 transition"
          >
            <option value="todo">To Do</option>
            <option value="in_progress">In Progress</option>
            <option value="done">Completed</option>
          </select>
        </div>

        {/* Action Buttons */}
        <div className="flex gap-3 pt-2">
          <button
            type="submit"
            className="flex-1 bg-blue-600 hover:bg-blue-700 text-white py-2 rounded-lg transition font-semibold flex items-center justify-center gap-2 shadow-md hover:shadow-lg"
          >
            {isEditing ? (
              <>
                <i className="fas fa-save"></i>
                Save Changes
              </>
            ) : (
              <>
                <i className="fas fa-plus"></i>
                Add Task
              </>
            )}
          </button>
          
          {isEditing && (
            <button
              type="button"
              onClick={onCancel}
              className="flex-1 bg-gray-600 hover:bg-gray-700 text-white py-2 rounded-lg transition font-semibold flex items-center justify-center gap-2 shadow-md hover:shadow-lg"
            >
              <i className="fas fa-times"></i>
              Cancel
            </button>
          )}
        </div>
      </div>
    </form>
  );
};

export default TaskForm;