import React, { useState, useEffect, useRef } from "react";
import { 
  MapPin, 
  TrendingUp, 
  TrendingDown, 
  Minus, 
  Code, 
  ChevronDown, 
  ChevronUp, 
  Newspaper,
  Clock,
  Send,
  Sun,
  Moon,
  Sparkles,
  Plus
} from "lucide-react";

// Responsive Custom SVG Line Chart Component
function TrendChart({ data }) {
  if (!data || data.length === 0) return null;
  
  const width = 500;
  const height = 220;
  const paddingLeft = 45;
  const paddingRight = 20;
  const paddingTop = 25;
  const paddingBottom = 35;
  
  const minVal = Math.min(...data);
  const maxVal = Math.max(...data);
  const valRange = maxVal - minVal;
  
  // Prevent division by zero if all values are identical
  const rangeDivisor = valRange === 0 ? 1 : valRange;
  
  const points = data.map((val, idx) => {
    const x = paddingLeft + (idx * (width - paddingLeft - paddingRight) / (data.length - 1));
    const y = height - paddingBottom - ((val - minVal) / rangeDivisor * (height - paddingTop - paddingBottom));
    return { x, y, value: val };
  });

  const pathD = points.reduce((acc, p, idx) => {
    return idx === 0 ? `M ${p.x} ${p.y}` : `${acc} L ${p.x} ${p.y}`;
  }, "");

  const areaD = points.length > 0 
    ? `${pathD} L ${points[points.length - 1].x} ${height - paddingBottom} L ${points[0].x} ${height - paddingBottom} Z` 
    : "";

  const labels = ["5w ago", "4w ago", "3w ago", "2w ago", "Latest"];

  return (
    <div className="trend-chart-container">
      <h4 className="chart-title">5-Week Job Posting Trend</h4>
      <div className="svg-wrapper">
        <svg viewBox={`0 0 ${width} ${height}`} className="trend-svg" width="100%" height="100%">
          <defs>
            <linearGradient id="chartGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="var(--chart-gradient-start)" stopOpacity="0.4" />
              <stop offset="100%" stopColor="var(--chart-gradient-end)" stopOpacity="0.0" />
            </linearGradient>
          </defs>
          
          {/* Horizontal Gridlines */}
          {[0, 0.25, 0.5, 0.75, 1].map((ratio, idx) => {
            const y = paddingTop + ratio * (height - paddingTop - paddingBottom);
            const gridVal = Math.round(maxVal - ratio * valRange);
            return (
              <g key={idx} className="grid-group">
                <line 
                  x1={paddingLeft} 
                  y1={y} 
                  x2={width - paddingRight} 
                  y2={y} 
                  stroke="var(--border-color)" 
                  strokeWidth="1" 
                  strokeDasharray="4 4" 
                />
                <text 
                  x={paddingLeft - 10} 
                  y={y + 4} 
                  textAnchor="end" 
                  className="grid-text"
                >
                  {gridVal}
                </text>
              </g>
            );
          })}

          {/* Area under the line */}
          {areaD && <path d={areaD} fill="url(#chartGrad)" />}

          {/* Main trend line */}
          {pathD && (
            <path 
              d={pathD} 
              fill="none" 
              stroke="var(--accent-color)" 
              strokeWidth="3.5" 
              strokeLinecap="round" 
              strokeLinejoin="round"
              className="trend-line-path"
            />
          )}

          {/* Interactive highlight dots */}
          {points.map((p, idx) => (
            <g key={idx} className="dot-group">
              <circle 
                cx={p.x} 
                cy={p.y} 
                r="6" 
                fill="var(--accent-color)" 
                stroke="var(--bg-card)" 
                strokeWidth="2" 
                className="chart-dot"
              />
              <text 
                x={p.x} 
                y={p.y - 12} 
                textAnchor="middle" 
                className="dot-value-text"
              >
                {p.value}
              </text>
            </g>
          ))}

          {/* X Axis Labels */}
          {points.map((p, idx) => (
            <text 
              key={idx} 
              x={p.x} 
              y={height - 12} 
              textAnchor="middle" 
              className="axis-label-text"
            >
              {labels[idx]}
            </text>
          ))}
        </svg>
      </div>
    </div>
  );
}

