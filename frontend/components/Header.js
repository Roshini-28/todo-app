"use client";

export default function Header({ onMenuClick, taskCount, user, onLogout }) {
  return (
    <header className="bg-white border-b border-gray-200 px-4 py-3 flex items-center justify-between">
      <div className="flex items-center gap-3">
        <button
          onClick={onMenuClick}
          className="lg:hidden p-2 hover:bg-gray-100 rounded-lg transition-colors"
          aria-label="Toggle menu"
        >
          <svg className="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
          </svg>
        </button>
        <h2 className="text-lg font-semibold text-gray-800">Dashboard</h2>
      </div>
      <div className="flex items-center gap-3">
        <span className="text-sm text-gray-500">
          {taskCount} task{taskCount !== 1 ? "s" : ""}
        </span>
        {user && (
          <div className="flex items-center gap-2">
            <span className="text-sm text-gray-600">
              Welcome, <span className="font-medium">{user.username}</span>
            </span>
            <button
              onClick={onLogout}
              className="px-3 py-1.5 text-sm text-gray-600 hover:text-danger hover:bg-danger-light rounded-lg transition-colors"
            >
              Logout
            </button>
          </div>
        )}
        <div className="w-8 h-8 bg-primary rounded-full flex items-center justify-center">
          <span className="text-white text-sm font-medium">
            {user?.username?.charAt(0).toUpperCase() || "U"}
          </span>
        </div>
      </div>
    </header>
  );
}
