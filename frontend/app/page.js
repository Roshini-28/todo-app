"use client";

import { useState, useEffect } from "react";
import { isAuthenticated, getUser, logout } from "../services/auth";
import LoginPage from "../components/LoginPage";
import Sidebar from "../components/Sidebar";
import Header from "../components/Header";
import SearchBar from "../components/SearchBar";
import TodoList from "../components/TodoList";
import AddTaskModal from "../components/AddTaskModal";
import EditTaskModal from "../components/EditTaskModal";
import AIChat from "../components/AIChat";
import {
  getTasks,
  createTask,
  updateTask,
  completeTask,
  uncompleteTask,
  deleteTask,
  clearCompletedTasks,
  getPages,
  createPage,
  deletePage,
  reorderTasks,
} from "../services/api";
import { getAuthHeaders } from "../services/auth";

export default function Home() {
  const [authenticated, setAuthenticated] = useState(false);
  const [checking, setChecking] = useState(true);
  const [user, setUser] = useState(null);

  // Data
  const [tasks, setTasks] = useState([]);
  const [pages, setPages] = useState([]);
  const [taskCounts, setTaskCounts] = useState({});
  const [users, setUsers] = useState([]);

  // UI State
  const [selectedPage, setSelectedPage] = useState(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [statusFilter, setStatusFilter] = useState("All");
  const [sortBy, setSortBy] = useState("newest");
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);
  const [error, setError] = useState("");
  const [sidebarOpen, setSidebarOpen] = useState(false);

  // Modals
  const [showAddTask, setShowAddTask] = useState(false);
  const [showEditTask, setShowEditTask] = useState(false);
  const [showAIChat, setShowAIChat] = useState(false);
  const [editingTask, setEditingTask] = useState(null);

  // Check authentication on mount
  useEffect(() => {
    const checkAuth = async () => {
      if (isAuthenticated()) {
        try {
          const token = localStorage.getItem("token");
          const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000"}/auth/me`, {
            headers: { Authorization: `Bearer ${token}` },
          });
          if (response.ok) {
            const userData = await response.json();
            setAuthenticated(true);
            setUser(userData);
          } else {
            // Token is invalid or expired
            localStorage.removeItem("token");
            localStorage.removeItem("user");
            setAuthenticated(false);
            setUser(null);
          }
        } catch (err) {
          // Network error or server error
          localStorage.removeItem("token");
          localStorage.removeItem("user");
          setAuthenticated(false);
          setUser(null);
        }
      }
      setChecking(false);
    };
    checkAuth();
  }, []);

  // Load pages on mount
  useEffect(() => {
    if (authenticated) {
      loadPages();
      loadUsers();
    }
  }, [authenticated]);

  // Load tasks when page, search, or filter changes
  useEffect(() => {
    if (authenticated && selectedPage !== null) {
      loadTasks();
    }
  }, [authenticated, selectedPage, searchQuery, statusFilter]);

  const loadUsers = async () => {
    try {
      const token = localStorage.getItem("token");
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000"}/auth/users`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      if (response.ok) {
        const usersData = await response.json();
        setUsers(usersData);
      }
    } catch (err) {
      console.error("Failed to load users:", err);
    }
  };

  const loadPages = async () => {
    try {
      const pagesData = await getPages();
      setPages(pagesData);
      if (pagesData.length > 0 && selectedPage === null) {
        setSelectedPage(pagesData[0].name);
      }
      // Load task counts for each page
      const counts = {};
      for (const page of pagesData) {
        try {
          const pageTasks = await getTasks({ page: page.name });
          counts[page.name] = pageTasks.length;
        } catch {
          counts[page.name] = 0;
        }
      }
      setTaskCounts(counts);
    } catch (err) {
      setError(err.message);
    }
  };

  const loadTasks = async () => {
    setLoading(true);
    setError("");
    try {
      const params = { page: selectedPage };
      if (searchQuery) params.search = searchQuery;
      if (statusFilter !== "All") params.status = statusFilter;

      let tasksData = await getTasks(params);

      // Sort
      if (sortBy === "oldest") {
        tasksData = tasksData.reverse();
      } else if (sortBy === "updated") {
        tasksData = [...tasksData].sort(
          (a, b) => new Date(b.updated_at) - new Date(a.updated_at)
        );
      }

      setTasks(tasksData);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Task actions
  const handleCreateTask = async (taskData) => {
    setActionLoading(true);
    try {
      await createTask(taskData);
      await loadTasks();
      await loadPages(); // Refresh counts
    } catch (err) {
      throw err;
    } finally {
      setActionLoading(false);
    }
  };

  const handleUpdateTask = async (taskId, taskData) => {
    setActionLoading(true);
    try {
      await updateTask(taskId, taskData);
      await loadTasks();
    } catch (err) {
      throw err;
    } finally {
      setActionLoading(false);
    }
  };

  const handleCompleteTask = async (taskId) => {
    setActionLoading(true);
    try {
      await completeTask(taskId);
      await loadTasks();
      await loadPages();
    } catch (err) {
      setError(err.message);
    } finally {
      setActionLoading(false);
    }
  };

  const handleUncompleteTask = async (taskId) => {
    setActionLoading(true);
    try {
      await uncompleteTask(taskId);
      await loadTasks();
      await loadPages();
    } catch (err) {
      setError(err.message);
    } finally {
      setActionLoading(false);
    }
  };

  const handleDeleteTask = async (taskId) => {
    if (!confirm("Are you sure you want to delete this task?")) return;
    setActionLoading(true);
    try {
      await deleteTask(taskId);
      await loadTasks();
      await loadPages();
    } catch (err) {
      setError(err.message);
    } finally {
      setActionLoading(false);
    }
  };

  const handleClearCompleted = async () => {
    if (!confirm("Delete all completed tasks from this page?")) return;
    setActionLoading(true);
    try {
      await clearCompletedTasks(selectedPage);
      await loadTasks();
      await loadPages();
    } catch (err) {
      setError(err.message);
    } finally {
      setActionLoading(false);
    }
  };

  // Page actions
  const handleCreatePage = async (name, sharedWith = []) => {
    try {
      await createPage(name, sharedWith);
      await loadPages();
      setSelectedPage(name);
    } catch (err) {
      throw new Error(err.message);
    }
  };

  const handleDeletePage = async (pageName) => {
    const page = pages.find((p) => p.name === pageName);
    if (!page) return;
    await deletePage(page.id);
    if (selectedPage === pageName) {
      const remaining = pages.filter((p) => p.name !== pageName);
      setSelectedPage(remaining.length > 0 ? remaining[0].name : null);
    }
    await loadPages();
  };

  // AI actions
  const handleCreateAITasks = async (suggestions, page) => {
    setActionLoading(true);
    try {
      for (const title of suggestions) {
        await createTask({ title, description: "", page: page || selectedPage });
      }
      await loadTasks();
      await loadPages();
    } catch (err) {
      throw new Error(err.message);
    } finally {
      setActionLoading(false);
    }
  };

  const handleSelectPage = (pageName) => {
    setSelectedPage(pageName);
    setSearchQuery("");
    setStatusFilter("All");
    setSidebarOpen(false);
  };

  const handleReorder = async (taskIds) => {
    // Store previous state for rollback
    const previousTasks = [...tasks];

    // Optimistic update
    setTasks((prevTasks) => {
      const taskMap = new Map(prevTasks.map((t) => [t.id, t]));
      return taskIds.map((id) => taskMap.get(id)).filter(Boolean);
    });

    try {
      await reorderTasks(taskIds);
    } catch (err) {
      // Rollback on failure
      setTasks(previousTasks);
      setError(err.message || "Failed to reorder tasks");
    }
  };

  const handleLogout = () => {
    logout();
    setAuthenticated(false);
    setUser(null);
    setTasks([]);
    setPages([]);
    setSelectedPage(null);
  };

  // Filter counts
  const filteredTasks = tasks;
  const pendingCount = tasks.filter((t) => t.status === "Pending").length;
  const completedCount = tasks.filter((t) => t.status === "Completed").length;

  // Show loading while checking auth
  if (checking) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="w-8 h-8 border-4 border-primary border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p className="text-gray-500">Loading...</p>
        </div>
      </div>
    );
  }

  // Show login page if not authenticated
  if (!authenticated) {
    return <LoginPage onLogin={() => {
      setAuthenticated(true);
      setUser(getUser());
    }} />;
  }

  return (
    <div className="flex h-screen overflow-hidden">
      <Sidebar
        pages={pages}
        selectedPage={selectedPage}
        onSelectPage={handleSelectPage}
        onAddPage={handleCreatePage}
        onDeletePage={handleDeletePage}
        taskCounts={taskCounts}
        isOpen={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
        currentUser={user}
      />

      <div className="flex-1 flex flex-col min-w-0">
        <Header
          onMenuClick={() => setSidebarOpen(true)}
          taskCount={tasks.length}
          user={user}
          onLogout={handleLogout}
        />

        <main className="flex-1 overflow-y-auto p-4 lg:p-6">
          {/* Error Banner */}
          {error && (
            <div className="mb-4 p-3 bg-danger-light text-danger text-sm rounded-lg flex items-center justify-between">
              <span>{error}</span>
              <button onClick={() => setError("")} className="text-danger hover:text-red-700">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
          )}

          {/* Page Title & Actions */}
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-4">
            <div>
              <h1 className="text-2xl font-bold text-gray-800">
                {selectedPage || "Select a Page"}
              </h1>
              <p className="text-sm text-gray-500 mt-0.5">
                {tasks.length} task{tasks.length !== 1 ? "s" : ""}
              </p>
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={() => setShowAIChat(true)}
                className="flex items-center gap-1.5 px-3 py-2 text-sm text-primary bg-primary-light hover:bg-primary/20 rounded-lg transition-colors"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
                AI Assistant
              </button>
              <button
                onClick={() => setShowAddTask(true)}
                className="flex items-center gap-1.5 px-4 py-2 text-sm text-white bg-primary hover:bg-primary-hover rounded-lg transition-colors"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                </svg>
                Add Task
              </button>
            </div>
          </div>

          {/* Search & Filters */}
          <div className="flex flex-col sm:flex-row gap-3 mb-4">
            <div className="flex-1">
              <SearchBar value={searchQuery} onChange={setSearchQuery} loading={false} />
            </div>
            <div className="flex items-center gap-2">
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary"
              >
                <option value="All">All ({tasks.length})</option>
                <option value="Pending">Pending ({pendingCount})</option>
                <option value="Completed">Completed ({completedCount})</option>
              </select>
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value)}
                className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary"
              >
                <option value="newest">Newest first</option>
                <option value="oldest">Oldest first</option>
                <option value="updated">Recently updated</option>
              </select>
            </div>
          </div>

          {/* Clear Completed */}
          {completedCount > 0 && (
            <div className="mb-4">
              <button
                onClick={handleClearCompleted}
                className="text-sm text-gray-500 hover:text-danger transition-colors"
              >
                Clear {completedCount} completed task{completedCount > 1 ? "s" : ""}
              </button>
            </div>
          )}

          {/* Todo List */}
          <TodoList
            tasks={filteredTasks}
            loading={loading}
            onComplete={handleCompleteTask}
            onUncomplete={handleUncompleteTask}
            onEdit={(task) => { setEditingTask(task); setShowEditTask(true); }}
            onDelete={handleDeleteTask}
            onReorder={handleReorder}
          />
        </main>
      </div>

      {/* Modals */}
      <AddTaskModal
        isOpen={showAddTask}
        onClose={() => setShowAddTask(false)}
        onAdd={handleCreateTask}
        pages={pages}
        users={users}
        defaultPage={selectedPage}
      />
      <EditTaskModal
        isOpen={showEditTask}
        onClose={() => { setShowEditTask(false); setEditingTask(null); }}
        onUpdate={handleUpdateTask}
        task={editingTask}
        pages={pages}
        users={users}
      />
      <AIChat
        isOpen={showAIChat}
        onClose={() => setShowAIChat(false)}
        onCreateTasks={handleCreateAITasks}
        defaultPage={selectedPage}
      />
    </div>
  );
}
