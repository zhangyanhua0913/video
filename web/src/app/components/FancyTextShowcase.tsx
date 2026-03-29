import { Sparkles, Highlighter, Type, MessageSquareText, BadgeCheck } from "lucide-react";

export type FancyTemplateId =
  | "sticker"
  | "neon"
  | "karaoke"
  | "subtitle"
  | "default"
  | "transparent_outline"
  | "transparent_neon"
  | "transparent_subtitle"
  | "promo_tag"
  | "brand_banner"
  | "news_flash"
  | "luxury_minimal"
  | "yellow_black_bold"
  | "yellow_black_glow"
  | "yellow_orange_flash"
  | "black_plate_yellow"
  | "popup_zoom_gold"
  | "popup_bounce_red"
  | "popup_neon_flash"
  | "popup_explosion"
  | "popup_scale_purple"
  | "popup_shake_yellow";

type FancyTemplate = {
  id: FancyTemplateId;
  name: string;
  sample: string;
  hint: string;
  className: string;
};

const TEMPLATES: FancyTemplate[] = [
  {
    id: "sticker",
    name: "贴纸描边",
    sample: "爆款推荐",
    hint: "白色粗描边 + 半透明底板",
    className:
      "rounded-2xl border-2 border-white/90 bg-white/20 px-5 py-3 text-yellow-100 [text-shadow:0_1px_0_rgba(0,0,0,0.45),0_0_4px_rgba(0,0,0,0.22)] [-webkit-text-stroke:1px_rgba(255,255,255,0.9)] shadow-[0_10px_30px_rgba(0,0,0,0.28)] backdrop-blur-md",
  },
  {
    id: "neon",
    name: "霓虹描边",
    sample: "今晚就冲",
    hint: "黑描边 + 青色发光",
    className:
      "rounded-xl border border-cyan-300/60 bg-slate-900/70 px-5 py-3 text-cyan-200 [text-shadow:0_0_4px_rgba(34,211,238,0.7),0_0_8px_rgba(34,211,238,0.45)] [-webkit-text-stroke:1px_rgba(0,0,0,0.85)]",
  },
  {
    id: "karaoke",
    name: "卡拉 OK 描边",
    sample: "一起开唱吧",
    hint: "厚描边字幕条",
    className:
      "rounded-xl border border-yellow-300/70 bg-black/65 px-5 py-3 text-yellow-200 [-webkit-text-stroke:1px_rgba(0,0,0,0.85)] shadow-[inset_0_0_0_1px_rgba(253,224,71,0.35)]",
  },
  {
    id: "subtitle",
    name: "电影字幕",
    sample: "一句话讲重点",
    hint: "稳重信息表达",
    className: "rounded-lg bg-black/70 px-5 py-3 text-white [-webkit-text-stroke:0.7px_rgba(0,0,0,0.85)]",
  },
  {
    id: "default",
    name: "基础描边",
    sample: "文本模板",
    hint: "通用描边风格",
    className: "rounded-lg bg-slate-800/55 px-5 py-3 text-slate-100 [-webkit-text-stroke:0.8px_rgba(0,0,0,0.8)]",
  },
  {
    id: "transparent_outline",
    name: "透明描边",
    sample: "无底板清晰字",
    hint: "无背景，仅白色描边",
    className:
      "rounded-lg bg-transparent px-5 py-3 text-white [text-shadow:0_1px_0_rgba(0,0,0,0.35)] [-webkit-text-stroke:1.2px_rgba(255,255,255,0.9)]",
  },
  {
    id: "transparent_neon",
    name: "透明霓虹",
    sample: "轻发光字幕",
    hint: "无底板，弱霓虹",
    className:
      "rounded-lg bg-transparent px-5 py-3 text-cyan-200 [text-shadow:0_0_4px_rgba(34,211,238,0.45)] [-webkit-text-stroke:0.8px_rgba(0,0,0,0.8)]",
  },
  {
    id: "transparent_subtitle",
    name: "透明字幕",
    sample: "简洁信息字",
    hint: "无底板，轻描边",
    className: "rounded-lg bg-transparent px-5 py-3 text-white [-webkit-text-stroke:0.8px_rgba(0,0,0,0.8)]",
  },
  {
    id: "promo_tag",
    name: "促销价签",
    sample: "限时特价",
    hint: "电商促销感",
    className:
      "rounded-lg border border-yellow-300/90 bg-red-500/35 px-5 py-3 text-yellow-100 [-webkit-text-stroke:1px_rgba(120,53,15,0.9)]",
  },
  {
    id: "brand_banner",
    name: "品牌横幅",
    sample: "品牌甄选",
    hint: "品牌广告条",
    className:
      "rounded-md border border-white/80 bg-black/55 px-5 py-3 text-white tracking-wider [-webkit-text-stroke:0.6px_rgba(0,0,0,0.85)]",
  },
  {
    id: "news_flash",
    name: "快讯条",
    sample: "新品速递",
    hint: "资讯播报风",
    className:
      "rounded-md border border-white/90 bg-blue-500/35 px-5 py-3 text-white [-webkit-text-stroke:0.6px_rgba(0,0,0,0.8)]",
  },
  {
    id: "luxury_minimal",
    name: "高端极简",
    sample: "旗舰系列",
    hint: "高级感排版",
    className:
      "rounded-md bg-transparent px-5 py-3 text-slate-100 tracking-[0.12em] [-webkit-text-stroke:0.6px_rgba(0,0,0,0.78)]",
  },
    {
      id: "yellow_black_bold",
      name: "黄字黑粗描边",
      sample: "在他的照片里",
      hint: "同款短视频字幕风",
      className:
        "rounded-md bg-transparent px-5 py-3 text-[#F2D10A] [text-shadow:0_0_0_#000] [-webkit-text-stroke:2px_#000] [paint-order:stroke_fill]",
    },
    {
      id: "yellow_black_glow",
      name: "金黄发光描边",
      sample: "限时秒杀",
      hint: "黄字黑描边 + 橙色微发光",
      className:
        "rounded-md bg-transparent px-5 py-3 text-[#FFD54A] [text-shadow:0_0_5px_rgba(255,153,0,0.6)] [-webkit-text-stroke:2px_rgba(0,0,0,0.95)] [paint-order:stroke_fill]",
    },
    {
      id: "yellow_orange_flash",
      name: "橙黄高亮字",
      sample: "限时开抢",
      hint: "更亮更抓眼",
      className:
        "rounded-md bg-transparent px-5 py-3 text-[#FFC61A] [text-shadow:0_0_5px_rgba(255,138,0,0.55)] [-webkit-text-stroke:1.8px_rgba(44,26,0,0.95)] [paint-order:stroke_fill]",
    },
    {
      id: "black_plate_yellow",
      name: "黑底黄字牌",
      sample: "限时秒杀",
      hint: "图中同款牌匾感",
      className:
        "rounded-md bg-black/40 px-5 py-3 text-[#FFD54A] [-webkit-text-stroke:2px_rgba(0,0,0,0.95)] [paint-order:stroke_fill]",
    },
  {
    id: "popup_zoom_gold",
    name: "弹出-金色爆炸",
    sample: "哇哦！",
    hint: "高亮金边",
    className:
      "rounded-md bg-transparent px-5 py-3 text-white [text-shadow:0_0_6px_rgba(255,215,0,0.6)] [-webkit-text-stroke:2px_rgba(255,215,0,0.95)]",
  },
  {
    id: "popup_bounce_red",
    name: "弹出-红色冲击",
    sample: "注意！",
    hint: "强烈冲击感",
    className:
      "rounded-md bg-transparent px-5 py-3 text-red-500 [text-shadow:0_0_5px_rgba(255,69,0,0.55)] [-webkit-text-stroke:2px_rgba(253,224,71,0.95)]",
  },
  {
    id: "popup_neon_flash",
    name: "弹出-霓虹闪烁",
    sample: "超赞！",
    hint: "霓虹闪现",
    className:
      "rounded-md bg-transparent px-5 py-3 text-cyan-300 [text-shadow:0_0_5px_rgba(34,211,238,0.6)] [-webkit-text-stroke:1.6px_rgba(236,72,153,0.95)]",
  },
  {
    id: "popup_explosion",
    name: "弹出-炸裂特效",
    sample: "爆了！",
    hint: "爆发感最强",
    className:
      "rounded-md bg-transparent px-5 py-3 text-white [text-shadow:0_0_7px_rgba(249,115,22,0.65)] [-webkit-text-stroke:2px_rgba(239,68,68,0.95)]",
  },
  {
    id: "popup_scale_purple",
    name: "弹出-紫色缩放",
    sample: "精彩！",
    hint: "优雅弹出",
    className:
      "rounded-md bg-transparent px-5 py-3 text-violet-500 [text-shadow:0_0_5px_rgba(244,114,182,0.45)] [-webkit-text-stroke:1.8px_rgba(255,255,255,0.9)]",
  },
  {
    id: "popup_shake_yellow",
    name: "弹出-黄色震动",
    sample: "震撼！",
    hint: "漫画震感",
    className:
      "rounded-md bg-transparent px-5 py-3 text-yellow-300 [text-shadow:0_0_4px_rgba(251,191,36,0.45)] [-webkit-text-stroke:2.2px_rgba(0,0,0,0.95)]",
  },
];

