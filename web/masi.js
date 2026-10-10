// © 1993–2026 Abhishek Choudhary. All rights reserved. AyeAI.
// SPDX-License-Identifier: GPL-3.0-or-later
// Browser tools. A token stays in this page. It is not written to a file by this script.

export async function saltedHash(identifier, salt) {
  const key = await crypto.subtle.importKey(
    "raw", new TextEncoder().encode(salt), {name: "HMAC", hash: "SHA-256"}, false, ["sign"]
  );
  const mac = await crypto.subtle.sign("HMAC", key, new TextEncoder().encode(identifier));
  return [...new Uint8Array(mac)].map(b => b.toString(16).padStart(2, "0")).join("");
}

export function fold(events, matterId) {
  const state = {matter_id: matterId, dimensions: {}, assessments: [], facts: {}};
  for (const event of events) {
    if (event.matter_id !== matterId) continue;
    state.dimensions[event.dimension || "venue"] = event.new_state;
    if (event.event_type === "assessment") state.assessments.push(event.evidence || {});
    Object.assign(state.facts, event.evidence || {});
  }
  return state;
}

export function gateG3(state, publicMint) {
  if (publicMint && state.facts.patent_unfiled && !state.facts.defensive_publication) {
    return "G3: unfiled patent blocks a public mint";
  }
  return null;
}

export function holdToken(value) {
  return {loaded: Boolean(value), stored_in_repo: false};
}
