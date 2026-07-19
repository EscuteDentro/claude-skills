/**
 * animacao-video — biblioteca de componentes Remotion reutilizaveis.
 *
 * Extraidos de um projeto real (video narrado -> motion graphics em camadas,
 * estilo claymation). Cada tecnica aqui resolveu um problema especifico visto
 * na pratica — o comentario em cada uma explica o porque, nao so o o-que.
 *
 * Copiar este arquivo para src/helpers.tsx do seu projeto Remotion e importar
 * o que precisar. Ver exemplo-composicao.tsx para um uso completo, e
 * SKILL.md para o fluxo de producao inteiro (geracao de assets -> transcricao
 * -> composicao -> render).
 */
import {
  AbsoluteFill,
  Easing,
  Img,
  interpolate,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import React from "react";

export const FPS = 30;

/** Helper pra referenciar assets em public/assets/. Ajuste o prefixo se sua
 * estrutura de pastas for diferente. */
export const asset = (name: string) => staticFile(`assets/${name}`);

// ── Fundo com Ken Burns ancorado ──────────────────────────────────────────
//
// PEGADINHA (perdi tempo real com isso): `transform: scale(x)` sem
// transformOrigin explicito escala a partir do CENTRO do elemento. Se seu
// fundo tem um elemento importante perto de uma borda (uma faixa de chao,
// uma silhueta no horizonte) e voce quer que o zoom "puxe mais dela pra
// dentro do quadro" em vez de empurrar pra fora, PRECISA de
// transformOrigin correspondente aquela borda ("center bottom", "center
// top", etc). Sem isso o zoom faz o oposto do esperado.
export const KenBurnsBg: React.FC<{
  src: string;
  frames: number;
  zoomOut?: boolean;
  baseScale?: number;
  transformOrigin?: string;
  clipPath?: string;
}> = ({ src, frames, zoomOut, baseScale = 1, transformOrigin = "center center", clipPath }) => {
  const frame = useCurrentFrame();
  const start = zoomOut ? baseScale * 1.16 : baseScale;
  const target = zoomOut ? baseScale : baseScale * 1.12;
  const scale = interpolate(frame, [0, frames], [start, target], { extrapolateRight: "clamp" });
  return (
    <AbsoluteFill style={{ overflow: "hidden", clipPath }}>
      <Img
        src={asset(src)}
        style={{
          width: "100%",
          height: "100%",
          objectFit: "cover",
          transform: `scale(${scale})`,
          transformOrigin,
        }}
      />
    </AbsoluteFill>
  );
};

// ── Oclusao de primeiro plano ("atras de X") ──────────────────────────────
//
// Técnica pra fazer um elemento (ex: sol descendo) parecer que passa POR
// TRAS de uma parte do fundo (ex: dunas, montanhas, prédios no horizonte):
// renderiza a MESMA imagem de fundo, com o MESMO scale/transformOrigin (pra
// ficar pixel-alinhada), so que recortada via clip-path só na faixa que deve
// ficar por cima — e essa copia entra DEPOIS (por cima, no JSX) do elemento
// que deve "desaparecer atras". clipPath="inset(69% 0 0 0)" = mostra só o
// que sobra dos 69% pra baixo (ajustar a porcentagem pra sua imagem).
export const ForegroundOcclusion: React.FC<{
  src: string;
  frames: number;
  zoomOut?: boolean;
  baseScale?: number;
  transformOrigin?: string;
  clipPath: string;
}> = (props) => <KenBurnsBg {...props} />;

// ── Parallax por profundidade ──────────────────────────────────────────────
//
// Adaptado do mecanismo de scroll-parallax de sites 2.5D (ex: kits de
// "cinematic scroll"): la, cada camada recebe um translateY proporcional a
// quao perto ela esta (fundo desloca pouco, primeiro plano desloca muito),
// dirigido pelo progresso de scroll. Aqui o driver e o FRAME em vez do
// scroll, e como a "camera" deste sistema e zoom (Ken Burns), profundidade
// vira ESCALA extra em vez de deslocamento: objetos mais perto crescem mais
// rapido que os mais longe conforme o tempo passa, como um zoom real.
// Sem isso, elementos em camada ficam com o mesmo tamanho fixo a cena
// inteira enquanto so o fundo se move — com isso, cada camada tem parallax
// de verdade entre si, nao so o fundo.
export function parallaxScale(frame: number, totalFrames: number, depth: number, intensity = 0.15) {
  if (!depth) return 1;
  return interpolate(frame, [0, totalFrames], [1, 1 + depth * intensity], {
    extrapolateRight: "clamp",
  });
}

// Crash zoom: zoom rapido e abrupto que "aterrissa" numa composicao (em vez
// do Ken Burns suave/continuo). Easing.in(cubic) acelera conforme aproxima
// do final — comeca quase parado, "atropela" no fim. Usar pra transicoes de
// corte forte (aproximar ate um detalhe pra virar outra cena). `maxScale`
// grande (>15x) funciona bem pra um detalhe pequeno (testa, olho); pra
// aproximar um objeto inteiro, algo entre 2x-6x.
export function crashZoomScale(frame: number, totalFrames: number, maxScale: number) {
  return interpolate(frame, [0, totalFrames], [1, maxScale], {
    extrapolateRight: "clamp",
    easing: Easing.in(Easing.cubic),
  });
}

// ── Tilt-shift (efeito miniatura/diorama) ─────────────────────────────────
// Banda horizontal nitida + blur gradual acima/abaixo — reforca a leitura
// de "diorama"/maquete em qualquer cena claymation ou motion graphics em
// camadas. Mecanismo: renderiza o conteudo 2x, a segunda copia com blur e
// mascarada por um gradiente (nitido nas pontas do gradiente = onde o blur
// aparece, transparente no meio = onde a copia sharp de baixo aparece).
// Calibrar bandCenterPct/bandHalfWidthPct pra cobrir o SUJEITO PRINCIPAL
// inteiro (cabeca a pes) — cortar isso borra o rosto e quebra o efeito.
export const TiltShiftWrapper: React.FC<{
  children: React.ReactNode;
  bandCenterPct?: number;
  bandHalfWidthPct?: number;
  featherPct?: number;
  blurPx?: number;
}> = ({ children, bandCenterPct = 55, bandHalfWidthPct = 20, featherPct = 12, blurPx = 14 }) => {
  const a = bandCenterPct - bandHalfWidthPct - featherPct;
  const b = bandCenterPct - bandHalfWidthPct;
  const c = bandCenterPct + bandHalfWidthPct;
  const d = bandCenterPct + bandHalfWidthPct + featherPct;
  const mask = `linear-gradient(to bottom, white 0%, white ${a}%, transparent ${b}%, transparent ${c}%, white ${d}%, white 100%)`;
  return (
    <AbsoluteFill>
      {children}
      <AbsoluteFill
        style={{ filter: `blur(${blurPx}px)`, WebkitMaskImage: mask, maskImage: mask, WebkitMaskMode: "alpha", maskMode: "alpha" }}
      >
        {children}
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

// ── Truck/slider lateral (translateX puro, sem escala) ────────────────────
// Deslocamento lateral continuo da camera fisica. So fica com profundidade
// de verdade quando cada CAMADA se move a uma taxa diferente (perto anda
// mais, longe anda menos) — nao mover a cena inteira como bloco rigido (isso
// e so "pan", nao demonstra parallax nenhum). Exemplo de uso por camada:
//   const x = interpolate(frame, [0, total], [-70*depth, 70*depth]);
//   <div style={{ transform: `translateX(${x}px)` }}>...</div>
// ATENCAO (bug comum): se o wrapper que recebe o translateX for o proprio
// viewport (AbsoluteFill sem overflow:hidden fixo por fora), o pan expoe
// borda vazia/preta no lado que "sobra". Sempre manter um AbsoluteFill
// externo fixo com overflow:hidden, e aplicar o transform + margem extra
// (scale ~1.1-1.2) só no filho que se move.

// ── Handheld sway (micro-jitter organico) ──────────────────────────────────
// Jitter pequeno e continuo via soma de senos com frequencias incomensu-
// raveis (nao periodicas em ciclos curtos, parece organico em vez de
// mecanico). Da sensacao de "vivo"/documental. Mesmo cuidado de borda do
// truck: aplicar scale de margem extra (~1.05-1.08) no wrapper que se move.
function handheldNoise(frame: number) {
  const x = Math.sin(frame * 0.19) * 2.4 + Math.sin(frame * 0.071) * 1.6;
  const y = Math.sin(frame * 0.13 + 1.7) * 2.1 + Math.sin(frame * 0.053 + 0.4) * 1.3;
  const r = Math.sin(frame * 0.09 + 0.9) * 0.35;
  return { x, y, r };
}

export const HandheldWrapper: React.FC<{ children: React.ReactNode; margin?: number }> = ({ children, margin = 1.06 }) => {
  const frame = useCurrentFrame();
  const { x, y, r } = handheldNoise(frame);
  return (
    <AbsoluteFill style={{ overflow: "hidden" }}>
      <AbsoluteFill style={{ transform: `scale(${margin}) translate(${x}px, ${y}px) rotate(${r}deg)`, transformOrigin: "center center" }}>
        {children}
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

// ── Entrada com mola (pop-in) ──────────────────────────────────────────────
export const PopIn: React.FC<{
  children: React.ReactNode;
  delay?: number;
  style?: React.CSSProperties;
  /** 0 (fundo) a 1 (primeiro plano). So ativa parallax se totalFrames tambem for passado. */
  depth?: number;
  totalFrames?: number;
}> = ({ children, delay = 0, style, depth = 0, totalFrames }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const local = frame - delay;
  const s = spring({ frame: local, fps, config: { damping: 12, mass: 0.6 } });
  const opacity = interpolate(local, [0, 8], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const parallax = totalFrames ? parallaxScale(frame, totalFrames, depth) : 1;
  return (
    <div
      style={{
        ...style,
        transform: `scale(${(local < 0 ? 0 : s) * parallax})`,
        opacity: local < 0 ? 0 : opacity,
      }}
    >
      {children}
    </div>
  );
};

// ── Flutua pra cima e desaparece (bolhas, particulas, "leveza") ──────────
export const FloatUpFade: React.FC<{
  children: React.ReactNode;
  delay?: number;
  distance?: number;
  duration?: number;
  style?: React.CSSProperties;
}> = ({ children, delay = 0, distance = 260, duration = 110, style }) => {
  const frame = useCurrentFrame();
  const local = Math.max(0, frame - delay);
  const y = interpolate(local, [0, duration], [0, -distance], { extrapolateRight: "clamp" });
  const opacity = interpolate(local, [0, duration * 0.25, duration], [0, 1, 0], {
    extrapolateRight: "clamp",
  });
  return (
    <div style={{ ...style, transform: `translateY(${y}px)`, opacity: frame < delay ? 0 : opacity }}>
      {children}
    </div>
  );
};

// ── Desce e desaparece (peso caindo, algo se dissolvendo) ────────────────
export const DissolveDown: React.FC<{
  children: React.ReactNode;
  delay?: number;
  distance?: number;
  duration?: number;
  style?: React.CSSProperties;
}> = ({ children, delay = 0, distance = 140, duration = 110, style }) => {
  const frame = useCurrentFrame();
  const local = Math.max(0, frame - delay);
  const y = interpolate(local, [0, duration], [0, distance], { extrapolateRight: "clamp" });
  const opacity = interpolate(local, [0, duration], [1, 0], { extrapolateRight: "clamp" });
  return (
    <div style={{ ...style, transform: `translateY(${y}px)`, opacity: frame < delay ? 1 : opacity }}>
      {children}
    </div>
  );
};

// ── Personagem fixo, reaproveitado em varias cenas ────────────────────────
//
// Por que reaproveitar o MESMO PNG recortado em vez de gerar o personagem de
// novo em cada cena: cada geracao de imagem por IA e independente, nao ha
// "memoria" de uma cena pra outra — gerar de novo quebra a consistencia
// visual (cor, proporcao, expressao mudam sutilmente a cada chamada). Gerar
// UMA VEZ, aprovar, remover o fundo, e so entao posicionar/escalar/animar
// esse mesmo arquivo em cada cena via CSS resolve isso.
export const Character: React.FC<{ src: string; scale?: number; top?: string; widthPct?: number }> = ({
  src,
  scale = 1,
  top = "20%",
  widthPct = 64,
}) => (
  <AbsoluteFill style={{ alignItems: "center" }}>
    <div style={{ position: "absolute", top, width: `${widthPct}%`, transform: `scale(${scale})` }}>
      <Img src={asset(src)} style={{ width: "100%", display: "block" }} />
    </div>
  </AbsoluteFill>
);

// ── Legendas com timing REAL por palavra ──────────────────────────────────
//
// Por que nao "N frames por palavra" fixo: fala humana nao tem cadencia
// constante (pausas, palavras longas x curtas). Um reveal com passo fixo
// sente "errado" mesmo se a duracao total bater — fica devagar-devagar-
// -rapidorapidorapido. A solucao e pegar timestamp real por palavra (via
// Whisper, --word_timestamps True — o fscript e outras ferramentas de
// transcricao geralmente so dao timestamp por FRASE) e revelar cada palavra
// exatamente quando ela e dita.
//
// buildGroups quebra um roteiro longo em blocos curtos (~5 palavras, ajustar
// `size`) pra caber em 1-2 linhas na tela, e calcula o frame de entrada de
// cada palavra dentro do bloco a partir do timestamp real.
export type TimedWord = { word: string; start: number; end: number };

export function buildGroups(words: TimedWord[], sceneEndFrame: number, size = 5, fps = FPS) {
  const groups: { from: number; to: number; words: { text: string; at: number }[] }[] = [];
  for (let i = 0; i < words.length; i += size) {
    const slice = words.slice(i, i + size);
    const from = Math.round(slice[0].start * fps);
    const nextSlice = words[i + size];
    const to = nextSlice ? Math.round(nextSlice.start * fps) : sceneEndFrame;
    groups.push({
      from,
      to,
      words: slice.map((w) => ({ text: w.word, at: Math.round(w.start * fps) - from })),
    });
  }
  return groups;
}

export type CaptionGroup = ReturnType<typeof buildGroups>[number];

/** Estilo "massinha": contorno grosso + camadas de sombra empilhadas simulam
 * profundidade 3D sem precisar de fonte customizada. Ajustar cores/espessura
 * pro seu estilo visual — o principio (stroke grosso + shadow em camadas
 * escalonadas) vale pra qualquer efeito "esculpido/brinquedo". */
export const CLAY_TEXT_STYLE: React.CSSProperties = {
  fontFamily: "'Arial Rounded MT Bold', ui-rounded, system-ui, sans-serif",
  fontWeight: 800,
  color: "#ffedcf",
  WebkitTextStroke: "9px #3a2010",
  paintOrder: "stroke fill",
  textShadow: "0 3px 0 #3a2010, 0 6px 0 #2c1809, 0 9px 0 #2c1809, 0 13px 22px rgba(0,0,0,0.5)",
  lineHeight: 1.12,
  display: "inline-block",
};

/** Renderiza o grupo de legenda ativo no frame atual, revelando palavra por
 * palavra no timestamp real de cada uma. Sem caixa/fundo — texto puro
 * posicionado dentro da faixa central de seguranca (evita corte por UI do
 * Reels/TikTok/Shorts, que cobre topo e base). */
export const Captions: React.FC<{ groups: CaptionGroup[]; fontSize?: number; top?: string }> = ({
  groups,
  fontSize = 62,
  top = "66%",
}) => {
  const frame = useCurrentFrame();
  const current = groups.find((c) => frame >= c.from && frame < c.to);
  if (!current) return null;
  const local = frame - current.from;
  const revealCount = current.words.filter((w) => local >= w.at).length || 1;
  return (
    <AbsoluteFill style={{ alignItems: "center" }}>
      <div style={{ position: "absolute", top, maxWidth: "90%", textAlign: "center" }}>
        <span style={{ ...CLAY_TEXT_STYLE, fontSize }}>
          {current.words
            .slice(0, revealCount)
            .map((w) => w.text)
            .join(" ")}
        </span>
      </div>
    </AbsoluteFill>
  );
};

// ── Tipografia com glifos recortados (letras de verdade, nao CSS) ─────────
//
// Alternativa ao CLAY_TEXT_STYLE: em vez de simular textura com contorno+
// sombra, usa letras geradas de verdade no estilo do vídeo, recortadas com
// scripts/recortar_alfabeto.py (gera um glifos.json com {char: {file,w,h}}).
// Testado num título de capa real — ficou mais integrado visualmente que o
// CSS puro. Cada glifo é escalado pela altura de crop (w/h do glifos.json)
// pra uma ALTURA ALVO comum. Pré-requisito: os crops precisam ter proporção
// tinta/altura consistente entre linhas da folha original (ver SKILL.md,
// secao "Bug recorrente — tamanho inconsistente entre linhas") — corrigir
// isso nos PNGs/glifos.json antes de usar aqui, nao em runtime.
export type GlyphMeta = { file: string; w: number; h: number };
export type GlyphTable = Record<string, GlyphMeta>;

// Sombra opcional (drop-shadow segue o alpha do PNG, ao contrario de
// box-shadow) pra dar contraste contra fundos de tom proximo ao da massinha
// (ceu bege/laranja/dourado, tipico em cenas de por-do-sol). Empilhar 2-3
// camadas simula o contorno+sombra em camadas do CLAY_TEXT_STYLE em CSS.
export const GLYPH_SHADOW_DEFAULT =
  "drop-shadow(0 2px 0 #2c1809) drop-shadow(0 4px 0 #2c1809) drop-shadow(0 7px 10px rgba(0,0,0,0.55))";

function layoutGlyphLines(
  text: string,
  glyphs: GlyphTable,
  maxWidthPx: number,
  targetHeight: number,
  gap: number
) {
  const wordWidth = (word: string) =>
    Array.from(word).reduce((sum, ch) => {
      const g = glyphs[ch];
      if (!g) return sum; // caractere sem glifo: ignora
      return sum + (g.w * targetHeight) / g.h + gap;
    }, -gap);
  const spaceWidth = targetHeight * 0.32;

  const lines: string[][] = [[]];
  let cur = 0;
  for (const word of text.split(" ")) {
    const ww = wordWidth(word);
    const extra = cur > 0 ? spaceWidth : 0;
    if (cur + extra + ww > maxWidthPx && cur > 0) {
      lines.push([]);
      cur = 0;
    }
    if (cur > 0) cur += spaceWidth;
    lines[lines.length - 1].push(word);
    cur += ww;
  }
  return lines;
}

const GlyphLine: React.FC<{ words: string[]; glyphs: GlyphTable; targetHeight: number; gap?: number; shadow?: string }> = ({
  words,
  glyphs,
  targetHeight,
  gap = 6,
  shadow,
}) => {
  const spaceWidth = targetHeight * 0.32;
  let cursor = 0;
  const items: { file: string; x: number; w: number }[] = [];
  words.forEach((word, wi) => {
    if (wi > 0) cursor += spaceWidth;
    for (const ch of Array.from(word)) {
      const g = glyphs[ch];
      if (!g) continue;
      const scaledW = (g.w * targetHeight) / g.h;
      items.push({ file: g.file, x: cursor, w: scaledW });
      cursor += scaledW + gap;
    }
  });
  return (
    <div style={{ position: "relative", height: targetHeight, width: cursor - gap, filter: shadow }}>
      {items.map((it, i) => (
        <Img
          key={i}
          src={asset(`alfabeto/${it.file}.png`)}
          style={{ position: "absolute", left: it.x, top: 0, width: it.w, height: targetHeight }}
        />
      ))}
    </div>
  );
};

/** Tipografa um texto com glifos recortados (ver glifos.json de
 * recortar_alfabeto.py), quebrando linha automaticamente pra caber em
 * maxWidthPx, cada linha centralizada. Assume minúsculas (lowercase o
 * texto de entrada) — gerar maiúsculas também se seu estilo precisar.
 * `shadow`: passar GLYPH_SHADOW_DEFAULT (ou uma variante) se o fundo da cena
 * tiver pouco contraste com a cor da massinha. */
export const GlyphText: React.FC<{
  text: string;
  glyphs: GlyphTable;
  maxWidthPx: number;
  targetHeight: number;
  lineGap?: number;
  shadow?: string;
}> = ({ text, glyphs, maxWidthPx, targetHeight, lineGap = 14, shadow }) => {
  const lines = layoutGlyphLines(text.toLowerCase(), glyphs, maxWidthPx, targetHeight, 6);
  return (
    <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: lineGap }}>
      {lines.map((words, i) => (
        <GlyphLine key={i} words={words} glyphs={glyphs} targetHeight={targetHeight} shadow={shadow} />
      ))}
    </div>
  );
};
