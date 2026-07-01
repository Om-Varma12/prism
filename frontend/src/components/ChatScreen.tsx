/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { ChatMessage, Screen } from '../types';
import { 
  INITIAL_CHAT_MESSAGES, 
  CONVERSATION_HISTORY, 
  CHAT_RESPONSES, 
  MOCK_SUSPECTS 
} from '../data/mockData';
import { 
  Plus, 
  ChevronRight, 
  ChevronDown, 
  Send, 
  Mic, 
  User, 
  MapPin, 
  CornerDownRight, 
  BadgeAlert, 
  Server,
  FileText
} from 'lucide-react';

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
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };

    setMessages(prev => [...prev, userMessage]);
    setInputText('');
    setIsTyping(true);

    // AI response generation matching preset responses or mock intelligent response
    setTimeout(() => {
      const normalizedQuery = text.toLowerCase().trim();
      let matchedResponse = CHAT_RESPONSES[normalizedQuery];

      if (!matchedResponse) {
        // Generic fallback response with real-feel table data
        matchedResponse = {
          sender: 'ai',
          text: `Executing intelligence scanning for query: "${text}". No perfect pre-computed pattern match found, but standard threat analytics highlight active monitoring zones in Bengaluru South and Hubballi.`,
          tableData: [
            { firNo: 'FIR-2023-BS-1419', crimeType: 'Suspicious Activity', district: 'Bengaluru South', status: 'ACTIVE' },
            { firNo: 'FIR-2023-HC-0922', crimeType: 'Public Disturbance', district: 'Hubballi Central', status: 'INVESTIGATION' }
          ],
          sqlQuery: `SELECT * FROM general_firs WHERE incident_description LIKE "%${text}%" AND status IN ("ACTIVE", "INVESTIGATION");`,
          scannedRecords: 5120
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

      setMessages(prev => [...prev, aiMessage]);
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
        text: `Load previous inquiry: "${title}"`,
        timestamp: '08:40 AM'
      },
      {
        id: `msg-ai-hist`,
        sender: 'ai',
        text: `Loaded archived session index. Summarizing data regarding: "${title}". Real-time tactical feeds indicate historical patterns remain consistent with the current command overview.`,
        timestamp: '08:40 AM',
        tableData: [
          { firNo: 'FIR-2023-BN-0847', crimeType: 'Robbery', district: 'Bengaluru North', status: 'ACTIVE' },
          { firNo: 'FIR-2023-MW-0502', crimeType: 'House Break-in', district: 'Mysore West', status: 'ACTIVE' }
        ],
        sqlQuery: 'SELECT * FROM archive_logs WHERE session_id = ? LIMIT 10;',
        scannedRecords: 142
      }
    ]);
  };

  return (
    <div className="flex-1 flex overflow-hidden bg-[#050505] h-full">
      {/* Column 1: Historical Conversation list */}
      <aside className="w-[230px] flex-shrink-0 bg-black border-r border-white/10 flex flex-col hidden lg:flex select-none">
        <div className="p-4 border-b border-white/10">
          <button 
            onClick={handleNewConversation}
            className="w-full flex items-center justify-center gap-2 py-2.5 px-3 border border-[#00F0FF] text-[#00F0FF] bg-[#00F0FF]/5 hover:bg-[#00F0FF]/15 transition-colors text-[10px] font-black tracking-widest uppercase font-mono"
          >
            <Plus className="w-4 h-4" />
            NEW_SESSION
          </button>
        </div>

        {/* Categories of History */}
        <div className="flex-1 overflow-y-auto custom-scrollbar p-3 space-y-6">
          {['Today', 'Previous 7 Days'].map((cat) => {
            const items = CONVERSATION_HISTORY.filter(h => h.category === cat);
            return (
              <div key={cat}>
                <h3 className="text-white/40 text-[9px] uppercase font-bold tracking-[0.2em] mb-2 px-2 font-mono">
                  {cat}
                </h3>
                <ul className="space-y-1">
                  {items.map((item) => {
                    const isActive = activeHistoryId === item.id;
                    return (
                      <li key={item.id}>
                        <button
                          onClick={() => handleHistoryClick(item.id, item.title)}
                          className={`w-full text-left px-3 py-2.5 text-xs transition-all truncate block uppercase tracking-wider font-bold ${
                            isActive
                              ? 'bg-white/5 text-[#00F0FF] border-l-2 border-[#00F0FF]'
                              : 'text-white/60 hover:bg-white/5 hover:text-white'
                          }`}
                        >
                          {item.title}
                        </button>
                      </li>
                    );
                  })}
                </ul>
              </div>
            );
          })}
        </div>
      </aside>

      {/* Column 2: Active chat workspace */}
      <section className="flex-1 flex flex-col relative bg-[#050505] min-w-0">
        {/* Mobile Header block */}
        <header className="lg:hidden h-14 border-b border-white/10 flex items-center px-4 justify-between bg-black">
          <div className="font-mono text-xs font-black text-white uppercase tracking-[0.2em]">
            Intelligence Chat
          </div>
          <button 
            onClick={handleNewConversation}
            className="text-[10px] uppercase font-bold border border-[#00F0FF] px-2.5 py-1 text-[#00F0FF] font-mono"
          >
            New Session
          </button>
        </header>

        {/* Active Messages Feed */}
        <div 
          ref={scrollContainerRef}
          className="flex-1 overflow-y-auto custom-scrollbar p-6 space-y-8 pb-32"
        >
          <AnimatePresence initial={false}>
            {messages.map((msg) => (
              <motion.div 
                key={msg.id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3 }}
                className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div className={`max-w-[85%] lg:max-w-[75%] p-4 leading-relaxed text-xs font-mono border ${
                  msg.sender === 'user'
                    ? 'bg-[#00F0FF] text-black border-[#00F0FF] font-bold'
                    : 'bg-black border-white/10 text-white shadow-xl'
                }`}>
                  {/* Timestamp header */}
                  <div className={`flex items-center gap-1.5 mb-2 text-[9px] font-bold tracking-[0.1em] ${
                    msg.sender === 'user' ? 'text-black/60' : 'text-white/40'
                  } select-none`}>
                    <span>{msg.sender === 'user' ? 'OFFICER' : 'PRISM CORE // COGNITIVE'}</span>
                    <span>•</span>
                    <span>{msg.timestamp}</span>
                  </div>

                  {/* Text statement */}
                  <p className="whitespace-pre-wrap font-sans text-sm tracking-wide leading-relaxed">{msg.text}</p>

                  {/* Embedded highly detailed table list */}
                  {msg.tableData && msg.tableData.length > 0 && (
                    <div className="border border-white/10 overflow-hidden mt-4 bg-black">
                      <table className="w-full text-left text-xs font-mono">
                        <thead className="bg-white/5 border-b border-white/10 text-white/70">
                          <tr>
                            <th className="py-2.5 px-3 font-bold tracking-wider">FIR NO</th>
                            <th className="py-2.5 px-3 font-bold tracking-wider">CRIME TYPE</th>
                            <th className="py-2.5 px-3 font-bold tracking-wider">DISTRICT</th>
                            <th className="py-2.5 px-3 font-bold tracking-wider text-right">STATUS</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-white/5 text-white/90">
                          {msg.tableData.map((row, idx) => (
                            <tr key={idx} className="hover:bg-white/5 transition-colors">
                              <td className="py-2.5 px-3 font-bold text-[#00F0FF]">
                                {row.firNo}
                              </td>
                              <td className="py-2.5 px-3">{row.crimeType}</td>
                              <td className="py-2.5 px-3 text-white/50">{row.district}</td>
                              <td className="py-2.5 px-3 text-right">
                                <span className={`inline-block px-1.5 py-0.5 text-[9px] font-black border tracking-widest ${
                                  row.status === 'ACTIVE'
                                    ? 'border-[#ff9f1a] text-[#ff9f1a]'
                                    : row.status === 'INVESTIGATION'
                                    ? 'border-white/30 text-white/50'
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

                  {/* Collapsible Action sections (SQL, scanned documents) */}
                  {msg.sqlQuery && (
                    <div className="mt-4 space-y-1.5 border-t border-white/10 pt-3">
                      {/* SQL Toggle */}
                      <div>
                        <button 
                          onClick={() => setOpenSqlQueryId(openSqlQueryId === msg.id ? null : msg.id)}
                          className="flex items-center gap-1.5 text-white/40 hover:text-white font-mono text-[10px] uppercase font-bold tracking-wider transition-colors"
                        >
                          {openSqlQueryId === msg.id ? (
                            <ChevronDown className="w-3.5 h-3.5 text-[#00F0FF]" />
                          ) : (
                            <ChevronRight className="w-3.5 h-3.5 text-white/40" />
                          )}
                          <span>View SQL Query</span>
                        </button>
                        
                        {openSqlQueryId === msg.id && (
                          <motion.div 
                            initial={{ height: 0, opacity: 0 }}
                            animate={{ height: 'auto', opacity: 1 }}
                            className="bg-black border border-white/10 p-3 text-[11px] font-mono text-green-400 overflow-x-auto whitespace-pre mt-1.5"
                          >
                            <code>{msg.sqlQuery}</code>
                          </motion.div>
                        )}
                      </div>

                      {/* Scanned Database Records */}
                      {msg.scannedRecords && (
                        <div>
                          <button 
                            onClick={() => setOpenSourcesId(openSourcesId === msg.id ? null : msg.id)}
                            className="flex items-center gap-1.5 text-white/40 hover:text-white font-mono text-[10px] uppercase font-bold tracking-wider transition-colors"
                          >
                            {openSourcesId === msg.id ? (
                              <ChevronDown className="w-3.5 h-3.5 text-[#00F0FF]" />
                            ) : (
                              <ChevronRight className="w-3.5 h-3.5 text-white/40" />
                            )}
                            <span>Data Sources ({msg.scannedRecords} records scanned)</span>
                          </button>

                          {openSourcesId === msg.id && (
                            <motion.div 
                              initial={{ height: 0, opacity: 0 }}
                              animate={{ height: 'auto', opacity: 1 }}
                              className="text-[10px] font-mono text-white/40 pl-5 mt-1.5 space-y-1"
                            >
                              <div className="flex items-center gap-1.5">
                                <Server className="w-3 h-3 text-[#00F0FF]" />
                                <span>ksp_state_central_db.archive_fir (Index: OPTIMIZED)</span>
                              </div>
                              <div className="flex items-center gap-1.5">
                                <FileText className="w-3 h-3 text-[#00F0FF]" />
                                <span>nlp_extracted_pattern_manifest_2026.json</span>
                              </div>
                            </motion.div>
                          )}
                        </div>
                      )}
                    </div>
                  )}

                </div>
              </motion.div>
            ))}
          </AnimatePresence>

          {isTyping && (
            <div className="flex justify-start">
              <div className="bg-black border border-white/10 text-white/60 px-4 py-3 text-[10px] font-mono tracking-wider flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-[#00F0FF] animate-ping"></span>
                <span>PRISM CORE GENERATING THREAT METRICS...</span>
              </div>
            </div>
          )}
        </div>

        {/* Input Text Form Area */}
        <div className="absolute bottom-0 left-0 w-full p-4 bg-black border-t border-white/10 z-20">
          <form 
            onSubmit={(e) => { e.preventDefault(); handleSendMessage(inputText); }}
            className="max-w-4xl mx-auto relative flex items-center"
          >
            <input 
              type="text"
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              placeholder="Ask about FIRs, accused, locations, or patterns..."
              className="w-full bg-black border border-white/10 py-3.5 pl-4 pr-24 text-sm text-white placeholder-white/20 outline-none focus:border-[#00F0FF] focus:ring-1 focus:ring-[#00F0FF] transition-all font-mono"
            />
            <div className="absolute right-2.5 flex items-center gap-1.5">
              <button 
                type="button"
                onClick={() => setInputText('Robbery cases in Yelahanka')}
                title="Voice Input simulation"
                className="p-1.5 text-white/30 hover:text-[#00F0FF] transition-colors"
              >
                <Mic className="w-4 h-4" />
              </button>
              <button 
                type="submit"
                className="p-1.5 bg-[#00F0FF] text-black hover:bg-white transition-colors"
              >
                <Send className="w-4 h-4" />
              </button>
            </div>
          </form>
        </div>
      </section>

      {/* Column 3: Context and entities list */}
      <aside className="w-[270px] flex-shrink-0 bg-black border-l border-white/10 hidden xl:flex flex-col overflow-y-auto custom-scrollbar p-4 space-y-6 select-none">
        {/* Mentioned Entities section */}
        <div>
          <h3 className="text-white/40 text-[9px] uppercase font-bold tracking-[0.2em] mb-3 font-mono">
            Mentioned Entities
          </h3>
          
          <div className="space-y-3">
            {/* Suspect Suresh Hegde */}
            <div 
              onClick={() => onNavigate(Screen.NETWORK)}
              className="border border-white/10 p-3.5 bg-[#050505] hover:border-[#00F0FF]/50 transition-colors cursor-pointer group"
            >
              <div className="flex justify-between items-start mb-1">
                <div className="flex items-center gap-1.5 text-white">
                  <User className="w-4 h-4 text-white/30 group-hover:text-[#00F0FF]" />
                  <span className="text-xs uppercase font-bold tracking-wider group-hover:text-white transition-colors">
                    Suresh Hegde
                  </span>
                </div>
              </div>
              <div className="text-[10px] tracking-wide text-white/40 font-mono">Accused Person</div>
              
              <div className="flex items-center justify-between mt-3 pt-3 border-t border-white/10 text-[9px] font-mono">
                <span className="text-white/50">6 active cases</span>
                <span className="px-1.5 py-0.5 border border-[#ff4d4d] text-[#ff4d4d] text-[8px] font-black">
                  HIGH-RISK
                </span>
              </div>
            </div>

            {/* Location PS */}
            <div className="border border-white/10 p-3.5 bg-[#050505] hover:border-[#00F0FF]/50 transition-colors cursor-pointer group">
              <div className="flex justify-between items-start mb-1">
                <div className="flex items-center gap-1.5 text-white">
                  <MapPin className="w-4 h-4 text-white/30 group-hover:text-[#00F0FF]" />
                  <span className="text-xs uppercase font-bold tracking-wider group-hover:text-white transition-colors">
                    Yelahanka PS
                  </span>
                </div>
              </div>
              <div className="text-[10px] tracking-wide text-white/40 font-mono">Location Node</div>
              
              <div className="flex items-center justify-between mt-3 pt-3 border-t border-white/10 text-[9px] font-mono">
                <span className="text-white/50">12 incidents / 24h</span>
                <span className="text-[#00F0FF] group-hover:translate-x-0.5 transition-transform flex items-center font-bold">
                  MAP
                  <CornerDownRight className="w-2.5 h-2.5 ml-0.5" />
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Suggested Queries Follow-ups */}
        <div>
          <h3 className="text-white/40 text-[9px] uppercase font-bold tracking-[0.2em] mb-3 font-mono">
            Suggested Follow-ups
          </h3>
          
          <div className="flex flex-col gap-2">
            {[
              { text: 'Expand search to surrounding sectors', query: 'expand search to surrounding sectors' },
              { text: 'Show similar modus operandi in Mysore', query: 'show similar modus operandi in Mysore' },
              { text: 'Cross-reference with KA-01 vehicle sightings', query: 'cross-reference with KA-01 vehicle sightings' }
            ].map((item, idx) => (
              <button
                key={idx}
                onClick={() => handleSendMessage(item.query)}
                className="text-left px-3.5 py-2.5 text-xs text-white/70 bg-white/5 border border-white/10 hover:bg-[#00F0FF] hover:text-black hover:border-[#00F0FF] transition-all font-mono font-bold uppercase tracking-wider"
              >
                {item.text}
              </button>
            ))}
          </div>
        </div>
      </aside>
    </div>
  );
}
