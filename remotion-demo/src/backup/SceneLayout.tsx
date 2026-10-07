import { Audio } from "@remotion/media";
import { AbsoluteFill, CanvasImage, Easing, interpolate, staticFile, useCurrentFrame, useVideoConfig } from "remotion";

type Props = {
  title: string;
  note: string;
  kicker: string;
  asset: string;
  step: number;
  box: number[];
};

export const SceneLayout = ({title, note, kicker, asset, step, box}: Props) => {
  const frame = useCurrentFrame();
  const {durationInFrames} = useVideoConfig();
  const clamp = {extrapolateLeft: "clamp", extrapolateRight: "clamp"} as const;
  return (
    <AbsoluteFill style={{background: "#091426", color: "#f5f8ff", fontFamily: "Arial, sans-serif"}}>
      <Audio src={staticFile(`audio/american/${asset}.mp3`)} />
      <div style={{position: "absolute", left: 80, top: 64, fontSize: 24, fontWeight: 700, letterSpacing: 3, color: "#b0c2da"}}>STOCK PORTFOLIO ANALYZER</div>
      <div style={{position: "absolute", right: 80, top: 64, fontSize: 24, color: "#b0c2da"}}>PRODUCT WALKTHROUGH · {String(step).padStart(2, "0")} / 08</div>
      <div style={{position: "absolute", left: 80, top: 260, width: 500,
        opacity: interpolate(frame, [0, 20], [0, 1], clamp),
        translate: interpolate(frame, [0, 28], ["0px 28px", "0px 0px"], {...clamp, easing: Easing.bezier(0.16, 1, 0.3, 1)})}}>
        <div style={{fontSize: 24, fontWeight: 700, letterSpacing: 3, color: "#63d9c5", marginBottom: 30}}>{kicker}</div>
        <div style={{fontSize: 70, fontWeight: 700, letterSpacing: -3, lineHeight: 1.05, whiteSpace: "pre-line"}}>{title}</div>
        <div style={{height: 4, width: 72, background: "#63d9c5", marginTop: 38, marginBottom: 32}} />
        <div style={{fontSize: 32, lineHeight: 1.45, color: "#b0c2da", maxWidth: 460}}>{note}</div>
      </div>
      <div style={{position: "absolute", left: 640, top: 155, width: 1200, height: 810, borderRadius: 20,
        overflow: "hidden", background: "white", boxShadow: "0 24px 80px #0008",
        opacity: interpolate(frame, [3, 25], [0, 1], clamp),
        translate: interpolate(frame, [0, 30], ["30px 0px", "0px 0px"], {...clamp, easing: Easing.bezier(0.16, 1, 0.3, 1)})}}>
        <CanvasImage src={staticFile(`screens/${asset}.png`)} style={{position: "absolute", left: -277, top: -10, width: 1477, height: 831}} />
        <div style={{position: "absolute", left: (box[0]-300)*0.923, top: box[1]*0.923-10,
          width: box[2]*0.923, height: box[3]*0.923, border: "4px solid #20b59e", borderRadius: 12,
          boxShadow: "0 0 0 4px #20b59e22", pointerEvents: "none",
          opacity: interpolate(frame, [45, 65, durationInFrames-25, durationInFrames-5], [0, 1, 1, 0], clamp)}} />
      </div>
      <div style={{position: "absolute", left: 80, bottom: 55, fontSize: 22, color: "#8fa5c2"}}>SAMPLE PORTFOLIO · LAST-TRADE PRICES · LIVE PRICING OFF</div>
      <div style={{position: "absolute", right: 80, bottom: 55, fontSize: 22, color: "#8fa5c2"}}>Import → Explore → Track</div>
      <div style={{position: "absolute", left: 0, bottom: 0, height: 5, background: "#63d9c5",
        width: interpolate(frame, [0, durationInFrames-1], [(step-1)*240, step*240], clamp)}} />
    </AbsoluteFill>
  );
};
