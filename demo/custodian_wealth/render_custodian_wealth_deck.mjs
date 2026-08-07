import fs from "node:fs/promises";
import path from "node:path";
import { Presentation, PresentationFile } from "@oai/artifact-tool";

const ROOT = process.env.ONTO2AI_REPO_ROOT;
const MANIFEST = process.env.ONTO2AI_DEMO_MANIFEST;
const REF_IMAGE = process.env.ONTO2AI_REFERENCE_IMAGE;
const OUT_DECK = process.env.ONTO2AI_RENDERED_DECK;
const FRAME_DIR = process.env.ONTO2AI_FRAME_DIR;
const PREVIEW_DIR = process.env.ONTO2AI_PREVIEW_DIR || FRAME_DIR;
const MODELLER_ASSET_DIR = path.join(ROOT, "demo", "custodian_wealth", "assets", "modeller");

const W = 1280;
const H = 720;
const C = {
  night: "#080C18",
  panel: "#131A2B",
  panel2: "#172338",
  text: "#F4F7FC",
  muted: "#A9B4C7",
  blue: "#32B8FF",
  cyan: "#52E5E7",
  violet: "#7C5CFC",
  orange: "#FF8A35",
  amber: "#F9C74F",
  green: "#48D597",
  line: "#41506A",
};

async function writeBlob(file, blob) {
  await fs.writeFile(file, new Uint8Array(await blob.arrayBuffer()));
}

function rect(slide, position, fill, line = "none", radius = 0) {
  return slide.shapes.add({
    geometry: radius ? "roundRect" : "rect",
    position,
    fill,
    borderRadius: radius,
    line: { style: "solid", fill: line, width: line === "none" ? 0 : 1 },
  });
}

function text(slide, value, position, style = {}) {
  const shape = slide.shapes.add({
    geometry: "textbox",
    position,
    fill: "none",
    line: { style: "solid", fill: "none", width: 0 },
  });
  shape.text = value;
  shape.text.style = {
    fontSize: 22,
    color: C.text,
    fontFamily: "Aptos",
    ...style,
  };
  return shape;
}

function line(slide, x, y, width, color = C.line, height = 3) {
  return rect(slide, { left: x, top: y, width, height }, color);
}

function chrome(slide, index, total, label) {
  slide.background.fill = C.night;
  rect(slide, { left: 0, top: 0, width: W, height: 10 }, C.cyan);
  rect(slide, { left: 0, top: H - 8, width: W, height: 8 }, C.orange);
  text(slide, "Onto2AI Modeller", { left: 54, top: 666, width: 280, height: 26 }, {
    fontSize: 16, bold: true, color: C.cyan,
  });
  text(slide, label, { left: 430, top: 666, width: 420, height: 24 }, {
    fontSize: 14, color: C.muted, alignment: "center",
  });
  text(slide, `${String(index + 1).padStart(2, "0")} / ${String(total).padStart(2, "0")}`,
    { left: 1114, top: 666, width: 110, height: 24 },
    { fontSize: 15, color: C.muted, alignment: "right" });
}

function header(slide, titleValue, subtitle, eyebrow) {
  text(slide, eyebrow.toUpperCase(), { left: 68, top: 50, width: 340, height: 24 }, {
    fontSize: 13, bold: true, color: C.cyan,
  });
  text(slide, titleValue, { left: 68, top: 82, width: 1120, height: 58 }, {
    fontSize: 38, bold: true,
  });
  text(slide, subtitle || "", { left: 70, top: 142, width: 1060, height: 34 }, {
    fontSize: 19, color: C.muted,
  });
  line(slide, 68, 188, 1144, C.line, 1);
}

function card(slide, titleValue, body, x, y, width, height, accent = C.blue) {
  rect(slide, { left: x, top: y, width, height }, C.panel, "#2D3E59", 8);
  rect(slide, { left: x, top: y, width: 7, height }, accent);
  text(slide, titleValue, { left: x + 22, top: y + 18, width: width - 40, height: 30 }, {
    fontSize: 21, bold: true,
  });
  text(slide, body, { left: x + 22, top: y + 56, width: width - 40, height: height - 68 }, {
    fontSize: 16, color: C.muted,
  });
}

function node(slide, label, x, y, width = 180, accent = C.violet) {
  rect(slide, { left: x, top: y, width, height: 68 }, C.panel2, accent, 6);
  rect(slide, { left: x, top: y, width, height: 9 }, accent);
  text(slide, label, { left: x + 10, top: y + 25, width: width - 20, height: 24 }, {
    fontSize: 16, bold: true, alignment: "center",
  });
}

