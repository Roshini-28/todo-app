"use client";

import { useState, useEffect, useRef } from "react";
import { getAIStatus, suggestTasks } from "../services/api";

export default function AIChat({ isOpen, onClose, onCreateTasks, defaultPage }) {
  const [prompt, setPrompt] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [suggestions, setSuggestions] = useState([]);
  const [aiConfigured, setAiConfigured] = useState(null);
  const [creating, setCreating] = useState(false);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    if (isOpen) {
      checkAIStatus();
      setSuggestions([]);
      setError("");
      setPrompt("");
    }
  }, [isOpen]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [suggestions]);

  const checkAIStatus = async () => {
    try {
      const status = await getAIStatus();
      setAiConfigured(status.configured);
    } catch {
      setAiConfigured(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!prompt.trim()) return;

    setLoading(true);
    setError("");
    setSuggestions([]);

    try {
      const response = await suggestTasks(prompt.trim());
      setSuggestions(response.suggestions);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateTasks = async () => {
    if (suggestions.length === 0) return;

    setCreating(true);
    try {
      await onCreateTasks(suggestions, defaultPage);
      setSuggestions([]);
      setPrompt("");
    } catch (err) {
      setError(err.message);
    } finally {
      setCreating(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-black/50" onClick={onClose} />
      <div className="relative bg-white rounded-2xl shadow-xl w-full max-w-lg flex flex-col max-h-[80vh]">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-gray-200">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center">
              <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
            <h2 className="text-lg font-semibold text-gray-800">AI Assistant</h2>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Status */}
        {aiConfigured === false && (
          <div className="mx-4 mt-3 p-3 bg-warning/10 border border-warning/20 rounded-lg">
            <p className="text-sm text-warning">
              AI is not configured. Set <code className="bg-gray-100 px-1 rounded">OPENAI_API_KEY</code> in your backend <code className="bg-gray-100 px-1 rounded">.env</code> file.
            </p>
          </div>
        )}

        {/* Messages Area */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {/* Welcome message */}
          <div className="bg-gray-50 rounded-xl p-4">
            <p className="text-sm text-gray-600">
              Hi! I'm your AI assistant. Tell me what you need to accomplish, and I'll suggest tasks for you.
            </p>
            <p className="text-xs text-gray-400 mt-2">
              Example: "I need to prepare for my Java interview"
            </p>
          </div>

          {/* Loading */}
          {loading && (
            <div className="flex items-center gap-2 text-sm text-gray-500">
              <div className="w-4 h-4 border-2 border-primary border-t-transparent rounded-full animate-spin" />
              AI is thinking...
            </div>
          )}

          {/* Error */}
          {error && (
            <div className="bg-danger-light text-danger text-sm p-3 rounded-lg">
              {error}
            </div>
          )}

          {/* Suggestions */}
          {suggestions.length > 0 && (
            <div className="space-y-3">
              <p className="text-sm font-medium text-gray-700">Here are some suggested tasks:</p>
              <div className="space-y-2">
                {suggestions.map((suggestion, index) => (
                  <div
                    key={index}
                    className="flex items-center gap-2 p-3 bg-primary-light/50 border border-primary/20 rounded-lg"
                  >
                    <span className="w-5 h-5 bg-primary text-white text-xs rounded-full flex items-center justify-center flex-shrink-0">
                      {index + 1}
                    </span>
                    <span className="text-sm text-gray-700">{suggestion}</span>
                  </div>
                ))}
              </div>
              <button
                onClick={handleCreateTasks}
                disabled={creating}
                className="w-full px-4 py-2.5 text-sm text-white bg-primary hover:bg-primary-hover rounded-lg disabled:opacity-50 transition-colors"
              >
                {creating ? "Creating tasks..." : `Create ${suggestions.length} Suggested Task${suggestions.length > 1 ? "s" : ""}`}
              </button>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <form onSubmit={handleSubmit} className="p-4 border-t border-gray-200">
          <div className="flex gap-2">
            <input
              type="text"
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="What do you need to do?"
              className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary text-sm"
              disabled={loading || !aiConfigured}
            />
            <button
              type="submit"
              disabled={loading || !prompt.trim() || !aiConfigured}
              className="px-4 py-2 text-sm text-white bg-primary hover:bg-primary-hover rounded-lg disabled:opacity-50 transition-colors"
            >
              {loading ? "..." : "Ask"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
