#!/usr/bin/env python3
"""
Levenshtein Distance Visual Illustrator
=======================================
An educational, animated visualizer that SHOWS, rather than tells,
how the Levenshtein Distance dynamic programming matrix is calculated
and how the optimal edit path is reconstructed.

Compatible with Python 3.7+ (standard library only).
Designed to accompany the CS361 Levenshtein Microservice.
"""

import sys
import os
import time
import argparse
import html
from typing import List, Tuple, Dict, Any, Optional


# ANSI Color Codes for Terminal Output
class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    UNDERLINE = "\033[4m"
    
    # Foreground
    FG_BLACK = "\033[30m"
    FG_RED = "\033[31m"
    FG_GREEN = "\033[32m"
    FG_YELLOW = "\033[33m"
    FG_BLUE = "\033[34m"
    FG_MAGENTA = "\033[35m"
    FG_CYAN = "\033[36m"
    FG_WHITE = "\033[37m"
    
    # Bright Foreground
    FG_BRIGHT_BLACK = "\033[90m"
    FG_BRIGHT_RED = "\033[91m"
    FG_BRIGHT_GREEN = "\033[92m"
    FG_BRIGHT_YELLOW = "\033[93m"
    FG_BRIGHT_BLUE = "\033[94m"
    FG_BRIGHT_MAGENTA = "\033[95m"
    FG_BRIGHT_CYAN = "\033[96m"
    FG_BRIGHT_WHITE = "\033[97m"
    
    # Background
    BG_BLACK = "\033[40m"
    BG_BLUE = "\033[44m"
    BG_CYAN = "\033[46m"
    BG_YELLOW = "\033[43m"
    BG_GREEN = "\033[42m"
    BG_MAGENTA = "\033[45m"
    BG_WHITE = "\033[47m"


def clear_screen():
    """Clear terminal screen and move cursor to home position."""
    sys.stdout.write("\033[2J\033[H")
    sys.stdout.flush()


