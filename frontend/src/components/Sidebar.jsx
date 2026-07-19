import React from "react";

export default function Sidebar({
  chats,
  activeChatId,
  onSelectChat,
  onNewChat,
  onDeleteChat,
  isOpen,
  onToggle
}) {
  return (
    <aside className={`chat-sidebar ${isOpen ? "sidebar--open" : "sidebar--closed"}`}>
      <div className="sidebar-header">
        <button className="new-chat-btn" onClick={onNewChat}>
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
            <line x1="12" y1="5" x2="12" y2="19" />
            <line x1="5" y1="12" x2="19" y2="12" />
          </svg>
          <span>New Chat</span>
        </button>
        <button className="sidebar-toggle-mobile" onClick={onToggle} aria-label="Toggle sidebar">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <line x1="18" y1="6" x2="6" y2="18"></line>
            <line x1="6" y1="6" x2="18" y2="18"></line>
          </svg>
        </button>
      </div>

      <div className="sidebar-list-container">
        <div className="sidebar-section-title">Recent Conversations</div>
        <div className="sidebar-list">
          {chats.length === 0 ? (
            <div className="sidebar-empty">No conversations yet</div>
          ) : (
            chats.map((chat) => (
              <div
                key={chat.session_id}
                className={`sidebar-item ${chat.session_id === activeChatId ? "sidebar-item--active" : ""}`}
                onClick={() => onSelectChat(chat.session_id)}
              >
                <div className="sidebar-item-content">
                  <svg className="chat-bubble-icon" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
                  </svg>
                  <span className="sidebar-item-title" title={chat.title}>
                    {chat.title}
                  </span>
                </div>
                <button
                  className="delete-chat-btn"
                  onClick={(e) => {
                    e.stopPropagation();
                    if (window.confirm("Are you sure you want to delete this chat?")) {
                      onDeleteChat(chat.session_id);
                    }
                  }}
                  title="Delete Chat"
                >
                  <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <polyline points="3 6 5 6 21 6" />
                    <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" />
                  </svg>
                </button>
              </div>
            ))
          )}
        </div>
      </div>
    </aside>
  );
}
