/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useRef, useCallback, useEffect, useState } from 'react';
import ForceGraph2D, { ForceGraphMethods, NodeObject, LinkObject } from 'react-force-graph-2d';
import { NetworkGraphNode, NetworkGraphEdge } from '../../types/network';

// ─── Types ───────────────────────────────────────────────────────────────────

interface FGNode extends NodeObject {
  id: string;
  label: string;
  size: number;
  color: string;
  nodeData: NetworkGraphNode;
}

interface FGLink extends LinkObject {
  source: string | FGNode;
  target: string | FGNode;
  color: string;
  thickness: number;
  strength: number;
  incidents: number[];
}

interface NetworkGraphProps {
  nodes: NetworkGraphNode[];
  edges: NetworkGraphEdge[];
  selectedNodeId?: string | null;
  onNodeClick?: (nodeId: string) => void;
}

// ─── Gang cluster colour palette (Obsidian-inspired) ─────────────────────────
const CLUSTER_COLORS: Record<number, string> = {
  0:  '#7B61FF', // violet
  1:  '#FF6B6B', // coral
  2:  '#4ECDC4', // teal
  3:  '#FFE66D', // gold
  4:  '#A8FF78', // lime
  5:  '#FF8B94', // pink
  6:  '#00D2FF', // cyan
  7:  '#FF9A3C', // orange
};

const getClusterColor = (cluster: number | null | undefined): string =>
  cluster != null ? (CLUSTER_COLORS[cluster % 8] ?? '#7B61FF') : '#5A6478';

// ─── Canvas node painter (Obsidian glow style) ────────────────────────────────
function paintNode(
  node: FGNode,
  ctx: CanvasRenderingContext2D,
  globalScale: number,
  isSelected: boolean,
  isConnected: boolean,
  hasSelection: boolean,
) {
  const { x = 0, y = 0, nodeData } = node;
  // Base radius scaled inversely to globalScale so they look larger when zoomed out
  const baseRadius = Math.max(4, (node.size * 0.6) / Math.sqrt(globalScale));
  const dimmed = hasSelection && !isSelected && !isConnected;
  const color = getClusterColor(nodeData.gang_cluster);

  ctx.save();
  ctx.globalAlpha = dimmed ? 0.15 : 1;

  // ── Glow rings ─────────────────────────────────────────────
  if (!dimmed) {
    const glowLayers = isSelected ? 4 : 2;
    for (let i = glowLayers; i > 0; i--) {
      ctx.beginPath();
      ctx.arc(x, y, baseRadius + i * 4, 0, 2 * Math.PI);
      ctx.fillStyle = color;
      ctx.globalAlpha = (isSelected ? 0.12 : 0.05) / i;
      ctx.fill();
    }
    ctx.globalAlpha = dimmed ? 0.15 : 1;
  }

  // ── Core circle ────────────────────────────────────────────
  ctx.beginPath();
  ctx.arc(x, y, baseRadius, 0, 2 * Math.PI);
  ctx.fillStyle = color;
  ctx.fill();

  // ── White ring for selected ────────────────────────────────
  if (isSelected) {
    ctx.beginPath();
    ctx.arc(x, y, baseRadius + 3, 0, 2 * Math.PI);
    ctx.strokeStyle = '#ffffff';
    ctx.lineWidth = 1.5 / globalScale;
    ctx.stroke();
  }

  // ── Absconding indicator (dashed outline) ──────────────────
  if (nodeData.is_absconding && !dimmed) {
    ctx.beginPath();
    ctx.arc(x, y, baseRadius + (isSelected ? 6 : 4), 0, 2 * Math.PI);
    ctx.strokeStyle = '#FF6B6B';
    ctx.lineWidth = 1 / globalScale;
    ctx.setLineDash([2, 2]);
    ctx.stroke();
    ctx.setLineDash([]);
  }

  // ── Label — always visible, font shrinks as user zooms in ──────────
  const fontSize = Math.max(4, 10 / globalScale);
  ctx.font = `${isSelected ? '600' : '400'} ${fontSize}px Inter, sans-serif`;
  ctx.fillStyle = dimmed ? 'rgba(255,255,255,0.2)' : '#E8EAF0';
  ctx.textAlign = 'center';
  ctx.textBaseline = 'top';
  ctx.fillText(node.label, x, y + baseRadius + 3 / globalScale);

  ctx.restore();
}

// ─── Component ────────────────────────────────────────────────────────────────

