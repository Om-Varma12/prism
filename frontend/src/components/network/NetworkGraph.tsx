/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState, useRef } from 'react';
import { NetworkGraphNode, NetworkGraphEdge } from '../../types/network';

interface NetworkGraphProps {
  nodes: NetworkGraphNode[];
  edges: NetworkGraphEdge[];
  selectedNodeId?: string | null;
  onNodeClick?: (nodeId: string) => void;
}

export function NetworkGraph({ nodes, edges, selectedNodeId, onNodeClick }: NetworkGraphProps) {
  const svgRef = useRef<SVGSVGElement>(null);
  const [hoveredEdge, setHoveredEdge] = useState<NetworkGraphEdge | null>(null);
  const [transform, setTransform] = useState({ x: 0, y: 0, scale: 1 });
  const [isDragging, setIsDragging] = useState(false);
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 });

  // Calculate node positions using simple force-directed layout simulation
  const nodePositions = React.useMemo(() => {
    const positions: Record<string, { x: number; y: number }> = {};
    
    // Initialize positions in a circle
    const centerX = 400;
    const centerY = 300;
    const radius = 200;
    
    nodes.forEach((node, index) => {
      const angle = (index / nodes.length) * 2 * Math.PI;
      positions[node.id] = {
        x: centerX + radius * Math.cos(angle),
        y: centerY + radius * Math.sin(angle),
      };
    });
    
    // Simple force simulation (run for a few iterations)
    for (let iter = 0; iter < 50; iter++) {
      // Repulsion between nodes
      nodes.forEach((node1, i) => {
        nodes.forEach((node2, j) => {
          if (i >= j) return;
          const pos1 = positions[node1.id];
          const pos2 = positions[node2.id];
          if (!pos1 || !pos2) return;
          const dx = pos2.x - pos1.x;
          const dy = pos2.y - pos1.y;
          const dist = Math.sqrt(dx * dx + dy * dy) || 1;
          const force = 500 / (dist * dist);
          const fx = (dx / dist) * force;
          const fy = (dy / dist) * force;
          pos1.x -= fx;
          pos1.y -= fy;
          pos2.x += fx;
          pos2.y += fy;
        });
      });

      
      // Attraction along edges
      edges.forEach(edge => {
        const pos1 = positions[edge.source];
        const pos2 = positions[edge.target];
        if (!pos1 || !pos2) return;
        const dx = pos2.x - pos1.x;
        const dy = pos2.y - pos1.y;
        const dist = Math.sqrt(dx * dx + dy * dy) || 1;
        const force = (dist - 100) * 0.01;
        const fx = (dx / dist) * force;
        const fy = (dy / dist) * force;
        pos1.x += fx;
        pos1.y += fy;
        pos2.x -= fx;
        pos2.y -= fy;
      });
      
      // Center gravity
      nodes.forEach(node => {
        const pos = positions[node.id];
        const dx = centerX - pos.x;
        const dy = centerY - pos.y;
        pos.x += dx * 0.01;
        pos.y += dy * 0.01;
      });
    }
    
    return positions;
  }, [nodes, edges]);

  // Pan and zoom handlers
  const handleMouseDown = (e: React.MouseEvent) => {
    if (e.button === 0) {
      setIsDragging(true);
      setDragStart({ x: e.clientX - transform.x, y: e.clientY - transform.y });
    }
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (isDragging) {
      setTransform({
        x: e.clientX - dragStart.x,
        y: e.clientY - dragStart.y,
        scale: transform.scale,
      });
    }
  };

  const handleMouseUp = () => {
    setIsDragging(false);
  };

  const handleWheel = (e: React.WheelEvent) => {
    e.preventDefault();
    const zoomFactor = e.deltaY > 0 ? 0.9 : 1.1;
    const newScale = Math.max(0.1, Math.min(5, transform.scale * zoomFactor));
    setTransform({ ...transform, scale: newScale });
  };

  const handleNodeClick = (nodeId: string) => {
    if (onNodeClick) {
      onNodeClick(nodeId);
    }
  };

  // Get connected node IDs for highlighting
  const getConnectedNodeIds = (nodeId: string): Set<string> => {
    const connected = new Set<string>();
    edges.forEach(edge => {
      if (edge.source === nodeId) connected.add(edge.target);
      if (edge.target === nodeId) connected.add(edge.source);
    });
    return connected;
  };

  const connectedNodeIds = selectedNodeId ? getConnectedNodeIds(selectedNodeId) : new Set();

  return (
    <div className="w-full h-full relative overflow-hidden bg-[#050608]">
      <svg
        ref={svgRef}
        className="w-full h-full cursor-grab"
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}
        onWheel={handleWheel}
        style={{ cursor: isDragging ? 'grabbing' : 'grab' }}
      >
        <g transform={`translate(${transform.x}, ${transform.y}) scale(${transform.scale})`}>
          {/* Render edges */}
          {edges.map((edge, index) => {
            const sourcePos = nodePositions[edge.source];
            const targetPos = nodePositions[edge.target];
            if (!sourcePos || !targetPos) return null;
            
            const isConnectedToSelected = selectedNodeId && 
              (edge.source === selectedNodeId || edge.target === selectedNodeId);
            
            return (
              <line
                key={index}
                x1={sourcePos.x}
                y1={sourcePos.y}
                x2={targetPos.x}
                y2={targetPos.y}
                stroke={edge.color}
                strokeWidth={edge.thickness}
                strokeOpacity={isConnectedToSelected ? 1 : 0.3}
                onMouseEnter={() => setHoveredEdge(edge)}
                onMouseLeave={() => setHoveredEdge(null)}
              />
            );
          })}
          
          {/* Render nodes */}
          {nodes.map((node) => {
            const pos = nodePositions[node.id];
            if (!pos) return null;
            
            const isSelected = node.id === selectedNodeId;
            const isConnected = connectedNodeIds.has(node.id);
            const isDimmed = selectedNodeId && !isSelected && !isConnected;
            
            return (
              <g
                key={node.id}
                onClick={(e) => {
                  e.stopPropagation();
                  handleNodeClick(node.id);
                }}
                style={{ cursor: 'pointer' }}
              >
                {/* Node circle */}
                <circle
                  cx={pos.x}
                  cy={pos.y}
                  r={node.size}
                  fill={node.color}
                  stroke={isSelected ? '#fff' : 'none'}
                  strokeWidth={isSelected ? 2 : 0}
                  opacity={isDimmed ? 0.3 : 1}
                />
                
                {/* Node label */}
                <text
                  x={pos.x}
                  y={pos.y + node.size + 15}
                  textAnchor="middle"
                  fill="#fff"
                  fontSize="10"
                  opacity={isDimmed ? 0.3 : 1}
                >
                  {node.label}
                </text>
              </g>
            );
          })}
        </g>
      </svg>
      
      {/* Edge tooltip */}
      {hoveredEdge && (
        <div className="absolute top-4 left-4 bg-[#111318] border border-[#252830] px-3 py-2 rounded text-xs text-on-surface pointer-events-none">
          <div>Strength: {hoveredEdge.strength}</div>
          <div>Incidences: {hoveredEdge.incidents.length}</div>
        </div>
      )}
      
      {/* Zoom controls */}
      <div className="absolute bottom-4 right-4 flex flex-col gap-2">
        <button
          onClick={() => setTransform({ ...transform, scale: Math.min(5, transform.scale * 1.2) })}
          className="bg-[#111318] border border-[#252830] w-8 h-8 rounded text-on-surface hover:bg-[#1A1D24]"
        >
          +
        </button>
        <button
          onClick={() => setTransform({ ...transform, scale: Math.max(0.1, transform.scale / 1.2) })}
          className="bg-[#111318] border border-[#252830] w-8 h-8 rounded text-on-surface hover:bg-[#1A1D24]"
        >
          -
        </button>
        <button
          onClick={() => setTransform({ x: 0, y: 0, scale: 1 })}
          className="bg-[#111318] border border-[#252830] w-8 h-8 rounded text-on-surface hover:bg-[#1A1D24]"
        >
          ⟲
        </button>
      </div>
    </div>
  );
}
