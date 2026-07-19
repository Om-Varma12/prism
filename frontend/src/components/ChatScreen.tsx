/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useEffect, useRef } from 'react';
import { ChatMessage, ConversationItem } from '../types';
import { useChat } from '../hooks/useChat';

interface ChatScreenProps {
  onNavigate: unknown;
}

const shell = {
  obsidian: '#0b0c0f',
  panel: '#111318',
  panelRaised: '#161921',
  line: '#1b1e26',
  surface: '#1c212b',
  teal: '#5eead4',
  tealMuted: '#2c6b63',
  blue: '#60a5fa',
  blueMuted: '#1e3a5f',
  gold: '#fbbf24',
  goldMuted: '#5c4a1f',
  red: '#f87171',
  redMuted: '#5c2a2a',
  green: '#4ade80',
  greenMuted: '#1e4a2e',
  slate: '#94a3b8',
  ghost: '#334155',
  dim: '#475569',
};

const quickActions = [
  ['travel_explore', shell.teal, 'Area pattern scan', 'Robbery cases in Bengaluru North'],
  ['shield_person', shell.blue, 'High-risk offenders', 'List high-risk offenders in Mysuru'],
  ['hub', shell.gold, 'Network lead', 'Find connected accused in vehicle theft cases'],
  ['warning', shell.red, 'Hotspot scan', 'Identify active crime hotspots in Bengaluru'],
  ['article', shell.green, 'Executive brief', 'Draft an executive briefing on current FIR trends'],
];

function Glyph({
  name,
  className = '',
  style,
}: {
  name: string;
  className?: string;
  style?: React.CSSProperties;
}) {
  return (
    <span className={`material-symbols-outlined ${className}`} style={style}>
      {name}
    </span>
  );
}

function ScanStyles() {
  return (
    <style>
      {`
        .sentinel-grid {
          background-color: ${shell.obsidian};
          background-image:
            linear-gradient(rgba(94, 234, 212, 0.015) 1px, transparent 1px),
            linear-gradient(90deg, rgba(94, 234, 212, 0.015) 1px, transparent 1px);
          background-size: 60px 60px;
        }
        .sentinel-grid::before {
          content: '';
          position: absolute;
          inset: 0;
          pointer-events: none;
          z-index: 30;
          background: repeating-linear-gradient(0deg, transparent, transparent 2px, rgba(0,0,0,0.03) 2px, rgba(0,0,0,0.03) 4px);
        }
        @keyframes sentinelMsgIn {
          from { opacity: 0; transform: translateY(10px) scale(0.98); }
          to { opacity: 1; transform: translateY(0) scale(1); }
        }
        @keyframes sentinelPulse {
          0% { box-shadow: 0 0 0 0 rgba(74, 222, 128, 0.4); }
          70% { box-shadow: 0 0 0 6px rgba(74, 222, 128, 0); }
          100% { box-shadow: 0 0 0 0 rgba(74, 222, 128, 0); }
        }
        @keyframes sentinelDot {
          0%, 60%, 100% { transform: translateY(0); }
          30% { transform: translateY(-4px); }
        }
        @keyframes sentinelScan {
          0% { left: 0; opacity: 0; }
          10% { opacity: 1; }
          90% { opacity: 1; }
          100% { left: 100%; opacity: 0; }
        }
        .sentinel-msg-in { animation: sentinelMsgIn 0.35s cubic-bezier(0.22, 1, 0.36, 1) forwards; }
        .sentinel-status-pulse { animation: sentinelPulse 2s infinite; }
        .sentinel-dot { animation: sentinelDot 1.2s infinite ease-in-out; }
        .sentinel-dot:nth-child(2) { animation-delay: 0.15s; }
        .sentinel-dot:nth-child(3) { animation-delay: 0.3s; }
        .sentinel-scroll { scrollbar-width: thin; scrollbar-color: #242a36 transparent; }
        .sentinel-scroll::-webkit-scrollbar { width: 5px; height: 5px; }
        .sentinel-scroll::-webkit-scrollbar-track { background: transparent; }
        .sentinel-scroll::-webkit-scrollbar-thumb { background: #242a36; border-radius: 3px; }
        .sentinel-scroll::-webkit-scrollbar-thumb:hover { background: #334155; }
        .sentinel-sidebar-item { position: relative; transition: all 0.15s ease; }
        .sentinel-sidebar-item::before {
          content: '';
          position: absolute;
          left: 0;
          top: 50%;
          transform: translateY(-50%);
          width: 2px;
          height: 0;
          background: ${shell.teal};
          border-radius: 0 2px 2px 0;
          transition: height 0.2s ease;
        }
        .sentinel-sidebar-item:hover::before { height: 16px; }
        .sentinel-sidebar-item.active::before { height: 28px; }
        .sentinel-quick { transition: all 0.2s ease; }
        .sentinel-quick:hover {
          transform: translateY(-1px);
          box-shadow: 0 0 0 1px rgba(94, 234, 212, 0.2), 0 4px 16px rgba(0,0,0,0.3);
        }
        .sentinel-scan { position: relative; overflow: hidden; }
        .sentinel-scan::after {
          content: '';
          position: absolute;
          top: 0;
          bottom: 0;
          width: 40px;
          background: linear-gradient(90deg, transparent, rgba(94,234,212,0.08), transparent);
          animation: sentinelScan 3s linear infinite;
        }
      `}
    </style>
  );
}

