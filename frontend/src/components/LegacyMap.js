import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
/**
 * LegacyMap — "My Legacy Map" interactive visual graph of all connected
 * works, credits, collaborators, platforms, and earnings streams.
 *
 * Renders a force-directed-style node graph using SVG.
 * Supports both music and TV/Film works.
 * VIP-exclusive feature.
 */
import { useEffect, useRef, useState } from "react";
const NODE_COLORS = {
    artist: "#A855F7",
    work: "#7C3AED",
    collaborator: "#C084FC",
    platform: "#6D28D9",
    pro: "#DDD6FE",
    film: "#F59E0B",
    tvshow: "#F97316",
};
const NODE_RADIUS = {
    artist: 22,
    work: 14,
    collaborator: 11,
    platform: 13,
    pro: 11,
    film: 15,
    tvshow: 15,
};
function forceLayout(nodes, edges, w, h, iterations = 80) {
    const pos = {};
    const cx = w / 2, cy = h / 2;
    nodes.forEach((n, i) => {
        const angle = (2 * Math.PI * i) / nodes.length;
        pos[n.id] = {
            x: cx + Math.cos(angle) * (Math.min(w, h) * 0.35),
            y: cy + Math.sin(angle) * (Math.min(w, h) * 0.35),
        };
    });
    const K = 60; // spring rest length
    const repel = 3500; // repulsion constant
    const attract = 0.04; // attraction strength
    const damp = 0.85;
    const vel = {};
    nodes.forEach((n) => { vel[n.id] = { x: 0, y: 0 }; });
    for (let iter = 0; iter < iterations; iter++) {
        const force = {};
        nodes.forEach((n) => { force[n.id] = { x: 0, y: 0 }; });
        // Repulsion
        for (let i = 0; i < nodes.length; i++) {
            for (let j = i + 1; j < nodes.length; j++) {
                const a = nodes[i], b = nodes[j];
                if (!a || !b)
                    continue;
                const pa = pos[a.id], pb = pos[b.id], fa = force[a.id], fb = force[b.id];
                if (!pa || !pb || !fa || !fb)
                    continue;
                const dx = pa.x - pb.x;
                const dy = pa.y - pb.y;
                const dist = Math.max(1, Math.sqrt(dx * dx + dy * dy));
                const f = repel / (dist * dist);
                fa.x += (dx / dist) * f;
                fa.y += (dy / dist) * f;
                fb.x -= (dx / dist) * f;
                fb.y -= (dy / dist) * f;
            }
        }
        // Attraction (edges)
        edges.forEach((e) => {
            const a = pos[e.from], b = pos[e.to];
            const fa = force[e.from], fb = force[e.to];
            if (!a || !b || !fa || !fb)
                return;
            const dx = b.x - a.x, dy = b.y - a.y;
            const dist = Math.max(1, Math.sqrt(dx * dx + dy * dy));
            const f = attract * (dist - K);
            fa.x += (dx / dist) * f;
            fa.y += (dy / dist) * f;
            fb.x -= (dx / dist) * f;
            fb.y -= (dy / dist) * f;
        });
        // Gravity toward center
        nodes.forEach((n) => {
            const fn = force[n.id], pn = pos[n.id];
            if (!fn || !pn)
                return;
            fn.x += (cx - pn.x) * 0.005;
            fn.y += (cy - pn.y) * 0.005;
        });
        // Integrate
        nodes.forEach((n) => {
            const v = vel[n.id], f = force[n.id], p = pos[n.id];
            if (!v || !f || !p)
                return;
            v.x = (v.x + f.x) * damp;
            v.y = (v.y + f.y) * damp;
            p.x = Math.max(30, Math.min(w - 30, p.x + v.x));
            p.y = Math.max(30, Math.min(h - 30, p.y + v.y));
        });
    }
    return pos;
}
// ===========================================================================
// API data builder
// ===========================================================================
async function buildLegacyMapData(artistId, apiBase) {
    const nodes = [];
    const edges = [];
    const seen = new Set();
    const addNode = (n) => {
        if (!seen.has(n.id)) {
            seen.add(n.id);
            nodes.push(n);
        }
    };
    // Artist center node
    const artistNodeId = `artist-${artistId}`;
    addNode({ id: artistNodeId, label: "You", type: "artist" });
    try {
        const [worksRes, personaRes] = await Promise.all([
            fetch(`${apiBase}/artists/${artistId}/works`).catch(() => null),
            fetch(`${apiBase}/artists/${artistId}/persona`).catch(() => null),
        ]);
        // Works
        const worksData = worksRes?.ok ? await worksRes.json() : [];
        const works = Array.isArray(worksData) ? worksData : (worksData.works ?? []);
        for (const w of works.slice(0, 30)) {
            const wid = `work-${w.id}`;
            const wtype = w.work_type === "film" ? "film" : w.work_type === "tv" ? "tvshow" : "work";
            addNode({ id: wid, label: w.title?.slice(0, 20) ?? "Work", type: wtype, detail: w.isrc });
            edges.push({ from: artistNodeId, to: wid });
            if (w.publisher) {
                const pid = `pro-${w.publisher}`;
                addNode({ id: pid, label: w.publisher.slice(0, 16), type: "pro" });
                edges.push({ from: wid, to: pid, label: "Published by" });
            }
        }
        // Persona collaborators
        if (personaRes?.ok) {
            const persona = await personaRes.json();
            for (const collab of (persona.collaborators ?? []).slice(0, 8)) {
                const cid = `collab-${collab}`;
                addNode({ id: cid, label: String(collab).slice(0, 18), type: "collaborator" });
                edges.push({ from: artistNodeId, to: cid, label: "Collaborated" });
            }
        }
    }
    catch {
        /* fail silently, show partial graph */
    }
    // Platforms (static for now)
    for (const plat of ["Spotify", "Apple Music", "YouTube"]) {
        const pid = `plat-${plat}`;
        addNode({ id: pid, label: plat, type: "platform" });
        edges.push({ from: artistNodeId, to: pid, label: "Distributed" });
    }
    return { nodes, edges };
}
// ===========================================================================
// Component
// ===========================================================================
export function LegacyMap({ artistId, apiBase = "", width = 560, height = 400 }) {
    const [data, setData] = useState(null);
    const [pos, setPos] = useState({});
    const [selected, setSelected] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");
    const svgRef = useRef(null);
    useEffect(() => {
        let mounted = true;
        buildLegacyMapData(artistId, apiBase)
            .then((d) => {
            if (!mounted)
                return;
            setData(d);
            setPos(forceLayout(d.nodes, d.edges, width, height));
            setLoading(false);
        })
            .catch(() => {
            if (mounted) {
                setError("Could not load Legacy Map.");
                setLoading(false);
            }
        });
        return () => { mounted = false; };
    }, [artistId, apiBase, width, height]);
    if (loading) {
        return (_jsx("div", { className: "legacy-map-container flex items-center justify-center", style: { width, height }, children: _jsx("p", { className: "text-purple-400 text-sm animate-pulse", children: "Building your Legacy Map\u2026" }) }));
    }
    if (error || !data) {
        return (_jsx("div", { className: "legacy-map-container flex items-center justify-center", style: { width, height }, children: _jsx("p", { className: "text-red-400 text-sm", children: error || "No data." }) }));
    }
    const selectedNode = selected ? data.nodes.find((n) => n.id === selected) : null;
    return (_jsxs("div", { className: "legacy-map-outer", children: [_jsxs("div", { className: "flex items-center gap-2 px-4 py-3 border-b border-purple-800/30", children: [_jsx("span", { className: "text-lg", children: "\uD83D\uDDFA" }), _jsxs("div", { children: [_jsx("h3", { className: "text-purple-100 text-sm font-semibold", children: "My Legacy Map" }), _jsxs("p", { className: "text-purple-500 text-xs", children: [data.nodes.length, " nodes \u00B7 ", data.edges.length, " connections"] })] }), selectedNode && (_jsxs("div", { className: "ml-auto text-right", children: [_jsx("p", { className: "text-purple-300 text-xs font-medium", children: selectedNode.label }), _jsx("p", { className: "text-purple-500 text-xs capitalize", children: selectedNode.type })] }))] }), _jsxs("svg", { ref: svgRef, width: width, height: height, viewBox: `0 0 ${width} ${height}`, className: "block", style: { background: "transparent", cursor: "default" }, children: [_jsxs("defs", { children: [_jsxs("filter", { id: "glow", children: [_jsx("feGaussianBlur", { stdDeviation: "2.5", result: "coloredBlur" }), _jsxs("feMerge", { children: [_jsx("feMergeNode", { in: "coloredBlur" }), _jsx("feMergeNode", { in: "SourceGraphic" })] })] }), _jsxs("radialGradient", { id: "bgGrad", cx: "50%", cy: "50%", r: "50%", children: [_jsx("stop", { offset: "0%", stopColor: "rgba(168,85,247,0.04)" }), _jsx("stop", { offset: "100%", stopColor: "rgba(0,0,0,0)" })] })] }), _jsx("rect", { width: width, height: height, fill: "url(#bgGrad)" }), data.edges.map((e, i) => {
                        const a = pos[e.from], b = pos[e.to];
                        if (!a || !b)
                            return null;
                        return (_jsx("line", { x1: a.x, y1: a.y, x2: b.x, y2: b.y, stroke: "rgba(168,85,247,0.25)", strokeWidth: 1.5 }, i));
                    }), data.nodes.map((n) => {
                        const p = pos[n.id];
                        if (!p)
                            return null;
                        const r = NODE_RADIUS[n.type] ?? 12;
                        const c = NODE_COLORS[n.type] ?? "#A855F7";
                        const isSelected = selected === n.id;
                        return (_jsxs("g", { transform: `translate(${p.x},${p.y})`, className: "cursor-pointer", onClick: () => setSelected(isSelected ? null : n.id), children: [isSelected && (_jsx("circle", { r: r + 6, fill: "none", stroke: c, strokeWidth: 1.5, opacity: 0.5 })), _jsx("circle", { r: r, fill: `${c}22`, stroke: c, strokeWidth: isSelected ? 2 : 1.2, filter: isSelected ? "url(#glow)" : undefined }), _jsx("text", { textAnchor: "middle", dy: "0.35em", fontSize: n.type === "artist" ? 9 : 7, fill: n.type === "artist" ? "#E9D5FF" : "#C4B5FD", className: "select-none", children: n.label.length > 12 ? n.label.slice(0, 11) + "…" : n.label })] }, n.id));
                    })] }), _jsx("div", { className: "flex flex-wrap gap-3 px-4 py-2 border-t border-purple-800/30", children: Object.entries(NODE_COLORS).map(([type, color]) => (_jsxs("div", { className: "flex items-center gap-1 text-xs text-purple-400", children: [_jsx("div", { className: "w-2.5 h-2.5 rounded-full", style: { background: color } }), _jsx("span", { className: "capitalize", children: type })] }, type))) }), _jsx("style", { children: `
        .legacy-map-outer {
          background: linear-gradient(160deg, rgba(10,3,25,0.98) 0%, rgba(20,6,45,0.98) 100%);
          border: 1px solid rgba(168,85,247,0.20);
          border-radius: 14px;
          overflow: hidden;
          width: fit-content;
        }
        .legacy-map-container {
          background: rgba(10,3,25,0.98);
          border: 1px solid rgba(168,85,247,0.20);
          border-radius: 14px;
        }
      ` })] }));
}
