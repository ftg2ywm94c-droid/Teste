import React from "react";
import { Composition } from "remotion";
import { PisaShort, PISA_FRAMES } from "./videos/pisa/Pisa";
import { BridgeShort, BRIDGE_FRAMES } from "./videos/bridge/Bridge";
import { ApagaoShort, APAGAO_FRAMES } from "./videos/apagao/Apagao";
import { LuzShort, LUZ_FRAMES } from "./videos/luz/Luz";
import { VendavalShort, VENDAVAL_FRAMES } from "./videos/vendaval/Vendaval";
import { OnibusShort, ONIBUS_FRAMES } from "./videos/onibus/Onibus";
import { Vendaval2Short, VENDAVAL2_FRAMES } from "./videos/vendaval2/Vendaval2";
import { Onibus2Short, ONIBUS2_FRAMES } from "./videos/onibus2/Onibus2";
// Cada desenho novo: copie templates/pisa/ para src/videos/<nome>/, renomeie e registre aqui.
export const Root: React.FC = () => (
  <>
    <Composition id="PisaShort" component={PisaShort} durationInFrames={PISA_FRAMES} fps={30} width={1080} height={1920} />
    <Composition id="ApagaoShort" component={ApagaoShort} durationInFrames={APAGAO_FRAMES} fps={30} width={1080} height={1920} />
    <Composition id="LuzShort" component={LuzShort} durationInFrames={LUZ_FRAMES} fps={30} width={1080} height={1920} />
    <Composition id="VendavalShort" component={VendavalShort} durationInFrames={VENDAVAL_FRAMES} fps={30} width={1080} height={1920} />
    <Composition id="OnibusShort" component={OnibusShort} durationInFrames={ONIBUS_FRAMES} fps={30} width={1080} height={1920} />
    <Composition id="Vendaval2Short" component={Vendaval2Short} durationInFrames={VENDAVAL2_FRAMES} fps={30} width={1080} height={1920} />
    <Composition id="Onibus2Short" component={Onibus2Short} durationInFrames={ONIBUS2_FRAMES} fps={30} width={1080} height={1920} />
    <Composition id="BridgeShort" component={BridgeShort} durationInFrames={BRIDGE_FRAMES} fps={30} width={1080} height={1920} />
  </>
);