export function NetworkGraph({ nodes, edges, selectedNodeId, onNodeClick }: NetworkGraphProps) {
  const fgRef = useRef<ForceGraphMethods<FGNode, FGLink> | undefined>(undefined);
  const containerRef = useRef<HTMLDivElement>(null);
  const [dimensions, setDimensions] = useState({ width: 800, height: 600 });
  const [hoveredNode, setHoveredNode] = useState<FGNode | null>(null);
  const [hoveredLink, setHoveredLink] = useState<FGLink | null>(null);

  // Measure container
  useEffect(() => {
    const el = containerRef.current;
    if (!el) return;
    const obs = new ResizeObserver(entries => {
      const { width, height } = entries[0].contentRect;
      setDimensions({ width, height });
    });
    obs.observe(el);
    setDimensions({ width: el.clientWidth, height: el.clientHeight });
    return () => obs.disconnect();
  }, []);

  // Build force-graph data from props
  const graphData = React.useMemo(() => {
    const fgNodes: FGNode[] = nodes.map(n => ({
      id: n.id,
      label: n.label,
      size: Math.max(6, Math.min(20, 6 + n.fir_count * 1.5)),
      color: getClusterColor(n.gang_cluster),
      nodeData: n,
    }));

    const nodeSet = new Set(fgNodes.map(n => n.id));

    const fgLinks: FGLink[] = edges
      .filter(e => nodeSet.has(e.source) && nodeSet.has(e.target))
      .map(e => ({
        source: e.source,
        target: e.target,
        color: e.color || '#3A3F4E',
        thickness: Math.max(0.5, e.thickness),
        strength: e.strength,
        incidents: e.incidents,
      }));

    return { nodes: fgNodes, links: fgLinks };
  }, [nodes, edges]);

  // Connected node IDs for highlight
  const connectedIds = React.useMemo<Set<string>>(() => {
    if (!selectedNodeId) return new Set();
    const s = new Set<string>();
    graphData.links.forEach(l => {
      const src = typeof l.source === 'object' ? (l.source as FGNode).id : l.source as string;
      const tgt = typeof l.target === 'object' ? (l.target as FGNode).id : l.target as string;
      if (src === selectedNodeId) s.add(tgt);
      if (tgt === selectedNodeId) s.add(src);
    });
    return s;
  }, [selectedNodeId, graphData.links]);

  // Node painter
  const nodeCanvasObject = useCallback((node: object, ctx: CanvasRenderingContext2D, globalScale: number) => {
    const n = node as FGNode;
    const isSelected = n.id === selectedNodeId;
    const isConnected = connectedIds.has(n.id);
    paintNode(n, ctx, globalScale, isSelected, isConnected, !!selectedNodeId);
  }, [selectedNodeId, connectedIds]);

  // Link painter
  const linkCanvasObject = useCallback((link: object, ctx: CanvasRenderingContext2D) => {
    const l = link as FGLink;
    const src = typeof l.source === 'object' ? l.source as FGNode : null;
    const tgt = typeof l.target === 'object' ? l.target as FGNode : null;
    if (!src || !tgt || src.x == null || src.y == null || tgt.x == null || tgt.y == null) return;

    const srcId = src.id;
    const tgtId = tgt.id;
    const isHighlighted = selectedNodeId &&
      (srcId === selectedNodeId || tgtId === selectedNodeId ||
       connectedIds.has(srcId) || connectedIds.has(tgtId));

    const alpha = selectedNodeId ? (isHighlighted ? 0.9 : 0.08) : 0.35;

    ctx.save();
    ctx.globalAlpha = alpha;
    ctx.beginPath();
    ctx.moveTo(src.x!, src.y!);
    ctx.lineTo(tgt.x!, tgt.y!);

    if (isHighlighted) {
      // Glowing link
      ctx.shadowBlur = 6;
      ctx.shadowColor = getClusterColor(src.nodeData.gang_cluster);
      ctx.strokeStyle = '#ffffff';
      ctx.lineWidth = l.thickness + 0.5;
    } else {
      ctx.strokeStyle = '#3A4560';
      ctx.lineWidth = l.thickness * 0.5;
    }
    ctx.stroke();
    ctx.restore();
  }, [selectedNodeId, connectedIds]);

  const handleNodeClick = useCallback((node: object) => {
    const n = node as FGNode;
    if (onNodeClick) onNodeClick(n.id);
    // Smoothly zoom/center on clicked node
    if (fgRef.current && n.x != null && n.y != null) {
      fgRef.current.centerAt(n.x, n.y, 600);
      fgRef.current.zoom(3, 600);
    }
  }, [onNodeClick]);

  const handleBackgroundClick = useCallback(() => {
    if (onNodeClick && selectedNodeId) onNodeClick('');
  }, [onNodeClick, selectedNodeId]);

  return (
    <div ref={containerRef} className="w-full h-full relative overflow-hidden" style={{ background: '#050608' }}>
      <ForceGraph2D<FGNode, FGLink>
        ref={fgRef}
        width={dimensions.width}
        height={dimensions.height}
        graphData={graphData}
        nodeId="id"
        nodeLabel={() => ''}
        nodeCanvasObject={nodeCanvasObject}
        nodeCanvasObjectMode={() => 'replace'}
        linkCanvasObject={linkCanvasObject}
        linkCanvasObjectMode={() => 'replace'}
        onNodeClick={handleNodeClick}
        onBackgroundClick={handleBackgroundClick}
        onNodeHover={node => setHoveredNode(node as FGNode | null)}
        onLinkHover={link => setHoveredLink(link as FGLink | null)}
        backgroundColor="#050608"
        linkDirectionalParticles={3}
        linkDirectionalParticleWidth={(link: object) => {
          const l = link as FGLink;
          const src = typeof l.source === 'object' ? (l.source as FGNode).id : l.source as string;
          const tgt = typeof l.target === 'object' ? (l.target as FGNode).id : l.target as string;
          return (selectedNodeId && (src === selectedNodeId || tgt === selectedNodeId)) ? 2 : 0;
        }}
        linkDirectionalParticleColor={() => '#ffffff'}
        linkDirectionalParticleSpeed={0.004}
        cooldownTicks={120}
        d3AlphaDecay={0.02}
        d3VelocityDecay={0.3}
        enableNodeDrag
        enableZoomInteraction
        enablePanInteraction
      />

      {/* Hovered node tooltip */}
      {hoveredNode && (
        <div
          className="absolute top-4 left-4 pointer-events-none z-10"
          style={{
            background: 'rgba(10, 12, 18, 0.92)',
            border: `1px solid ${getClusterColor(hoveredNode.nodeData.gang_cluster)}55`,
            borderRadius: 10,
            padding: '10px 14px',
            boxShadow: `0 0 20px ${getClusterColor(hoveredNode.nodeData.gang_cluster)}33`,
            minWidth: 200,
          }}
        >
          <div style={{ fontSize: 13, fontWeight: 600, color: '#E8EAF0', marginBottom: 6 }}>
            {hoveredNode.nodeData.label}
          </div>
          <div style={{ fontSize: 11, color: '#8A909E', display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '3px 12px' }}>
            <span>FIRs</span>
            <span style={{ color: '#E8EAF0' }}>{hoveredNode.nodeData.fir_count}</span>
            <span>Risk Score</span>
            <span style={{ color: hoveredNode.nodeData.risk_score > 0.7 ? '#FF6B6B' : '#4ECDC4' }}>
              {(hoveredNode.nodeData.risk_score * 100).toFixed(0)}
            </span>
            {hoveredNode.nodeData.gang_cluster != null && (
              <>
                <span>Cluster</span>
                <span style={{ color: getClusterColor(hoveredNode.nodeData.gang_cluster) }}>
                  Gang #{hoveredNode.nodeData.gang_cluster}
                </span>
              </>
            )}
            <span>Status</span>
            <span style={{ color: hoveredNode.nodeData.is_absconding ? '#FF6B6B' : '#4ECDC4' }}>
              {hoveredNode.nodeData.is_absconding ? 'Absconding' : 'Arrested'}
            </span>
            {hoveredNode.nodeData.primary_district && (
              <>
                <span>District</span>
                <span style={{ color: '#E8EAF0' }}>{hoveredNode.nodeData.primary_district}</span>
              </>
            )}
          </div>
        </div>
      )}

      {/* Hovered link tooltip */}
      {hoveredLink && !hoveredNode && (
        <div
          className="absolute top-4 left-4 pointer-events-none z-10"
          style={{
            background: 'rgba(10,12,18,0.92)',
            border: '1px solid #252830',
            borderRadius: 10,
            padding: '8px 12px',
            fontSize: 11,
            color: '#8A909E',
          }}
        >
          <span style={{ color: '#E8EAF0' }}>Shared FIRs: </span>{hoveredLink.incidents.length}
          <span style={{ marginLeft: 12, color: '#E8EAF0' }}>Strength: </span>
          {(hoveredLink.strength * 100).toFixed(0)}%
        </div>
      )}

      {/* Legend */}
      <div
        className="absolute bottom-4 left-4 z-10 pointer-events-none"
        style={{
          background: 'rgba(10,12,18,0.85)',
          border: '1px solid #1E2130',
          borderRadius: 8,
          padding: '8px 12px',
          fontSize: 10,
          color: '#5A6478',
        }}
      >
        <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
            <div style={{ width: 8, height: 8, borderRadius: '50%', background: '#7B61FF' }} />
            <span>Gang cluster node</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
            <div style={{ width: 8, height: 8, borderRadius: '50%', border: '1px dashed #FF6B6B', background: 'transparent' }} />
            <span>Absconding</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
            <div style={{ width: 12, height: 2, background: 'rgba(255,255,255,0.3)' }} />
            <span>Shared FIR link</span>
          </div>
        </div>
      </div>

      {/* Zoom controls */}
      <div className="absolute bottom-4 right-4 flex flex-col gap-2 z-10">
        {[
          { label: '+', action: () => fgRef.current?.zoom(1.4, 300) },
          { label: '−', action: () => fgRef.current?.zoom(0.7, 300) },
          { label: '⟳', action: () => { fgRef.current?.centerAt(0, 0, 400); fgRef.current?.zoom(1, 400); } },
        ].map(({ label, action }) => (
          <button
            key={label}
            onClick={action}
            style={{
              width: 32, height: 32,
              background: 'rgba(10,12,18,0.9)',
              border: '1px solid #252830',
              borderRadius: 6,
              color: '#8A909E',
              fontSize: 14,
              cursor: 'pointer',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
            }}
          >
            {label}
          </button>
        ))}
      </div>
    </div>
  );
}
