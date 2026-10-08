"use client";

import { useState } from "react";

export default function Sidebar({
  pages,
  selectedPage,
  onSelectPage,
  onAddPage,
  onDeletePage,
  taskCounts,
  isOpen,
  onClose,
  currentUser,
}) {
  const [showAddPage, setShowAddPage] = useState(false);
  const [newPageName, setNewPageName] = useState("");
  const [sharedWith, setSharedWith] = useState([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  // Get all users for sharing
  const [allUsers, setAllUsers] = useState([]);

  const fetchUsers = async () => {
    try {
      const token = localStorage.getItem("token");
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000"}/auth/users`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (response.ok) {
        const users = await response.json();
        setAllUsers(users.filter((u) => u.id !== currentUser?.id));
      }
    } catch (err) {
      console.error("Failed to fetch users:", err);
    }
  };

  const handleAddPage = async (e) => {
    e.preventDefault();
    if (!newPageName.trim()) return;

    setLoading(true);
    setError("");
    try {
      await onAddPage(newPageName.trim(), sharedWith);
      setNewPageName("");
      setSharedWith([]);
      setShowAddPage(false);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleDeletePage = async (pageName) => {
    if (confirm(`Delete page "${pageName}"? Tasks will be moved to Uncategorized.`)) {
      try {
        await onDeletePage(pageName);
      } catch (err) {
        alert(err.message);
      }
    }
  };

  const myPages = pages.filter((p) => p.created_by === currentUser?.id);
  const sharedPages = pages.filter((p) => p.created_by !== currentUser?.id);

  return (
    <>
      {/* Mobile overlay */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-40 lg:hidden"
          onClick={onClose}
        />
      )}

      <aside
        className={`
          fixed lg:static inset-y-0 left-0 z-50
          w-64 bg-white border-r border-gray-200
          transform transition-transform duration-200 ease-in-out
          ${isOpen ? "translate-x-0" : "-translate-x-full lg:translate-x-0"}
          flex flex-col
        `}
      >
        {/* Logo */}
        <div className="p-4 border-b border-gray-200">
          <h1 className="text-xl font-bold text-primary flex items-center gap-2">
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
            </svg>
            Todo App
          </h1>
        </div>

        {/* Navigation */}
        <nav className="flex-1 overflow-y-auto p-3">
          {/* Add Page Button */}
          <button
            onClick={() => {
              setShowAddPage(!showAddPage);
              if (!showAddPage) fetchUsers();
            }}
            className="w-full flex items-center gap-2 px-3 py-2 text-sm text-gray-600 hover:bg-gray-100 rounded-lg mb-2 transition-colors"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            Add Page
          </button>

          {/* Add Page Form */}
          {showAddPage && (
            <form onSubmit={handleAddPage} className="mb-3 px-1">
              <input
                type="text"
                value={newPageName}
                onChange={(e) => setNewPageName(e.target.value)}
                placeholder="Page name"
                className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary"
                autoFocus
              />
              {allUsers.length > 0 && (
                <div className="mt-2">
                  <p className="text-xs text-gray-500 mb-1">Share with:</p>
                  <div className="max-h-24 overflow-y-auto border border-gray-200 rounded-lg p-1">
                    {allUsers.map((u) => (
                      <label key={u.id} className="flex items-center gap-2 p-1 hover:bg-gray-50 rounded cursor-pointer">
                        <input
                          type="checkbox"
                          checked={sharedWith.includes(u.id)}
                          onChange={(e) => {
                            if (e.target.checked) {
                              setSharedWith([...sharedWith, u.id]);
                            } else {
                              setSharedWith(sharedWith.filter((id) => id !== u.id));
                            }
                          }}
                          className="w-3 h-3 text-primary rounded"
                        />
                        <span className="text-xs text-gray-700">{u.username}</span>
                      </label>
                    ))}
                  </div>
                </div>
              )}
              {error && <p className="text-xs text-danger mt-1">{error}</p>}
              <div className="flex gap-2 mt-2">
                <button
                  type="submit"
                  disabled={loading}
                  className="flex-1 px-3 py-1.5 text-xs bg-primary text-white rounded-lg hover:bg-primary-hover disabled:opacity-50 transition-colors"
                >
                  {loading ? "..." : "Create"}
                </button>
                <button
                  type="button"
                  onClick={() => { setShowAddPage(false); setError(""); }}
                  className="px-3 py-1.5 text-xs text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
                >
                  Cancel
                </button>
              </div>
            </form>
          )}

          {/* My Pages */}
          <div className="space-y-1">
            <p className="px-3 py-1 text-xs font-semibold text-gray-400 uppercase tracking-wider">
              My Pages
            </p>
            {myPages.length === 0 ? (
              <p className="px-3 py-2 text-sm text-gray-400 italic">No pages yet</p>
            ) : (
              myPages.map((page) => (
                <div
                  key={page.id}
                  className={`
                    group flex items-center justify-between px-3 py-2 rounded-lg cursor-pointer transition-colors
                    ${selectedPage === page.name
                      ? "bg-primary-light text-primary font-medium"
                      : "text-gray-600 hover:bg-gray-100"
                    }
                  `}
                  onClick={() => onSelectPage(page.name)}
                >
                  <div className="flex items-center gap-2 min-w-0">
                    <svg className="w-4 h-4 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" />
                    </svg>
                    <span className="text-sm truncate">{page.name}</span>
                    {taskCounts[page.name] !== undefined && (
                      <span className="text-xs bg-gray-200 text-gray-600 px-1.5 py-0.5 rounded-full">
                        {taskCounts[page.name]}
                      </span>
                    )}
                  </div>
                  <button
                    onClick={(e) => { e.stopPropagation(); handleDeletePage(page.name); }}
                    className="opacity-0 group-hover:opacity-100 p-1 hover:bg-gray-200 rounded transition-all"
                    title="Delete page"
                  >
                    <svg className="w-3.5 h-3.5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                  </button>
                </div>
              ))
            )}
          </div>

          {/* Shared with Me */}
          {sharedPages.length > 0 && (
            <div className="space-y-1 mt-4">
              <p className="px-3 py-1 text-xs font-semibold text-gray-400 uppercase tracking-wider">
                Shared with Me
              </p>
              {sharedPages.map((page) => (
                <div
                  key={page.id}
                  className={`
                    group flex items-center justify-between px-3 py-2 rounded-lg cursor-pointer transition-colors
                    ${selectedPage === page.name
                      ? "bg-green-100 text-green-700 font-medium"
                      : "text-gray-600 hover:bg-gray-100"
                    }
                  `}
                  onClick={() => onSelectPage(page.name)}
                >
                  <div className="flex items-center gap-2 min-w-0">
                    <svg className="w-4 h-4 flex-shrink-0 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z" />
                    </svg>
                    <span className="text-sm truncate">{page.name}</span>
                    <span className="text-xs text-gray-400">by {page.created_by_username}</span>
                    {taskCounts[page.name] !== undefined && (
                      <span className="text-xs bg-gray-200 text-gray-600 px-1.5 py-0.5 rounded-full">
                        {taskCounts[page.name]}
                      </span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </nav>

        {/* Footer */}
        <div className="p-3 border-t border-gray-200">
          <p className="text-xs text-gray-400 text-center">Full-Stack Todo App</p>
        </div>
      </aside>
    </>
  );
}