def recommend_forgiveness(correct_answer: str) -> int:
    """Calculates forgiveness threshold matching main.py logic."""
    l = len(correct_answer)
    return l - (l * 8 // 10 + 1)


class LevenshteinStep:
    """Represents a single step in the DP matrix computation or traceback."""
    def __init__(self, step_type: str, i: int, j: int, **kwargs):
        self.step_type = step_type  # 'base', 'cell', 'traceback', 'done'
        self.i = i
        self.j = j
        self.details = kwargs


def compute_levenshtein_steps(s1: str, s2: str) -> Tuple[List[List[int]], List[LevenshteinStep], List[Tuple[int, int, str]]]:
    """
    Computes Levenshtein matrix and records every animation step and traceback path.
    Matches the exact recurrence in main.py:
        cache[i][j] = min(cache[i-1][j] + 1, cache[i][j-1] + 1, cache[i-1][j-1] + cost)
    """
    m, n = len(s1), len(s2)
    cache = [[-1 for _ in range(n + 1)] for _ in range(m + 1)]
    steps: List[LevenshteinStep] = []

    # Step-by-step matrix fill
    for i in range(m + 1):
        for j in range(n + 1):
            if min(i, j) == 0:
                val = max(i, j)
                cache[i][j] = val
                reason = "Empty string prefix base case"
                steps.append(LevenshteinStep('base', i, j, value=val, reason=reason))
            else:
                top_val = cache[i - 1][j]
                left_val = cache[i][j - 1]
                diag_val = cache[i - 1][j - 1]

                char1 = s1[i - 1]
                char2 = s2[j - 1]
                match = (char1 == char2)
                sub_cost = 0 if match else 1

                candidate_a = top_val + 1   # Deletion
                candidate_b = left_val + 1  # Insertion
                candidate_c = diag_val + sub_cost  # Match or Substitution

                min_val = min(candidate_a, candidate_b, candidate_c)
                cache[i][j] = min_val

                chosen = []
                if min_val == candidate_c:
                    chosen.append("DIAGONAL (" + ("MATCH +0" if match else "SUBSTITUTE +1") + ")")
                if min_val == candidate_a:
                    chosen.append("TOP (DELETE +1)")
                if min_val == candidate_b:
                    chosen.append("LEFT (INSERT +1)")

                steps.append(LevenshteinStep(
                    'cell', i, j,
                    char1=char1, char2=char2, match=match,
                    top_val=top_val, cand_a=candidate_a,
                    left_val=left_val, cand_b=candidate_b,
                    diag_val=diag_val, sub_cost=sub_cost, cand_c=candidate_c,
                    winner=min_val, chosen=", ".join(chosen)
                ))

    # Traceback optimal path
    traceback_path: List[Tuple[int, int, str]] = []
    curr_i, curr_j = m, n

    while curr_i > 0 or curr_j > 0:
        if curr_i > 0 and curr_j > 0:
            char1 = s1[curr_i - 1]
            char2 = s2[curr_j - 1]
            cost = 0 if char1 == char2 else 1
            if cache[curr_i][curr_j] == cache[curr_i - 1][curr_j - 1] + cost:
                op = "MATCH" if cost == 0 else f"SUBSTITUTE '{char1}' -> '{char2}'"
                traceback_path.append((curr_i, curr_j, op))
                curr_i -= 1
                curr_j -= 1
                continue
            elif cache[curr_i][curr_j] == cache[curr_i - 1][curr_j] + 1:
                op = f"DELETE '{char1}'"
                traceback_path.append((curr_i, curr_j, op))
                curr_i -= 1
                continue
            else:
                op = f"INSERT '{char2}'"
                traceback_path.append((curr_i, curr_j, op))
                curr_j -= 1
                continue
        elif curr_i > 0:
            char1 = s1[curr_i - 1]
            op = f"DELETE '{char1}'"
            traceback_path.append((curr_i, curr_j, op))
            curr_i -= 1
        else:
            char2 = s2[curr_j - 1]
            op = f"INSERT '{char2}'"
            traceback_path.append((curr_i, curr_j, op))
            curr_j -= 1

    traceback_path.append((0, 0, "START"))
    traceback_path.reverse()

    return cache, steps, traceback_path


def render_terminal_frame(
    s1: str, s2: str,
    partial_cache: List[List[Optional[int]]],
    current_step: LevenshteinStep,
    step_num: int, total_steps: int,
    trace_set: set = None
) -> str:
    """Renders a single frame of terminal animation with rich ANSI formatting."""
    m, n = len(s1), len(s2)
    lines = []

    C = Colors
    lines.append(f"{C.BOLD}{C.FG_BRIGHT_CYAN}=== LEVENSHTEIN DISTANCE VISUAL ILLUSTRATOR ==={C.RESET}")
    lines.append(f"{C.DIM}Comparing:{C.RESET} '{C.BOLD}{C.FG_BRIGHT_YELLOW}{s1}{C.RESET}' (source) -> '{C.BOLD}{C.FG_BRIGHT_GREEN}{s2}{C.RESET}' (target)")
    lines.append(f"{C.DIM}Progress: Step {step_num}/{total_steps}{C.RESET}")
    lines.append("")

    # Build Header Row (Columns = s2)
    col_header = "       ε  "
    for char in s2:
        col_header += f" {C.BOLD}{C.FG_BRIGHT_GREEN}{char}{C.RESET}  "
    lines.append(col_header)

    border = "    +" + "----+" * (n + 1)
    lines.append(f"{C.DIM}{border}{C.RESET}")

    # Build Table Rows (Rows = s1)
    for i in range(m + 1):
        row_char = "ε" if i == 0 else s1[i - 1]
        row_str = f" {C.BOLD}{C.FG_BRIGHT_YELLOW}{row_char}{C.RESET}  |"
        for j in range(n + 1):
            val = partial_cache[i][j]
            is_active = (i == current_step.i and j == current_step.j)
            is_top = (current_step.step_type == 'cell' and i == current_step.i - 1 and j == current_step.j)
            is_left = (current_step.step_type == 'cell' and i == current_step.i and j == current_step.j - 1)
            is_diag = (current_step.step_type == 'cell' and i == current_step.i - 1 and j == current_step.j - 1)
            is_trace = trace_set and (i, j) in trace_set

            if val is None or val == -1:
                cell_text = f" {C.DIM}·{C.RESET}  |"
            else:
                num_str = f"{val:2d}"
                if is_active:
                    cell_text = f"{C.BG_YELLOW}{C.FG_BLACK}{C.BOLD}{num_str} {C.RESET}|"
                elif is_trace:
                    cell_text = f"{C.BG_GREEN}{C.FG_BLACK}{C.BOLD}{num_str} {C.RESET}|"
                elif is_diag:
                    cell_text = f"{C.BG_MAGENTA}{C.FG_WHITE}{C.BOLD}{num_str} {C.RESET}|"
                elif is_top:
                    cell_text = f"{C.BG_BLUE}{C.FG_WHITE}{C.BOLD}{num_str} {C.RESET}|"
                elif is_left:
                    cell_text = f"{C.BG_CYAN}{C.FG_BLACK}{C.BOLD}{num_str} {C.RESET}|"
                else:
                    cell_text = f" {C.FG_BRIGHT_WHITE}{num_str}{C.RESET} |"

            row_str += cell_text
        lines.append(row_str)
        lines.append(f"{C.DIM}{border}{C.RESET}")

    lines.append("")

    # Explanation Panel
    if current_step.step_type == 'base':
        lines.append(f"{C.BOLD}Phase: Base Case Initialization{C.RESET}")
        lines.append(f"  At cell ({current_step.i}, {current_step.j}): Empty prefix requires max({current_step.i}, {current_step.j}) = {C.BOLD}{C.FG_BRIGHT_YELLOW}{current_step.details['value']}{C.RESET} operations.")
    elif current_step.step_type == 'cell':
        d = current_step.details
        c1, c2, match = d['char1'], d['char2'], d['match']
        match_symbol = f"{C.FG_BRIGHT_GREEN}== (Match, cost=0){C.RESET}" if match else f"{C.FG_BRIGHT_RED}!= (Mismatch, cost=1){C.RESET}"
        
        lines.append(f"{C.BOLD}Computing Cell ({current_step.i}, {current_step.j}):{C.RESET} Comparing '{C.FG_BRIGHT_YELLOW}{c1}{C.RESET}' vs '{C.FG_BRIGHT_GREEN}{c2}{C.RESET}' -> {match_symbol}")
        lines.append(f"  3 Neighbor Options:")
        lines.append(f"    {C.BG_BLUE}{C.FG_WHITE} ⬆ Top (Delete)     {C.RESET} : cache[{current_step.i-1}][{current_step.j}] + 1 = {d['top_val']} + 1 = {d['cand_a']}")
        lines.append(f"    {C.BG_CYAN}{C.FG_BLACK} ⬅ Left (Insert)    {C.RESET} : cache[{current_step.i}][{current_step.j-1}] + 1 = {d['left_val']} + 1 = {d['cand_b']}")
        lines.append(f"    {C.BG_MAGENTA}{C.FG_WHITE} ↖ Diag (Match/Sub) {C.RESET} : cache[{current_step.i-1}][{current_step.j-1}] + {d['sub_cost']} = {d['diag_val']} + {d['sub_cost']} = {d['cand_c']}")
        lines.append(f"  {C.BOLD}Formula:{C.RESET} min({d['cand_a']}, {d['cand_b']}, {d['cand_c']}) = {C.BOLD}{C.FG_BRIGHT_YELLOW}{d['winner']}{C.RESET}  --> Chosen: {C.FG_BRIGHT_CYAN}{d['chosen']}{C.RESET}")
    elif current_step.step_type == 'traceback':
        lines.append(f"{C.BOLD}{C.FG_BRIGHT_GREEN}Phase: Optimal Alignment Traceback{C.RESET}")
        lines.append(f"  Tracing optimal edit path from bottom-right (distance: {current_step.details.get('distance')}) back to (0,0)...")

    return "\n".join(lines)


def run_terminal_animation(s1: str, s2: str, delay: float = 0.15, step_mode: bool = False):
    """Executes the animated terminal visualizer."""
    m, n = len(s1), len(s2)
    cache, steps, traceback_path = compute_levenshtein_steps(s1, s2)
    partial_cache = [[None for _ in range(n + 1)] for _ in range(m + 1)]

    total_steps = len(steps) + len(traceback_path)
    step_num = 0

    clear_screen()
    print("Starting Levenshtein Distance animation...")
    time.sleep(0.5)

    # 1. Animate DP Table computation
    for step in steps:
        step_num += 1
        if step.step_type == 'base':
            partial_cache[step.i][step.j] = step.details['value']
        else:
            partial_cache[step.i][step.j] = step.details['winner']

        clear_screen()
        frame = render_terminal_frame(s1, s2, partial_cache, step, step_num, total_steps)
        print(frame)

        if step_mode:
            input(f"\n{Colors.DIM}[Press Enter to continue, or Ctrl+C to exit]{Colors.RESET}")
        elif delay > 0:
            time.sleep(delay)

    # 2. Animate Traceback
    trace_set = set()
    dist = cache[m][n]
    for (ti, tj, op) in traceback_path:
        step_num += 1
        trace_set.add((ti, tj))
        trace_step = LevenshteinStep('traceback', ti, tj, distance=dist, op=op)
        clear_screen()
        frame = render_terminal_frame(s1, s2, cache, trace_step, step_num, total_steps, trace_set=trace_set)
        print(frame)
        print(f"\n  {Colors.BOLD}{Colors.FG_BRIGHT_YELLOW}Step Action:{Colors.RESET} at ({ti}, {tj}) -> {op}")

        if step_mode:
            input(f"\n{Colors.DIM}[Press Enter to continue, or Ctrl+C to exit]{Colors.RESET}")
        elif delay > 0:
            time.sleep(delay * 1.5)

    # 3. Final Summary
    print("\n" + "=" * 55)
    print(f"{Colors.BOLD}{Colors.FG_BRIGHT_GREEN}✓ COMPUTATION COMPLETE!{Colors.RESET}")
    print(f"  • Source string:            '{s1}'")
    print(f"  • Target string:            '{s2}'")
    print(f"  • Levenshtein Distance:     {Colors.BOLD}{Colors.FG_BRIGHT_YELLOW}{dist}{Colors.RESET}")
    forgiveness = recommend_forgiveness(s1)
    print(f"  • Forgiveness Threshold:    {Colors.BOLD}{Colors.FG_BRIGHT_CYAN}{forgiveness}{Colors.RESET} (from main.recommend_forgiveness)")
    print("\nOptimal Alignment Actions:")
    for idx, (ti, tj, op) in enumerate(traceback_path):
        if op != "START":
            print(f"  {idx}. {op}")
    print("=" * 55 + "\n")


def generate_html_content(default_s1: str = "hello", default_s2: str = "shells") -> str:
    """Generates the self-contained interactive HTML educational illustrator."""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Levenshtein Distance Interactive Visualizer</title>
  <script src="https://www.gstatic.com/antigravity/web/dev/tailwindcss.min.js"></script>
  <style>
    :root {{
      --background: #0f172a;
      --card: #1e293b;
      --border: #334155;
      --foreground: #f8fafc;
      --muted-foreground: #94a3b8;
      --primary: #38bdf8;
      --primary-foreground: #0f172a;
      --accent: #a855f7;
    }}
    .cell-transition {{
      transition: all 0.25s ease-in-out;
    }}
    .pulse-glow {{
      animation: pulse-glow 1.5s infinite alternate;
    }}
    @keyframes pulse-glow {{
      0% {{ box-shadow: 0 0 4px rgba(56, 189, 248, 0.4); }}
      100% {{ box-shadow: 0 0 16px rgba(56, 189, 248, 0.9); }}
    }}
    /* Custom scrollbar */
    ::-webkit-scrollbar {{
      width: 6px;
      height: 6px;
    }}
    ::-webkit-scrollbar-track {{
      background: var(--card);
    }}
    ::-webkit-scrollbar-thumb {{
      background: var(--border);
      border-radius: 3px;
    }}
  </style>
</head>
<body class="bg-transparent text-[var(--foreground)] antialiased p-3 sm:p-5 font-sans select-none">

  <!-- Main Container Card -->
  <div class="max-w-4xl mx-auto bg-[var(--card)] text-[var(--foreground)] border border-[var(--border)] rounded-2xl shadow-2xl p-4 sm:p-6 space-y-5">
    
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between border-b border-[var(--border)] pb-4 gap-3">
      <div>
        <div class="flex items-center gap-2">
          <span class="inline-flex items-center justify-center w-8 h-8 rounded-lg bg-sky-500/20 text-sky-400 font-bold text-lg">⚡</span>
          <h1 class="text-xl sm:text-2xl font-bold tracking-tight text-[var(--foreground)]">Levenshtein Distance Illustrator</h1>
        </div>
        <p class="text-xs sm:text-sm text-[var(--muted-foreground)] mt-1">
          Interactive educational animation showing dynamic programming matrix calculation & traceback.
        </p>
      </div>
      <div class="flex items-center gap-2 self-start sm:self-auto">
        <span class="text-xs px-2.5 py-1 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-medium">CS361 Microservice</span>
      </div>
    </div>

    <!-- Controls & Input Bar -->
    <div class="grid grid-cols-1 sm:grid-cols-12 gap-3 bg-slate-900/40 p-3 rounded-xl border border-[var(--border)]">
      <!-- Input String 1 -->
      <div class="sm:col-span-4">
        <label class="block text-xs font-semibold text-[var(--muted-foreground)] uppercase tracking-wider mb-1">Source (string1)</label>
        <input id="inputS1" type="text" value="{default_s1}" maxlength="12" class="w-full bg-[var(--card)] border border-[var(--border)] rounded-lg px-3 py-1.5 text-sm font-mono text-[var(--foreground)] focus:outline-none focus:border-sky-400 transition" />
      </div>

      <!-- Input String 2 -->
      <div class="sm:col-span-4">
        <label class="block text-xs font-semibold text-[var(--muted-foreground)] uppercase tracking-wider mb-1">Target (string2)</label>
        <input id="inputS2" type="text" value="{default_s2}" maxlength="12" class="w-full bg-[var(--card)] border border-[var(--border)] rounded-lg px-3 py-1.5 text-sm font-mono text-[var(--foreground)] focus:outline-none focus:border-sky-400 transition" />
      </div>

      <!-- Presets Dropdown -->
      <div class="sm:col-span-4">
        <label class="block text-xs font-semibold text-[var(--muted-foreground)] uppercase tracking-wider mb-1">Presets</label>
        <select id="presetSelect" class="w-full bg-[var(--card)] border border-[var(--border)] rounded-lg px-3 py-1.5 text-sm text-[var(--foreground)] focus:outline-none focus:border-sky-400 transition cursor-pointer">
          <option value="hello,shells">"hello" → "shells" (Microservice Example)</option>
          <option value="kitten,sitting">"kitten" → "sitting" (Classic Textbook)</option>
          <option value="saturday,sunday">"saturday" → "sunday"</option>
          <option value="book,back">"book" → "back"</option>
          <option value="algorithm,alligator">"algorithm" → "alligator"</option>
          <option value="cake,bake">"cake" → "bake" (1 Substitution)</option>
        </select>
      </div>
    </div>

    <!-- Playback Toolbar -->
    <div class="flex flex-wrap items-center justify-between gap-3 bg-slate-900/60 p-2.5 rounded-xl border border-[var(--border)]">
      <div class="flex items-center gap-1.5">
        <!-- Play / Pause -->
        <button id="btnPlayPause" class="px-3.5 py-1.5 bg-sky-500 hover:bg-sky-400 text-slate-950 font-semibold rounded-lg text-xs flex items-center gap-1.5 transition shadow-sm">
          <span id="playIcon">▶</span> <span id="playText">Play</span>
        </button>

        <!-- Step Prev -->
        <button id="btnPrev" class="px-2.5 py-1.5 bg-[var(--card)] hover:bg-slate-700 border border-[var(--border)] rounded-lg text-xs transition" title="Previous step">
          ⏮ Prev
        </button>

        <!-- Step Next -->
        <button id="btnNext" class="px-2.5 py-1.5 bg-[var(--card)] hover:bg-slate-700 border border-[var(--border)] rounded-lg text-xs transition" title="Next step">
          Next ⏭
        </button>

        <!-- Reset -->
        <button id="btnReset" class="px-2.5 py-1.5 bg-[var(--card)] hover:bg-slate-700 border border-[var(--border)] rounded-lg text-xs text-[var(--muted-foreground)] hover:text-white transition" title="Reset">
          ↺ Reset
        </button>
      </div>

      <!-- Speed & Jump -->
      <div class="flex items-center gap-3">
        <div class="flex items-center gap-1.5 text-xs text-[var(--muted-foreground)]">
          <span>Speed:</span>
          <select id="speedSelect" class="bg-[var(--card)] border border-[var(--border)] rounded px-2 py-1 text-xs text-[var(--foreground)] focus:outline-none">
            <option value="600">0.5x (Slow)</option>
            <option value="250" selected>1x (Normal)</option>
            <option value="100">2x (Fast)</option>
            <option value="20">10x (Blazing)</option>
          </select>
        </div>
        <button id="btnFinish" class="px-2.5 py-1.5 bg-[var(--card)] hover:bg-slate-700 border border-[var(--border)] rounded-lg text-xs text-sky-400 transition">
          ⏩ Jump to End
        </button>
      </div>
    </div>

    <!-- Active Step Explanation Card -->
    <div id="stepCard" class="bg-gradient-to-r from-slate-900 to-slate-800/80 p-3.5 rounded-xl border border-[var(--border)] space-y-2">
      <div class="flex items-center justify-between">
        <span id="stepPhaseBadge" class="text-xs font-mono font-semibold px-2 py-0.5 rounded bg-sky-500/20 text-sky-300 border border-sky-500/30">
          Ready
        </span>
        <span id="stepCounter" class="text-xs text-[var(--muted-foreground)] font-mono">
          Step 0 / 0
        </span>
      </div>

      <!-- Dynamic Visual Decision Box -->
      <div id="decisionBox" class="text-xs sm:text-sm text-[var(--foreground)]">
        Press Play or Next to begin illustrating how the table is populated.
      </div>
    </div>

    <!-- Visual DP Table Display -->
    <div class="overflow-x-auto pb-2">
      <div id="tableContainer" class="inline-block min-w-full flex justify-center py-2">
        <!-- Injected dynamically via JS -->
      </div>
    </div>

    <!-- Legend & Formula Reference -->
    <div class="grid grid-cols-2 sm:grid-cols-4 gap-2 pt-2 border-t border-[var(--border)] text-xs text-[var(--muted-foreground)]">
      <div class="flex items-center gap-2 p-1.5 rounded bg-blue-500/10 border border-blue-500/20">
        <span class="w-3 h-3 rounded bg-blue-500 inline-block"></span>
        <span><b>Top:</b> Delete (+1)</span>
      </div>
      <div class="flex items-center gap-2 p-1.5 rounded bg-cyan-500/10 border border-cyan-500/20">
        <span class="w-3 h-3 rounded bg-cyan-500 inline-block"></span>
        <span><b>Left:</b> Insert (+1)</span>
      </div>
      <div class="flex items-center gap-2 p-1.5 rounded bg-purple-500/10 border border-purple-500/20">
        <span class="w-3 h-3 rounded bg-purple-500 inline-block"></span>
        <span><b>Diag:</b> Match(+0)/Sub(+1)</span>
      </div>
      <div class="flex items-center gap-2 p-1.5 rounded bg-emerald-500/10 border border-emerald-500/20">
        <span class="w-3 h-3 rounded bg-emerald-500 inline-block"></span>
        <span><b>Traceback:</b> Optimal Path</span>
      </div>
    </div>

    <!-- Alignment Transformation Morph Card (Shown on finish) -->
    <div id="alignmentCard" class="hidden bg-slate-900/80 p-4 rounded-xl border border-emerald-500/30 space-y-3">
      <div class="flex items-center justify-between">
        <h3 class="text-sm font-semibold text-emerald-400 flex items-center gap-2">
          <span>✨</span> Optimal Transformation Sequence
        </h3>
        <div class="flex gap-2">
          <span id="finalDistanceBadge" class="text-xs font-mono px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
            Distance: 0
          </span>
          <span id="finalForgivenessBadge" class="text-xs font-mono px-2 py-0.5 rounded bg-purple-500/20 text-purple-300 border border-purple-500/30">
            Forgiveness: 0
          </span>
        </div>
      </div>
      
      <div id="alignmentDisplay" class="font-mono text-sm space-y-1.5 overflow-x-auto p-2 bg-[var(--card)] rounded-lg border border-[var(--border)]">
        <!-- Traceback steps rendered here -->
      </div>
    </div>

  </div>

  <script>
    // --- State & Logic ---
    let s1 = "{default_s1}";
    let s2 = "{default_s2}";
    let steps = [];
    let currentStepIndex = 0;
    let isPlaying = false;
    let playTimer = null;
    let cacheMatrix = [];
    let tracebackPath = [];

    const inputS1 = document.getElementById('inputS1');
    const inputS2 = document.getElementById('inputS2');
    const presetSelect = document.getElementById('presetSelect');
    const btnPlayPause = document.getElementById('btnPlayPause');
    const playIcon = document.getElementById('playIcon');
    const playText = document.getElementById('playText');
    const btnPrev = document.getElementById('btnPrev');
    const btnNext = document.getElementById('btnNext');
    const btnReset = document.getElementById('btnReset');
    const btnFinish = document.getElementById('btnFinish');
    const speedSelect = document.getElementById('speedSelect');
    const tableContainer = document.getElementById('tableContainer');
    const stepCard = document.getElementById('stepCard');
    const stepPhaseBadge = document.getElementById('stepPhaseBadge');
    const stepCounter = document.getElementById('stepCounter');
    const decisionBox = document.getElementById('decisionBox');
    const alignmentCard = document.getElementById('alignmentCard');
    const alignmentDisplay = document.getElementById('alignmentDisplay');
    const finalDistanceBadge = document.getElementById('finalDistanceBadge');
    const finalForgivenessBadge = document.getElementById('finalForgivenessBadge');

    function recommendForgiveness(str) {{
      const l = str.length;
      return l - (Math.floor(l * 8 / 10) + 1);
    }}

    function buildSteps(word1, word2) {{
      const m = word1.length;
      const n = word2.length;
      const cache = Array.from({{ length: m + 1 }}, () => Array(n + 1).fill(-1));
      const stepList = [];

      for (let i = 0; i <= m; i++) {{
        for (let j = 0; j <= n; j++) {{
          if (Math.min(i, j) === 0) {{
            const val = Math.max(i, j);
            cache[i][j] = val;
            stepList.push({{
              type: 'base',
              i, j,
              val,
              reason: `Empty string prefix: transforming ${{i === 0 ? `"" -> "${{word2.slice(0, j)}}"` : `"${{word1.slice(0, i)}}" -> ""`}} takes ${{val}} edits.`
            }});
          }} else {{
            const topVal = cache[i - 1][j];
            const leftVal = cache[i][j - 1];
            const diagVal = cache[i - 1][j - 1];
            const char1 = word1[i - 1];
            const char2 = word2[j - 1];
            const match = (char1 === char2);
            const subCost = match ? 0 : 1;

            const candA = topVal + 1;
            const candB = leftVal + 1;
            const candC = diagVal + subCost;
            const minVal = Math.min(candA, candB, candC);
            cache[i][j] = minVal;

            stepList.push({{
              type: 'cell',
              i, j,
              char1, char2, match,
              topVal, candA,
              leftVal, candB,
              diagVal, subCost, candC,
              winner: minVal
            }});
          }}
        }}
      }}

      // Traceback
      const tb = [];
      let ci = m, cj = n;
      while (ci > 0 || cj > 0) {{
        if (ci > 0 && cj > 0) {{
          const c1 = word1[ci - 1];
          const c2 = word2[cj - 1];
          const cost = (c1 === c2) ? 0 : 1;
          if (cache[ci][cj] === cache[ci - 1][cj - 1] + cost) {{
            tb.push({{ i: ci, j: cj, op: cost === 0 ? `MATCH '${{c1}}'` : `SUBSTITUTE '${{c1}}' -> '${{c2}}'`, cost }});
            ci--; cj--;
            continue;
          }} else if (cache[ci][cj] === cache[ci - 1][cj] + 1) {{
            tb.push({{ i: ci, j: cj, op: `DELETE '${{c1}}'`, cost: 1 }});
            ci--;
            continue;
          }} else {{
            tb.push({{ i: ci, j: cj, op: `INSERT '${{c2}}'`, cost: 1 }});
            cj--;
            continue;
          }}
        }} else if (ci > 0) {{
          tb.push({{ i: ci, j: cj, op: `DELETE '${{word1[ci - 1]}}'`, cost: 1 }});
          ci--;
        }} else {{
          tb.push({{ i: ci, j: cj, op: `INSERT '${{word2[cj - 1]}}'`, cost: 1 }});
          cj--;
        }}
      }}
      tb.push({{ i: 0, j: 0, op: 'START', cost: 0 }});
      tb.reverse();

      return {{ cache, stepList, tb }};
    }}

    function initTable() {{
      const m = s1.length;
      const n = s2.length;
      let html = '<table class="border-collapse text-xs sm:text-sm font-mono">';
      
      // Top header with s2 characters
      html += '<thead><tr><th class="p-2 border border-slate-700/60 bg-slate-900/60 text-slate-400"></th>';
      html += '<th class="p-2 border border-slate-700/60 bg-slate-900/60 text-emerald-400 font-bold">ε</th>';
      for (let j = 0; j < n; j++) {{
        html += `<th class="p-2 border border-slate-700/60 bg-slate-900/60 text-emerald-400 font-bold">${{s2[j]}}</th>`;
      }}
      html += '</tr></thead><tbody>';

      // Rows with s1 characters
      for (let i = 0; i <= m; i++) {{
        const rowChar = (i === 0) ? 'ε' : s1[i - 1];
        html += `<tr><th class="p-2 border border-slate-700/60 bg-slate-900/60 text-amber-400 font-bold">${{rowChar}}</th>`;
        for (let j = 0; j <= n; j++) {{
          html += `<td id="cell-${{i}}-${{j}}" class="cell-transition w-10 sm:w-12 h-10 sm:h-12 text-center border border-slate-700/80 bg-[var(--card)] text-slate-500 font-medium cursor-pointer hover:border-sky-400/50" onclick="inspectCell(${{i}}, ${{j}})">·</td>`;
        }}
        html += '</tr>';
      }}
      html += '</tbody></table>';
      tableContainer.innerHTML = html;
    }}

    function resetSimulation() {{
      pause();
      s1 = inputS1.value.trim() || "hello";
      s2 = inputS2.value.trim() || "shells";
      const data = buildSteps(s1, s2);
      cacheMatrix = data.cache;
      steps = data.stepList;
      tracebackPath = data.tb;
      currentStepIndex = 0;
      initTable();
      alignmentCard.classList.add('hidden');
      stepPhaseBadge.textContent = "Ready";
      stepPhaseBadge.className = "text-xs font-mono font-semibold px-2 py-0.5 rounded bg-sky-500/20 text-sky-300 border border-sky-500/30";
      stepCounter.textContent = `Step 0 / ${{steps.length}}`;
      decisionBox.innerHTML = `Ready to compute Levenshtein distance between <b>"${{s1}}"</b> and <b>"${{s2}}"</b>. Press Play or Next!`;
    }}

    function applyStep(index, highlight=true) {{
      if (index < 0 || index >= steps.length) return;
      const step = steps[index];
      const cell = document.getElementById(`cell-${{step.i}}-${{step.j}}`);
      if (!cell) return;

      // Set cell value
      cell.textContent = (step.type === 'base') ? step.val : step.winner;
      cell.classList.remove('text-slate-500');
      cell.classList.add('text-white');

      if (highlight) {{
        // Clear all previous highlight classes across table
        clearCellHighlights();

        // Highlight active cell
        cell.classList.add('ring-2', 'ring-sky-400', 'bg-sky-500/20', 'pulse-glow');

        // If step is a regular cell, highlight predecessors
        if (step.type === 'cell') {{
          const topCell = document.getElementById(`cell-${{step.i - 1}}-${{step.j}}`);
          const leftCell = document.getElementById(`cell-${{step.i}}-${{step.j - 1}}`);
          const diagCell = document.getElementById(`cell-${{step.i - 1}}-${{step.j - 1}}`);

          if (topCell) topCell.classList.add('ring-1', 'ring-blue-400', 'bg-blue-500/20');
          if (leftCell) leftCell.classList.add('ring-1', 'ring-cyan-400', 'bg-cyan-500/20');
          if (diagCell) diagCell.classList.add('ring-1', 'ring-purple-400', 'bg-purple-500/20');

          stepPhaseBadge.textContent = "Computing Cell";
          stepPhaseBadge.className = "text-xs font-mono font-semibold px-2 py-0.5 rounded bg-amber-500/20 text-amber-300 border border-amber-500/30";

          const matchBadge = step.match
            ? '<span class="text-emerald-400 font-bold bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20">MATCH (\'+0\')</span>'
            : '<span class="text-rose-400 font-bold bg-rose-500/10 px-2 py-0.5 rounded border border-rose-500/20">DIFFER (\'+1\')</span>';

          decisionBox.innerHTML = `
            <div class="space-y-2">
              <div class="flex items-center gap-2">
                <span>Comparing: row <b>'${{step.char1}}'</b> vs col <b>'${{step.char2}}'</b></span>
                ${{matchBadge}}
              </div>
              <div class="grid grid-cols-1 sm:grid-cols-3 gap-2 text-xs">
                <div class="p-2 rounded bg-blue-500/10 border border-blue-500/20 ${{step.winner === step.candA ? 'ring-1 ring-blue-400 font-bold' : 'opacity-80'}}">
                  ⬆ <b>Top (Delete):</b> ${{step.topVal}} + 1 = <b>${{step.candA}}</b>
                </div>
                <div class="p-2 rounded bg-cyan-500/10 border border-cyan-500/20 ${{step.winner === step.candB ? 'ring-1 ring-cyan-400 font-bold' : 'opacity-80'}}">
                  ⬅ <b>Left (Insert):</b> ${{step.leftVal}} + 1 = <b>${{step.candB}}</b>
                </div>
                <div class="p-2 rounded bg-purple-500/10 border border-purple-500/20 ${{step.winner === step.candC ? 'ring-1 ring-purple-400 font-bold' : 'opacity-80'}}">
                  ↖ <b>Diag (${{step.match ? 'Match' : 'Sub'}}):</b> ${{step.diagVal}} + ${{step.subCost}} = <b>${{step.candC}}</b>
                </div>
              </div>
              <div class="text-xs text-sky-300">
                👉 Result = min(${{step.candA}}, ${{step.candB}}, ${{step.candC}}) = <span class="text-amber-300 font-bold text-sm">${{step.winner}}</span>
              </div>
            </div>
          `;
        }} else {{
          stepPhaseBadge.textContent = "Base Case";
          stepPhaseBadge.className = "text-xs font-mono font-semibold px-2 py-0.5 rounded bg-sky-500/20 text-sky-300 border border-sky-500/30";
          decisionBox.innerHTML = `<span class="text-sky-300">${{step.reason}}</span>`;
        }}
      }}
      stepCounter.textContent = `Step ${{index + 1}} / ${{steps.length}}`;
    }}

    function clearCellHighlights() {{
      const cells = tableContainer.querySelectorAll('td');
      cells.forEach(c => {{
        c.classList.remove('ring-2', 'ring-1', 'ring-sky-400', 'ring-blue-400', 'ring-cyan-400', 'ring-purple-400', 'ring-emerald-400', 'bg-sky-500/20', 'bg-blue-500/20', 'bg-cyan-500/20', 'bg-purple-500/20', 'pulse-glow');
      }});
    }}

    function finishAllSteps() {{
      pause();
      clearCellHighlights();
      for (let i = 0; i < steps.length; i++) {{
        applyStep(i, false);
      }}
      currentStepIndex = steps.length;
      showTraceback();
    }}

    function showTraceback() {{
      clearCellHighlights();
      tracebackPath.forEach(pt => {{
        const cell = document.getElementById(`cell-${{pt.i}}-${{pt.j}}`);
        if (cell) {{
          cell.classList.add('bg-emerald-500/30', 'text-emerald-300', 'ring-1', 'ring-emerald-400', 'font-bold');
        }}
      }});

      stepPhaseBadge.textContent = "Traceback Finished";
      stepPhaseBadge.className = "text-xs font-mono font-semibold px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 border border-emerald-500/30";

      const finalDist = cacheMatrix[s1.length][s2.length];
      const forgiveness = recommendForgiveness(s1);

      decisionBox.innerHTML = `
        <div class="text-emerald-300">
          🎉 Matrix complete! The green path highlights the optimal edit sequence from <b>(0,0)</b> to <b>(${{s1.length}},${{s2.length}})</b>.
          Levenshtein Distance = <b>${{finalDist}}</b> edit(s).
        </div>
      `;

      finalDistanceBadge.textContent = `Levenshtein Distance: ${{finalDist}}`;
      finalForgivenessBadge.textContent = `Forgiveness Threshold: ${{forgiveness}}`;

      let tbHtml = '';
      tracebackPath.forEach((pt, idx) => {{
        if (pt.op === 'START') return;
        let badgeColor = 'text-slate-300';
        if (pt.op.startsWith('MATCH')) badgeColor = 'text-emerald-400';
        else if (pt.op.startsWith('SUBSTITUTE')) badgeColor = 'text-amber-400';
        else if (pt.op.startsWith('INSERT')) badgeColor = 'text-cyan-400';
        else if (pt.op.startsWith('DELETE')) badgeColor = 'text-rose-400';

        tbHtml += `<div class="flex items-center gap-2"><span class="text-xs text-slate-500">Step ${{idx}}:</span> <span class="${{badgeColor}} font-semibold">${{pt.op}}</span></div>`;
      }});
      alignmentDisplay.innerHTML = tbHtml;
      alignmentCard.classList.remove('hidden');
    }}

    function stepForward() {{
      if (currentStepIndex < steps.length) {{
        applyStep(currentStepIndex, true);
        currentStepIndex++;
        if (currentStepIndex === steps.length) {{
          pause();
          setTimeout(showTraceback, 400);
        }}
      }} else {{
        showTraceback();
        pause();
      }}
    }}

    function stepBackward() {{
      if (currentStepIndex > 1) {{
        currentStepIndex -= 2;
        // re-render up to currentStepIndex
        initTable();
        for (let i = 0; i <= currentStepIndex; i++) {{
          applyStep(i, i === currentStepIndex);
        }}
        currentStepIndex++;
      }} else if (currentStepIndex === 1) {{
        resetSimulation();
      }}
    }}

    function play() {{
      if (currentStepIndex >= steps.length) {{
        resetSimulation();
      }}
      isPlaying = true;
      playIcon.textContent = '⏸';
      playText.textContent = 'Pause';
      btnPlayPause.classList.replace('bg-sky-500', 'bg-amber-500');

      const speed = parseInt(speedSelect.value, 10);
      playTimer = setInterval(() => {{
        if (currentStepIndex < steps.length) {{
          stepForward();
        }} else {{
          pause();
        }}
      }}, speed);
    }}

    function pause() {{
      isPlaying = false;
      playIcon.textContent = '▶';
      playText.textContent = 'Play';
      btnPlayPause.classList.replace('bg-amber-500', 'bg-sky-500');
      if (playTimer) {{
        clearInterval(playTimer);
        playTimer = null;
      }}
    }}

    function inspectCell(i, j) {{
      const step = steps.find(s => s.i === i && s.j === j);
      if (!step) return;
      pause();
      clearCellHighlights();
      const targetCell = document.getElementById(`cell-${{i}}-${{j}}`);
      if (targetCell) {{
        targetCell.classList.add('ring-2', 'ring-sky-400', 'bg-sky-500/20');
      }}
      if (step.type === 'cell') {{
        const topCell = document.getElementById(`cell-${{i - 1}}-${{j}}`);
        const leftCell = document.getElementById(`cell-${{i}}-${{j - 1}}`);
        const diagCell = document.getElementById(`cell-${{i - 1}}-${{j - 1}}`);
        if (topCell) topCell.classList.add('ring-1', 'ring-blue-400', 'bg-blue-500/20');
        if (leftCell) leftCell.classList.add('ring-1', 'ring-cyan-400', 'bg-cyan-500/20');
        if (diagCell) diagCell.classList.add('ring-1', 'ring-purple-400', 'bg-purple-500/20');

        decisionBox.innerHTML = `
          <div class="space-y-1">
            <span class="text-sky-300 font-bold">Inspecting Cell (${{i}}, ${{j}}):</span>
            Row char '${{step.char1}}' vs Col char '${{step.char2}}' (${{step.match ? 'Match +0' : 'Differ +1'}})
            <div class="grid grid-cols-3 gap-2 mt-1 text-xs">
              <div class="p-1.5 rounded bg-blue-500/10 border border-blue-500/20">Top: ${{step.topVal}} + 1 = <b>${{step.candA}}</b></div>
              <div class="p-1.5 rounded bg-cyan-500/10 border border-cyan-500/20">Left: ${{step.leftVal}} + 1 = <b>${{step.candB}}</b></div>
              <div class="p-1.5 rounded bg-purple-500/10 border border-purple-500/20">Diag: ${{step.diagVal}} + ${{step.subCost}} = <b>${{step.candC}}</b></div>
            </div>
            <div class="text-xs text-amber-300">Minimum = ${{step.winner}}</div>
          </div>
        `;
      }} else {{
        decisionBox.innerHTML = `<span class="text-sky-300">Base Case Cell (${{i}}, ${{j}}): ${{step.reason}}</span>`;
      }}
    }}

    // --- Event Listeners ---
    btnPlayPause.addEventListener('click', () => {{
      if (isPlaying) pause();
      else play();
    }});

    btnNext.addEventListener('click', () => {{
      pause();
      stepForward();
    }});

    btnPrev.addEventListener('click', () => {{
      pause();
      stepBackward();
    }});

    btnReset.addEventListener('click', resetSimulation);
    btnFinish.addEventListener('click', finishAllSteps);

    speedSelect.addEventListener('change', () => {{
      if (isPlaying) {{
        pause();
        play();
      }}
    }});

    presetSelect.addEventListener('change', (e) => {{
      const [w1, w2] = e.target.value.split(',');
      inputS1.value = w1;
      inputS2.value = w2;
      resetSimulation();
    }});

    inputS1.addEventListener('input', resetSimulation);
    inputS2.addEventListener('input', resetSimulation);

    // Initial setup
    resetSimulation();
  </script>
</body>
</html>
"""


def main():
    parser = argparse.ArgumentParser(
        description="Levenshtein Distance Visual Illustrator (Educational Animation)"
    )
    parser.add_argument("string1", nargs="?", default="hello", help="Source string (default: hello)")
    parser.add_argument("string2", nargs="?", default="shells", help="Target string (default: shells)")
    parser.add_argument("--delay", type=float, default=0.15, help="Animation delay in seconds (default: 0.15)")
    parser.add_argument("--step", action="store_true", help="Interactive step-by-step mode (press Enter to advance)")
    parser.add_argument("--html", type=str, nargs="?", const="levenshtein_illustrator.html",
                        help="Export self-contained interactive HTML visualizer to file")
    parser.add_argument("--web", action="store_true", help="Generate HTML and launch local interactive server")

    parser.add_argument("--cli", action="store_true", help="Also run the terminal animation when exporting HTML")

    args = parser.parse_args()

    # Handle HTML export
    if args.html or args.web:
        filename = args.html if args.html else "levenshtein_illustrator.html"
        html_code = generate_html_content(args.string1, args.string2)
        with open(filename, "w", encoding="utf-8") as f:
            f.write(html_code)
        print(f"Generated interactive HTML visualizer: {os.path.abspath(filename)}")

        if args.web:
            import http.server
            import socketserver

            PORT = 8085
            Handler = http.server.SimpleHTTPRequestHandler
            print(f"Starting local visualizer server at http://localhost:{PORT}/{filename}")
            try:
                with socketserver.TCPServer(("", PORT), Handler) as httpd:
                    print("Press Ctrl+C to stop the server.")
                    httpd.serve_forever()
            except KeyboardInterrupt:
                print("\nServer stopped.")
            return

        if not args.cli:
            print("Open the HTML file in any browser to explore the interactive visual animation!")
            return

    # Run terminal animation
    run_terminal_animation(args.string1, args.string2, delay=args.delay, step_mode=args.step)


if __name__ == "__main__":
    main()
