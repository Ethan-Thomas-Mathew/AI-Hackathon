"""
Generates SUMMARY.pdf — the 1-page Technical Summary Sheet deliverable.
Run once: python build_summary_pdf.py
(Not needed at hackathon runtime — SUMMARY.pdf is committed to the repo.)
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                 TableStyle, HRFlowable)
from reportlab.lib.enums import TA_LEFT, TA_CENTER

OUT_PATH = "SUMMARY.pdf"

styles = getSampleStyleSheet()
title_style = ParagraphStyle("TitleSm", parent=styles["Title"], fontSize=15,
                              leading=18, spaceAfter=2, alignment=TA_CENTER)
subtitle_style = ParagraphStyle("Subtitle", parent=styles["Normal"], fontSize=9.5,
                                 leading=12, alignment=TA_CENTER, textColor=colors.HexColor("#444444"))
h2_style = ParagraphStyle("H2", parent=styles["Heading2"], fontSize=11.5, leading=14,
                           spaceBefore=8, spaceAfter=4, textColor=colors.HexColor("#1F3B57"))
body_style = ParagraphStyle("BodySm", parent=styles["Normal"], fontSize=8.7, leading=11.5)
mono_style = ParagraphStyle("Mono", parent=styles["Normal"], fontName="Courier",
                             fontSize=8.5, leading=11.5)
cell_style = ParagraphStyle("Cell", parent=styles["Normal"], fontSize=8.3, leading=10.5)
cell_hdr_style = ParagraphStyle("CellHdr", parent=styles["Normal"], fontSize=8.3,
                                 leading=10.5, textColor=colors.white, fontName="Helvetica-Bold")

doc = SimpleDocTemplate(OUT_PATH, pagesize=letter,
                         topMargin=0.45 * inch, bottomMargin=0.45 * inch,
                         leftMargin=0.55 * inch, rightMargin=0.55 * inch)

story = []

# ---------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------
story.append(Paragraph("Warehouse Logistics Agent — Technical Summary Sheet", title_style))
story.append(Paragraph("Track 1 · Unit 2 (Informed Search) · A* Search with Manhattan Distance Heuristic",
                        subtitle_style))
story.append(Spacer(1, 6))

header_data = [
    [Paragraph("Course Code", cell_hdr_style), Paragraph("[Fill in]", cell_style),
     Paragraph("Group ID", cell_hdr_style), Paragraph("[Fill in]", cell_style)],
    [Paragraph("Team Members", cell_hdr_style), Paragraph("[Name 1, Name 2, Name 3]", cell_style),
     Paragraph("Selected Track", cell_hdr_style), Paragraph("Track 1 — Warehouse Logistics Agent", cell_style)],
    [Paragraph("GitHub Repository URL", cell_hdr_style), Paragraph("[Paste repo link here]", cell_style), "", ""],
]
header_table = Table(header_data, colWidths=[1.3 * inch, 2.55 * inch, 1.1 * inch, 1.75 * inch])
header_table.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#1F3B57")),
    ("BACKGROUND", (2, 0), (2, 0), colors.HexColor("#1F3B57")),
    ("BACKGROUND", (2, 1), (2, 1), colors.HexColor("#1F3B57")),
    ("SPAN", (1, 2), (3, 2)),
    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#BBBBBB")),
    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ("TOPPADDING", (0, 0), (-1, -1), 3),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ("LEFTPADDING", (0, 0), (-1, -1), 5),
]))
story.append(header_table)

# ---------------------------------------------------------------------
# PEAS
# ---------------------------------------------------------------------
story.append(Paragraph("PEAS Framework", h2_style))
peas_data = [
    [Paragraph("Performance Measure", cell_hdr_style),
     Paragraph("Total path cost (moves) across all deliveries; nodes expanded (search "
               "efficiency); all packages delivered; zero shelf collisions", cell_style)],
    [Paragraph("Environment", cell_hdr_style),
     Paragraph("Discrete 14x10 grid warehouse; static shelf layout, fully observable; the "
               "person watching may click cells to add/remove obstacles mid-run, so the "
               "environment is dynamic and only semi-predictable; single-agent", cell_style)],
    [Paragraph("Actuators", cell_hdr_style),
     Paragraph("Move Up / Down / Left / Right one cell; Pick-up package; Drop-off package", cell_style)],
    [Paragraph("Sensors", cell_hdr_style),
     Paragraph("Full grid-state knowledge (shelf/package/bay coordinates); obstacle-"
               "appearance detection that triggers live replanning", cell_style)],
]
peas_table = Table(peas_data, colWidths=[1.35 * inch, 5.35 * inch])
peas_table.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#3D6E96")),
    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#BBBBBB")),
    ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ("TOPPADDING", (0, 0), (-1, -1), 4),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ("LEFTPADDING", (0, 0), (-1, -1), 5),
]))
story.append(peas_table)

# ---------------------------------------------------------------------
# Algorithmic formulation
# ---------------------------------------------------------------------
story.append(Paragraph("Core Algorithmic Formulation", h2_style))
formulation = """
<b>State space:</b> a state is a grid cell (x, y), 0&le;x&lt;14, 0&le;y&lt;10, excluding
static-shelf and dynamic-obstacle cells. <b>Actions:</b> 4-connected unit moves
{Up, Down, Left, Right}, each with step cost 1. &nbsp;&nbsp;
<b>Initial state:</b> the forklift's current cell (dock (0,0) for the first leg,
then each package/bay cell it just reached). &nbsp;&nbsp;
<b>Goal test:</b> current cell == the active leg's target cell (next package to
collect, or the assigned bay once carrying a package). &nbsp;&nbsp;
<b>Path cost:</b> g(n) = number of moves from the leg's start to n; total path
cost = sum of g(goal) over all 6 legs (3 pickups + 3 deliveries).
"""
story.append(Paragraph(formulation, body_style))
story.append(Spacer(1, 3))
story.append(Paragraph(
    "<b>Heuristic (Manhattan distance):</b>  h(n) = |x<sub>n</sub> - x<sub>goal</sub>| + "
    "|y<sub>n</sub> - y<sub>goal</sub>|  &nbsp;&nbsp; f(n) = g(n) + h(n)", mono_style))
story.append(Paragraph(
    "h is admissible (never overestimates true cost on a 4-connected unit-cost grid, since "
    "diagonal shortcuts do not exist) and consistent (h(n) &le; cost(n,n') + h(n') for every "
    "edge), so A* is guaranteed to return the optimal path on every leg.", body_style))
story.append(Paragraph(
    "<b>Live interactive replanning:</b> the person watching can click any open cell during "
    "the run to drop or remove an obstacle. If it blocks the path currently being driven, the "
    "agent re-invokes A* with start = agent's current cell, goal = unchanged leg target. If "
    "every route to the goal is sealed off, the agent parks in a BLOCKED state and "
    "automatically resumes as soon as an obstacle is cleared &mdash; demonstrated live and on "
    "demand rather than on a fixed schedule.", body_style))

# ---------------------------------------------------------------------
# Complexity analysis
# ---------------------------------------------------------------------
story.append(Paragraph("Complexity Analysis", h2_style))

complexity_text = """
Let V = walkable cells, E = edges (&le;4 per cell). With a binary-heap open set,
A* runs in <b>O((V + E) log V)</b> time in the worst case and <b>O(V)</b> space
for the open/closed sets and g-score/came-from maps. A well-informed, consistent
heuristic (like Manhattan distance here) typically expands far fewer than V nodes
in practice, since f(n) prunes branches that cannot beat the current best estimate.
"""
story.append(Paragraph(complexity_text, body_style))
story.append(Spacer(1, 3))

metrics_header = [Paragraph(x, cell_hdr_style) for x in
                   ["Leg (no obstacles placed — baseline)", "Path Cost", "Nodes Expanded", "Planning Time (ms)"]]
metrics_rows = [
    ["1. Dock -> Package A", "4", "7", "0.072"],
    ["2. Package A -> Bay 1", "10", "15", "0.114"],
    ["3. Bay 1 -> Package B", "8", "16", "0.074"],
    ["4. Package B -> Bay 2", "8", "12", "0.045"],
    ["5. Bay 2 -> Package C", "6", "12", "0.043"],
    ["6. Package C -> Bay 3", "6", "9", "0.049"],
]
totals_row = ["TOTAL (6 legs)", "42", "71", "~0.40 total"]

metrics_data = [metrics_header] + [[Paragraph(c, cell_style) for c in row] for row in metrics_rows] \
    + [[Paragraph(f"<b>{c}</b>", cell_style) for c in totals_row]]
metrics_table = Table(metrics_data, colWidths=[2.55 * inch, 1.35 * inch, 1.4 * inch, 1.4 * inch])
metrics_table.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1F3B57")),
    ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#E9EEF3")),
    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#BBBBBB")),
    ("ALIGN", (1, 0), (-1, -1), "CENTER"),
    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ("TOPPADDING", (0, 0), (-1, -1), 3),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
]))
story.append(metrics_table)
story.append(Spacer(1, 4))
story.append(Paragraph(
    "Grid: 14x10 = 140 cells, 104 walkable (V=104, E&asymp;208 directed edges). Table above is "
    "the no-interaction baseline. Observed nodes expanded per leg (7-16) stay well below V=104, "
    "confirming the Manhattan heuristic effectively prunes the search versus an uninformed "
    "search (BFS/Dijkstra) which would expand close to all 104 reachable cells. All measured "
    "path costs equal the optimal Manhattan-consistent A* result, confirming optimality on "
    "every leg. Each live obstacle click during the demo triggers one additional bounded A* "
    "call (same O((V+E) log V) worst case) from the agent's current cell, typically expanding "
    "under 20 nodes given the small local search radius. Planning time excludes Pygame "
    "animation delay.",
    body_style))

story.append(Spacer(1, 4))
story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#BBBBBB")))
story.append(Paragraph(
    "AI Express Hackathon — Units 1-4 (AI Foundations, Problem-Solving Agents, Logical Agents, FOL)",
    ParagraphStyle("Footer", parent=styles["Normal"], fontSize=7.3, alignment=TA_CENTER,
                   textColor=colors.HexColor("#888888"), spaceBefore=4)))

doc.build(story)
print(f"Wrote {OUT_PATH}")
