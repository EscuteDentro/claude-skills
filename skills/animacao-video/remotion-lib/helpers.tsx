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
