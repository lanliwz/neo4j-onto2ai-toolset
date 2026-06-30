import fs from "node:fs/promises";
import path from "node:path";
import { Presentation, PresentationFile } from "@oai/artifact-tool";

const ROOT = process.env.ONTO2AI_REPO_ROOT;
const MANIFEST = process.env.ONTO2AI_DEMO_MANIFEST;
const REF_IMAGE = process.env.ONTO2AI_REFERENCE_IMAGE;
const OUT_DECK = process.env.ONTO2AI_RENDERED_DECK;
const FRAME_DIR = process.env.ONTO2AI_FRAME_DIR;
const PREVIEW_DIR = process.env.ONTO2AI_PREVIEW_DIR || FRAME_DIR;

const W = 1280;
const H = 720;
const COLORS = {
  navy: "#07111E",
  ink: "#EAF5FF",
  muted: "#AAB7C8",
  blue: "#22B7FF",
  cyan: "#35E4FF",
  orange: "#FF8B24",
  amber: "#FFD66B",
  line: "#2B4664",
  panel: "#102033",
  panel2: "#151B2E",
};

const EYEBROWS = [
  "Introduction",
  "Challenge",
  "Goal",
  "Source ontology",
  "Subset selection",
  "Target ontology",
  "Implementation",
  "Distribution",
  "Modeller",
  "AI context",
  "Takeaway",
];

async function writeBlob(file, blob) {
  await fs.writeFile(file, new Uint8Array(await blob.arrayBuffer()));
}

function addRect(slide, position, fill, line = "none") {
  return slide.shapes.add({
    geometry: "rect",
    position,
    fill,
    line: { style: "solid", fill: line, width: line === "none" ? 0 : 1 },
  });
}

function addRound(slide, position, fill, line = COLORS.line) {
  return slide.shapes.add({
    geometry: "roundRect",
    position,
    fill,
    borderRadius: 12,
    line: { style: "solid", fill: line, width: 1 },
  });
}

function addText(slide, text, position, style = {}) {
  const shape = slide.shapes.add({
    geometry: "textbox",
    position,
    fill: "none",
    line: { style: "solid", fill: "none", width: 0 },
  });
  shape.text = text;
  shape.text.style = {
    fontSize: 24,
    color: COLORS.ink,
    ...style,
  };
  return shape;
}

function addChrome(slide, section, slideNo, total) {
  slide.background.fill = COLORS.navy;
  addRect(slide, { left: 0, top: 0, width: W, height: 12 }, COLORS.cyan);
  addRect(slide, { left: 0, top: H - 10, width: W, height: 10 }, COLORS.orange);
  addRect(slide, { left: 72, top: 646, width: 1136, height: 1 }, "#334963");
  addText(slide, "Onto2AI Modeller", { left: 72, top: 664, width: 300, height: 28 }, {
    fontSize: 18,
    bold: true,
    color: COLORS.cyan,
  });
  addText(slide, section, { left: 460, top: 664, width: 360, height: 26 }, {
    fontSize: 15,
    color: COLORS.muted,
    alignment: "center",
  });
  addText(slide, `${String(slideNo).padStart(2, "0")} / ${String(total).padStart(2, "0")}`, {
    left: 1110,
    top: 664,
    width: 98,
    height: 26,
  }, {
    fontSize: 16,
    color: COLORS.muted,
    alignment: "right",
  });
}

function addHeader(slide, eyebrow, title, text) {
  addText(slide, eyebrow.toUpperCase(), { left: 82, top: 68, width: 320, height: 26 }, {
    fontSize: 13,
    bold: true,
    color: COLORS.cyan,
  });
  addRect(slide, { left: 72, top: 102, width: 8, height: 106 }, COLORS.amber);
  addText(slide, title, { left: 106, top: 104, width: 780, height: 112 }, {
    fontSize: 42,
    bold: true,
    color: "#FFFFFF",
  });
  addText(slide, text, { left: 106, top: 232, width: 820, height: 72 }, {
    fontSize: 22,
    color: COLORS.muted,
  });
}

function addCard(slide, title, body, x, y, w, h, accent = COLORS.blue) {
  addRound(slide, { left: x, top: y, width: w, height: h }, COLORS.panel, "#264461");
  addRect(slide, { left: x, top: y, width: 8, height: h }, accent);
  addText(slide, title, { left: x + 26, top: y + 24, width: w - 44, height: 32 }, {
    fontSize: 24,
    bold: true,
    color: "#FFFFFF",
  });
  addText(slide, body, { left: x + 26, top: y + 68, width: w - 44, height: h - 82 }, {
    fontSize: 17,
    color: COLORS.muted,
  });
}

function addBulletCards(slide, bullets, colors = [COLORS.blue, COLORS.orange, COLORS.amber]) {
  for (let i = 0; i < bullets.length; i++) {
    addCard(slide, `0${i + 1}`, bullets[i], 92 + i * 382, 346, 330, 150, colors[i % colors.length]);
  }
}

function titleFor(index, slideData) {
  if (index === 0) return "Onto2AI Toolset";
  if (index === 10) return "Ontology-driven architecture made practical";
  return slideData.title;
}

