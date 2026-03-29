import { Sparkles, Type, BadgeCheck, Zap } from "lucide-react";

export type PopupTemplateId =
  | "auto"
  | "popup_zoom_gold"
  | "popup_bounce_red"
  | "popup_neon_flash"
  | "popup_explosion"
  | "popup_scale_purple"
  | "popup_shake_yellow";

type PopupTemplate = {
  id: PopupTemplateId;
  name: string;
  sample: string;
  hint: string;
  className: string;
};

const POPUP_TEMPLATES: PopupTemplate[] = [
  {
    id: "auto",
    name: "自动",
    sample: "自动匹配",
    hint: "跟随当前花字模板",
    className:
      "rounded-md bg-slate-900/30 px-5 py-3 text-white [-webkit-text-stroke:1px_rgba(0,0,0,0.85)]",
  },
  {
    id: "popup_zoom_gold",
    name: "金色爆炸",
    sample: "限时抢购",
    hint: "亮金边+上跳",
    className:
      "rounded-md bg-transparent px-5 py-3 text-[#FFF8D9] [text-shadow:0_0_6px_rgba(255,159,28,0.72)] [-webkit-text-stroke:2px_rgba(255,213,74,0.95)]",
  },
  {
    id: "popup_bounce_red",
    name: "红色冲击",
    sample: "马上开抢",
    hint: "红黄冲击感",
    className:
      "rounded-md bg-transparent px-5 py-3 text-[#FF3B30] [text-shadow:0_0_6px_rgba(255,90,31,0.75)] [-webkit-text-stroke:2px_rgba(255,224,102,0.95)]",
  },
  {
    id: "popup_neon_flash",
    name: "霓虹闪烁",
    sample: "惊喜加码",
    hint: "霓虹轻浮动",
    className:
      "rounded-md bg-transparent px-5 py-3 text-[#B8F6FF] [text-shadow:0_0_7px_rgba(34,211,238,0.85)] [-webkit-text-stroke:1.8px_rgba(255,79,216,0.95)]",
  },
  {
    id: "popup_explosion",
    name: "炸裂特效",
    sample: "全场狂欢",
    hint: "爆发感最强",
    className:
      "rounded-md bg-transparent px-5 py-3 text-[#FFF7E8] [text-shadow:0_0_8px_rgba(255,122,0,0.88)] [-webkit-text-stroke:2.2px_rgba(255,45,45,0.95)]",
  },
  {
    id: "popup_scale_purple",
    name: "紫色缩放",
    sample: "精彩继续",
    hint: "优雅弹出",
    className:
      "rounded-md bg-transparent px-5 py-3 text-[#9B5DE5] [text-shadow:0_0_6px_rgba(244,114,182,0.72)] [-webkit-text-stroke:2px_rgba(253,226,255,0.95)]",
  },
  {
    id: "popup_shake_yellow",
    name: "黄色震动",
    sample: "注意注意",
    hint: "左右抖动",
    className:
      "rounded-md bg-transparent px-5 py-3 text-[#FFD93D] [text-shadow:0_0_6px_rgba(255,183,3,0.68)] [-webkit-text-stroke:2.2px_rgba(0,0,0,0.95)]",
  },
];

interface PopupTemplateShowcaseProps {
  selectedTemplate: PopupTemplateId;
  onSelectTemplate: (id: PopupTemplateId) => void;
}

export function PopupTemplateShowcase({ selectedTemplate, onSelectTemplate }: PopupTemplateShowcaseProps) {
  return (
    <div className="space-y-4">
      <div className="rounded-lg border border-amber-200/70 bg-gradient-to-br from-amber-50/80 via-orange-50/70 to-rose-50/70 p-2.5">
        <div className="mb-1.5 flex items-center gap-1.5 text-[11px] font-bold text-amber-700">
          <Sparkles className="h-3 w-3" />
          弹出模板预览
        </div>
        <div className="grid grid-cols-2 gap-1.5 md:grid-cols-4">
          {POPUP_TEMPLATES.map((item) => {
            const active = selectedTemplate === item.id;
            return (
              <button
                key={item.id}
                type="button"
                onClick={() => onSelectTemplate(item.id)}
                className={`group rounded-md border p-2 text-left transition-all ${
                  active
                    ? "border-amber-400 bg-white shadow-[0_4px_12px_rgba(245,158,11,0.25)]"
                    : "border-amber-100 bg-white/80 hover:border-amber-300 hover:bg-white"
                }`}
              >
                <div className="mb-1 flex items-center justify-between">
                  <div className="text-[11px] font-semibold text-slate-700">{item.name}</div>
                  {active ? <BadgeCheck className="h-3 w-3 text-amber-600" /> : <Type className="h-3 w-3 text-slate-400" />}
                </div>
                <div className="mb-1 flex min-h-[38px] items-center justify-center rounded-md bg-slate-900/15 p-1">
                  <span className={`${item.className} text-base font-black tracking-wide`}>{item.sample}</span>
                </div>
                <div className="flex items-center gap-1 text-[10px] text-slate-500">
                  <Zap className="h-2.5 w-2.5" />
                  {item.hint}
                </div>
              </button>
            );
          })}
        </div>
      </div>
    </div>
  );
}