function arrow(slide, x1, y1, x2, y2, label = "") {
  const width = Math.max(20, Math.abs(x2 - x1));
  line(slide, Math.min(x1, x2), y1, width, C.line, 3);
  text(slide, "▶", { left: x2 - 8, top: y1 - 10, width: 24, height: 24 }, { fontSize: 15, color: C.line });
  if (label) text(slide, label, { left: Math.min(x1, x2), top: y1 - 28, width, height: 20 }, {
    fontSize: 12, color: C.muted, alignment: "center",
  });
}

function bulletRow(slide, bullets, y = 558) {
  bullets.slice(0, 3).forEach((bullet, index) => {
    const x = 70 + index * 390;
    rect(slide, { left: x, top: y, width: 360, height: 68 }, C.panel, "#293B55", 6);
    rect(slide, { left: x + 16, top: y + 25, width: 12, height: 12 }, [C.cyan, C.orange, C.green][index]);
    text(slide, bullet, { left: x + 40, top: y + 15, width: 302, height: 45 }, {
      fontSize: 14, color: C.muted,
    });
  });
}

function sourceSearchScene(slide) {
  rect(slide, { left: 64, top: 214, width: 260, height: 330 }, C.panel, "#2B3D58", 6);
  text(slide, "SOURCE ONTOLOGY", { left: 84, top: 232, width: 210, height: 24 }, { fontSize: 14, bold: true, color: C.cyan });
  rect(slide, { left: 82, top: 270, width: 224, height: 42 }, "#0D1423", "#40516D", 5);
  text(slide, "account", { left: 96, top: 281, width: 150, height: 22 }, { fontSize: 16 });
  ["account", "payment", "party", "financial instrument", "currency"].forEach((name, i) => {
    text(slide, name, { left: 92, top: 328 + i * 39, width: 200, height: 24 }, {
      fontSize: 15, color: i === 0 ? C.amber : C.muted, bold: i === 0,
    });
  });

  rect(slide, { left: 342, top: 214, width: 590, height: 330 }, "#0D1220", "#2B3D58", 6);
  node(slide, "account", 548, 340, 180, C.violet);
  node(slide, "party", 374, 246, 150, C.blue);
  node(slide, "payment", 748, 246, 150, C.orange);
  node(slide, "identifier", 374, 448, 150, C.green);
  node(slide, "currency", 748, 448, 150, C.amber);
  arrow(slide, 520, 281, 548, 281);
  arrow(slide, 728, 281, 748, 281);
  arrow(slide, 520, 481, 548, 481);
  arrow(slide, 728, 481, 748, 481);

  rect(slide, { left: 950, top: 214, width: 266, height: 330 }, C.panel, "#2B3D58", 6);
  text(slide, "PROPERTIES", { left: 970, top: 232, width: 210, height: 24 }, { fontSize: 14, bold: true, color: C.cyan });
  text(slide, "Class", { left: 970, top: 278, width: 90, height: 20 }, { fontSize: 13, color: C.muted });
  text(slide, "account", { left: 970, top: 302, width: 210, height: 26 }, { fontSize: 20, bold: true });
  text(slide, "Definition", { left: 970, top: 348, width: 100, height: 20 }, { fontSize: 13, color: C.muted });
  text(slide, "A record of financial activity and associated obligations.", { left: 970, top: 374, width: 218, height: 74 }, { fontSize: 15 });
  text(slide, "URI + relationships + properties", { left: 970, top: 470, width: 218, height: 44 }, { fontSize: 14, color: C.green });
}

function meaningReviewScene(slide) {
  rect(slide, { left: 66, top: 218, width: 700, height: 330 }, "#0D1220", "#2B3D58", 6);
  node(slide, "account", 326, 346, 180, C.violet);
  node(slide, "party", 102, 246, 150, C.blue);
  node(slide, "payment", 574, 246, 150, C.orange);
  node(slide, "identifier", 102, 448, 150, C.green);
  node(slide, "currency", 574, 448, 150, C.amber);
  arrow(slide, 252, 280, 326, 280, "owned by");
  arrow(slide, 506, 280, 574, 280, "used by");
  arrow(slide, 252, 482, 326, 482, "identified by");
  arrow(slide, 506, 482, 574, 482, "denominated in");

  card(slide, "DEFINITION", "A record of financial activity and associated obligations. Confirm the intended financial context.", 798, 218, 416, 92, C.blue);
  card(slide, "STABLE URI", "The identifier preserves source provenance even when Northstar adopts enterprise terminology.", 798, 330, 416, 92, C.orange);
  card(slide, "PROPERTIES + RELATIONSHIPS", "Review datatypes, cardinalities, inheritance, and incoming and outgoing semantic links.", 798, 442, 416, 106, C.green);
}

