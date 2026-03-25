import { useMemo, useState } from "react";
import { Play, Search, Shuffle, Volume2 } from "lucide-react";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Label } from "./ui/label";
import { RadioGroup, RadioGroupItem } from "./ui/radio-group";
import { toast } from "sonner";

interface VoiceOption {
  id: string;
  name: string;
  description?: string;
}

interface VoiceSelectorProps {
  selectedVoice: string;
  onVoiceChange: (voiceId: string) => void;
  onPreview: (voiceId: string) => void;
  voices?: VoiceOption[];
}

function shortenText(text: string, maxLength: number): string {
  if (!text) {
    return "";
  }
  return text.length > maxLength ? `${text.slice(0, maxLength)}...` : text;
}

const DEFAULT_VOICES: VoiceOption[] = [
  { id: "xiaoyun", name: "晓云", description: "默认温柔女声" },
  { id: "yunyang", name: "云扬", description: "默认沉稳男声" },
  { id: "xiaochen", name: "晓辰", description: "活泼年轻风格" },
  { id: "yunxiao", name: "云霄", description: "明亮男声风格" },
];

export function VoiceSelector({ selectedVoice, onVoiceChange, onPreview, voices }: VoiceSelectorProps) {
  const [keyword, setKeyword] = useState("");
  const list = voices && voices.length > 0 ? voices : DEFAULT_VOICES;

  const filteredList = useMemo(() => {
    const query = keyword.trim().toLowerCase();
    if (!query) {
      return list;
    }
    return list.filter((voice) => {
      const name = (voice.name || "").toLowerCase();
      const desc = (voice.description || "").toLowerCase();
      const id = (voice.id || "").toLowerCase();
      return name.includes(query) || desc.includes(query) || id.includes(query);
    });
  }, [keyword, list]);

  const handleRandomVoice = () => {
    const randomVoice = filteredList[Math.floor(Math.random() * filteredList.length)] || list[Math.floor(Math.random() * list.length)];
    if (!randomVoice) {
      return;
    }
    onVoiceChange(randomVoice.id);
    toast.success(`已随机选择音色：${randomVoice.name}`);
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2.5">
          <div className="relative">
            <div className="absolute inset-0 rounded-xl bg-cyan-400/30 blur-md" />
            <div className="relative rounded-xl bg-gradient-to-br from-cyan-500 to-blue-600 p-1.5">
              <Volume2 className="h-4 w-4 text-white" />
            </div>
          </div>
          <h3 className="bg-gradient-to-r from-cyan-700 to-blue-700 bg-clip-text font-semibold text-transparent">选择配音音色</h3>
        </div>

        <Button
          onClick={handleRandomVoice}
          size="sm"
          variant="outline"
          className="gap-1.5 border-cyan-200 font-semibold text-cyan-700 shadow-sm transition-all hover:border-cyan-400 hover:bg-cyan-50"
        >
          <Shuffle className="h-3.5 w-3.5" />
          随机
        </Button>
      </div>

      <div className="relative">
        <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-cyan-600/70" />
        <Input
          value={keyword}
          onChange={(e) => setKeyword(e.target.value)}
          placeholder="搜索音色名称或编码"
          className="border-cyan-200 bg-cyan-50/40 pl-9"
        />
      </div>

      <RadioGroup value={selectedVoice} onValueChange={onVoiceChange}>
        <div className="grid h-[240px] gap-3 overflow-y-auto pr-1 scrollbar-thin scrollbar-thumb-cyan-300 scrollbar-track-transparent hover:scrollbar-thumb-cyan-400">
          {filteredList.map((voice) => (
            <div
              key={voice.id}
              onClick={() => onVoiceChange(voice.id)}
              onKeyDown={(event) => {
                if (event.key === "Enter" || event.key === " ") {
                  event.preventDefault();
                  onVoiceChange(voice.id);
                }
              }}
              role="button"
              tabIndex={0}
              className={`flex items-center justify-between rounded-xl border-2 p-4 backdrop-blur transition-all duration-300 ${
                selectedVoice === voice.id
                  ? "border-cyan-400 bg-gradient-to-r from-cyan-50/80 to-blue-50/80 shadow-lg shadow-cyan-200/60"
                  : "border-gray-200/80 bg-white/40 hover:border-cyan-300"
              }`}
            >
              <div className="flex items-center gap-3">
                <RadioGroupItem value={voice.id} id={voice.id} className="border-cyan-500 text-cyan-600" />
                <Label htmlFor={voice.id} className="max-w-[170px] cursor-pointer">
                  <div className="space-y-1">
                    <span className="block truncate font-semibold text-gray-800">{shortenText(voice.name, 18)}</span>
                    <p className="text-xs leading-4 whitespace-normal break-all text-gray-600">{shortenText(voice.description || voice.id, 50)}</p>
                  </div>
                </Label>
              </div>

              <Button
                onClick={(event) => {
                  event.stopPropagation();
                  onPreview(voice.id);
                }}
                size="sm"
                variant="outline"
                className="gap-1 border-cyan-300 font-medium text-cyan-700 transition-all hover:border-cyan-500 hover:bg-cyan-50"
              >
                <Play className="h-3 w-3" />
                试听
              </Button>
            </div>
          ))}
          {filteredList.length === 0 && (
            <div className="rounded-xl border border-dashed border-cyan-300 bg-cyan-50/40 p-4 text-center text-sm text-cyan-700">未找到匹配音色</div>
          )}
        </div>
      </RadioGroup>
    </div>
  );
}