async function main() {
  for (const [name, value] of Object.entries({ ROOT, MANIFEST, REF_IMAGE, OUT_DECK, FRAME_DIR })) {
    if (!value) throw new Error(`Missing required environment variable: ${name}`);
  }
  await fs.mkdir(FRAME_DIR, { recursive: true });
  await fs.mkdir(PREVIEW_DIR, { recursive: true });
  await fs.mkdir(path.dirname(OUT_DECK), { recursive: true });

  const source = JSON.parse(await fs.readFile(MANIFEST, "utf8"));
  const imageBytes = await fs.readFile(REF_IMAGE);
  const deck = Presentation.create({ slideSize: { width: W, height: H } });
  deck.theme.colorScheme = {
    name: "Onto2AI LinkedIn Cyber",
    themeColors: {
      accent1: COLORS.blue,
      accent2: COLORS.orange,
      accent3: COLORS.cyan,
      accent4: COLORS.amber,
      accent5: "#7D6BFF",
      accent6: "#27D79D",
      bg1: COLORS.navy,
      bg2: "#0B1624",
      tx1: COLORS.ink,
      tx2: COLORS.muted,
      dk1: "#000000",
      dk2: "#0B1624",
      lt1: "#FFFFFF",
      lt2: "#D9E8F6",
      hlink: COLORS.cyan,
      folHlink: COLORS.orange,
    },
  };

  const total = source.slides.length;
  source.slides.forEach((slideData, index) => {
    const slide = deck.slides.add();
    const scene = source.narrative_lines[index];
    if (index === 0 || index === total - 1) {
      slide.images.add({
        blob: imageBytes,
        contentType: "image/png",
        alt: "Onto2AI LinkedIn visual style reference",
        fit: "cover",
        position: { left: 0, top: 0, width: W, height: H },
      });
      addRect(slide, { left: 0, top: 0, width: W, height: H }, index === 0 ? "#020914/54" : "#020914/66");
      addRect(slide, { left: 0, top: 0, width: 590, height: H }, "#030A14/58");
      addText(slide, index === 0 ? "ONTO2AI INTRODUCTION" : "CLOSING TAKEAWAY", {
        left: 76,
        top: 70,
        width: 360,
        height: 28,
      }, { fontSize: 14, bold: true, color: COLORS.cyan });
      addText(slide, titleFor(index, slideData), {
        left: 76,
        top: 124,
        width: 680,
        height: 138,
      }, { fontSize: index === 0 ? 54 : 48, bold: true, color: "#FFFFFF" });
      addText(slide, scene.text, { left: 80, top: 304, width: 560, height: 104 }, {
        fontSize: 22,
        color: "#DCEBFF",
      });
      addRound(slide, { left: 80, top: 560, width: 390, height: 46 }, "#0B1E33/86", COLORS.cyan);
      addText(slide, "From industry ontology to domain models", {
        left: 102,
        top: 572,
        width: 348,
        height: 24,
      }, { fontSize: 15, bold: true, color: COLORS.ink });
      return;
    }

    addChrome(slide, EYEBROWS[index], index + 1, total);
    addHeader(slide, EYEBROWS[index], titleFor(index, slideData), scene.text);

    if (index === 5) {
      addRound(slide, { left: 210, top: 456, width: 860, height: 78 }, "#122640", COLORS.blue);
      addRound(slide, { left: 290, top: 384, width: 700, height: 72 }, "#1C2840", COLORS.orange);
      addRound(slide, { left: 370, top: 318, width: 540, height: 66 }, "#2A2634", COLORS.amber);
      addText(slide, "TARGET ONTOLOGY", { left: 370, top: 338, width: 540, height: 28 }, { fontSize: 25, bold: true, alignment: "center" });
      addText(slide, "CONSOLIDATION", { left: 290, top: 406, width: 700, height: 28 }, { fontSize: 25, bold: true, alignment: "center" });
      addText(slide, "SOURCE PROVENANCE", { left: 210, top: 478, width: 860, height: 28 }, { fontSize: 25, bold: true, alignment: "center" });
    } else if (index === 8) {
      addCard(slide, "Source Ontology", "Inspect standards and enterprise source models.", 92, 330, 500, 118, COLORS.blue);
      addCard(slide, "Target Ontology", "Review and tune the working domain model.", 656, 330, 500, 118, COLORS.orange);
      addCard(slide, "Semantic Interaction", "Ask modelling questions with ontology context.", 92, 486, 500, 118, COLORS.cyan);
      addCard(slide, "Native Query", "Inspect and troubleshoot graph-native detail.", 656, 486, 500, 118, COLORS.amber);
    } else if (index === 3) {
      const labels = ["Load", "Inspect", "Select", "Extract", "Adapt"];
      for (let i = 0; i < labels.length; i++) {
        const x = 96 + i * 220;
        addRound(slide, { left: x, top: 388, width: 160, height: 92 }, i % 2 ? COLORS.panel2 : COLORS.panel, i % 2 ? COLORS.orange : COLORS.cyan);
        addText(slide, labels[i], { left: x + 18, top: 416, width: 124, height: 28 }, {
          fontSize: 22,
          bold: true,
          alignment: "center",
        });
        if (i < labels.length - 1) addRect(slide, { left: x + 166, top: 432, width: 48, height: 3 }, COLORS.line);
      }
    } else {
      addBulletCards(slide, slideData.bullets);
    }
  });

  for (const [index, slide] of deck.slides.items.entries()) {
    const stem = `template-slide-${String(index + 1).padStart(2, "0")}`;
    const png = await deck.export({ slide, format: "png", scale: 1 });
    await writeBlob(path.join(FRAME_DIR, `${stem}.png`), png);
    await writeBlob(path.join(PREVIEW_DIR, `${stem}.png`), png);
    await fs.writeFile(path.join(PREVIEW_DIR, `${stem}.layout.json`), await (await slide.export({ format: "layout" })).text());
  }
  await writeBlob(path.join(PREVIEW_DIR, "deck-montage.webp"), await deck.export({ format: "webp", montage: true, scale: 1 }));
  const pptx = await PresentationFile.exportPptx(deck);
  await pptx.save(OUT_DECK);
  console.log(OUT_DECK);
  console.log(FRAME_DIR);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
