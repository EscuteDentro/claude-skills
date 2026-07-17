/**
 * Exemplo minimo de uso do helpers.tsx — NAO e um projeto real, e um
 * esqueleto pra copiar e adaptar. Nomes de asset e texto sao ficticios.
 *
 * Fluxo real: gere os assets com scripts/gerar_asset.py, transcreva o audio
 * com scripts/transcrever.sh, preencha os TimedWord[] com o resultado
 * (reconciliado com o texto do seu roteiro, ver SKILL.md Fase 3), calcule as
 * fronteiras de cena, e monte as cenas como no exemplo abaixo.
 */
import { AbsoluteFill, Audio, Composition, Sequence, staticFile } from "remotion";
import React from "react";
import {
  Captions,
  Character,
  FloatUpFade,
  KenBurnsBg,
  PopIn,
  TimedWord,
  buildGroups,
} from "./helpers";

const FPS = 30;

// Fronteiras de cena (frames), derivadas da transcricao real do seu audio.
const S = {
  cena1: [0, 90],
  cena2: [90, 220],
} as const;

// Timing por palavra da cena 2, no formato que sai da reconciliacao
// roteiro x whisper (ver SKILL.md Fase 3).
const CENA2_WORDS: TimedWord[] = [
  { word: "Um", start: 3.0, end: 3.2 },
  { word: "exemplo", start: 3.2, end: 3.6 },
  { word: "de", start: 3.6, end: 3.7 },
  { word: "legenda", start: 3.7, end: 4.1 },
  { word: "sincronizada.", start: 4.1, end: 4.6 },
];

const CAPTION_GROUPS = buildGroups(CENA2_WORDS, S.cena2[1]);

const Cena1: React.FC = () => (
  <AbsoluteFill>
    <KenBurnsBg src="fundo.png" frames={S.cena1[1] - S.cena1[0]} baseScale={1.8} transformOrigin="center bottom" />
    <PopIn delay={0} style={{ position: "absolute", top: "10%", left: "50%", marginLeft: -100, width: 200 }}>
      <img src={staticFile("assets/objeto-a.png")} style={{ width: "100%" }} alt="" />
    </PopIn>
  </AbsoluteFill>
);

const Cena2: React.FC = () => (
  <AbsoluteFill>
    <KenBurnsBg src="fundo.png" frames={S.cena2[1] - S.cena2[0]} baseScale={1.8} transformOrigin="center bottom" />
    <Character src="personagem-cutout.png" top="24%" />
    <FloatUpFade delay={20} style={{ position: "absolute", top: "12%", left: "10%", width: 150 }}>
      <img src={staticFile("assets/particula.png")} style={{ width: "100%" }} alt="" />
    </FloatUpFade>
  </AbsoluteFill>
);

const MainVideo: React.FC = () => (
  <AbsoluteFill style={{ backgroundColor: "#000" }}>
    <Audio src={staticFile("narracao.mp3")} />
    <Sequence from={S.cena1[0]} durationInFrames={S.cena1[1] - S.cena1[0]}>
      <Cena1 />
    </Sequence>
    <Sequence from={S.cena2[0]} durationInFrames={S.cena2[1] - S.cena2[0]}>
      <Cena2 />
    </Sequence>
    <Captions groups={CAPTION_GROUPS} />
  </AbsoluteFill>
);

export const ExemploComposition = () => (
  <Composition
    id="Exemplo"
    component={MainVideo}
    durationInFrames={S.cena2[1]}
    fps={FPS}
    width={1080}
    height={1920}
  />
);