function targetGraphScene(slide) {
  const nodes = [
    ["Client", 535, 222, C.blue],
    ["Custody Account", 302, 326, C.violet],
    ["Portfolio", 535, 326, C.cyan],
    ["Service Agreement", 778, 326, C.orange],
    ["Holding", 302, 454, C.green],
    ["Cash Movement", 535, 454, C.amber],
    ["Settlement Instruction", 778, 454, C.orange],
  ];
  nodes.forEach(([label, x, y, color]) => node(slide, label, x, y, 190, color));
  line(slide, 630, 290, 3, C.line, 38);
  line(slide, 397, 395, 571, C.line, 3);
  line(slide, 397, 394, 3, C.line, 60);
  line(slide, 630, 394, 3, C.line, 60);
  line(slide, 873, 394, 3, C.line, 60);
}

function umlScene(slide) {
  const classes = [
    ["CustodianClient", ["clientRecordId: str", "clientDisplayName: str", "onboardingDate: date"], 100, 240],
    ["CustodyAccount", ["custodyAccountId: str", "baseCurrency: Currency", "status: AccountStatus"], 478, 240],
    ["CustodyPortfolio", ["portfolioId: str", "holdings: CustodyHolding[*]"], 856, 240],
  ];
  classes.forEach(([name, attrs, x, y], index) => {
    rect(slide, { left: x, top: y, width: 300, height: 220 }, C.panel, [C.blue, C.violet, C.green][index], 4);
    rect(slide, { left: x, top: y, width: 300, height: 48 }, [C.blue, C.violet, C.green][index]);
    text(slide, name, { left: x + 12, top: y + 12, width: 276, height: 25 }, { fontSize: 19, bold: true, alignment: "center" });
    attrs.forEach((attr, i) => text(slide, attr, { left: x + 20, top: y + 72 + i * 40, width: 260, height: 28 }, { fontSize: 15, color: C.muted }));
  });
  arrow(slide, 400, 350, 478, 350, "1..*");
  arrow(slide, 778, 350, 856, 350, "1..*");
}

function applicationSchemaScene(slide) {
  rect(slide, { left: 78, top: 220, width: 710, height: 330 }, "#0B101B", "#30415D", 6);
  const code = [
    ["class CustodyAccount(BaseModel):", C.cyan],
    ["    has_custody_account_id: str", C.text],
    ["    has_base_currency: str", C.text],
    ["    has_custody_portfolio: list[str]", C.text],
    ["    has_account_status: str", C.text],
    ["    has_settlement_instruction: list[str]", C.text],
    ["    records_cash_movement: list[CashMovement]", C.text],
  ];
  code.forEach(([value, color], i) => text(slide, value, { left: 106, top: 248 + i * 39, width: 650, height: 28 }, {
    fontSize: 18, color, fontFamily: "Menlo", bold: i === 0,
  }));
  card(slide, "Generated Contract", "Required fields, references, collections, enumerations, and validation rules remain traceable to the ontology.", 830, 220, 370, 144, C.orange);
  card(slide, "Multiple Targets", "Pydantic is one renderer. JSON Schema, TypeScript, Java, GraphQL, and other application models can share the same semantic source.", 830, 392, 370, 158, C.green);
}

function extractionScene(slide) {
  const steps = [
    ["FIBO", "Trusted source ontology", 72, C.blue],
    ["SEEDS", "Selected business concepts", 310, C.cyan],
    ["MCP", "Supporting neighborhood", 548, C.orange],
    ["STAGINGDB", "Governed working copy", 786, C.violet],
    ["TARGET", "Northstar vocabulary", 1024, C.green],
  ];
  steps.forEach(([titleValue, body, x, color], index) => {
    card(slide, titleValue, body, x, 302, 190, 150, color);
    if (index < steps.length - 1) arrow(slide, x + 190, 377, x + 232, 377);
  });
  text(slide, "FIBO remains unchanged", { left: 72, top: 480, width: 300, height: 26 }, { fontSize: 16, color: C.blue });
  text(slide, "source URI provenance retained", { left: 816, top: 480, width: 360, height: 26 }, { fontSize: 16, color: C.green, alignment: "right" });
}

