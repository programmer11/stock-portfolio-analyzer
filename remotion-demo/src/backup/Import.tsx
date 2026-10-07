import { SceneLayout } from "./SceneLayout";
export const Import = () => <SceneLayout
  title={"Import your\ntrade history."}
  note={"Upload a CSV with ticker, date, BUY or SELL, quantity and price."}
  kicker={"01 / INPUT"}
  asset={"02-loaded"}
  step={2}
  box={[380, 280, 550, 305]}
/>;
