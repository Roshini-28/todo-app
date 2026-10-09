"use client";

export default function TodoItem({ task, onComplete, onUncomplete, onEdit, onDelete, loading, draggable, onDragStart, onDragOver, onDrop, onDragEnd, isDragging }) {
  const isCompleted = task.status === "Completed";

  const formatDate = (dateString) => {
    if (!dateString) return "";
    const date = new Date(dateString);
    return date.toLocaleString("en-US", {
      month: "2-digit",
      day: "2-digit",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
      hour12: true,
    });
  };

  const getPriorityColor = (priority) => {
    switch (priority) {
      case "High":
        return "bg-red-100 text-red-700";
      case "Medium":
        return "bg-yellow-100 text-yellow-700";
      case "Low":
        return "bg-green-100 text-green-700";
      default:
        return "bg-gray-100 text-gray-600";
    }
  };

  const getPriorityIcon = (priority) => {
    switch (priority) {
      case "High":
        return "🔴";
      case "Medium":
        return "🟡";
      case "Low":
        return "🟢";
      default:
        return "⚪";
    }
  };

  return (
    <div
      draggable={draggable}
      onDragStart={onDragStart}
      onDragOver={onDragOver}
      onDrop={onDrop}
      onDragEnd={onDragEnd}
      className={`
        bg-white rounded-xl border p-4 transition-all hover:shadow-md
        ${isCompleted ? "border-green-200 bg-green-50/20" : "border-gray-200"}
        ${isDragging ? "opacity-50 scale-95" : ""}
        ${draggable ? "cursor-move" : ""}
      `}
    >
      <div className="flex items-start gap-3">
        {/* Drag Handle */}
        {draggable && (
          <div className="mt-0.5 text-gray-300 hover:text-gray-500 flex-shrink-0">
            <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
              <path d="M8 6a2 2 0 1 1-4 0 2 2 0 0 1 4 0zm0 6a2 2 0 1 1-4 0 2 2 0 0 1 4 0zm0 6a2 2 0 1 1-4 0 2 2 0 0 1 4 0zm8-12a2 2 0 1 1-4 0 2 2 0 0 1 4 0zm0 6a2 2 0 1 1-4 0 2 2 0 0 1 4 0zm0 6a2 2 0 1 1-4 0 2 2 0 0 1 4 0z" />
            </svg>
          </div>
        )}

        {/* Checkbox */}
        <button
          onClick={() => isCompleted ? onUncomplete(task.id) : onComplete(task.id)}
          disabled={loading}
          className={`
            mt-0.5 w-5 h-5 rounded-full border-2 flex items-center justify-center flex-shrink-0 transition-colors
            ${isCompleted
              ? "bg-green-500 border-green-500 text-white"
              : "border-gray-300 hover:border-indigo-500"
            }
            disabled:opacity-50
          `}
          aria-label={isCompleted ? "Mark as pending" : "Mark as completed"}
        >
          {isCompleted && (
            <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
            </svg>
          )}
        </button>

        {/* Content */}
        <div className="flex-1 min-w-0">
          <h3 className={`text-sm font-medium ${isCompleted ? "line-through text-gray-400" : "text-gray-800"}`}>
            {task.title}
          </h3>
          {task.description && (
            <p className={`text-xs mt-1 ${isCompleted ? "text-gray-300" : "text-gray-500"}`}>
              {task.description}
            </p>
          )}
          <div className="flex items-center gap-3 mt-2 text-xs text-gray-400">
            <span>Created: {formatDate(task.created_at)}</span>
            <span>Updated: {formatDate(task.updated_at)}</span>
          </div>
          <div className="flex items-center gap-2 mt-2 flex-wrap">
            <span className="text-xs bg-gray-100 text-gray-500 px-2 py-0.5 rounded-full">
              {task.page}
            </span>
            <span className={`text-xs px-2 py-0.5 rounded-full ${getPriorityColor(task.priority)}`}>
              {getPriorityIcon(task.priority)} {task.priority}
            </span>
            {task.assigned_to_usernames && task.assigned_to_usernames.length > 0 && (
              <span className="text-xs bg-blue-100 text-blue-700 px-2 py-0.5 rounded-full">
                👤 {task.assigned_to_usernames.join(", ")}
              </span>
            )}
            <span className={`text-xs px-2 py-0.5 rounded-full ${
              isCompleted
                ? "bg-green-100 text-green-600"
                : "bg-yellow-100 text-yellow-600"
            }`}>
              {task.status}
            </span>
          </div>
        </div>

        {/* Actions */}
        <div className="flex items-center gap-1 flex-shrink-0">
          <button
            onClick={() => onEdit(task)}
            disabled={loading}
            className="p-1.5 text-gray-400 hover:text-indigo-600 hover:bg-indigo-50 rounded-lg transition-colors"
            title="Edit task"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
            </svg>
          </button>
          <button
            onClick={() => onDelete(task.id)}
            disabled={loading}
            className="p-1.5 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
            title="Delete task"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
            </svg>
          </button>
        </div>
      </div>
    </div>
  );
}
