import { Composition, Folder, Series } from "remotion";
import { Welcome } from "./Welcome";
import { Import } from "./Import";
import { Manual } from "./Manual";
import { Holdings } from "./Holdings";
import { Breakdown } from "./Breakdown";
import { Returns } from "./Returns";
import { Trend } from "./Trend";
import { Close } from "./Close";
export const PortfolioDemo = () => <Series>
  <Series.Sequence name="Welcome" durationInFrames={494}><Welcome /></Series.Sequence>
  <Series.Sequence name="Import" durationInFrames={669}><Import /></Series.Sequence>
  <Series.Sequence name="Manual" durationInFrames={570}><Manual /></Series.Sequence>
  <Series.Sequence name="Holdings" durationInFrames={684}><Holdings /></Series.Sequence>
  <Series.Sequence name="Breakdown" durationInFrames={630}><Breakdown /></Series.Sequence>
  <Series.Sequence name="Returns" durationInFrames={654}><Returns /></Series.Sequence>
  <Series.Sequence name="Trend" durationInFrames={667}><Trend /></Series.Sequence>
  <Series.Sequence name="Close" durationInFrames={572}><Close /></Series.Sequence>
</Series>;
export const DemoCompositions = () => <>
  <Composition id="StockPortfolioDemo" component={PortfolioDemo} width={1920} height={1080} fps={30} durationInFrames={4940} />
  <Folder name="Scenes">
    <Composition id="Welcome" component={Welcome} width={1920} height={1080} fps={30} durationInFrames={494} />
    <Composition id="Import" component={Import} width={1920} height={1080} fps={30} durationInFrames={669} />
    <Composition id="Manual" component={Manual} width={1920} height={1080} fps={30} durationInFrames={570} />
    <Composition id="Holdings" component={Holdings} width={1920} height={1080} fps={30} durationInFrames={684} />
    <Composition id="Breakdown" component={Breakdown} width={1920} height={1080} fps={30} durationInFrames={630} />
    <Composition id="Returns" component={Returns} width={1920} height={1080} fps={30} durationInFrames={654} />
    <Composition id="Trend" component={Trend} width={1920} height={1080} fps={30} durationInFrames={667} />
    <Composition id="Close" component={Close} width={1920} height={1080} fps={30} durationInFrames={572} />
  </Folder>
</>;
