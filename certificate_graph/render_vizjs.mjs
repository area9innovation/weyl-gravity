#!/usr/bin/env node

// Reproducible fallback renderer for environments without a Graphviz binary.
// The module argument points to @viz-js/viz's ESM bundle; generated files are
// still Graphviz output, produced by the WebAssembly build of Graphviz.

import { readFileSync, writeFileSync } from "node:fs";
import { pathToFileURL } from "node:url";

const [modulePath, inputPath, format, outputPath] = process.argv.slice(2);
if (!modulePath || !inputPath || !format || !outputPath) {
  throw new Error(
    "usage: render_vizjs.mjs <viz.js> <input.dot> <format> <output>",
  );
}

const { instance } = await import(pathToFileURL(modulePath));
const viz = await instance();
const source = readFileSync(inputPath, "utf8");
writeFileSync(outputPath, viz.renderString(source, { format }));