function caseTraceScene(slide) {
  node(slide, "Harbor Ridge", 74, 316, 180, C.blue);
  node(slide, "USD Custody Account", 310, 316, 190, C.violet);
  node(slide, "Settlement 731", 556, 316, 180, C.orange);
  node(slide, "Cash Movement 731", 792, 316, 190, C.green);
  node(slide, "Payment Completed", 1038, 316, 180, C.amber);
  arrow(slide, 254, 350, 310, 350);
  arrow(slide, 500, 350, 556, 350);
  arrow(slide, 736, 350, 792, 350);
  arrow(slide, 982, 350, 1038, 350);
  text(slide, "NCT-USD-004218", { left: 310, top: 408, width: 190, height: 24 }, { fontSize: 14, color: C.muted, alignment: "center" });
  text(slide, "PAY-2026-000731", { left: 792, top: 408, width: 190, height: 24 }, { fontSize: 14, color: C.muted, alignment: "center" });
}

function semanticScene(slide) {
  rect(slide, { left: 84, top: 222, width: 1112, height: 330 }, C.panel, "#30415D", 8);
  text(slide, "SEMANTIC INTERACTION", { left: 112, top: 244, width: 280, height: 24 }, { fontSize: 14, bold: true, color: C.cyan });
  const prompts = [
    "Which FIBO concepts are unnecessary for this custody application?",
    "What is missing for settlement instruction lifecycle management?",
    "Does the target distinguish legal client, account owner, and beneficiary?",
  ];
  prompts.forEach((prompt, i) => {
    rect(slide, { left: 120, top: 292 + i * 72, width: 720, height: 52 }, "#0E1525", "#334764", 6);
    text(slide, prompt, { left: 140, top: 306 + i * 72, width: 680, height: 30 }, { fontSize: 16 });
  });
  rect(slide, { left: 876, top: 292, width: 282, height: 196 }, "#101D2C", C.green, 6);
  text(slide, "GRAPH-GROUNDED", { left: 900, top: 316, width: 234, height: 24 }, { fontSize: 14, bold: true, color: C.green, alignment: "center" });
  text(slide, "Discussion is grounded in the selected source concepts and the customized target ontology.", { left: 902, top: 362, width: 230, height: 100 }, { fontSize: 18, alignment: "center" });
}