interface FancyTextShowcaseProps {
  selectedTemplate: FancyTemplateId;
  onSelectTemplate: (id: FancyTemplateId) => void;
}

export function FancyTextShowcase({ selectedTemplate, onSelectTemplate }: FancyTextShowcaseProps) {
  return (
    <div className="space-y-4">
      <div className="rounded-lg border border-purple-200/70 bg-gradient-to-br from-indigo-50/80 via-fuchsia-50/70 to-pink-50/70 p-2.5">
        <div className="mb-1.5 flex items-center gap-1.5 text-[11px] font-bold text-purple-700">
          <Sparkles className="h-3 w-3" />
          花字模板预览
        </div>
        <div className="max-h-[420px] overflow-y-auto pr-1">
          <div className="grid grid-cols-2 gap-1.5 md:grid-cols-4">
          {TEMPLATES.map((item) => {
            const active = selectedTemplate === item.id;
            return (
              <button
                key={item.id}
                type="button"
                onClick={() => onSelectTemplate(item.id)}
                className={`group rounded-md border p-2 text-left transition-all ${
                  active
                    ? "border-purple-400 bg-white shadow-[0_4px_12px_rgba(147,51,234,0.2)]"
                    : "border-purple-100 bg-white/80 hover:border-purple-300 hover:bg-white"
                }`}
              >
                <div className="mb-1 flex items-center justify-between">
                  <div className="text-[11px] font-semibold text-slate-700">{item.name}</div>
                  {active ? <BadgeCheck className="h-3 w-3 text-purple-600" /> : <Type className="h-3 w-3 text-slate-400" />}
                </div>
                <div className="mb-1 flex min-h-[38px] items-center justify-center rounded-md bg-slate-900/15 p-1">
                  <span className={`${item.className} text-base font-black tracking-wide`}>{item.sample}</span>
                </div>
                <div className="flex items-center gap-1 text-[10px] text-slate-500">
                  <Highlighter className="h-2.5 w-2.5" />
                  {item.hint}
                </div>
              </button>
            );
          })}
          </div>
        </div>
      </div>
      <div className="rounded-md border border-pink-200/70 bg-gradient-to-r from-pink-50/80 to-rose-50/70 p-2 text-[10px] text-pink-700">
        <div className="mb-1 flex items-center gap-1.5 font-semibold">
          <MessageSquareText className="h-2.5 w-2.5" />
          说明
        </div>
        已选模板会在后端用 FFmpeg 的描边参数渲染，实际视频效果会比预览更明显。
      </div>
    </div>
  );
}
