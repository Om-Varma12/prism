/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState, useRef, useEffect } from 'react';
import { Screen, ChatMessage } from '../types';
import { 
  INITIAL_CHAT_MESSAGES, 
  CONVERSATION_HISTORY, 
  CHAT_RESPONSES 
} from '../data/mockData';

interface ChatScreenProps {
  onNavigate: (screen: Screen) => void;
}

export default function ChatScreen({ onNavigate }: ChatScreenProps) {
  const [messages, setMessages] = useState<ChatMessage[]>(INITIAL_CHAT_MESSAGES);
  const [inputText, setInputText] = useState('');
  const [openSqlQueryId, setOpenSqlQueryId] = useState<string | null>(null);
  const [openSourcesId, setOpenSourcesId] = useState<string | null>(null);
  const [activeHistoryId, setActiveHistoryId] = useState('ch-1');
  const [isTyping, setIsTyping] = useState(false);

  const scrollContainerRef = useRef<HTMLDivElement>(null);

  // Auto-scroll on new messages
  useEffect(() => {
    if (scrollContainerRef.current) {
      scrollContainerRef.current.scrollTop = scrollContainerRef.current.scrollHeight;
    }
  }, [messages, isTyping]);

  const handleSendMessage = (text: string) => {
    if (!text.trim()) return;

    // Add user message
    const userMessage: ChatMessage = {
      id: `msg-user-${Date.now()}`,
      sender: 'user',
      text: text,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      status: 'ACTIVE' // dummy property matching interface if required
    } as any;

    setMessages((prev) => [...prev, userMessage]);
    setInputText('');
    setIsTyping(true);

    setTimeout(() => {
      const normalizedQuery = text.toLowerCase().trim();
      let matchedResponse = CHAT_RESPONSES[normalizedQuery];

      if (!matchedResponse) {
        matchedResponse = {
          sender: 'ai',
          text: `Executing intelligence scanning for query: "${text}". No pre-computed threat signature matches this exact request, but real-time logs point to active units in Bengaluru North.`,
          tableData: [
            { firNo: 'FIR-2023-BN-1102', crimeType: 'Suspicious Activity', district: 'Bengaluru North', status: 'ACTIVE' },
            { firNo: 'FIR-2023-HC-0922', crimeType: 'Public Disturbance', district: 'Hubballi Central', status: 'INVESTIGATION' }
          ],
          sqlQuery: `SELECT * FROM general_firs WHERE incident_description LIKE "%${text}%" AND status IN ("ACTIVE", "INVESTIGATION");`,
          scannedRecords: 512
        };
      }

      const aiMessage: ChatMessage = {
        id: `msg-ai-${Date.now()}`,
        sender: 'ai',
        text: matchedResponse.text,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        tableData: matchedResponse.tableData,
        sqlQuery: matchedResponse.sqlQuery,
        scannedRecords: matchedResponse.scannedRecords
      };

      setMessages((prev) => [...prev, aiMessage]);
      setIsTyping(false);
    }, 1500);
  };

  const handleNewConversation = () => {
    setMessages([
      {
        id: `msg-init-${Date.now()}`,
        sender: 'ai',
        text: 'PRISM terminal online. State your inquiry regarding active FIR cases, suspect profiles, coordinate crossings, or hot spot trends.',
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      }
    ]);
  };

  const handleHistoryClick = (id: string, title: string) => {
    setActiveHistoryId(id);
    setMessages([
      {
        id: `msg-user-hist`,
        sender: 'user',
        text: title,
        timestamp: '08:41 AM'
      },
      {
        id: `msg-ai-hist`,
        sender: 'ai',
        text: `I have retrieved robbery cases associated with "${title}". Real-time tactical feeds have been loaded below.`,
        timestamp: '08:41 AM',
        tableData: [
          { firNo: 'FIR-2023-BN-0847', crimeType: 'Robbery', district: 'Bengaluru North', status: 'ACTIVE' },
          { firNo: 'FIR-2023-BN-0912', crimeType: 'Robbery', district: 'Bengaluru North', status: 'INVESTIGATION' },
          { firNo: 'FIR-2023-BN-1004', crimeType: 'Robbery', district: 'Bengaluru North', status: 'ACTIVE' }
        ],
        sqlQuery: 'SELECT * FROM fir_records WHERE crime_type = "Robbery" AND district = "Bengaluru North" AND status = "ACTIVE";',
        scannedRecords: 847
      }
    ]);
  };

  return (
    <div className="flex-1 flex overflow-hidden bg-layout-bg h-full select-none">
      {/* Column 1: Conversation History */}
      <aside className="w-[220px] flex-shrink-0 bg-layout-surface border-r border-layout-border flex flex-col hidden lg:flex">
        <div className="p-4 border-b border-layout-border">
          <button
            onClick={handleNewConversation}
            className="w-full flex items-center justify-center gap-2 py-2 px-3 border border-layout-border rounded text-primary-container hover:border-primary-container transition-colors font-body-sm font-semibold cursor-pointer"
          >
            <span className="material-symbols-outlined text-[18px]">add</span>
            New Conversation
          </button>
        </div>
        <div className="flex-1 overflow-y-auto custom-scrollbar p-3 space-y-6">
          <div>
            <h3 className="text-[#8B92A5] text-[10px] uppercase font-bold tracking-wider mb-2 px-2 font-mono">
              Today
            </h3>
            <ul className="space-y-1">
              {CONVERSATION_HISTORY.filter(h => h.category === 'Today').map((item) => {
                const isActive = activeHistoryId === item.id;
                return (
                  <li key={item.id}>
                    <button
                      onClick={() => handleHistoryClick(item.id, item.title)}
                      className={`w-full text-left block px-2 py-1.5 rounded text-sm truncate font-body-sm transition-colors cursor-pointer ${
                        isActive
                          ? 'bg-surface-container-high text-primary-fixed border-l-2 border-primary-container'
                          : 'text-on-surface-variant hover:bg-surface-container'
                      }`}
                    >
                      {item.title}
                    </button>
                  </li>
                );
              })}
            </ul>
          </div>
          <div>
            <h3 className="text-[#8B92A5] text-[10px] uppercase font-bold tracking-wider mb-2 px-2 font-mono">
              Previous 7 Days
            </h3>
            <ul className="space-y-1">
              {CONVERSATION_HISTORY.filter(h => h.category === 'Previous 7 Days').map((item) => {
                const isActive = activeHistoryId === item.id;
                return (
                  <li key={item.id}>
                    <button
                      onClick={() => handleHistoryClick(item.id, item.title)}
                      className={`w-full text-left block px-2 py-1.5 rounded text-sm truncate font-body-sm transition-colors cursor-pointer ${
                        isActive
                          ? 'bg-surface-container-high text-primary-fixed border-l-2 border-primary-container'
                          : 'text-on-surface-variant hover:bg-surface-container'
                      }`}
                    >
                      {item.title}
                    </button>
                  </li>
                );
              })}
            </ul>
          </div>
        </div>
      </aside>

      {/* Column 2: Center Workspace (Chat) */}
      <section className="flex-1 flex flex-col relative bg-layout-bg min-w-0">
        {/* Header for Mobile/Tablet */}
        <header className="lg:hidden h-16 border-b border-layout-border flex items-center px-4 justify-between bg-layout-surface">
          <div className="font-headline-sm text-headline-sm font-semibold text-primary">
            Intelligence Chat
          </div>
          <button 
            onClick={handleNewConversation}
            className="text-on-surface-variant hover:text-primary-container cursor-pointer"
          >
            <span className="material-symbols-outlined">menu</span>
          </button>
        </header>

        {/* Chat Scroll Area */}
        <div
          ref={scrollContainerRef}
          className="flex-1 overflow-y-auto custom-scrollbar p-6 space-y-8 pb-32"
        >
          {messages.map((msg) => (
            <div key={msg.id} className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
              {msg.sender === 'user' ? (
                <div className="bg-primary-container text-white px-4 py-3 rounded-lg max-w-[80%] lg:max-w-[70%] font-body-sm shadow-sm">
                  {msg.text}
                </div>
              ) : (
                <div className="flex flex-col max-w-[90%] lg:max-w-[85%]">
                  <div className="font-body-sm text-on-surface mb-4 leading-relaxed whitespace-pre-wrap">
                    {msg.text}
                  </div>

                  {/* Data Table */}
                  {msg.tableData && msg.tableData.length > 0 && (
                    <div className="border border-layout-border rounded bg-layout-surface overflow-hidden mb-4">
                      <table className="w-full text-left text-sm font-body-sm">
                        <thead className="bg-surface-container-high border-b border-layout-border text-on-surface-variant">
                          <tr>
                            <th className="py-2 px-3 font-semibold">FIR No.</th>
                            <th className="py-2 px-3 font-semibold">Crime Type</th>
                            <th className="py-2 px-3 font-semibold">District</th>
                            <th className="py-2 px-3 font-semibold text-right">Status</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-layout-border text-on-surface">
                          {msg.tableData.map((row, idx) => (
                            <tr key={idx} className="hover:bg-surface-container-lowest transition-colors">
                              <td className="py-2 px-3 font-label-mono text-label-mono text-primary-fixed">
                                {row.firNo}
                              </td>
                              <td className="py-2 px-3">{row.crimeType}</td>
                              <td className="py-2 px-3">{row.district}</td>
                              <td className="py-2 px-3 text-right">
                                <span className={`inline-block px-2 py-0.5 border text-[10px] font-bold rounded tracking-wide ${
                                  row.status === 'ACTIVE' 
                                    ? 'border-[#ffb68c] text-[#ffb68c]' 
                                    : row.status === 'INVESTIGATION'
                                    ? 'border-outline text-outline'
                                    : 'border-green-400 text-green-400'
                                }`}>
                                  {row.status}
                                </span>
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  )}

                  {/* Collapsed Actions */}
                  {msg.sqlQuery && (
                    <div className="space-y-2">
                      <div>
                        <button
                          onClick={() => setOpenSqlQueryId(openSqlQueryId === msg.id ? null : msg.id)}
                          className="flex items-center gap-1 text-[#4A5060] hover:text-on-surface-variant font-label-mono text-[11px] transition-colors group cursor-pointer"
                        >
                          <span className="material-symbols-outlined text-[14px] group-hover:text-primary-container">
                            {openSqlQueryId === msg.id ? 'arrow_drop_down' : 'arrow_right'}
                          </span>
                          View SQL Query
                        </button>
                        {openSqlQueryId === msg.id && (
                          <div className="mt-1 bg-black border border-layout-border p-3 rounded font-mono text-[11px] text-green-400 overflow-x-auto whitespace-pre">
                            <code>{msg.sqlQuery}</code>
                          </div>
                        )}
                      </div>

                      <div>
                        <button
                          onClick={() => setOpenSourcesId(openSourcesId === msg.id ? null : msg.id)}
                          className="flex items-center gap-1 text-[#4A5060] hover:text-on-surface-variant font-label-mono text-[11px] transition-colors group cursor-pointer"
                        >
                          <span className="material-symbols-outlined text-[14px] group-hover:text-primary-container">
                            {openSourcesId === msg.id ? 'arrow_drop_down' : 'arrow_right'}
                          </span>
                          Data Sources ({msg.scannedRecords || 0} records scanned)
                        </button>
                        {openSourcesId === msg.id && (
                          <div className="mt-1 pl-4 text-[10px] text-outline font-mono space-y-1">
                            <div>• ksp_state_central_db.archive_fir (Index: OPTIMIZED)</div>
                            <div>• nlp_extracted_pattern_manifest_2026.json</div>
                          </div>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          ))}

          {isTyping && (
            <div className="flex justify-start">
              <div className="bg-layout-surface border border-layout-border text-white/60 px-4 py-3 text-[10px] font-mono tracking-wider flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-primary-container animate-pulse"></span>
                <span>PRISM CORE GENERATING THREAT METRICS...</span>
              </div>
            </div>
          )}
        </div>

        {/* Input Area */}
        <div className="absolute bottom-0 left-0 w-full p-4 bg-layout-bg border-t border-layout-border">
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleSendMessage(inputText);
            }}
            className="max-w-4xl mx-auto relative flex items-center"
          >
            <input
              className="w-full bg-layout-surface border border-layout-border rounded-lg py-3 pl-4 pr-24 text-on-surface placeholder:text-outline-variant font-body-sm focus:outline-none focus:border-primary-container focus:ring-1 focus:ring-primary-container transition-all outline-none"
              placeholder="Ask about FIRs, accused, locations, or patterns..."
              type="text"
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
            />
            <div className="absolute right-2 flex items-center gap-1">
              <button
                type="button"
                onClick={() => setInputText('Robbery cases in Bengaluru North')}
                className="p-1.5 text-outline-variant hover:text-primary-container transition-colors rounded cursor-pointer"
              >
                <span className="material-symbols-outlined text-[20px]">mic</span>
              </button>
              <button
                type="submit"
                className="p-1.5 bg-primary-container text-white hover:bg-inverse-primary transition-colors rounded cursor-pointer"
              >
                <span className="material-symbols-outlined text-[20px]">send</span>
              </button>
            </div>
          </form>
        </div>
      </section>

      {/* Column 3: Related Context */}
      <aside className="w-[260px] flex-shrink-0 bg-layout-surface border-l border-layout-border hidden xl:flex flex-col overflow-y-auto custom-scrollbar p-4 space-y-6">
        <div>
          <h3 className="text-[#8B92A5] text-[10px] uppercase font-bold tracking-wider mb-3 font-mono">
            Mentioned Entities
          </h3>
          <div className="space-y-3">
            {/* Entity Card 1 */}
            <div
              onClick={() => onNavigate(Screen.NETWORK)}
              className="border border-layout-border rounded p-3 bg-layout-bg hover:border-primary-container/50 transition-colors cursor-pointer group"
            >
              <div className="flex justify-between items-start mb-2">
                <div className="flex items-center gap-2 text-on-surface">
                  <span className="material-symbols-outlined text-[16px] text-outline">person</span>
                  <span className="font-body-sm font-semibold">Suresh Hegde</span>
                </div>
              </div>
              <div className="text-[12px] text-on-surface-variant mb-2 font-mono">
                Accused Person
              </div>
              <div className="flex items-center justify-between mt-2 pt-2 border-t border-layout-border/50">
                <span className="text-[11px] font-label-mono text-outline">6 active cases</span>
                <span className="px-1.5 py-0.5 border border-tertiary text-tertiary text-[9px] font-bold rounded">
                  HIGH-RISK
                </span>
              </div>
            </div>
            {/* Entity Card 2 */}
            <div className="border border-layout-border rounded p-3 bg-layout-bg hover:border-primary-container/50 transition-colors cursor-pointer group">
              <div className="flex justify-between items-start mb-2">
                <div className="flex items-center gap-2 text-on-surface">
                  <span className="material-symbols-outlined text-[16px] text-outline">location_on</span>
                  <span className="font-body-sm font-semibold">Yelahanka PS</span>
                </div>
              </div>
              <div className="text-[12px] text-on-surface-variant mb-2 font-mono">
                Location
              </div>
              <div className="flex items-center justify-between mt-2 pt-2 border-t border-layout-border/50">
                <span className="text-[11px] font-label-mono text-outline">12 incidents / 24h</span>
              </div>
            </div>
          </div>
        </div>
        <div>
          <h3 className="text-[#8B92A5] text-[10px] uppercase font-bold tracking-wider mb-3 font-mono">
            Suggested Follow-ups
          </h3>
          <div className="flex flex-col gap-2">
            {[
              'Expand search to surrounding sectors',
              'Show similar modus operandi in Mysore',
              'Cross-reference with KA-01 vehicle sightings'
            ].map((text, idx) => (
              <button
                key={idx}
                onClick={() => handleSendMessage(text)}
                className="text-left px-3 py-2 text-[12px] text-on-surface-variant bg-surface-container-low border border-layout-border rounded hover:bg-surface-container hover:text-primary-fixed transition-colors cursor-pointer"
              >
                {text}
              </button>
            ))}
          </div>
        </div>
      </aside>
    </div>
  );
}