function validationScene(slide) {
  const checks = [
    ["SOURCE", "5 exact FIBO/Commons seeds", C.blue],
    ["TARGET", "12 classes and 34 properties", C.orange],
    ["DATA", "21 instances and 26 relationships", C.green],
    ["TRACE", "1 client-to-payment path", C.violet],
  ];
  checks.forEach(([titleValue, body, color], i) => {
    const x = 94 + (i % 2) * 570;
    const y = 230 + Math.floor(i / 2) * 170;
    card(slide, `✓  ${titleValue}`, body, x, y, 520, 132, color);
  });
  rect(slide, { left: 286, top: 574, width: 708, height: 48 }, "#153326", C.green, 7);
  text(slide, "PROTOTYPE ACCEPTED  •  READY FOR RDF + RELEASE GATES", { left: 310, top: 587, width: 660, height: 24 }, { fontSize: 17, bold: true, color: C.green, alignment: "center" });
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
  const modellerScenes = new Map([
    [2, "01-source-account-preview.png"],
    [3, "01-source-account-preview.png"],
    [4, "02-source-extraction-seeds.png"],
    [5, "04-target-ontology.png"],
    [6, "05-uml-schema.png"],
    [7, "06-application-schema.png"],
    [9, "07-semantic-interaction.png"],
    [10, "08-native-query-validation.png"],
  ]);
  const modellerImages = new Map();
  for (const [index, fileName] of modellerScenes) {
    modellerImages.set(index, await fs.readFile(path.join(MODELLER_ASSET_DIR, fileName)));
  }
  const deck = Presentation.create({ slideSize: { width: W, height: H } });
  const total = source.slides.length;

  source.slides.forEach((slideData, index) => {
    const slide = deck.slides.add();
    if (index === 0 || index === total - 1) {
      slide.images.add({
        blob: imageBytes,
        contentType: "image/png",
        alt: "Onto2AI visual identity",
        fit: "cover",
        position: { left: 0, top: 0, width: W, height: H },
      });
      rect(slide, { left: 0, top: 0, width: W, height: H }, index === 0 ? "#030816/64" : "#030816/74");
      rect(slide, { left: 0, top: 0, width: 720, height: H }, "#050A16/72");
      text(slide, index === 0 ? "ONTO2AI MODELLER DEMO" : "PUBLICATION PATH", { left: 70, top: 72, width: 470, height: 28 }, { fontSize: 15, bold: true, color: C.cyan });
      text(slide, slideData.title, { left: 70, top: 126, width: 690, height: 150 }, { fontSize: index === 0 ? 50 : 44, bold: true });
      text(slide, slideData.subtitle || "", { left: 74, top: 304, width: 590, height: 62 }, { fontSize: 22, color: C.muted });
      rect(slide, { left: 72, top: 526, width: 520, height: 70 }, "#0B1B2F/90", C.cyan, 7);
      text(slide, index === 0 ? "Northstar Custody Bank • fictional worked example" : "northstar-client-ontology • planned release artifact", { left: 96, top: 548, width: 472, height: 30 }, { fontSize: 17, bold: true, alignment: "center" });
      return;
    }

    const modellerImage = modellerImages.get(index);
    if (modellerImage) {
      slide.images.add({
        blob: modellerImage,
        contentType: "image/png",
        alt: `Onto2AI Modeller - ${slideData.title}`,
        fit: "cover",
        position: { left: 0, top: 0, width: W, height: H },
      });
      if (index >= 5 && index <= 7) {
        rect(slide, { left: 0, top: 680, width: W, height: 40 }, "#050A16/92");
        text(slide, `STEP ${String(index + 1).padStart(2, "0")}  •  ${slideData.title}`, { left: 44, top: 688, width: 1192, height: 22 }, {
          fontSize: 15, bold: true, color: C.text,
        });
        return;
      }
      rect(slide, { left: 0, top: 590, width: W, height: 130 }, "#050A16/92");
      text(slide, `STEP ${String(index + 1).padStart(2, "0")}  •  ${slideData.title}`, { left: 54, top: 606, width: 1172, height: 36 }, {
        fontSize: 24, bold: true, color: C.text,
      });
      text(slide, slideData.bullets.join("  •  "), { left: 56, top: 650, width: 1168, height: 42 }, {
        fontSize: 15, color: C.muted,
      });
      return;
    }

    chrome(slide, index, total, slideData.subtitle || "Custodian wealth-management workflow");
    header(slide, slideData.title, slideData.subtitle, ["Challenge", "Source Ontology", "Ontology View", "Extraction", "Target Ontology", "UML Schema", "Application Schema", "Design Loop", "Semantic Interaction", "Finalization"][index - 1]);

    if (index === 1) {
      card(slide, "Business Language", "Client, account, portfolio, holding, payment, and settlement overlap across business lines.", 72, 248, 350, 220, C.blue);
      card(slide, "Operational Meaning", "Custody, wealth, operations, and compliance attach different obligations to the same words.", 465, 248, 350, 220, C.orange);
      card(slide, "Application Risk", "Code-first models make unresolved assumptions expensive and difficult to govern.", 858, 248, 350, 220, C.green);
      bulletRow(slide, slideData.bullets);
    } else if (index === 2) {
      sourceSearchScene(slide);
    } else if (index === 3) {
      meaningReviewScene(slide);
    } else if (index === 4) {
      extractionScene(slide);
      bulletRow(slide, slideData.bullets, 548);
    } else if (index === 5) {
      targetGraphScene(slide);
      bulletRow(slide, slideData.bullets, 552);
    } else if (index === 6) {
      umlScene(slide);
      bulletRow(slide, slideData.bullets, 548);
    } else if (index === 7) {
      applicationSchemaScene(slide);
      bulletRow(slide, slideData.bullets, 566);
    } else if (index === 8) {
      caseTraceScene(slide);
      bulletRow(slide, slideData.bullets, 570);
    } else if (index === 9) {
      semanticScene(slide);
      bulletRow(slide, slideData.bullets, 570);
    } else if (index === 10) {
      validationScene(slide);
    }
  });

  for (const [index, slide] of deck.slides.items.entries()) {
    const stem = `custodian-slide-${String(index + 1).padStart(2, "0")}`;
    await writeBlob(path.join(FRAME_DIR, `${stem}.png`), await deck.export({ slide, format: "png", scale: 1 }));
    await writeBlob(path.join(PREVIEW_DIR, `${stem}.png`), await deck.export({ slide, format: "png", scale: 1 }));
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
