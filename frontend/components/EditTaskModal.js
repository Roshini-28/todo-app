"use client";

import { useState, useEffect } from "react";

export default function EditTaskModal({ isOpen, onClose, onUpdate, task, pages, users }) {
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [page, setPage] = useState("");
  const [priority, setPriority] = useState("Medium");
  const [assignedTo, setAssignedTo] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (isOpen && task) {
      setTitle(task.title);
      setDescription(task.description || "");
      setPage(task.page);
      setPriority(task.priority || "Medium");
      setAssignedTo(task.assigned_to || []);
      setError("");
    }
  }, [isOpen, task]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!title.trim()) {
      setError("Title is required");
      return;
    }
    if (!page) {
      setError("Please select a page");
      return;
    }

    setLoading(true);
    setError("");
    try {
      await onUpdate(task.id, { title: title.trim(), description: description.trim(), page, priority, assigned_to: assignedTo });
      onClose();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen || !task) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-black/50" onClick={onClose} />
      <div className="relative bg-white rounded-2xl shadow-xl w-full max-w-md p-6">
        <h2 className="text-lg font-semibold text-gray-800 mb-4">Edit Task</h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Title *</label>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="Enter task title"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500/50 focus:border-indigo-500 text-sm"
              autoFocus
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Enter task description"
              rows={3}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500/50 focus:border-indigo-500 text-sm resize-none"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Page *</label>
            <select
              value={page}
              onChange={(e) => setPage(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500/50 focus:border-indigo-500 text-sm"
            >
              <option value="">Select a page</option>
              {pages.map((p) => (
                <option key={p.id} value={p.name}>{p.name}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Priority</label>
            <div className="flex gap-2">
              {["Low", "Medium", "High"].map((p) => (
                <button
                  key={p}
                  type="button"
                  onClick={() => setPriority(p)}
                  className={`flex-1 px-3 py-2 text-sm rounded-lg border transition-colors ${
                    priority === p
                      ? p === "High"
                        ? "bg-red-100 border-red-500 text-red-700"
                        : p === "Medium"
                        ? "bg-yellow-100 border-yellow-500 text-yellow-700"
                        : "bg-green-100 border-green-500 text-green-700"
                      : "bg-gray-50 border-gray-200 text-gray-600 hover:bg-gray-100"
                  }`}
                >
                  {p === "High" ? "🔴" : p === "Medium" ? "🟡" : "🟢"} {p}
                </button>
              ))}
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Assign To (Hold Ctrl/Cmd to select multiple)</label>
            <div className="border border-gray-300 rounded-lg p-2 max-h-32 overflow-y-auto">
              <label className="flex items-center gap-2 p-1 hover:bg-gray-50 rounded cursor-pointer">
                <input
                  type="checkbox"
                  checked={assignedTo.length === 0}
                  onChange={() => setAssignedTo([])}
                  className="w-4 h-4 text-indigo-600 rounded"
                />
                <span className="text-sm text-gray-600">Unassigned</span>
              </label>
              {users.map((u) => (
                <label key={u.id} className="flex items-center gap-2 p-1 hover:bg-gray-50 rounded cursor-pointer">
                  <input
                    type="checkbox"
                    checked={assignedTo.includes(u.id)}
                    onChange={(e) => {
                      if (e.target.checked) {
                        setAssignedTo([...assignedTo, u.id]);
                      } else {
                        setAssignedTo(assignedTo.filter((id) => id !== u.id));
                      }
                    }}
                    className="w-4 h-4 text-indigo-600 rounded"
                  />
                  <span className="text-sm text-gray-700">{u.username}</span>
                </label>
              ))}
            </div>
            {assignedTo.length > 0 && (
              <p className="text-xs text-gray-500 mt-1">
                Assigned to: {assignedTo.length} user(s)
              </p>
            )}
          </div>
          {error && <p className="text-sm text-red-600">{error}</p>}
          <div className="flex gap-3 pt-2">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-4 py-2 text-sm text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="flex-1 px-4 py-2 text-sm text-white bg-indigo-600 hover:bg-indigo-700 rounded-lg disabled:opacity-50 transition-colors"
            >
              {loading ? "Saving..." : "Save Changes"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