function HistoryItem({
  item,
  active,
  onClick,
  color = shell.teal,
  muted = shell.tealMuted,
}: {
  item: ConversationItem;
  active: boolean;
  onClick: () => void;
  color?: string;
  muted?: string;
}) {
  const created = item.created_at
    ? new Date(item.created_at.replace(' ', 'T')).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    : 'now';

  return (
    <button
      type="button"
      onClick={onClick}
      className={`sentinel-sidebar-item flex w-full cursor-pointer items-start gap-2.5 rounded-lg px-3 py-2.5 text-left ${
        active ? 'active bg-white/[0.04]' : 'hover:bg-white/[0.03]'
      }`}
    >
      <span
        className="mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded border"
        style={{ backgroundColor: `${muted}33`, borderColor: `${muted}66`, color }}
      >
        <Glyph name="chat" className="text-[13px]" />
      </span>
      <span className="min-w-0 flex-1">
        <span className="block truncate text-[13px] font-medium leading-snug text-slate-100">{item.title}</span>
        <span className="mt-0.5 block truncate text-[11px]" style={{ color: shell.ghost }}>
          {active ? 'Active session' : 'Saved thread'} - {created}
        </span>
      </span>
    </button>
  );
}

function ResultTable({ message }: { message: ChatMessage }) {
  if (!message.tableData || message.tableData.length === 0) return null;

  // Derive columns dynamically from the first row's keys
  const columns = Object.keys(message.tableData[0]);

  // Detect status-like columns for colour coding
  const isStatusCol = (col: string) =>
    col.toLowerCase().includes('status') || col.toLowerCase().includes('state');

  const getCellStyle = (col: string, val: string) => {
    if (!isStatusCol(col)) return {};
    const upper = val.toUpperCase();
    if (upper.includes('ACTIVE') || upper.includes('PENDING'))
      return { color: shell.red, borderColor: `${shell.redMuted}99`, backgroundColor: `${shell.redMuted}55` };
    if (upper.includes('INVEST'))
      return { color: shell.gold, borderColor: `${shell.goldMuted}99`, backgroundColor: `${shell.goldMuted}55` };
    return { color: shell.green, borderColor: `${shell.greenMuted}99`, backgroundColor: `${shell.greenMuted}55` };
  };

  return (
    <div className="overflow-hidden rounded-xl border shadow-[0_0_0_1px_rgba(255,255,255,0.04),0_4px_24px_rgba(0,0,0,0.4)]" style={{ backgroundColor: shell.panelRaised, borderColor: shell.line }}>
      <div className="flex items-center justify-between border-b px-3.5 py-2" style={{ borderColor: shell.line, backgroundColor: 'rgba(28,33,43,0.4)' }}>
        <div className="flex items-center gap-2">
          <Glyph name="table" className="text-[15px]" style={{ color: shell.blue } as any} />
          <span className="text-[11px] font-semibold text-slate-200">Query Results</span>
        </div>
        <span className="font-mono text-[10px]" style={{ color: shell.ghost }}>{message.tableData.length} rows</span>
      </div>
      <div className="sentinel-scroll relative overflow-x-auto">
        <table className="w-full text-[11px]">
          <thead>
            <tr className="border-b" style={{ borderColor: shell.line, backgroundColor: 'rgba(28,33,43,0.3)' }}>
              {columns.map((col) => (
                <th key={col} className="whitespace-nowrap px-3.5 py-2 text-left font-semibold uppercase tracking-wider" style={{ color: shell.ghost }}>
                  {/* Convert camelCase / PascalCase to spaced label */}
                  {col.replace(/([A-Z])/g, ' $1').replace(/[_*()]/g, ' ').trim()}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {message.tableData.map((row, idx) => (
              <tr key={idx} className="border-b transition-colors hover:bg-teal-300/[0.04]" style={{ borderColor: 'rgba(27,30,38,0.6)' }}>
                {columns.map((col, ci) => {
                  const rawVal = row[col];
                  const val = String(rawVal !== null && rawVal !== undefined ? rawVal : 'N/A');
                  const sStyle = getCellStyle(col, val);
                  const isStatus = Object.keys(sStyle).length > 0;
                  return (
                    <td key={col} className="whitespace-nowrap px-3.5 py-2.5">
                      {isStatus ? (
                        <span className="inline-flex items-center gap-1 rounded border px-1.5 py-0.5 text-[10px] font-semibold" style={sStyle}>
                          {val}
                        </span>
                      ) : (
                        <span style={{ color: ci === 0 ? shell.teal : '#cbd5e1' }} className={ci === 0 ? 'font-medium' : ''}>
                          {val}
                        </span>
                      )}
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}


function MessageMetadata({
  message,
  openSqlQueryId,
  openSourcesId,
  setOpenSqlQueryId,
  setOpenSourcesId,
}: {
  message: ChatMessage;
  openSqlQueryId: string | null;
  openSourcesId: string | null;
  setOpenSqlQueryId: (id: string | null) => void;
  setOpenSourcesId: (id: string | null) => void;
}) {
  if (!message.sqlQuery) return null;

  const sqlOpen = openSqlQueryId === message.id;
  const sourcesOpen = openSourcesId === message.id;
  const sources = message.sources && message.sources.length > 0 ? message.sources : ['CaseMaster'];

  return (
    <>
      <div className="overflow-hidden rounded-xl border shadow-[0_0_0_1px_rgba(255,255,255,0.04),0_4px_24px_rgba(0,0,0,0.4)]" style={{ backgroundColor: shell.panelRaised, borderColor: shell.line }}>
        <button
          type="button"
          onClick={() => setOpenSqlQueryId(sqlOpen ? null : message.id)}
          className="group flex w-full items-center justify-between px-3.5 py-2.5 transition-colors hover:bg-white/[0.02]"
        >
          <div className="flex items-center gap-2">
            <Glyph name={sqlOpen ? 'expand_more' : 'chevron_right'} className="text-[15px] transition-colors" style={{ color: shell.ghost } as any} />
            <Glyph name="code" className="text-[15px]" style={{ color: shell.blue } as any} />
            <span className="text-[11px] font-semibold transition-colors" style={{ color: shell.ghost }}>Source Query</span>
          </div>
          <span className="font-mono text-[10px]" style={{ color: shell.ghost }}>SQL</span>
        </button>
        <div className={`${sqlOpen ? 'max-h-[600px] opacity-100' : 'max-h-0 opacity-0'} overflow-hidden transition-all duration-300`}>
          <div className="px-3.5 pb-3 pt-1">
            <div className="sentinel-scroll overflow-x-auto rounded-lg border p-3" style={{ backgroundColor: shell.obsidian, borderColor: shell.line }}>
              <pre className="whitespace-pre-wrap font-mono text-[11px] leading-relaxed" style={{ color: shell.slate }}>
                {message.sqlQuery}
              </pre>
            </div>
          </div>
        </div>
      </div>

      <div className="overflow-hidden rounded-xl border shadow-[0_0_0_1px_rgba(255,255,255,0.04),0_4px_24px_rgba(0,0,0,0.4)]" style={{ backgroundColor: shell.panelRaised, borderColor: shell.line }}>
        <button
          type="button"
          onClick={() => setOpenSourcesId(sourcesOpen ? null : message.id)}
          className="group flex w-full items-center justify-between px-3.5 py-2.5 transition-colors hover:bg-white/[0.02]"
        >
          <div className="flex items-center gap-2">
            <Glyph name={sourcesOpen ? 'expand_more' : 'chevron_right'} className="text-[15px]" style={{ color: shell.ghost } as any} />
            <Glyph name="menu_book" className="text-[15px]" style={{ color: shell.green } as any} />
            <span className="text-[11px] font-semibold" style={{ color: shell.ghost }}>Data Sources</span>
          </div>
          <span className="font-mono text-[10px]" style={{ color: shell.ghost }}>{sources.length} refs</span>
        </button>
        <div className={`${sourcesOpen ? 'max-h-[600px] opacity-100' : 'max-h-0 opacity-0'} overflow-hidden transition-all duration-300`}>
          <div className="space-y-1.5 px-3.5 pb-3 pt-1">
            {sources.map((source, idx) => (
              <div key={`${source}-${idx}`} className="flex items-center gap-2.5 rounded-lg border px-2.5 py-2 transition-colors hover:bg-teal-300/[0.08]" style={{ backgroundColor: 'rgba(28,33,43,0.3)', borderColor: 'rgba(27,30,38,0.6)' }}>
                <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded border" style={{ backgroundColor: `${shell.blueMuted}33`, borderColor: `${shell.blueMuted}66`, color: shell.blue }}>
                  <Glyph name="description" className="text-[13px]" />
                </span>
                <div className="min-w-0">
                  <p className="truncate text-[11px] font-medium text-slate-200">{source}</p>
                  <p className="truncate text-[10px]" style={{ color: shell.ghost }}>PRISM records - Evidence source</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </>
  );
}

function MessageBlock({
  message,
  openSqlQueryId,
  openSourcesId,
  setOpenSqlQueryId,
  setOpenSourcesId,
}: {
  message: ChatMessage;
  openSqlQueryId: string | null;
  openSourcesId: string | null;
  setOpenSqlQueryId: (id: string | null) => void;
  setOpenSourcesId: (id: string | null) => void;
}) {
  if (message.sender === 'user') {
    return (
      <div className="sentinel-msg-in flex justify-end gap-3">
        <div className="max-w-[75%]">
          <div className="mb-1 flex items-center justify-end gap-2">
            <span className="text-[10px] font-medium" style={{ color: shell.ghost }}>You</span>
            <span className="text-[10px]" style={{ color: shell.ghost }}>{message.timestamp}</span>
          </div>
          <div className="rounded-2xl rounded-tr-md border px-4 py-3 shadow-[0_0_12px_rgba(94,234,212,0.08)]" style={{ backgroundColor: 'rgba(94,234,212,0.08)', borderColor: 'rgba(94,234,212,0.15)' }}>
            <p className="text-sm leading-relaxed text-slate-200">{message.text}</p>
          </div>
        </div>
        <Avatar kind="user" className="mt-5" />
      </div>
    );
  }

  return (
    <div className="sentinel-msg-in flex gap-3">
      <Avatar kind="ai" className="mt-5" />
      <div className="max-w-[85%]">
        <div className="mb-1.5 flex items-center gap-2">
          <span className="text-[10px] font-semibold uppercase tracking-wider" style={{ color: shell.teal }}>Sentinel</span>
          <span className="text-[10px]" style={{ color: shell.ghost }}>{message.timestamp}</span>
        </div>
        <div className="space-y-3">
          <div className="rounded-2xl rounded-tl-md border px-4 py-3 shadow-[0_0_0_1px_rgba(255,255,255,0.04),0_4px_24px_rgba(0,0,0,0.4)]" style={{ backgroundColor: shell.panelRaised, borderColor: shell.line }}>
            <p className="whitespace-pre-wrap text-sm leading-relaxed text-slate-300">{message.text}</p>
          </div>
          <ResultTable message={message} />
          <MessageMetadata
            message={message}
            openSqlQueryId={openSqlQueryId}
            openSourcesId={openSourcesId}
            setOpenSqlQueryId={setOpenSqlQueryId}
            setOpenSourcesId={setOpenSourcesId}
          />
        </div>
      </div>
    </div>
  );
}

function Avatar({ kind, className = '' }: { kind: 'ai' | 'user'; className?: string }) {
  if (kind === 'user') {
    return (
      <div className={`flex h-7 w-7 shrink-0 items-center justify-center rounded-lg border ${className}`} style={{ backgroundColor: `${shell.blueMuted}33`, borderColor: `${shell.blueMuted}66` }}>
        <span className="text-[10px] font-bold" style={{ color: shell.blue }}>OM</span>
      </div>
    );
  }

  return (
    <div className={`flex h-7 w-7 shrink-0 items-center justify-center rounded-lg border ${className}`} style={{ backgroundColor: `${shell.tealMuted}33`, borderColor: `${shell.tealMuted}66` }}>
      <Glyph name="auto_awesome" className="text-[15px]" style={{ color: shell.teal } as any} />
    </div>
  );
}

function TypingBlock() {
  return (
    <div className="sentinel-msg-in flex gap-3">
      <Avatar kind="ai" className="mt-5" />
      <div className="max-w-[85%]">
        <div className="mb-1.5 flex items-center gap-2">
          <span className="text-[10px] font-semibold uppercase tracking-wider" style={{ color: shell.teal }}>Sentinel</span>
          <span className="text-[10px]" style={{ color: shell.ghost }}>now</span>
        </div>
        <div className="rounded-2xl rounded-tl-md border px-4 py-3 shadow-[0_0_0_1px_rgba(255,255,255,0.04),0_4px_24px_rgba(0,0,0,0.4)]" style={{ backgroundColor: shell.panelRaised, borderColor: shell.line }}>
          <div className="flex items-center gap-2">
            <div className="flex gap-1">
              <div className="sentinel-dot h-1.5 w-1.5 rounded-full" style={{ backgroundColor: shell.teal }} />
              <div className="sentinel-dot h-1.5 w-1.5 rounded-full" style={{ backgroundColor: shell.teal }} />
              <div className="sentinel-dot h-1.5 w-1.5 rounded-full" style={{ backgroundColor: shell.teal }} />
            </div>
            <span className="text-[11px]" style={{ color: shell.ghost }}>Analyzing intelligence data...</span>
          </div>
        </div>
      </div>
    </div>
  );
}

function EmptyTranscript({ onPrompt }: { onPrompt: (text: string) => void }) {
  return (
    <div className="flex h-full items-center justify-center px-5 py-8">
      <div className="max-w-xl text-center">
        <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-xl border rotate-45" style={{ backgroundColor: 'rgba(94,234,212,0.10)', borderColor: 'rgba(94,234,212,0.20)' }}>
          <Glyph name="fingerprint" className="-rotate-45 text-[24px]" style={{ color: shell.teal } as any} />
        </div>
        <h2 className="text-xl font-semibold text-slate-100">Start an intelligence session</h2>
        <p className="mt-2 text-sm leading-6 text-slate-400">
          Ask about FIRs, accused networks, hotspots, or patterns. Results will appear in the same Sentinel transcript format.
        </p>
      </div>
    </div>
  );
}

export default function ChatScreen({ onNavigate: _onNavigate }: ChatScreenProps) {
  const {
    messages,
    isTyping,
    history,
    activeSessionId,
    sendMessage,
    loadHistory,
    startNewConversation,
    selectConversation,
  } = useChat();

  const [inputText, setInputText] = React.useState('');
  const [historySearch, setHistorySearch] = React.useState('');
  const [openSqlQueryId, setOpenSqlQueryId] = React.useState<string | null>(null);
  const [openSourcesId, setOpenSourcesId] = React.useState<string | null>(null);
  const [isExporting, setIsExporting] = React.useState(false);
  const scrollContainerRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const historyInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    loadHistory();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    if (scrollContainerRef.current) {
      scrollContainerRef.current.scrollTop = scrollContainerRef.current.scrollHeight;
    }
  }, [messages, isTyping]);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
    }
  }, [inputText]);

  const handleSendMessage = (text = inputText) => {
    if (!text.trim()) return;
    sendMessage(text);
    setInputText('');
  };

  const handleExportPDF = async () => {
    if (!activeSessionId) return;

    setIsExporting(true);
    try {
      const apiBaseUrl = process.env.REACT_APP_API_URL || 'http://localhost:3001';
      const response = await fetch(`${apiBaseUrl}/api/chat/export-pdf?session_id=${activeSessionId}`);
      if (!response.ok) throw new Error('Failed to export PDF');
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `chat_export_${activeSessionId.slice(0, 8)}.pdf`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      console.error('Failed to export PDF:', error);
    } finally {
      setIsExporting(false);
    }
  };

  const handleShareSession = async () => {
    try {
      await navigator.clipboard?.writeText(window.location.href);
    } catch (error) {
      console.error('Failed to copy session link:', error);
    }
  };

  const filteredHistory = history.filter((item: ConversationItem) => item.title.toLowerCase().includes(historySearch.toLowerCase()));
  const currentConversation = history.find((item: ConversationItem) => item.session_id === activeSessionId);
  const activeTitle = currentConversation?.title || (messages.length > 0 ? 'Current conversation' : 'New conversation');

  return (
    <div className="sentinel-grid relative flex h-full flex-1 flex-col overflow-hidden text-slate-200">
      <ScanStyles />

      <div className="flex min-h-0 flex-1">
        <aside className="hidden w-[260px] shrink-0 flex-col border-r md:flex" style={{ backgroundColor: 'rgba(17,19,24,0.5)', borderColor: shell.line }}>
          <div className="p-3">
            <div className="relative">
              <Glyph name="search" className="absolute left-3 top-1/2 -translate-y-1/2 text-[15px]" style={{ color: shell.ghost } as any} />
              <input
                ref={historyInputRef}
                type="text"
                placeholder="Search history..."
                value={historySearch}
                onChange={(e) => setHistorySearch(e.target.value)}
                className="h-9 w-full rounded-lg border py-0 pl-9 pr-3 text-xs text-slate-200 outline-none transition-all placeholder:text-slate-700 focus:ring-1"
                style={{ backgroundColor: 'rgba(28,33,43,0.6)', borderColor: shell.line }}
              />
            </div>
          </div>

          <div className="px-3 pb-1.5">
            <span className="text-[10px] font-semibold uppercase tracking-widest" style={{ color: shell.ghost }}>Today</span>
          </div>
          <div className="sentinel-scroll flex-1 space-y-0.5 overflow-y-auto px-2">
            {filteredHistory.length > 0 ? (
              filteredHistory.map((item: ConversationItem) => (
                <HistoryItem
                  key={item.session_id}
                  item={item}
                  active={item.session_id === activeSessionId}
                  onClick={() => selectConversation(item.session_id)}
                />
              ))
            ) : (
              <div className="rounded-lg border border-dashed px-3 py-3 text-[12px] leading-5" style={{ borderColor: shell.line, color: shell.ghost }}>
                No previous conversations yet.
              </div>
            )}
          </div>

          <div className="border-t p-3" style={{ borderColor: shell.line }}>
            <button
              type="button"
              onClick={startNewConversation}
              className="flex h-9 w-full items-center justify-center gap-2 rounded-lg border text-xs font-semibold transition-all hover:bg-teal-300/15"
              style={{ backgroundColor: 'rgba(94,234,212,0.10)', borderColor: 'rgba(94,234,212,0.20)', color: shell.teal }}
            >
              <Glyph name="add" className="text-[16px]" />
              New Session
            </button>
          </div>
        </aside>

        <main className="flex min-w-0 flex-1 flex-col" style={{ backgroundColor: shell.obsidian }}>
          <div className="flex h-12 shrink-0 items-center justify-between border-b px-5" style={{ backgroundColor: 'rgba(17,19,24,0.30)', borderColor: shell.line }}>
            <div className="flex items-center gap-3">
              <div className="flex h-7 w-7 items-center justify-center rounded-lg border" style={{ backgroundColor: `${shell.tealMuted}33`, borderColor: `${shell.tealMuted}66` }}>
                <Glyph name="bar_chart" className="text-[15px]" style={{ color: shell.teal } as any} />
              </div>
              <div>
                <h1 className="text-sm font-semibold text-slate-100">{activeTitle}</h1>
                <p className="text-[11px]" style={{ color: shell.ghost }}>
                  {messages.length} messages
                </p>
              </div>
            </div>
            <div className="flex items-center gap-1">
              <button
                type="button"
                onClick={handleExportPDF}
                disabled={isExporting}
                className="flex h-7 items-center gap-1.5 rounded-md px-2.5 text-[11px] font-medium transition-all hover:bg-white/5 hover:text-slate-300 disabled:opacity-50 disabled:cursor-not-allowed"
                style={{ color: shell.ghost }}
              >
                {isExporting ? (
                  <>
                    <span className="animate-spin h-3 w-3 border-2 border-current border-t-transparent rounded-full" />
                    Exporting...
                  </>
                ) : (
                  <>
                    <Glyph name="download" className="text-[14px]" />
                    Export
                  </>
                )}
              </button>
              <button
                type="button"
                onClick={handleShareSession}
                className="flex h-7 items-center gap-1.5 rounded-md px-2.5 text-[11px] font-medium transition-all hover:bg-white/5 hover:text-slate-300"
                style={{ color: shell.ghost }}
              >
                <Glyph name="share" className="text-[14px]" />
                Share
              </button>
            </div>
          </div>

          <div ref={scrollContainerRef} className="sentinel-scroll min-h-0 flex-1 space-y-5 overflow-y-auto px-5 py-5">
            {messages.length === 0 ? (
              <EmptyTranscript onPrompt={(text) => handleSendMessage(text)} />
            ) : (
              messages.map((message) => (
                <MessageBlock
                  key={message.id}
                  message={message}
                  openSqlQueryId={openSqlQueryId}
                  openSourcesId={openSourcesId}
                  setOpenSqlQueryId={setOpenSqlQueryId}
                  setOpenSourcesId={setOpenSourcesId}
                />
              ))
            )}
            {isTyping && <TypingBlock />}
          </div>


          <div className="px-5 pb-4">
            <form
              onSubmit={(e) => {
                e.preventDefault();
                handleSendMessage();
              }}
              className="overflow-hidden rounded-2xl border shadow-[0_0_0_1px_rgba(255,255,255,0.05),0_8px_32px_rgba(0,0,0,0.5)]"
              style={{ backgroundColor: shell.panelRaised, borderColor: shell.line }}
            >
              <div className="flex items-start gap-3 px-4 py-3">
                <Avatar kind="user" className="mt-0.5" />
                <div className="min-w-0 flex-1">
                  <textarea
                    ref={textareaRef}
                    rows={1}
                    placeholder="Enter your intelligence query..."
                    value={inputText}
                    onChange={(e) => setInputText(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter' && !e.shiftKey) {
                        e.preventDefault();
                        handleSendMessage();
                      }
                    }}
                    className="sentinel-composer max-h-36 w-full resize-none bg-transparent py-1 text-sm leading-relaxed text-slate-200 outline-none placeholder:text-slate-700"
                  />
                </div>
              </div>
              <div className="flex items-center justify-between px-3 pb-2.5 pt-1">
                <div className="flex items-center gap-1">
                  <button
                    type="button"
                    onClick={() => textareaRef.current?.focus()}
                    className="flex h-7 items-center gap-1.5 rounded-lg px-2.5 text-[11px] transition-colors hover:bg-white/5 hover:text-slate-300"
                    style={{ color: shell.ghost }}
                  >
                    <Glyph name="attach_file" className="text-[15px]" />
                    Attach
                  </button>
                  <button
                    type="button"
                    onClick={() => setInputText('Use the active context to ')}
                    className="flex h-7 items-center gap-1.5 rounded-lg px-2.5 text-[11px] transition-colors hover:bg-white/5 hover:text-slate-300"
                    style={{ color: shell.ghost }}
                  >
                    <Glyph name="grid_view" className="text-[15px]" />
                    Context
                  </button>
                </div>
                <button
                  type="submit"
                  className="flex h-8 items-center gap-1.5 rounded-lg border px-4 text-xs font-semibold transition-all hover:bg-teal-300/15"
                  style={{ backgroundColor: 'rgba(94,234,212,0.10)', borderColor: 'rgba(94,234,212,0.20)', color: shell.teal }}
                >
                  <Glyph name="send" className="text-[15px]" />
                  Send
                </button>
              </div>
            </form>
          </div>
        </main>
      </div>
    </div>
  );
}