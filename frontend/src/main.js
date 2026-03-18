import { jsx as _jsx } from "react/jsx-runtime";
import React from "react";
import { createRoot } from "react-dom/client";
import { App } from "./App";
import "./styles.css";
const rootEl = document.getElementById("root");
if (!rootEl) {
    throw new Error("Root element not found");
}
createRoot(rootEl).render(_jsx(React.StrictMode, { children: _jsx(App, {}) }));
