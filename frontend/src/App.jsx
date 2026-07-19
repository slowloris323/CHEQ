import React, { useState, useEffect } from 'react'
import './App.css'
import Chat from './components/Chat'
import Confirmation from './components/Confirmation'
import Sidebar from './components/Sidebar'

function App() {
  const [resourceUri, setResourceUri] = useState(null)
  const [pendingFeedback, setPendingFeedback] = useState(null)
  const [chats, setChats] = useState([])
  const [activeChatId, setActiveChatId] = useState(null)
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const [messages, setMessages] = useState([
    { id: 1, message: "Hi! How can I help you today?", type: "Bot" },
  ])

  const fetchChats = async () => {
    try {
      const response = await fetch("http://127.0.0.1:8000/ai_agent/chats/");
      if (response.ok) {
        const data = await response.json();
        setChats(data);
        if (data.length > 0 && !activeChatId) {
          setActiveChatId(data[0].session_id);
        } else if (data.length === 0 && !activeChatId) {
          createNewChat();
        }
      }
    } catch (e) {
      console.error("Failed to fetch chats", e);
    }
  };

  const loadChatMessages = async (sid) => {
    try {
      const response = await fetch("http://127.0.0.1:8000/ai_agent/chats/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ session_id: sid })
      });
      if (response.ok) {
        const data = await response.json();
        setMessages(data);
      }
    } catch (e) {
      console.error("Failed to load chat messages", e);
    }
  };

  const createNewChat = () => {
    const newId = `session_${Math.random().toString(36).substr(2, 9)}`;
    setActiveChatId(newId);
    setMessages([
      { id: 1, message: "Hi! How can I help you today?", type: "Bot" }
    ]);
    setChats(prev => [
      { session_id: newId, title: "New Chat", updated_at: new Date().toISOString() },
      ...prev
    ]);
  };

  const deleteChat = async (sid) => {
    try {
      const response = await fetch(`http://127.0.0.1:8000/ai_agent/chats/?session_id=${sid}`, {
        method: "DELETE"
      });
      if (response.ok) {
        const remaining = chats.filter(c => c.session_id !== sid);
        setChats(remaining);
        if (activeChatId === sid) {
          if (remaining.length > 0) {
            setActiveChatId(remaining[0].session_id);
          } else {
            createNewChat();
          }
        }
      }
    } catch (e) {
      console.error("Failed to delete chat", e);
    }
  };

  useEffect(() => {
    fetchChats();
  }, []);

  useEffect(() => {
    if (activeChatId) {
      loadChatMessages(activeChatId);
    }
  }, [activeChatId]);

  useEffect(() => {
    const handleLocationChange = () => {
      const params = new URLSearchParams(window.location.search)
      const uri = params.get('resource_uri')
      setResourceUri(uri || null)
    }

    handleLocationChange()
    window.addEventListener('popstate', handleLocationChange)

    return () => {
      window.removeEventListener('popstate', handleLocationChange)
    }
  }, [])

  if (resourceUri) {
    return <Confirmation resourceUri={resourceUri} onBack={(decision) => {
      setPendingFeedback(decision || null)
      window.history.pushState({}, document.title, '/')
      window.dispatchEvent(new PopStateEvent('popstate'))
    }} />
  }

  return (
    <div className="app-layout">
      <Sidebar
        chats={chats}
        activeChatId={activeChatId}
        onSelectChat={setActiveChatId}
        onNewChat={createNewChat}
        onDeleteChat={deleteChat}
        isOpen={sidebarOpen}
        onToggle={() => setSidebarOpen(!sidebarOpen)}
      />
      <div className="chat-main-container">
        {activeChatId && (
          <Chat 
            messages={messages} 
            setMessages={setMessages} 
            sessionId={activeChatId} 
            pendingFeedback={pendingFeedback}
            onFeedbackProcessed={() => setPendingFeedback(null)}
            onNewMessageSent={fetchChats}
            toggleSidebar={() => setSidebarOpen(!sidebarOpen)}
          />
        )}
      </div>
    </div>
  )
}

export default App