export default function App() {
  const [theme, setTheme] = useState(() => localStorage.getItem("theme") || "dark");
  const [hasSearched, setHasSearched] = useState(false);
  const [messages, setMessages] = useState([
    {
      id: "welcome-1",
      sender: "bot",
      type: "text",
      text: "Hello! I'm the JobPulse AI Assistant. I analyze vacancy postings and local hiring news to check if the recruitment market is heating up, stable, or cooling down."
    },
    {
      id: "welcome-2",
      sender: "bot",
      type: "text",
      text: "What job role would you like to investigate?"
    }
  ]);
  const [step, setStep] = useState("awaiting_role"); // awaiting_role, awaiting_city, ready
  const [role, setRole] = useState("");
  const [inputValue, setInputValue] = useState("");
  const [loading, setLoading] = useState(false);
  const [expandedJsonId, setExpandedJsonId] = useState(null);

  const chatHistoryRef = useRef(null);

  // Sync theme
  useEffect(() => {
    document.body.classList.toggle("light-mode", theme === "light");
    localStorage.setItem("theme", theme);
  }, [theme]);

  // Scroll to bottom when messages list changes
  useEffect(() => {
    if (chatHistoryRef.current) {
      const scrollContainer = chatHistoryRef.current;
      const performScroll = () => {
        scrollContainer.scrollTo({
          top: scrollContainer.scrollHeight,
          behavior: "smooth"
        });
      };
      performScroll();
      // Wait briefly for complex visual dashboard nodes to complete rendering
      const timer = setTimeout(performScroll, 80);
      return () => clearTimeout(timer);
    }
  }, [messages, loading, hasSearched]);

  const toggleTheme = () => {
    setTheme(prev => prev === "dark" ? "light" : "dark");
  };

  const handleReset = () => {
    setHasSearched(false);
    setRole("");
    setInputValue("");
    setStep("awaiting_role");
    setMessages([
      {
        id: "welcome-1",
        sender: "bot",
        type: "text",
        text: "Hello! I'm the JobPulse AI Assistant. I analyze vacancy postings and local hiring news to check if the recruitment market is heating up, stable, or cooling down."
      },
      {
        id: "welcome-2",
        sender: "bot",
        type: "text",
        text: "What job role would you like to investigate?"
      }
    ]);
  };

  const parseDirectQuery = (text) => {
    const lower = text.toLowerCase();
    let parsedRole = "";
    let parsedCity = "";
    
    // Check "Role in City" format
    if (lower.includes(" in ")) {
      const index = lower.indexOf(" in ");
      parsedRole = text.slice(0, index).trim();
      parsedCity = text.slice(index + 4).trim();
    } 
    // Check "Role, City" format
    else if (text.includes(",")) {
      const parts = text.split(",");
      parsedRole = parts[0].trim();
      parsedCity = parts.slice(1).join(",").trim();
    }
    
    if (parsedRole && parsedCity) {
      return { role: parsedRole, city: parsedCity };
    }
    return null;
  };

  const handleSendMessage = async (textToSend) => {
    const text = (textToSend || inputValue).trim();
    if (!text) return;

    if (!textToSend) {
      setInputValue("");
    }

    // Add user message
    const userMessageId = `user-${Date.now()}`;
    const userMessage = {
      id: userMessageId,
      sender: "user",
      type: "text",
      text: text
    };
    
    setMessages(prev => [...prev, userMessage]);

    // Handle flow
    if (step === "awaiting_role" || step === "ready") {
      const direct = parseDirectQuery(text);
      if (direct) {
        setRole(direct.role);
        await performSearch(direct.role, direct.city);
      } else {
        // Just role
        setRole(text);
        setStep("awaiting_city");
        // Ask for city
        setTimeout(() => {
          setMessages(prev => [...prev, {
            id: `bot-${Date.now()}`,
            sender: "bot",
            type: "text",
            text: `Got it: ${text}. Which city or metro area should we analyze?`
          }]);
        }, 300);
      }
    } else if (step === "awaiting_city") {
      await performSearch(role, text);
    }
  };

  const performSearch = async (searchRole, searchCity) => {
    setLoading(true);
    setStep("ready");

    const loadingMessageId = `loading-${Date.now()}`;
    // Add temporary loading indicator message
    setMessages(prev => [...prev, {
      id: loadingMessageId,
      sender: "bot",
      type: "loading"
    }]);

    try {
      const url = `http://localhost:8000/api/v1/job-pulse?role=${encodeURIComponent(searchRole)}&city=${encodeURIComponent(searchCity)}`;
      const response = await fetch(url);
      
      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(errorText || `Backend responded with status ${response.status}`);
      }
      
      const data = await response.json();
      
      // Remove loading message and add result inline dashboard
      setMessages(prev => {
        const filtered = prev.filter(m => m.id !== loadingMessageId);
        return [
          ...filtered,
          {
            id: `result-${Date.now()}`,
            sender: "bot",
            type: "results",
            data: data
          },
          {
            id: `bot-followup-${Date.now()}`,
            sender: "bot",
            type: "text",
            text: "Let me know if you would like to run another job pulse check! (e.g. 'Data Scientist in Austin')"
          }
        ];
      });
    } catch (err) {
      console.error(err);
      const errMsg = err.message || "Failed to fetch market data. Please verify backend is running on port 8000.";
      
      setMessages(prev => {
        const filtered = prev.filter(m => m.id !== loadingMessageId);
        return [
          ...filtered,
          {
            id: `error-${Date.now()}`,
            sender: "bot",
            type: "error",
            text: errMsg,
            retryParams: { role: searchRole, city: searchCity }
          }
        ];
      });
    } finally {
      setLoading(false);
    }
  };

  const handleSuggestionClick = (suggestion) => {
    handleSendMessage(suggestion);
  };

  const handleLandingSearch = () => {
    const text = inputValue.trim();
    if (!text) return;
    setInputValue("");
    setHasSearched(true);
    startQueryFlow(text);
  };

  const handleLandingSuggestionClick = (sug) => {
    setHasSearched(true);
    startQueryFlow(sug);
  };

  const startQueryFlow = (text) => {
    const botWelcomeMsg = {
      id: "welcome-1",
      sender: "bot",
      type: "text",
      text: "Hello! I'm the JobPulse AI Assistant. Let's analyze the vacancy postings and local hiring news for you."
    };

    const userMsg = {
      id: `user-${Date.now()}`,
      sender: "user",
      type: "text",
      text: text
    };

    setMessages([botWelcomeMsg, userMsg]);

    const direct = parseDirectQuery(text);
    if (direct) {
      setRole(direct.role);
      performSearch(direct.role, direct.city);
    } else {
      setRole(text);
      setStep("awaiting_city");
      setTimeout(() => {
        setMessages(prev => [...prev, {
          id: `bot-${Date.now()}`,
          sender: "bot",
          type: "text",
          text: `Got it: ${text}. Which city or metro area should we analyze?`
        }]);
      }, 300);
    }
  };

  const getTrendBadgeProps = (trend) => {
    const t = (trend || "").toLowerCase();
    if (t === "heating up") {
      return {
        className: "badge-heating",
        icon: <TrendingUp className="icon-heating" size={14} />,
        text: "Heating Up",
        themeColor: "var(--heating-color)",
        gradientStart: "#d97d64",
        gradientEnd: "#e6927d"
      };
    } else if (t === "cooling down") {
      return {
        className: "badge-cooling",
        icon: <TrendingDown className="icon-cooling" size={14} />,
        text: "Cooling Down",
        themeColor: "var(--cooling-color)",
        gradientStart: "#8c90b3",
        gradientEnd: "#a0a4c7"
      };
    } else {
      return {
        className: "badge-stable",
        icon: <Minus className="icon-stable" size={14} />,
        text: "Stable",
        themeColor: "var(--stable-color)",
        gradientStart: "#7fa499",
        gradientEnd: "#92b8ac"
      };
    }
  };

  const roleSuggestions = [
    "Software Engineer in San Francisco",
    "Product Manager in New York",
    "Data Scientist in Austin",
    "DevOps Engineer in Seattle"
  ];

  const citySuggestions = [
    "San Francisco",
    "New York",
    "Austin",
    "Seattle"
  ];

  const renderMessageContent = (msg) => {
    if (msg.type === "loading") {
      return (
        <div className="typing-indicator">
          <div className="typing-dot"></div>
          <div className="typing-dot"></div>
          <div className="typing-dot"></div>
        </div>
      );
    }

    if (msg.type === "error") {
      return (
        <div className="error-card" style={{ padding: 0, background: "none", border: "none", textAlign: "left", boxShadow: "none" }}>
          <div className="error-icon" style={{ fontSize: "2rem" }}>⚠️</div>
          <h3 style={{ margin: "0.25rem 0 0.5rem", fontSize: "1.1rem" }}>Analysis Failed</h3>
          <p style={{ marginBottom: "1rem", fontSize: "0.9rem", color: "var(--text-secondary)" }}>{msg.text}</p>
          <button 
            onClick={() => performSearch(msg.retryParams.role, msg.retryParams.city)} 
            className="btn-retry"
          >
            Try Again
          </button>
        </div>
      );
    }

    if (msg.type === "results") {
      const result = msg.data;
      const badgeProps = getTrendBadgeProps(result.market_trend);
      const isJsonExpanded = expandedJsonId === msg.id;

      return (
        <div 
          className="results-container animate-fade-in"
          style={{
            "--accent-color": badgeProps.themeColor,
            "--chart-gradient-start": badgeProps.gradientStart,
            "--chart-gradient-end": "rgba(34, 139, 230, 0)"
          }}
        >
          {/* Market Trend Header */}
          <div className="pulse-card" style={{ borderLeftWidth: 4, paddingLeft: "1rem", marginBottom: "0.5rem" }}>
            <div className="pulse-header" style={{ marginBottom: "0.75rem", paddingBottom: "0.75rem", gap: "1rem" }}>
              <div>
                <span className="analysis-meta">Analysis for:</span>
                <h2 style={{ fontSize: "1.45rem", margin: "0.1rem 0", fontWeight: 800 }}>{result.role}</h2>
                <span className="location-name" style={{ fontSize: "0.9rem" }}>📍 {result.city}</span>
              </div>
              <div className={`trend-badge ${badgeProps.className}`} style={{ padding: "0.4rem 0.8rem", fontSize: "0.8rem" }}>
                {badgeProps.icon}
                <span>{badgeProps.text}</span>
              </div>
            </div>

            <div className="pulse-score-row" style={{ gap: "1.5rem" }}>
              <div className="score-item">
                <span className="score-label">Momentum Score</span>
                <span className="score-value" style={{ fontSize: "1.25rem" }}>
                  {result.postings.score > 0 ? "+" : ""}
                  {(result.postings.score * 100).toFixed(1)}%
                </span>
              </div>
              <div className="score-item">
                <span className="score-label">As of timestamp</span>
                <span className="score-value time-val" style={{ fontSize: "0.95rem" }}>
                  <Clock size={11} className="clock-icon" />
                  {new Date(result.as_of).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </span>
              </div>
            </div>
          </div>

          {/* Chart & Reasoning Grid */}
          <div className="details-grid">
            <div className="chart-card">
              <TrendChart data={result.postings.weekly_counts} />
            </div>

            <div className="reasoning-card">
              <h3 style={{ fontSize: "0.9rem" }}>AI Explanation</h3>
              <p className="explanation-text" style={{ fontSize: "0.9rem", lineHeight: 1.6 }}>{result.llm_explanation}</p>
            </div>
          </div>

          {/* News articles */}
          <div className="news-card" style={{ marginTop: "0.5rem" }}>
            <div className="news-header" style={{ marginBottom: "0.75rem", paddingBottom: "0.5rem" }}>
              <Newspaper size={16} className="news-icon" />
              <h3 style={{ fontSize: "0.9rem" }}>Recent Hiring & Layoffs News Context</h3>
            </div>
            {result.news && result.news.length > 0 ? (
              <ul className="news-list">
                {result.news.slice(0, 3).map((item, idx) => (
                  <li key={idx} className="news-item">
                    <span className="news-bullet" style={{ marginTop: "0.45rem", minWidth: "5px", height: "5px" }}></span>
                    <p className="news-text" style={{ fontSize: "0.85rem" }}>{item}</p>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="no-news" style={{ fontSize: "0.85rem" }}>No local hiring news headlines available for this query.</p>
            )}
          </div>

          {/* Expandable Raw JSON */}
          <div className="json-card" style={{ marginTop: "0.5rem" }}>
            <button 
              onClick={() => setExpandedJsonId(isJsonExpanded ? null : msg.id)} 
              className="json-toggle-btn"
              style={{ padding: "0.75rem 0", fontSize: "0.85rem" }}
            >
              <div className="json-btn-label">
                <Code size={14} />
                <span>Raw JSON Response</span>
              </div>
              {isJsonExpanded ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
            </button>
            
            {isJsonExpanded && (
              <div className="json-content">
                <pre style={{ fontSize: "0.75rem" }}><code>{JSON.stringify(result, null, 2)}</code></pre>
              </div>
            )}
          </div>
        </div>
      );
    }

    return <p>{msg.text}</p>;
  };

  return (
    <div className="root-layout">
      {/* Slim Vertical Left Sidebar */}
      <aside className="sidebar-panel">
        <button 
          onClick={handleReset} 
          className="sidebar-btn"
          aria-label="Start a New Search"
          title="New Chat"
        >
          <Plus size={20} />
        </button>
      </aside>

      {/* Main Content Area */}
      <main className="main-content-area">
        {/* Top-Right Theme Toggle */}
        <div className="theme-toggle-header">
          <button 
            onClick={toggleTheme} 
            className="theme-toggle-btn"
            aria-label="Toggle theme"
            title={theme === "dark" ? "Switch to Light Mode" : "Switch to Dark Mode"}
          >
            {theme === "dark" ? <Sun size={18} /> : <Moon size={18} />}
          </button>
        </div>

        {/* Unified Chat Console Container */}
        <div className="chat-console-unified">
          
          {/* Centered Home Welcome View */}
          <div className={`landing-wrapper-transition ${!hasSearched ? "visible" : "hidden"}`}>
            <header className="app-header" style={{ marginBottom: "2.5rem" }}>
              <div className="logo-section">
                <div className="logo-pulse"></div>
                <h1>JobPulse</h1>
              </div>
              <p className="app-tagline">Real-time market analytics powered by USAJobs & Gemini AI</p>
            </header>

            <h2 className="landing-title">What job market should we pulse today?</h2>

            <form 
              onSubmit={(e) => { e.preventDefault(); handleLandingSearch(); }} 
              className="chat-search-capsule"
              style={{ maxWidth: "660px", margin: "0 auto" }}
            >
              <input 
                type="text" 
                className="chat-search-input"
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                placeholder="Ask about a role and city (e.g. Software Engineer in SF)..."
                required
                disabled={loading}
              />
              <button 
                type="submit" 
                className="landing-btn-send"
                disabled={loading || !inputValue.trim()}
                aria-label="Search market"
              >
                <Send size={18} />
              </button>
            </form>

            <div className="landing-suggestions">
              {roleSuggestions.map((sug, idx) => (
                <button 
                  key={idx} 
                  onClick={() => handleLandingSuggestionClick(sug)}
                  className="landing-chip"
                  disabled={loading}
                >
                  <Sparkles size={12} style={{ color: "var(--accent-color)", marginRight: "4px" }} />
                  {sug}
                </button>
              ))}
            </div>
          </div>

          {/* Active Chat Stream View */}
          <div className={`chat-stream-transition ${hasSearched ? "visible" : "hidden"}`}>
            {/* Messages History */}
            <div className="chat-history-unified" ref={chatHistoryRef}>
              {messages.map((msg) => (
                <div key={msg.id} className={`chat-message-row ${msg.sender}`}>
                  <div className={`message-bubble ${msg.type === "results" ? "results-dashboard-bubble" : ""}`}>
                    {renderMessageContent(msg)}
                  </div>
                </div>
              ))}
            </div>

            {/* Suggestion Chips (Awaiting City) */}
            <div className="suggestion-container" style={{ marginBottom: "0.5rem" }}>
              {step === "awaiting_city" && citySuggestions.map((sug, idx) => (
                <button 
                  key={idx} 
                  onClick={() => handleSuggestionClick(sug)}
                  className="chip-btn"
                  disabled={loading}
                >
                  <MapPin size={12} className="info-icon" style={{ color: "var(--accent-color)" }} />
                  <span>{sug}</span>
                </button>
              ))}
            </div>

            {/* Bottom Input Capsule */}
            <div className="chat-input-bar-unified">
              <form 
                onSubmit={(e) => { e.preventDefault(); handleSendMessage(); }} 
                className="chat-search-capsule"
              >
                <input 
                  type="text" 
                  className="chat-search-input"
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  placeholder={
                    step === "awaiting_role" 
                      ? "Enter job title..." 
                      : step === "awaiting_city" 
                        ? `Enter city for ${role}...` 
                        : "Ask about a role and city..."
                  }
                  disabled={loading}
                  required
                />
                <button 
                  type="submit" 
                  className="landing-btn-send"
                  disabled={loading || !inputValue.trim()}
                  aria-label="Send query"
                >
                  <Send size={18} />
                </button>
              </form>
            </div>
          </div>

        </div>
      </main>
    </div>
  );
}
