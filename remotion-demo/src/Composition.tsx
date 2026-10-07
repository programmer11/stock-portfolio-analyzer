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
  <Series.Sequence name="Welcome" durationInFrames={334}><Welcome /></Series.Sequence>
  <Series.Sequence name="Import" durationInFrames={417}><Import /></Series.Sequence>
  <Series.Sequence name="Manual" durationInFrames={365}><Manual /></Series.Sequence>
  <Series.Sequence name="Holdings" durationInFrames={450}><Holdings /></Series.Sequence>
  <Series.Sequence name="Breakdown" durationInFrames={429}><Breakdown /></Series.Sequence>
  <Series.Sequence name="Returns" durationInFrames={391}><Returns /></Series.Sequence>
  <Series.Sequence name="Trend" durationInFrames={387}><Trend /></Series.Sequence>
  <Series.Sequence name="Close" durationInFrames={382}><Close /></Series.Sequence>
</Series>;
export const DemoCompositions = () => <>
  <Composition id="StockPortfolioDemo" component={PortfolioDemo} width={1920} height={1080} fps={30} durationInFrames={3155} />
  <Folder name="Scenes">
    <Composition id="Welcome" component={Welcome} width={1920} height={1080} fps={30} durationInFrames={334} />
    <Composition id="Import" component={Import} width={1920} height={1080} fps={30} durationInFrames={417} />
    <Composition id="Manual" component={Manual} width={1920} height={1080} fps={30} durationInFrames={365} />
    <Composition id="Holdings" component={Holdings} width={1920} height={1080} fps={30} durationInFrames={450} />
    <Composition id="Breakdown" component={Breakdown} width={1920} height={1080} fps={30} durationInFrames={429} />
    <Composition id="Returns" component={Returns} width={1920} height={1080} fps={30} durationInFrames={391} />
    <Composition id="Trend" component={Trend} width={1920} height={1080} fps={30} durationInFrames={387} />
    <Composition id="Close" component={Close} width={1920} height={1080} fps={30} durationInFrames={382} />
  </Folder>
</>;
